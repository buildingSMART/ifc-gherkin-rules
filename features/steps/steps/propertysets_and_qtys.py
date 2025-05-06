import functools
import itertools
import json
import operator
import os
import re
from typing import List

from validation_handling import gherkin_ifc
from utils import ifc, misc, system
from . import ValidationOutcome, OutcomeSeverity

template_type_to_expected = {
    'PSET_TYPEDRIVENONLY': 'IfcTypeObject',
    'PSET_PERFORMANCEDRIVEN': 'IfcPerformanceHistory',
    'PSET_OCCURRENCEDRIVEN': 'IfcObject'
}


@functools.cache
def get_predefined_type(inst):
    import ifcopenshell.util.element
    if inst.is_a("IfcTypeObject"):
        _type = inst
    else:
        if inst.PredefinedType:
            if inst.PredefinedType == 'USERDEFINED':
                return inst.ObjectType
            else:
                return inst.PredefinedType
        _type = ifcopenshell.util.element.get_type(inst)
    if _type and _type.PredefinedType:
        if _type.PredefinedType == 'USERDEFINED':
            return _type.ElementType
        else:
            return _type.PredefinedType


def take_first_if_single_length(li: List):
    return li[0] if len(li) == 1 else li


def upper_case_if_string(v):
    try:
        return v.upper()
    except AttributeError:
        return v


@functools.cache
def get_pset_definitions(schema, table):
    schema_specific_path = system.get_abs_path(f"resources/{schema.upper()}/{table}.csv")

    if os.path.exists(schema_specific_path):
        tbl_path = schema_specific_path
    else:
        tbl_path = system.get_abs_path(f"resources/{table}.csv")

    tbl = system.get_csv(tbl_path, return_type='dict')
    return {d['property_set_name']: d for d in tbl}


class AlwaysEqualDict(dict):
    """
    Just to accept as an argument to functools.cache, make sure that
    other arguments are present to differentiate cache entries.
    >>> {AlwaysEqualDict({}): 1} | {AlwaysEqualDict({'a':1}):2}
    {{}: 2}
    """

    def __hash__(self):
        return 0

    def __eq__(self, _):
        return True


@functools.cache
def establish_accepted_pset_values(name: str, _schema: str, _table: str, property_set_definitions: AlwaysEqualDict):
    # _schema and _table are only for cache key, property_set_definitions is derived from _schema, _table,
    # but unhashable because it's a dict
    def make_obj(s):
        if s:
            return json.loads(s.replace("'", '"'))
        else:
            return ''

    try:
        property_set_attr = property_set_definitions[name]
    except KeyError:  # Pset_ not found in template
        property_set_attr = ''
        return property_set_attr

    accepted_values = dict()
    accepted_values['template_type'] = property_set_attr.get('template_type', '')

    accepted_values['property_names'] = []
    accepted_values['property_types'] = []
    accepted_values['data_types'] = []

    for property_def in make_obj(property_set_attr['property_definitions']):
        accepted_values['property_names'].append(property_def['property_name'])
        accepted_values['property_types'].append(property_def['property_type'])
        accepted_values['data_types'].append(property_def['data_type'])

    accepted_values['applicable_entities'] = [s.split('/')[0] for s in
                                              make_obj(property_set_attr['applicable_entities'])]

    # in the ifc2x3 data, predefined type restrictions are imposed as:
    # | | | applicable_type_value                     | |
    # | | | {entity}.PredefinedType={predefinedtype}  | |
    if property_set_attr['applicable_type_value'] and '.PredefinedType=' in property_set_attr['applicable_type_value']:
        ptype = property_set_attr['applicable_type_value'].split('.PredefinedType=')[1].upper()
        accepted_values['applicable_entities_with_predefined_types'] = list(zip(
            accepted_values['applicable_entities'],
            (ptype for _ in itertools.count())
        ))
    else:
        # in the ifc4 data, predefined type restrictions are imposed as:
        # | | | applicable_entities                                                     | |
        # | | | ['{entity}','{entity}/{predefinedtype}','{entity2}/{predefinedtype2}']  | |
        accepted_values['applicable_entities_with_predefined_types'] = [
            ((ab[0], ab[1].upper()) if len(ab) == 2 else (ab[0], None)) for ab in
            (s.split('/') for s in make_obj(property_set_attr['applicable_entities']))]

    return accepted_values


@functools.cache
def normalize_pset(name: str) -> str:
    """
    Normalizes variations of 'Pset' to ensure consistent formatting.
    Converts "Pset followed by a symbol or letter" into "Pset_"

    Examples:
    - "Pset.WallCommon" → "Pset_WallCommon"
    - "Pset-WallCommon" → "Pset_WallCommon"
    - "Pset WallCommon" → "Pset_WallCommon"
    - "PsetWallCommon" → "Pset_WallCommon"
    - "pset_WallCommon" → "Pset_WallCommon" (fix capitalization)
    """

    name = re.sub(r'^[Pp][Ss][Ee][Tt]', "Pset", name)

    if name.startswith("Pset_"):
        return name
    name = re.sub(r"^Pset[\W]?", "Pset_", name)

    return name


@gherkin_ifc.step(
    "The .{inst_type:property_set_or_element_quantity}. attribute .Name. must use standard values [according to the table] '{table}'")
def step_impl(context, inst, table, inst_type=None):
    property_set_definitions = get_pset_definitions(context.model.schema, table)
    name = normalize_pset(getattr(inst, 'Name', 'Attribute not found'))

    if name not in property_set_definitions.keys():
        yield ValidationOutcome(inst=inst, observed={'value': name}, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Each associated IfcProperty must be named [according to the table] '{table}'")
def step_impl(context, inst, table, inst_type=None):
    property_set_definitions = get_pset_definitions(context.model.schema, table)
    name = normalize_pset(getattr(inst, 'Name', 'Attribute not found'))

    accepted_values = establish_accepted_pset_values(name, context.model.schema, table,
                                                     AlwaysEqualDict(property_set_definitions))

    if accepted_values:  # If not it's a custom Pset_ prefixed attribute, e.g. Pset_Mywall (no need for further Pset_ checks),

        # first check association to occurrences
        # notes:
        #  - this inverse relationship from IfcPropertySet (IfcPropertyDefinition in IFC4+) to IfcRelDefinesByProperties got renamed
        #  - usage of this relationship is invalid if template type is PSET_TYPEDRIVENONLY

        try:
            relations = inst.PropertyDefinitionOf  # IFC2x3 https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifckernel/lexical/ifcpropertysetdefinition.htm
        except AttributeError:  # IFC4-CHANGE Inverse attribute renamed from PropertyDefinitionOf with upward compatibility for file-based exchange.
            # https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPropertySet.htm
            relations = inst.DefinesOccurrence
        except IndexError:  # IfcPropertySet not assigned to IfcObjects
            relations = []

        related_objects = list(itertools.chain.from_iterable(relation.RelatedObjects for relation in relations))
        for obj in (o for o in related_objects if not o.is_a("IfcTypeObject")):
            if accepted_values['template_type'] and accepted_values['template_type'] in ['PSET_TYPEDRIVENONLY']:
                yield ValidationOutcome(inst=inst, expected={
                    'entity': template_type_to_expected[accepted_values['template_type']]}, observed=obj,
                                        severity=OutcomeSeverity.ERROR)

            correct = [accepted_object.lower() for accepted_object in accepted_values['applicable_entities'] if
                       obj.is_a(accepted_object)]
            if not any(correct):
                yield ValidationOutcome(inst=inst, expected=accepted_values['applicable_entities'], observed=obj,
                                        severity=OutcomeSeverity.ERROR)
            else:
                # - when entity validation succeeds we continue to check predefined type
                # - we take note of the predefined types that are allowed for the entity that was used to select the current applicability (this has to take into account inheritance) [could be multiple in case of inheritance - sometimes we see in IFC that both the parent as well as the child entity are explicitly allowed]
                # - we filter the allowed predefined types based on the entity used for selection [could be multiple]
                # - if this contains None, then no predefined type is allowed, so we don't need to do any further checks
                # - if it doesn't contain none we do need to check if the predefined type in the model (can be null) is part of the allowed predefined types.
                allowed_predefined_types_for_matching_entity = [ptype.upper() if ptype else None for entity, ptype
                                                                in accepted_values[
                                                                    'applicable_entities_with_predefined_types'] if
                                                                entity.lower() in correct]
                if None not in allowed_predefined_types_for_matching_entity:
                    # None means here that the predefined type is not constrained, or bare entity is also allowed -> no further check
                    observed_ptype = upper_case_if_string(get_predefined_type(obj))

                    if observed_ptype not in allowed_predefined_types_for_matching_entity:
                        yield ValidationOutcome(inst=inst, expected=take_first_if_single_length(
                            sorted(set(allowed_predefined_types_for_matching_entity))), observed=observed_ptype,
                                                severity=OutcomeSeverity.ERROR)

        # Now check association to type objects.
        # Notes:
        #  - This is a different mechanism, no objectified relationship, but direct forward attribute on IfcTypeObject
        #  - In same cases the applicable entities are only **the occurences** regardless of template type
        #  - In IFC4 RelDefinesByProperties.RelatedObjects was promoted from Object to ObjectType, so we do need to check also the objectified rels

        related_objects = [o for o in related_objects if o.is_a("IfcTypeObject")]
        related_objects += inst.DefinesType
        for obj in related_objects:
            if accepted_values['template_type'] and accepted_values['template_type'] in ['PSET_OCCURRENCEDRIVEN',
                                                                                         'PSET_PERFORMANCEDRIVEN']:
                yield ValidationOutcome(inst=inst, expected={
                    "entity": template_type_to_expected[accepted_values['template_type']]}, observed=obj,
                                        severity=OutcomeSeverity.ERROR)

            correct = [accepted_object.lower() for accepted_object in accepted_values['applicable_entities'] if
                       obj.is_a(accepted_object)]

            # Translate occurence to type name for when template is typedriven(override) but applicability only lists occurrence
            def schema_has_declaration_name(s):
                try:
                    return obj.wrapped_data.declaration().schema().declaration_by_name(s) is not None
                except:
                    return False

            correct_type1 = [accepted_object.lower() for accepted_object in accepted_values['applicable_entities']
                             if (schema_has_declaration_name(accepted_object + "Type") and obj.is_a(
                    accepted_object + "Type"))]
            # in rare occasions (IfcWindow and IfcDoor) in IFC4, the Type object is named IfcDoorStyle
            correct_type2 = [accepted_object.lower() for accepted_object in accepted_values['applicable_entities']
                             if (schema_has_declaration_name(accepted_object + "Style") and obj.is_a(
                    accepted_object + "Style"))]
            correct = functools.reduce(operator.add, (correct, correct_type1, correct_type2))

            if not any(correct):
                yield ValidationOutcome(inst=inst, expected=accepted_values['applicable_entities'], observed=obj,
                                        severity=OutcomeSeverity.ERROR)
            else:
                allowed_predefined_types_for_matching_entity = [ptype.upper() if ptype else None for entity, ptype
                                                                in accepted_values[
                                                                    'applicable_entities_with_predefined_types'] if
                                                                entity.lower() in correct]
                if None not in allowed_predefined_types_for_matching_entity:
                    # None means here that the predefined type is not constrained, or bare entity is also allowed -> no further check
                    observed_ptype = upper_case_if_string(get_predefined_type(obj))

                    if observed_ptype not in allowed_predefined_types_for_matching_entity:
                        yield ValidationOutcome(inst=inst, expected=take_first_if_single_length(
                            sorted(set(allowed_predefined_types_for_matching_entity))), observed=observed_ptype,
                                                severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The IfcPropertySet must be related to a valid entity type [according to the table] '{table}'")
def step_impl(context, inst, table, inst_type=None):
    property_set_definitions = get_pset_definitions(context.model.schema, table)
    name = normalize_pset(getattr(inst, 'Name', 'Attribute not found'))

    accepted_values = establish_accepted_pset_values(name, context.model.schema, table,
                                                     AlwaysEqualDict(property_set_definitions))

    if accepted_values:  # If not it's a custom Pset_ prefixed attribute, e.g. Pset_Mywall (no need for further Pset_ checks),

        properties = inst.HasProperties
        for prop in properties:
            if prop.Name not in accepted_values['property_names']:
                yield ValidationOutcome(inst=inst, expected=accepted_values['property_names'],
                                        observed=prop.Name, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    "Each associated IfcProperty must be of valid entity type [according to the table] '{table}'")
def step_impl(context, inst, table, inst_type=None):
    property_set_definitions = get_pset_definitions(context.model.schema, table)
    name = normalize_pset(getattr(inst, 'Name', 'Attribute not found'))

    accepted_values = establish_accepted_pset_values(name, context.model.schema, table,
                                                     AlwaysEqualDict(property_set_definitions))

    if accepted_values:  # If not it's a custom Pset_ prefixed attribute, e.g. Pset_Mywall (no need for further Pset_ checks),

        accepted_property_name_type_map = dict(
            zip(accepted_values['property_names'], accepted_values['property_types']))
        for prop in inst.HasProperties:

            try:
                accepted_property_type = accepted_property_name_type_map[prop.Name]
            except KeyError:  # Custom property name, not matching the Pset_ expected property. Error found in previous step, no need to check more.
                continue

            if not prop.is_a(accepted_property_type):
                yield ValidationOutcome(inst=inst, expected=accepted_property_type, observed=prop,
                                        severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    "Each associated IfcProperty value must be of valid data type [according to the table] '{table}'")
def step_impl(context, inst, table, inst_type=None):
    property_set_definitions = get_pset_definitions(context.model.schema, table)
    name = normalize_pset(getattr(inst, 'Name', 'Attribute not found'))

    accepted_values = establish_accepted_pset_values(name, context.model.schema, table,
                                                     AlwaysEqualDict(property_set_definitions))

    if accepted_values:  # If not it's a custom Pset_ prefixed attribute, e.g. Pset_Mywall (no need for further Pset_ checks),
        accepted_property_name_datatype_map = dict(
            zip(accepted_values['property_names'], accepted_values['data_types']))

        for prop in inst.HasProperties:
            try:
                accepted_data_type = accepted_property_name_datatype_map[prop.Name]
            except KeyError:  # Custom property name, not matching the Pset_ expected property. Error found in previous step, no need to check more.
                continue

            if prop.is_a('IfcPropertySingleValue'):
                values = prop.NominalValue
                if values and not values.is_a(accepted_data_type['instance'].strip()):
                    yield ValidationOutcome(inst=inst, expected=accepted_data_type['instance'],
                                            observed=values.is_a(), severity=OutcomeSeverity.ERROR)

            elif prop.is_a('IfcPropertyEnumeratedValue'):
                values = prop.EnumerationValues
                if values:
                    for value in values:
                        if not value.wrappedValue in accepted_data_type['values']:
                            yield ValidationOutcome(inst=inst, expected=accepted_data_type['values'],
                                                    observed=value.wrappedValue, severity=OutcomeSeverity.ERROR)

            # @todo other properties such as list/bounded/etc.

            else:
                continue

            # @tfk not sure about this one, but for now empty values on a property are probably
            # not a universal error. This is more IDS territory.
            # if not values:
            #     yield ValidationOutcome(inst=inst, expected= {"oneOf": accepted_data_type['instance']}, observed = {'value':None}, severity=OutcomeSeverity.ERROR)
