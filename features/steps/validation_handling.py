import json
from utils import misc
from functools import wraps
import ifcopenshell
from behave import step
import sys
import os
from pathlib import Path
import inspect
import itertools
from operator import attrgetter
import ast
from validation_results import ValidationOutcome, OutcomeSeverity, ValidationOutcomeCode

from behave.runner import Context
from pydantic import BaseModel, field_validator, Field
from typing import Any, Union
from typing_extensions import Annotated


class StepOutcome(BaseModel):
    inst: Union[ifcopenshell.entity_instance, str] = None
    context: Context
    expected: Any = None
    observed: Any = None
    outcome_code: Annotated[str, Field(validate_default=True, max_length=6)] = 'N00010'
    severity : Annotated[OutcomeSeverity, Field(validate_default=True)] = OutcomeSeverity.ERROR # severity must be validated after outcome_coxd

    def __str__(cls):
        return(f"Step finished with a/an {cls.severity} {cls.outcome_code}. Expected value: {cls.expected}. Observed value: {cls.observed}")

    @field_validator('expected')
    def format_expected(cls, v):
        if isinstance(v, list):
            return json.dumps({'OneOf': v})
        return v

    @field_validator('outcome_code')
    @classmethod
    def valid_outcome_code(cls, outcome_code : str, values):
        """
        Function to validate and/or determine the outcome code of a step implementation.
        In case the outcome code is not specified in the step implementation, the outcome code of respectively the scenario and feature is used.
        The outcome code must be included in the tags of the .feature file.
        The severity of the outcome code must be either ERROR or WARNING.

        For a scenario in the .feature file with multiple tags,
        the topmost tag is utilized by default, except when overridden by user input.
        For instance, given the tags:
        @E00001
        @E00002
        Scenario: X

        @E00001 is used by default, unless the user specifies @E00002 in the step implementation.
        """
        valid_outcome_codes = {code.name for code in ValidationOutcomeCode}

        context = values.data.get('context')
        feature_tags = context.feature.tags
        scenario_tags = context.scenario.tags

        # current_rule_tags = [tag for tag in values.data.get('context').feature.tags + values.data.get('context').scenario.tags if tag in valid_outcome_codes]
        current_rule_tags = [tag for tag in feature_tags + scenario_tags if tag in valid_outcome_codes]

        default = cls.model_fields['outcome_code'].default
        if outcome_code == default:
            if scenario_tags:
                outcome_code = scenario_tags[0]
            elif valid_outcome_codes:
                for tag in valid_outcome_codes:
                    if tag in feature_tags:
                        outcome_code = tag
                        break
        else:
            # should an implementer be allowed to use a custom outcome code (i.e. not mentioned in the .feature file)?
            assert outcome_code in current_rule_tags, 'Outcome code not included in tags of .feature file'
        assert getattr(ValidationOutcomeCode, outcome_code).determine_severity().name in ["ERROR", "WARNING"], "Outcome code at step implementation must be either ERROR or WARNING"
        return outcome_code

    @field_validator('severity')
    @classmethod
    def valid_severity(cls, severity : OutcomeSeverity, values):
        """
        Validates and determines the severity of a step implementation in a Pydantic model.
        In Pydantic, field validation follows the order in which fields are defined in the model.
        Therefore, the 'severity' field will be validated after the 'outcome_code' field.

        To set the severity to 'WARNING', the 'outcome_code' must correspond to a code beginning with 'W'.
        Conversely, to set the severity to 'ERROR', the 'outcome_code' should start with 'E'.
        For example:

        - @W00001 leads to Severity 'WARNING'
        - @E00001 leads to Severity 'ERROR'
        """
        return getattr(ValidationOutcomeCode, values.data.get('outcome_code')).determine_severity().name

    # @field_validator('inst')


    # @field_validator('warning', mode='after')
    # def validate_warning(cls, value, values):
    #     pass
        # if values.get('warning'):
        #     return True

        # has_warning_tag = lambda tags: any(tag.lower() == 'warning' for tag in tags)

        # if has_warning_tag(values.get('context').scenario.tags) or \
        #    has_warning_tag(values.get('context').feature.tags):
        #     return True

        # return False


    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


def generate_error_message(context, errors):
    error_formatter = (lambda dc: json.dumps(misc.asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format([str(error) for error in errors])



def get_optional_fields(result, fields):
    """
    Extracts optional fields from a result object.

    :param result: The result object to extract fields from.
    :param fields: A list of field names to check in the result object.
    :return: A dictionary with the fields found in the result object.
    """
    return {field: getattr(result, field) for field in fields if hasattr(result, field)}

def get_stack_tree(context):
    """Returns the stack tree of the current context. To be used for 'attribute stacking', e.g. in GEM004"""
    return list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

def check_layer_for_entity_instance(i, stack_tree):
    for layer in stack_tree:
        if len(layer) > i and layer[i] and isinstance(layer[i], ifcopenshell.entity_instance):
            return layer[i]
    return None

def get_activation_instances(context, instances):
    """Returns the activation instances of the current context. To be used for 'attribute stacking', e.g. in GEM004
    In many case, context.instances are actual ifcopenshell.entity_instance objects, but in some cases they are not. For example in the following scenario:
    Given An IfcProduct
    Given Its attribute Representation
    Given its attribute Representations
    Given Its Attribute RepresentationIdentifier

    We calculate a stack tree, which is done by the function get_stack_tree(context). The stack tree is a list of lists, where each list represents a layer of the stack.
    In the example above, this would look something like this:
    [(None), ('Value', 'Axis')]
    [(IfcShapeRepr, IfcShapeRepr), (IfcShapeRepr, IfcShapeRepr)]
    [IfcProductDefintionShape, IfcProductDefinitionShape]
    [IfcRoof, IfcSlab]

    Note that each layer is formatted in the same way as the previous layer. This is done by the misc.map_state function.

    The activation_instance is then the first instance in the stack tree that is an actual ifcopenshell.entity_instance object.
    In this case, this would be IfcProductDefinitionShape.
    """
    stack_tree = get_stack_tree(context)
    if isinstance(stack_tree[0], list):
        return [check_layer_for_entity_instance(i, stack_tree) for i in range(len(stack_tree[0]))]
    else:  # e.g. with IFC001, where stack is ifcopenshell.file.file
        return instances

def flatten_list_of_lists(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list_of_lists(item))
        else:
            result.append(item)
    return result

def handle_nested(instance):
    if isinstance(instance, tuple):
        return

def is_list_of_tuples_or_none(var):
    return isinstance(var, list) and all(item is None or isinstance(item, tuple) for item in var)


def apply_operation(fn, inst, context, **kwargs):
    results = fn(context, inst, **kwargs)  
    return misc.do_try(lambda: list(map(attrgetter('instance_id'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, results)))[0], None)

def map_given_state(values, fn, context, depth=0, **kwargs):
    def is_nested(val):
        return isinstance(val, (tuple, list))

    def should_apply(values, depth):
        if depth == 0:
            return not is_nested(values)
        elif depth == 1:
            return is_nested(values) and all(not is_nested(v) for v in values)
        return False

    if should_apply(values, depth):
        return apply_operation(fn, values, context, **kwargs)
    elif is_nested(values):
        new_depth = depth if depth > 0 else 0
        return type(values)(map_given_state(v, fn, context, new_depth, **kwargs) for v in values)
    else:
        return apply_operation(fn, values, context, **kwargs)


def handle_given(context, fn, **kwargs):
    """
    'Given' statements include four distinct functionalities.
    1) Set file-wide context.applicable. No further steps (given or then) have to be executed when context.applicability is set to False
    2) Set an initial set of instances ('Given an IfcAlignment' -> [IfcAlignm, IfcAlignm, IfcAlign])
    3) Filter the set of IfcAlignment based on a value ('Given attribute == X' -> [IfcAlignm, None, IfcAlignm])
    4) Set instances to a given attribute ('Given its attribute Representation') -> [IfcProdDefShape, IfcProdDefShape, IfcProdDefShape]
    """
    if not 'inst' in inspect.getargs(fn.__code__).args:
        gen = fn(context, **kwargs)
        if gen: # (2) Set initial set of instances
            insts = list(gen)
            context.instances = list(map(attrgetter('instance_id'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, insts)))
            pass
        else:
            pass # (1) -> context.applicable is set within the function ; replace this with a simple True/False and set applicability here?
    else:
        context._push('attribute') # for attribute stacking
        if 'at depth 1' in context.step.name: 
            #todo @gh develop a more standardize approach
            context.instances = list(filter(None, map_given_state(context.instances, fn, context, depth=1, **kwargs)))
        else:
            context.instances = list(filter(None, map_given_state(context.instances, fn, context, **kwargs)))

def safe_method_call(obj, method_name, default=None ):
    method = getattr(obj, method_name, None)
    if callable(method):
        return method()
    return default

def handle_then(context, fn, **kwargs):
    instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])

    # if 'instances' are not actual ifcopenshell.entity_instance objects, but e.g. tuple of string values then get the actual instances from the stack tree
    # see for more info docstring of get_activation_instances
    activation_instances = get_activation_instances(context, instances) if instances and get_stack_tree(context) else instances

    validation_outcome = ValidationOutcome(
        outcome_code=ValidationOutcomeCode.EXECUTED,  # "Executed", but not no error/pass/warning #deactivated for now
        observed=None,
        expected=None,
        feature=context.feature.name,
        feature_version=misc.define_feature_version(context),
        severity=OutcomeSeverity.EXECUTED,
        validation_task_id=context.validation_task_id
    )
    context.gherkin_outcomes.append(validation_outcome)

    def map_then_state(items, fn, context, current_path=[], depth=0, **kwargs):
        def apply_then_operation(fn, inst, context, current_path, depth=0, **kwargs):
            top_level_index = current_path[0] if current_path else None
            activation_inst = inst if not current_path or activation_instances[top_level_index] is None else activation_instances[top_level_index]
            if isinstance(activation_inst, ifcopenshell.file):
                activation_inst = None  # in case of blocking IFC101 check, for safety set explicitly to None

            step_results = list(filter(lambda x: x.severity in [OutcomeSeverity.ERROR, OutcomeSeverity.WARNING], list(fn(context, inst=inst, **kwargs))))
            for result in step_results:
                validation_outcome = ValidationOutcome(
                    outcome_code=get_outcome_code(result, context),
                    observed=expected_behave_output(context, result.observed),
                    expected=expected_behave_output(context, result.expected),
                    feature=context.feature.name,
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.WARNING if any(tag.lower() == "industry-practice" for tag in context.feature.tags) else OutcomeSeverity.ERROR,
                    instance_id = safe_method_call(activation_inst, 'id', None),
                    validation_task_id=context.validation_task_id
                )
                context.gherkin_outcomes.append(validation_outcome)

                if not step_results:

                    validation_outcome = ValidationOutcome(
                        outcome_code=ValidationOutcomeCode.PASSED,  # todo @gh "Rule passed" # deactivated until code table is added to django model
                        observed=None,
                        expected=None,
                        feature=context.feature.name,
                        feature_version=misc.define_feature_version(context),
                        severity=OutcomeSeverity.PASSED,
                        instance_id = safe_method_call(activation_inst, 'id', None),
                        validation_task_id=context.validation_task_id
                    )
                    context.gherkin_outcomes.append(validation_outcome)



        def is_nested(val):
            return isinstance(val, (tuple, list))

        def should_apply(items, depth):
            if depth == 0:
                return not is_nested(items)
            elif depth == 1:
                return is_nested(items) and all(not is_nested(v) for v in items)
            return False

        if should_apply(items, depth):
            return apply_then_operation(fn, items, context, current_path, **kwargs)
        elif is_nested(items):
            new_depth = depth if depth > 0 else 0
            return type(items)(map_then_state(v, fn, context, current_path + [i], new_depth, **kwargs) for i, v in enumerate(items))
        else:
            return apply_then_operation(fn, items, context, **kwargs)
    plural_steps = ['the values must be identical']
    #todo @gh find a more standardized approach
    map_then_state(instances, fn, context, depth = 1 if 'at depth 1' in context.step.name.lower() else 0, **kwargs)

    # evokes behave error
    generate_error_message(context, [gherkin_outcome for gherkin_outcome in context.gherkin_outcomes if gherkin_outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]])

class gherkin_ifc():

    def step(step_text):
        def wrapped_step(func):
            return step(step_text)(execute_step(func))

        return wrapped_step

def execute_step(fn):
    while hasattr(fn, '__wrapped__'): # unwrap the function if it is wrapped by a decorator in casse of catching multiple string platterns
        fn = fn.__wrapped__
    @wraps(fn)
    def inner(context, **kwargs):
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

        if not getattr(context, 'applicable', True):
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

        else: # applicability is set to True

            step_type = context.step.step_type
            if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
                handle_given(context, fn, **kwargs)
            elif step_type.lower() == 'then':
                handle_then(context, fn, **kwargs)

    return inner

def serialize_item(item: Any) -> Any:
    if isinstance(item, ifcopenshell.entity_instance):
        return getattr(item, 'GlobalId', item.is_a())
    else:
        return item

def serialize_to_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return json.dumps(result)
    return wrapper

@serialize_to_json
def expected_behave_output(context: Context, data: Any) -> str:
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            pass

    
    match data:
        case list() | set() | tuple():
            serialized_data = [serialize_item(item) for item in data]
            return {"OneOf": serialized_data}
        case bool() | None:
            return data
        case str():
            if data in [x.name() for x in ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.model.schema).entities()]:
                return {'entity': data} # e.g. 'the type must be IfcCompositeCurve'
            else:
                return {'value': data} # e.g. "The value must be 'Body'"
        case ifcopenshell.entity_instance():
            return {'ifc_instance': getattr(data, 'GlobalId', data.is_a())}
        case int() | float():
            return {'count': data}
        case _:
            return data
        
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