from utils import misc, ifc

import ifcopenshell
from validation_handling import gherkin_ifc, global_rule

from behave import register_type
from parse_type import TypeBuilder
from enum import Enum, auto

from utils.subtype_handling import SubTypeHandling, check_entity_type

register_type(include_or_exclude_subtypes=TypeBuilder.make_enum({"including subtypes": SubTypeHandling.INCLUDE, "excluding subtypes": SubTypeHandling.EXCLUDE }))

@global_rule
@gherkin_ifc.step("Return to {entity}")
@gherkin_ifc.step("Return to {entity} {include_or_exclude_subtypes:include_or_exclude_subtypes}")
def step_impl(context, entity, include_or_exclude_subtypes=SubTypeHandling.EXCLUDE):
    """
    Disclaimer: Currently untested for normative rules

        | Feature Step               | Context Stack                       |
        |----------------------------|-------------------------------------|
        | Given an IfcEntity         | [entity1, entity2, entity3]         |
        | Given its attribute X      | [attr, None, attr]                  |
        | Given Y is attr            | [True, False, True]                 |
        | Given return to IfcEntity  | [entity1, entity2, entity3]         |
    For rules used for activation, this is not a problem (one is sufficient to activate the rule). 
    However, for normative rules, we do not want to consider entity2. 
    Simply using indexes would not work as the stack is often nested.
    """
    context.include_or_exclude_subtypes = include_or_exclude_subtypes
    def filter_stack_tree(layer):
        def check_inclusion_criteria(input):
            """
            Verifies if layer includes a boolean variable or instance of {entity}
            """
            is_bool = isinstance(input, bool)
            correct_entity = False
            if isinstance(input, ifcopenshell.entity_instance):
                correct_entity = check_entity_type(input, entity, context.include_or_exclude_subtypes)
            context.include_layer = is_bool or correct_entity
        layer = layer.get('instances')
        misc.map_state(layer, check_inclusion_criteria)
        return layer if context.include_layer else None

    #ensure the stack does not get pupulated when nothing was yielded in the last step
    if (lambda f: f(f))(lambda f: lambda data: bool(data) and (not isinstance(data, (list, tuple)) or any(f(f)(item) for item in data)))(context.instances):
        stack_tree_filtered = list(
            filter(None, list(map(filter_stack_tree, context._stack))))
        context.instances = stack_tree_filtered