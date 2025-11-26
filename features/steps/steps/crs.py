from pyproj.database import query_crs_info
from pyproj import CRS
from validation_handling import gherkin_ifc
from utils import misc
import operator

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("The value must refer to a valid EPSG code")
@gherkin_ifc.step("The value refers to a valid EPSG code")
def step_impl(context, inst):
    valid_epsg_codes = {f"EPSG:{crs.code}" for crs in query_crs_info(auth_name="EPSG")}
    if inst not in valid_epsg_codes:
        yield ValidationOutcome(inst=inst, observed=inst, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)
        
    
@gherkin_ifc.step("The CRS should define a vertical component")
@gherkin_ifc.step("The CRS defines a vertical component")
def step_impl(context, inst):
    crs = CRS.from_string(inst)
    if crs.is_compound or crs.is_vertical:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)


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
            if unit.is_a('IfcNamedUnit')
                unit_type = unit.UnitType
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