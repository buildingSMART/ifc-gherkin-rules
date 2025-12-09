from utils import system

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]

@gherkin_ifc.step('A relationship .{relationship}. {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}.')
@gherkin_ifc.step('A relationship .{relationship}. ^{exist_or_not_exist:exist_or_not_exist}^ {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}.')
@gherkin_ifc.step('A relationship .{relationship}. ^{exist_or_not_exist:exist_or_not_exist}^ {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}. {tail:maybe_and_following_that}')
@gherkin_ifc.step('A relationship .{relationship}. {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}. {tail:maybe_and_following_that}')
@gherkin_ifc.step('A *{required}* relationship .{relationship}. {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}.')
@gherkin_ifc.step('A *{required}* relationship .{relationship}. {dir1:from_to} .{entity}. {dir2:from_to} .{other_entity}. {tail:maybe_and_following_that}')
def step_impl(context, inst, relationship, dir1, entity, dir2, other_entity, tail=False, exist_or_not_exist='exists', required=False):
    assert dir1 != dir2

    required = exist_or_not_exist not in ["does not exist", "must not exist"]
    if exist_or_not_exist == 'must exist':
        tail=True # output the other entity

    instances = []
    relationships = [i for i in context.model.get_inverse(inst, with_attribute_indices=True, allow_duplicate=True) if i[0].is_a(relationship)]

    for rel, attribute_index in relationships:
        attr_to_entity = relating_attr_matrix.get(rel.is_a())
        attr_to_other = {0: v for k, v in related_attr_matrix.items() if rel.is_a(k)}.get(0)

        assert attr_to_entity
        assert attr_to_other

        if dir1 == "to":
            attr_to_entity, attr_to_other = attr_to_other, attr_to_entity

        def make_aggregate(val):
            if not isinstance(val, (list, tuple)):
                val = [val]
            return val
        
        if rel.attribute_name(attribute_index) == attr_to_entity:
            for other in other_entity.split(' or '):
                try:
                    to_other = list(filter(lambda i: i.is_a(other), make_aggregate(getattr(rel, attr_to_other))))
                except RuntimeError:
                    # @nb RuntimeError typically comes from IfcOpenShell with invalid data, I don't understand
                    # why this particular statement handles this in this way
                    yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)

                if tail:
                    instances.extend(to_other)
                else:
                    instances.append(inst)

    severity = OutcomeSeverity.PASSED if bool(instances) == required else OutcomeSeverity.ERROR
    yield ValidationOutcome(inst=instances if instances else inst, severity=severity)


@gherkin_ifc.step("The element ^{relationship_type}^ an .{entity}.")
def step_impl(context, inst, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    if getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity):
        yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASSED)

