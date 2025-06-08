import itertools

from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity
from utils import misc
import operator
from pyproj import CRS
from enum import Enum

@gherkin_ifc.step("Its values")
@gherkin_ifc.step("Its values excluding {excluding}")
def step_impl(context, inst, excluding=None):
    yield ValidationOutcome(instance_id=inst.get_info(recursive=True, include_identifier=False, ignore=excluding),
                            severity=OutcomeSeverity.PASSED)


@gherkin_ifc.step("The values grouped pairwise at depth {ignored:d}")
def step_impl(context, inst, ignored=0):
    inst = itertools.pairwise(inst)
    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("The determinant of the placement matrix")
def step_impl(context, inst):
    import numpy as np
    import ifcopenshell.ifcopenshell_wrapper

    if inst.wrapped_data.file_pointer() == 0:
        # In some case we're processing operations on attributes that are 'derived in subtype', for
        # example the Operator on an IfcMirroredProfileDef. Derived attribute values are generated
        # on the fly and are not part of a file. Due to a limitation on the mapping expecting a file
        # object, such instances can also not be mapped. Therefore in such case we create a temporary
        # file to add the instance to.
        f = ifcopenshell.file(schema=context.model.schema_identifier)
        inst = f.add(inst)

    shp = ifcopenshell.ifcopenshell_wrapper.map_shape(ifcopenshell.geom.settings(), inst.wrapped_data)
    d = np.linalg.det(np.array(shp.components))
    yield ValidationOutcome(instance_id=d, severity=OutcomeSeverity.PASSED)
 

@gherkin_ifc.step("The {unit_types} unit(s) of the project ^{comparison_operator:equal_or_not_equal}^ equal to the {crs_unit_types} unit(s) of the .{crs_entity_type}.")
def step_impl(context, inst, unit_types, comparison_operator, crs_unit_types, crs_entity_type):
    assert unit_types == crs_unit_types, "it's only possible to compare equal unit types"
    pred = misc.negate(operator.eq) if comparison_operator in {"is not", "!="} else operator.eq
    unit_types = unit_types.split(' and ')

    conversion_based = False
    
    unit_type_attr_map= {
        'length' : 'LENGTHUNIT',
        'area': 'AREAUNIT',
        'volume': 'VOLUMEUNIT',
        'angle': 'PLANEANGLEUNIT',
    }
    
    def map_units(units):
        map = {}
        for unit in units:
            unit_type = getattr(unit, 'UnitType', None)
            if unit_type and unit_type not in map:
                map[unit_type] = unit
        return map
    
    # determine the project unit values
    project = context.model.by_type("IfcProject")[0]
    project_unit_map = map_units(getattr(project.UnitsInContext, 'Units', []))
    project_units = {utype : project_unit_map.get(unit_type_attr_map[utype]) for utype in unit_types}


    if 'length' in unit_types and (length := project_units.get('length')):
        prefix = getattr(length, 'Prefix', '')
        name = getattr(length, 'Name', '').lower()
        project_units['length'] =  (f"{prefix}{name}" if prefix else name).lower()

    if 'angle' in unit_types and (angle := project_units.get('angle')):
        if length.is_a('IfcSIUnit'):
            project_units['angle'] = {
                'name': (f"{prefix}{name}" if prefix else name).lower(),
                'conversion_factor' : None
            }
            conversion_based=True
        else:
            project_units['angle'] = {
                'name': getattr(angle, 'Name', '').lower(),
                'conversion_factor': misc.do_try(lambda: angle.ConversionFactor.ValueComponent.wrappedValue, '')
            }
    
    # determine the crs unit values
    crs = context.model.by_type(crs_entity_type)[0]
    epsg_crs = CRS.from_string(crs.Name)
    unit_attrs = [attr for attr in dir(crs) if attr.endswith('Unit')]
    crs_unit_map = map_units([getattr(crs, attr) for attr in unit_attrs if getattr(crs, attr, None) is not None])
    crs_units = {utype: crs_unit_map.get(unit_type_attr_map[utype]) for utype in unit_types}
    
    if 'length' in unit_types:
        if length := crs_units.get('length'):
            prefix = getattr(length, 'Prefix', '')
            name = getattr(length, 'Name', '').lower()
            crs_units['length'] =  (f"{prefix}{name}" if prefix else name).lower()
        else:
            crs_units['length'] = epsg_crs.coordinate_system.axis_list[0].unit_name
            
    if 'angle' in unit_types:
        if angle := crs_units.get('angle'):
            crs_units['angle'] = {
                'name': getattr(angle, 'Name').lower(),
                'conversion_factor': misc.do_try(lambda : project_units['angle'].ConversionFactor.ValueComponent.wrappedValue, '')
            }
        else:
            crs_units['angle'] = {
                'name' : epsg_crs.coordinate_system.axis_list[0].unit_name,
                'conversion_factor':  misc.do_try(lambda : epsg_crs.coordinate_system.axis_list[0].unit_conversion_factor, None) if conversion_based else None
            }
    
    
    if pred(project_units, crs_units):
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)