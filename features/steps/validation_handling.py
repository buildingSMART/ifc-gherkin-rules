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
current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(str(Path(current_script_dir).parent.parent))

# sys.path.append(r"PATH TO VALIDATE DB") # TODO -> add the path if necessary
try:
    from validation_results import OutcomeSeverity, ValidationOutcome, ValidationOutcomeCode
except (ModuleNotFoundError, ImportError):
    from validation_results import OutcomeSeverity, ValidationOutcome, ValidationOutcomeCode

from behave.runner import Context
import random
from pydantic import BaseModel, field_validator, Field
from typing import Any, Union
from typing_extensions import Annotated

check_execution_id = random.randint(1, 1000)  # Placeholder number for check_execution_id

class StepResult:
    def __init__(self, observed, expected, outcome_code=None, warning=None):
        """
        Represents the outcome of a step in a test.
        To be used in step_impl function and further processed in the StepOutcome class with information from the context and instance.

        The `outcome_code` and `warning` are optional and allow developers to manually 
        specify additional details in the step implementation if needed.
        """
        self.observed = observed
        self.expected = expected
        if outcome_code is not None:
            self.outcome_code = outcome_code
        if warning is not None:
            self.warning = warning

    def as_dict(self):
        """Return a dictionary representation.
        Outcome_code and warning are optional fields to check manual input of a developer
        (e.g. adding a warning to a rule or selecting an outcome_code).
        so they are only included if they are not None."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

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

class gherkin_ifc():

    def step(step_text):
        def wrapped_step(func):
            return step(step_text)(execute_step(func))

        return wrapped_step

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

def execute_step(fn):
    while hasattr(fn, '__wrapped__'): # unwrap the function if it is wrapped by a decorator in casse of catching multiple string platterns
        fn = fn.__wrapped__
    @wraps(fn)
    #@todo gh break function down into smaller functions
    def inner(context, **kwargs):
        step_type = context.step.step_type
        if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
            name = context.step.name
            if 'Body shape representation has RepresentationType' in name:
                pass
            if not 'inst' in inspect.getargs(fn.__code__).args:
                gen = fn(context, **kwargs)
                if gen: # in case only applicability is set to True or False, nothing is yielded
                    insts = list(gen)
                    context.instances = list(map(attrgetter('inst'), filter(lambda res: res.severity == OutcomeSeverity.PASS, insts)))
            else:
                context._push()
                if is_list_of_tuples_or_none(context.instances): # in case of stacking multiple attribute values for a single entity instance, e.g. in ALS004
                    context.instances = [fn(context, inst=inst, **kwargs) for inst in flatten_list_of_lists(context.instances)]
                else:
                    context.instances = list(map(attrgetter('inst'), filter(lambda res: res.severity == OutcomeSeverity.PASS, itertools.chain.from_iterable(fn(context, inst=inst, **kwargs) for inst in context.instances))))
                pass


        elif step_type.lower() == 'then':
            if not getattr(context, 'applicable', True):
                validation_outcome = ValidationOutcome(
                    outcome_code=ValidationOutcomeCode.N00010,  # "NOT_APPLICABLE", Given statement with schema/mvd check failed
                    observed=None,
                    expected=None,
                    feature=context.feature.name,
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.NA,
                    check_execution_id=check_execution_id
                )
                context.gherkin_outcomes.add(validation_outcome)
            else:
                instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])

                # if 'instances' are not actual ifcopenshell.entity_instance objects, but e.g. tuple of string values then get the actual instances from the stack tree
                # see for more info docstring of get_activation_instances
                activation_instances = get_activation_instances(context, instances) if instances and get_stack_tree(context) else instances

                validation_outcome = ValidationOutcome(
                    outcome_code=ValidationOutcomeCode.X00040,  # "Executed", but not no error/pass/warning
                    observed=None,
                    expected=None,
                    feature=context.feature.name,
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.EXECUTED,
                    check_execution_id=check_execution_id
                )
                context.gherkin_outcomes.add(validation_outcome)

                for i, inst in enumerate(instances):
                    activation_inst = inst if activation_instances == instances or activation_instances[i] is None else activation_instances[i]
                    if isinstance(activation_inst, ifcopenshell.file):
                        activation_inst = context.model.by_type("IfcRoot")[0] # in case of blocking IFC001 check
                        activation_inst = context.model.by_type("IfcRoot")[0] # in case of blocking IFC001 check
                    step_results = list(fn(context, inst = inst, **kwargs)) # note that 'inst' has to be a keyword argument
                    for result in step_results:
                        try:
                            instance_step_outcome = StepOutcome(inst=activation_inst, context=context, **result.as_dict())
                        except:
                            pass

                        validation_outcome = ValidationOutcome(
                            outcome_code=getattr(ValidationOutcomeCode, instance_step_outcome.outcome_code),
                            observed=instance_step_outcome.model_dump(include=('observed'))["observed"],  # TODO (parse it correctly)
                            expected=instance_step_outcome.model_dump(include=('expected'))["expected"],  # TODO (parse it correctly)
                            feature=context.feature.name,
                            feature_version=misc.define_feature_version(context),
                            severity=getattr(OutcomeSeverity, "WARNING" if any(tag.lower() == "warning" for tag in context.feature.tags) else "ERROR"),
                            ifc_instance_id = activation_inst.id(),
                            check_execution_id=check_execution_id
                        )
                        context.gherkin_outcomes.add(validation_outcome)

                    if not step_results:

                        StepOutcome(inst=activation_inst,
                                    context=context,
                                    expected=None,
                                    observed=None)  # expected / observed equal on passed rule?
                        validation_outcome = ValidationOutcome(
                            outcome_code=ValidationOutcomeCode.P00010,  # "Rule passed"
                            observed=None,
                            expected=None,
                            feature=context.feature.name,
                            feature_version=misc.define_feature_version(context),
                            severity=OutcomeSeverity.PASS,
                            ifc_instance_id=None,
                            check_execution_id=check_execution_id
                        )
                    context.gherkin_outcomes.add(validation_outcome)

                generate_error_message(context, [gherkin_outcome for gherkin_outcome in context.gherkin_outcomes if gherkin_outcome.severity >= OutcomeSeverity.WARNING])

    return inner
