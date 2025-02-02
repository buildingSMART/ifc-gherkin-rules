import functools
import json
import re
from utils import misc
from functools import wraps
import ifcopenshell
from behave import step
import inspect
from operator import attrgetter
import ast
from validation_results import ValidationOutcome, OutcomeSeverity, ValidationOutcomeCode
from behave import register_type

from behave.runner import Context
from typing import Any


"""
DECORATORS FOR STEPS
"""
def global_rule(func):
    """
    Use this decorator when the rule applies to the whole stack instead of a single instance.
    For instance
    @gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity}')
    @gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity} {tail:SubtypeHandling}')
    @global_rule
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.global_rule = True
    return wrapper

def full_stack_rule(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.full_stack_rule = True
    return wrapper

class gherkin_ifc():
    """
    Use this decorator before every step definition instead of @given and @then
    For instance;
    @gherkin_ifc.step("{attribute} {comparison_op:equal_or_not_equal} {value}")
    """
    def step(step_text):
        def wrapped_step(func):
            return step(step_text)(execute_step(func))

        return wrapped_step


def register_enum_type(cls):
    """
    Use this decorator to register an enum type for behave, e.g.
    @register_enum_type
    class SubtypeHandling(Enum):
        INCLUDE = "including subtypes"
        EXCLUDE = "excluding subtypes"
    """
    register_type(**{cls.__name__: cls})
    return cls


def generate_error_message(context, errors):
    """
    Function to trigger the behave error mechanism by raising an exception so that errors are printed to the console.
    """
    assert not errors, "Errors occured:" + ''.join(f'\n - {error}' for error in errors)


"""
Core validation handling functions operate as follows: 
The execute_step function is triggered by the gherkin_ifc decorator and manages the logic for each step. 
In case the step_type is 'Given', the handle_given function is invoked, and similarly, the handle_then function is called when the step_type is 'Then'. 
"""


def execute_step(fn):
    is_global_rule = False
    is_full_stack_rule = False
    while hasattr(fn, '__wrapped__'):
        # unwrap the function if it is wrapped by a decorator in case of catching multiple string platterns
        is_global_rule = is_global_rule or getattr(fn, 'global_rule', False)
        is_full_stack_rule = is_full_stack_rule or getattr(fn, 'full_stack_rule', False)
        fn = fn.__wrapped__

    @wraps(fn)
    def inner(context, **kwargs):
        context.is_global_rule = is_global_rule
        context.is_full_stack_rule = is_full_stack_rule

        """
        This section of code performs two primary checks:

        1. Applicability Check:
        Check for file-wide applicability with the 'context.instances' variable (set to either True or False)
        In case of non-applicability, further steps are are skipped to optimize performance and avoid unnecessary computations.
        For instance, when a rule requires IFC schema version IFC4X3 but the tested file contains schema version IFC2X3

        2. Handling 'Given' or 'Then' Statements:
        The code differentiates and appropriately handles the logic based on whether the statement is a 'Given' or a 'Then' statement.
        'Given' statements are used to establish the applicability of either the file or instances within the file.
        'Then' statements are used to run the checks on the previously defined instances or file.

        Data is circulated using the 'behave-context' and is ultimately stored in the database, as 'ValidationOutcome' corresponds to a database column.
        """
        # this basically serves as placeholder, later only the highest severity
        # outcomes are retained, so the state is initiated to NOT_APPLICABLE
        validation_outcome = ValidationOutcome(
            outcome_code=ValidationOutcomeCode.NOT_APPLICABLE,  # "NOT_APPLICABLE", Given statement with schema/mvd check  # deactivated until code table is added to django model
            observed=None,
            expected=None,
            feature=context.feature.name,
            feature_version=misc.define_feature_version(context),
            severity=OutcomeSeverity.NOT_APPLICABLE,
            validation_task_id=context.validation_task_id
        )
        context.gherkin_outcomes.append(validation_outcome)

        if getattr(context, 'applicable', True):
            step_type = context.step.step_type
            if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
                handle_given(context, fn, **kwargs)
            elif step_type.lower() == 'then':
                handle_then(context, fn, **kwargs)

    return inner


def handle_given(context, fn, **kwargs):
    """
    'Given' statements include four distinct functionalities.
    1) Set file-wide context.applicable. No further steps (given or then) have to be executed when context.applicability is set to False
    2) Set an initial set of instances ('Given an .IfcAlignment.' -> [IfcAlignm, IfcAlignm, IfcAlign])
    3) Filter the set of IfcAlignment based on a value ('Given attribute == X' -> [IfcAlignm, None, IfcAlignm])
    4) Set instances to a given attribute ('Given Its attribute .Representation.') -> [IfcProdDefShape, IfcProdDefShape, IfcProdDefShape]
    """
    if 'inst' not in inspect.getargs(fn.__code__).args:
        gen = fn(context, **kwargs)
        if gen: # (2) Set initial set of instances
            insts = list(gen)
            context.instances = list(map(attrgetter('instance_id'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, insts)))
            pass
        else:
            pass # (1) -> context.applicable is set within the function ; replace this with a simple True/False and set applicability here?
    else:
        context._push('attribute') # for attribute stacking
        depth = next(map(int, re.findall('at depth (\d+)$', context.step.name)), 0)
        if depth:
            context.instances = list(filter(None, map_given_state(context.instances, fn, context, depth=depth, **kwargs)))
        else:
            context.instances = map_given_state(context.instances, fn, context, **kwargs)


def apply_operation(fn, inst, context, **kwargs):
    results = fn(context, inst, **kwargs)  
    return misc.do_try(lambda: list(map(attrgetter('instance_id'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, results)))[0], None)


def map_given_state(values, fn, context, depth=0, **kwargs):
    def is_nested(val):
        return isinstance(val, (tuple, list))

    def should_apply(values, depth):
        if depth == 0:
            return not is_nested(values)
        else:
            return is_nested(values) and all(should_apply(v, depth-1) for v in values if v is not None)

    if should_apply(values, depth):
        return None if values is None else apply_operation(fn, values, context, **kwargs)
    elif is_nested(values):
        new_depth = depth if depth > 0 else 0
        return type(values)(map_given_state(v, fn, context, new_depth, **kwargs) for v in values)
    else:
        return None if values is None else apply_operation(fn, values, context, **kwargs)


def handle_then(context, fn, **kwargs):
    instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])

    # if 'instances' are not actual ifcopenshell.entity_instance objects, but e.g. tuple of string values then
    # get the actual instances from the stack tree
    activation_instances = misc.do_try(lambda: misc.get_stack_tree(context)[-1], instances)

    # ensure the rule is not activated when there are no instances
    # in case there are no instances but the rule is applicable (e.g. SPS001),
    # then the rule is still activated and will return either a pass or an error
    is_activated = any(misc.recursive_flatten(instances)) if instances else context.applicable
    if is_activated:
        context.gherkin_outcomes.append(
            ValidationOutcome(
                outcome_code=ValidationOutcomeCode.EXECUTED,  # "Executed", but not no error/pass/warning #deactivated for now
                observed=None,
                expected=None,
                feature=context.feature.name,
                feature_version=misc.define_feature_version(context),
                severity=OutcomeSeverity.EXECUTED,
                validation_task_id=context.validation_task_id
            )
        )

    def map_then_state(items, fn, context, current_path=[], depth=0, **kwargs):
        def apply_then_operation(fn, inst, context, current_path, depth=0, **kwargs):
            if inst is None:
                return
            if context.is_full_stack_rule:
                x = misc.get_stack_tree(context)[::-1]
                value_path = []
                idxs = [current_path[0:i+1] for i in range(len(current_path))]
                for idx, layer in zip(idxs, x):
                    v = layer
                    while idx:
                        i, *idx = idx
                        v = v[i]
                    value_path.append(v)
                kwargs = kwargs | {'path': value_path}
            top_level_index = current_path[0] if current_path else None
            activation_inst = inst if not current_path or activation_instances[top_level_index] is None else activation_instances[top_level_index]
# TODO: refactor into a more general solution that works for all rules
            if "GEM051" in context.feature.name and context.is_global_rule:
                activation_inst = activation_instances[0]
            if isinstance(activation_inst, ifcopenshell.file):
                activation_inst = None  # in case of blocking IFC101 check, for safety set explicitly to None

            step_results = list(filter(lambda x: x.severity in [OutcomeSeverity.ERROR, OutcomeSeverity.WARNING], fn(context, inst=inst, **kwargs) or []))
            for result in step_results:
                displayed_inst_override_trigger = "and display entity instance"
                displayed_inst_override = displayed_inst_override_trigger in context.step.name.lower()
                inst_to_display = inst if displayed_inst_override else activation_inst
                instance_id = safe_method_call(inst_to_display, 'id', None)

                validation_outcome = ValidationOutcome(
                    outcome_code=get_outcome_code(result, context),
                    observed=expected_behave_output(context, result.observed, is_observed=True),
                    expected=expected_behave_output(context, result.expected),
                    feature=context.feature.name,
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.WARNING if any(tag.lower() == "industry-practice" for tag in context.feature.tags) else OutcomeSeverity.ERROR,
                    instance_id=instance_id,
                    validation_task_id=context.validation_task_id
                )
                # suppress the 'display_entity' trigger text if it is used as part of the expected value
                validation_outcome.expected = (
                    validation_outcome.expected.split(displayed_inst_override_trigger)[0].strip()
                    if displayed_inst_override_trigger in validation_outcome.expected
                    else validation_outcome.expected)

                context.gherkin_outcomes.append(validation_outcome)
                context.scenario_outcome_state.append((len(context.gherkin_outcomes)-1, {'scenario': context.scenario.name, 'last_step': context.scenario.steps[-1], 'instance_id': instance_id}))

            # Currently, we should not inject passed outcomes for each individual instance to the databse
            # if not step_results:

            #     validation_outcome = ValidationOutcome(
            #         outcome_code=ValidationOutcomeCode.PASSED,  # todo @gh "Rule passed" # deactivated until code table is added to django model
            #         observed=None,
            #         expected=None,
            #         feature=context.feature.name,
            #         feature_version=misc.define_feature_version(context),
            #         severity=OutcomeSeverity.PASSED,
            #         instance_id = safe_method_call(activation_inst, 'id', None),
            #         validation_task_id=context.validation_task_id
            #     )
            #     context.gherkin_outcomes.append(validation_outcome)


        def is_nested(val):
            return isinstance(val, (tuple, list))

        def should_apply(items, depth):
            if depth == 0:
                return not is_nested(items)
            else:
                return is_nested(items) and all(should_apply(v, depth-1) for v in items if v is not None)

        if context.is_global_rule:
            return apply_then_operation(fn, [items], context, current_path=None, **kwargs)
        elif should_apply(items, depth):
            return apply_then_operation(fn, items, context, current_path, **kwargs)
        elif is_nested(items):
            new_depth = depth if depth > 0 else 0
            return type(items)(map_then_state(v, fn, context, current_path + [i], new_depth, **kwargs) for i, v in enumerate(items))
        else:
            return apply_then_operation(fn, items, context, current_path = None, **kwargs)

    # for generate_error_message() we only care about the outcomes generated by this then-step
    # so we take note of the outcomes that already existed. This is necessary since we accumulate
    # outcomes per feature and no longer per scenario.
    num_preexisting_outcomes = len(context.gherkin_outcomes)
    depth = next(map(int, re.findall('at depth (\d+)$', context.step.name)), 0)
    map_then_state(instances, fn, context, depth = depth, **kwargs)

    # evokes behave error
    generate_error_message(context, [gherkin_outcome for gherkin_outcome in context.gherkin_outcomes[num_preexisting_outcomes:] if gherkin_outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]])


def full_stack_rule(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.full_stack_rule = True
    return wrapper


def safe_method_call(obj, method_name, default=None ):
    """
    used to retrieve an instance_id, this is normally done by calling the method on the instance.
    However, if the method does not exist, the default (blank) value is returned
    """
    method = getattr(obj, method_name, None)
    if callable(method):
        return method()
    return default

"""
Functions that are related to displaying and serializing data
"""

def display_entity_instance(inst: ifcopenshell.entity_instance) -> str : 
    """
    Displays a message for an entity instance within the expected and observed table.
    For example, an instance of IfcAlignment would be displayed as:
    '(Expected/Observed) = IfcAlignment(#27)'
    """
    return misc.do_try(lambda: f'{inst.is_a()}(#{inst.id()})', getattr(inst, 'GlobalId', inst.id()))


def serialize_item(item: Any) -> Any:
    if isinstance(item, ifcopenshell.entity_instance):
        return display_entity_instance(item)
    else:
        return item

def expected_behave_output(context: Context, data: Any, is_observed : bool = False) -> str:
    """
    When serializing values in the observed field we never produce OneOf
    """
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            pass

    match data:
        case [_, *__]:
            # Non-empty aggregate
            serialized_data = [serialize_item(item) for item in data]
            return {("value" if is_observed else "oneOf"): serialized_data}
        case bool():
            return data
        case None:
            if is_observed:
                return None
            else:
                # step name is a good proxy for expected, but not for observed
                return context.step.name
        case str():
            if context.config.userdata.get("purepythonparser", False):
                return {'schema_identifier': data}
            elif data in [x.name() for x in ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.model.schema).entities()]:
                return {'entity': data} # e.g. 'the type must be IfcCompositeCurve'
            else:
                return {'value': data} # e.g. "The value must be 'Body'"
        case ifcopenshell.entity_instance():
            return {'instance': display_entity_instance(data)}
        case dict():
            # mostly for the pse001 rule, which already yields dicts
            return data
        case set(): # object of type set is not JSONserializable
            return tuple(data)
        case _:
            return {'value': data}
        
def get_outcome_code(validation_outcome: ValidationOutcome, context: Context) -> str:
    """
    Determines the outcome code for a step result.
    Check for :
    -> optional attributes in ValidationOutcome,
    -> variables set in tags from feature_file
    """
    try:
        if hasattr(validation_outcome, 'outcome_code') and validation_outcome.outcome_code and validation_outcome.outcome_code not in ['N00010', 'X00040', 'P00010']:
            return validation_outcome.outcome_code

        valid_outcome_codes = {code.value for code in ValidationOutcomeCode}
        feature_tags = context.feature.tags
        scenario_tags = context.scenario.tags
        for tag in scenario_tags:
            if tag in valid_outcome_codes:
                return tag
        for tag in valid_outcome_codes:
            if tag in feature_tags:
                return tag
        return ValidationOutcomeCode.N00010  # Default outcome code if none is found
    except:
        # tfk: we need to return something:
        # > HOOK-ERROR in after_scenario: IntegrityError: null value in column "outcome_code" of relation "ifc_validation_outcome" violates not-null constraint
        return ValidationOutcomeCode.VALUE_ERROR
