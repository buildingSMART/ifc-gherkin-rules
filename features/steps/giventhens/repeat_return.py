from utils import misc, ifc

import ifcopenshell
from behave import given, then

@given("Repeat step {step_count}")
@given("Repeat steps {step_count}")
@then("Repeat step {step_count}")
@then("Repeat steps {step_count}")
def step_impl(context, step_count):
    step_stack = list(
        filter(None, list(map(lambda layer: layer.get('step'), context._stack))))
    step_stack.reverse()
    step_count = list(step_count.split(','))
    steps = ('\n').join(
        [(' ').join(['Given', step_stack[int(n)-2].name + ' ']) for n in step_count])
    context.execute_steps(steps)

@given("Return to {entity}")
@then("Return to {entity}")
def step_impl(context, entity):
    def filter_stack_tree(layer):
        def check_inclusion_criteria(input):
            """
            Verifies if layer includes a boolean variable or instance of {entity}
            """
            is_bool = isinstance(input, bool)
            correct_entity = False
            if isinstance(input, ifcopenshell.entity_instance):
                correct_entity = ifc.IfcEntity(entity).is_entity_instance(input)
            context.include_layer = is_bool or correct_entity
        layer = layer.get('instances')
        misc.map_state(layer, check_inclusion_criteria)
        return layer if context.include_layer else None

    stack_tree_filtered = list(
        filter(None, list(map(filter_stack_tree, context._stack))))
    insts = ifc.ContinuingInstances()
    insts.collect_applicable_instances(stack_tree_filtered)
    context.instances = insts.instances