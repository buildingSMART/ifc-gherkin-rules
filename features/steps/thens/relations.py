from validation_handling import gherkin_ifc
import json

from utils import ifc, misc, system

from parse_type import TypeBuilder
from behave import register_type

from . import IfcValidationOutcome, OutcomeSeverity


register_type(aggregated_or_contained_or_positioned=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("aggregated", "contained", "positioned")))))

@gherkin_ifc.step('It must be {relationship} as per {table}')
def step_impl(context, inst, relationship, table):
    stmt_to_op_forward = {'aggregated': 'Decomposes'}
    stmt_to_op_reversed = {'aggregated': 'IsDecomposedBy'}
    assert relationship in stmt_to_op_forward

    tbl_path = system.get_abs_path(f"resources/{table}")
    tbl_forward = system.get_csv(tbl_path, return_type='dict')
    tbl_reversed = [dict(zip(d.keys(), reversed(d.values()))) for d in tbl_forward]

    opposites = {'RelatingObject': 'RelatedObjects'}

    for is_required, stmt_to_op, tbl, get_attr in ((True, stmt_to_op_forward, tbl_forward, lambda x: x), (False, stmt_to_op_reversed, tbl_reversed, opposites.__getitem__)):

        ent_tbl_header, relationship_tbl_header = list(tbl[0].keys())
        aggregated_table = misc.make_aggregrated_dict(tbl, ent_tbl_header, relationship_tbl_header)

        relationship_tbl_header = get_attr(relationship_tbl_header)

        applicable_entities = []
        for applicable_entity in aggregated_table.keys(): # check which applicable entity the currently processed entity is (inheritance), e.g IfcRailway -> IfcFacility
            if inst.is_a(applicable_entity):
                applicable_entities.append(applicable_entity)
        if len(applicable_entities) == 0: # no applicable entity found
            # @tfk. I think this simply means, no requirement imposed.
            # raise Exception(f'Entity {entity} was not found in the {table}')
            continue
        applicable_entity = ifc.order_by_ifc_inheritance(applicable_entities, base_class_last = True)[0]
        expected_relationship_objects = aggregated_table[applicable_entity]
        try:
            relation = getattr(inst, stmt_to_op[relationship], True)[0]
        except IndexError: # no relationship found for the entity
            if is_required:
                yield IfcValidationOutcome(inst=inst, expected=expected_relationship_objects, observed= None, severity=OutcomeSeverity.ERROR)
            continue
        relationship_objects = getattr(relation, relationship_tbl_header, True)
        if not isinstance(relationship_objects, tuple):
            relationship_objects = (relationship_objects,)


        for relationship_object in relationship_objects:
            is_correct = any(relationship_object.is_a(expected_relationship_object) for expected_relationship_object in expected_relationship_objects)
            if not is_correct:
                yield IfcValidationOutcome(inst=inst, expected=expected_relationship_objects, observed=relationship_object, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step('It must be assigned to the {relating}')
def step_impl(context, inst, relating):
    for rel in getattr(inst, 'Decomposes', []):
        if not rel.RelatingObject.is_a(relating):
            yield IfcValidationOutcome(inst=inst, expected=relating, observed= rel.RelatingObject.is_a(), severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step('It {decision} be {relationship:aggregated_or_contained_or_positioned} {preposition} {other_entity} {condition}')
def step_impl(context, inst, decision, relationship, preposition, other_entity, condition, *args):
    acceptable_decisions = ['must', 'must not']
    assert decision in acceptable_decisions

    acceptable_relationships = {
        'aggregated': ['Decomposes', 'RelatingObject'],
        'contained': ['ContainedInStructure', 'RelatingStructure'],
        'positioned': ['PositionedRelativeTo', 'RelatingPositioningElement']
    }

    assert relationship in acceptable_relationships

    acceptable_conditions = ['directly', 'indirectly', 'directly or indirectly', 'indirectly or directly']
    assert condition in acceptable_conditions

    if 'directly' in condition:
        required_directness = {condition} if condition not in ['directly or indirectly', 'indirectly or directly'] else {
            'directly', 'indirectly'}
        check_directness = True
    else:
        check_directness = False


    other_entity_reference = acceptable_relationships[relationship][0]  # eg Decomposes
    other_entity_relation = acceptable_relationships[relationship][1]  # eg RelatingObject

    relationship_reached = False
    if check_directness:
        observed_directness = set()
    if len(getattr(inst, other_entity_reference)) > 0:
        relation = getattr(inst, other_entity_reference)[0]
        relating_element = getattr(relation, other_entity_relation)
        relationship_reached = relating_element.is_a(other_entity)
        common_directness = required_directness & observed_directness  # values the required and observed situation have in common
        if relationship_reached:
            if check_directness:
                observed_directness.update({'directly'})
            if decision == 'must not':
                yield IfcValidationOutcome(inst=inst, expected=  f"{common_directness} {relationship}", observed = f"{decision} be {condition} {relationship}", severity=OutcomeSeverity.ERROR)

        if hasattr(relating_element, other_entity_reference): # in case the relation points to a wrong instance
            while len(getattr(relating_element, other_entity_reference)) > 0:
                relation = getattr(relating_element, other_entity_reference)[0]
                relating_element = getattr(relation, other_entity_relation)
                relationship_reached = relating_element.is_a(other_entity)
                if relationship_reached:
                    if check_directness:
                        observed_directness.update({'indirectly'})
                        break
                    if decision == 'must not':
                        yield IfcValidationOutcome(inst=inst, expected=f"{decision} be {condition} {relationship}", observed=f"{common_directness} {relationship}", severity=OutcomeSeverity.ERROR)
                        break

    if check_directness:
        common_directness = required_directness & observed_directness  # values the required and observed situation have in common
        directness_achieved = bool(common_directness)  # if there's a common value -> relationship achieved
        directness_expected = decision == 'must'  # check if relationship is expected
        if directness_achieved != directness_expected:
            yield IfcValidationOutcome(inst=inst, expected=  f"{common_directness} {relationship}", observed = f"{decision} be {condition} {relationship}", severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step('It must not be referenced by itself directly or indirectly')
def step_impl(context, inst):
    relationship = {'IfcGroup': ('HasAssignments', 'IfcRelAssignsToGroup', 'RelatingGroup')}

    def get_memberships(inst):
        for rel in filter(misc.is_a(ent), getattr(inst, inv, [])):
            container = getattr(rel, attr)
            yield container
            yield from get_memberships(container)

    inv, ent, attr = relationship[inst.is_a()]
    if inst in get_memberships(inst):
        yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step('The IfcPropertySet Name attribute value must use predefined values according to the {table} table')
@gherkin_ifc.step('The IfcPropertySet must be assigned according to the property set definitions table {table}')
@gherkin_ifc.step('Each associated IfcProperty must be named according to the property set definitions table {table}')
@gherkin_ifc.step('Each associated IfcProperty must be of type according to the property set definitions table {table}')
@gherkin_ifc.step('Each associated IfcProperty value must be of data type according to the property set definitions table {table}')
def step_impl(context, inst, table):

    tbl_path = system.get_abs_path(f"resources/property_set_definitions/{table}")
    tbl = system.get_csv(tbl_path, return_type='dict')
    property_set_definitons = {}
    for d in tbl:
        property_set_definitons[d['property_set_name']] = d

    def establish_accepted_pset_values(name, property_set_definitons):
        def make_obj(s):
            if s:
                return json.loads(s.replace("'", '"'))
            else:
                return ''

        try:
            property_set_attr = property_set_definitons[name]
        except KeyError:  # Pset_ not found in template
            property_set_attr = ''
            return property_set_attr

        accepted_values = {}
        accepted_values['template_type'] = property_set_attr.get('template_type', '')

        accepted_values['property_names'] = []
        accepted_values['property_types'] = []
        accepted_values['data_types'] = []

        for property_def in make_obj(property_set_attr['property_definitions']):
            accepted_values['property_names'].append(property_def['property_name'])
            accepted_values['property_types'].append(property_def['property_type'])
            accepted_values['data_types'].append(property_def['data_type'])

        accepted_values['applicable_entities'] = make_obj(property_set_attr['applicable_entities'])

        accepted_values['applicable_type_values'] = property_set_attr.get('applicable_type_value', '').split(',')

        return accepted_values

    name = getattr(inst, 'Name', 'Attribute not found')


    if 'IfcPropertySet Name attribute value must use predefined values according' in context.step.name:
        if name not in property_set_definitons.keys():
            # yield (err.InvalidValueError(False, inst, 'Name', name))  # A custom Pset_ prefixed attribute, e.g. Pset_Mywall
            yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

    accepted_values = establish_accepted_pset_values(name, property_set_definitons)

    if accepted_values:  # If not it's a custom Pset_ prefixed attribute, e.g. Pset_Mywall (no need for further Pset_ checks),

        if 'IfcPropertySet must be assigned according to the property set definitions table' in context.step.name:
            try:
                relations = inst.PropertyDefinitionOf  # IFC2x3 https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifckernel/lexical/ifcpropertysetdefinition.htm
            except AttributeError: # IFC4-CHANGE Inverse attribute renamed from PropertyDefinitionOf with upward compatibility for file-based exchange.
                # https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPropertySet.htm
                relations = inst.DefinesOccurrence
            except IndexError:  # IfcPropertySet not assigned to IfcObjects
                relations = []

            for relation in relations:
                related_objects = relation.RelatedObjects
                for obj in related_objects:

                    if accepted_values['template_type'] and accepted_values['template_type'] in ['PSET_TYPEDRIVENONLY']:
                        # yield (err.InvalidPropertySetDefinition(False, inst=inst, object=obj, name=name, template_type_enum=accepted_values['template_type']))
                        yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

                    correct = [obj.is_a(accepted_object) for accepted_object in accepted_values['applicable_entities']]
                    if not any(correct):
                        # yield (err.InvalidPropertySetDefinition(False, inst, obj, name, accepted_values['applicable_entities']))
                        yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)


            related_objects = inst.DefinesType
            for obj in related_objects:
                if accepted_values['template_type'] and accepted_values['template_type'] in ['PSET_OCCURRENCEDRIVEN', 'PSET_PERFORMANCEDRIVEN']:
                    # yield (err.InvalidPropertySetDefinition(False, inst=inst, object=obj, name=name, template_type_enum=accepted_values['template_type']))
                    yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

                correct = [obj.is_a(accepted_object) for accepted_object in accepted_values['applicable_type_values']]
                if not any(correct):
                    # yield (err.InvalidPropertySetDefinition(False, inst, obj, name, accepted_values['applicable_type_values']))
                    yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

        if 'Each associated IfcProperty must be named according to the property set definitions table' in context.step.name:
            properties = inst.HasProperties

            for property in properties:
                if property.Name not in accepted_values['property_names']:
                    # yield (err.InvalidPropertyDefinition(False, inst=inst, property=property, accepted_values=accepted_values['property_names']))
                    yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

        if 'Each associated IfcProperty must be of type according to the property set definitions table' in context.step.name:
            accepted_property_name_type_map = {}
            for accepted_property_name, accepted_property_type in zip(accepted_values['property_names'], accepted_values['property_types']):
                accepted_property_name_type_map[accepted_property_name] = accepted_property_type

            properties = inst.HasProperties
            for property in properties:

                try:
                    accepted_property_type = accepted_property_name_type_map[property.Name]
                except KeyError:  # Custom property name, not matching the Pset_ expected property. Error found in previous step, no need to check more.
                    break

                if not property.is_a(accepted_property_type):
                    # yield (err.InvalidPropertyDefinition(False, inst=inst, property=property, accepted_type=accepted_property_type))
                    yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

        if 'Each associated IfcProperty value must be of data type according to the property set definitions table' in context.step.name:
            accepted_property_name_datatype_map = {}
            for accepted_property_name, accepted_data_type in zip(accepted_values['property_names'], accepted_values['data_types']):
                accepted_property_name_datatype_map[accepted_property_name] = accepted_data_type

            properties = inst.HasProperties
            for property in properties:
                try:
                    accepted_data_type = accepted_property_name_datatype_map[property.Name]
                except KeyError:  # Custom property name, not matching the Pset_ expected property. Error found in previous step, no need to check more.
                    break

                if property.is_a('IfcPropertySingleValue'):
                    values = property.NominalValue
                    if not values.is_a(accepted_data_type['instance']):
                        # yield (err.InvalidPropertyDefinition(False, inst=inst, property=property, accepted_data_type_value=accepted_data_type['instance'], value=values))
                        yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)

                elif property.is_a('IfcPropertyEnumeratedValue'):
                    values = property.EnumerationValues
                    for value in values:
                        if not value.wrappedValue in accepted_data_type['values']:
                            # yield (err.InvalidPropertyDefinition(False, inst=inst, property=property, accepted_data_type_value=accepted_data_type['values'], value=value.wrappedValue))
                            yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)
                else:
                    continue

                if not values:
                    # yield (err.InvalidPropertyDefinition(False, inst=inst, property=property, accepted_data_type=accepted_data_type, value=values))
                    yield IfcValidationOutcome(inst=inst, expected= True, observed = False, severity=OutcomeSeverity.ERROR)