import os
import ifcopenshell
import ifcopenshell.template

dir = os.path.dirname(__file__)
rule_code = os.path.basename(dir)

for validity, elem, schema_identifier, scenario_num in [
    ("pass", 'IfcRailing', 'IFC4X3_ADD2', '01'),
    ("pass", 'IfcSlab', 'IFC4X3_ADD2', '01'),
    ("pass", 'IfcStairFlight', 'IFC4X3_ADD2', '01'),
    ("pass", 'IfcBeam', 'IFC4X3_ADD2', '01'),
    ("pass", 'IfcWall', 'IFC4X3_ADD2', '01'),
    ("pass", 'IfcWall', 'IFC2X3', '04'),
    ("fail", "IfcBuildingSystem", 'IFC4X3_ADD2', '01'), 
    ("fail", "IfcCivilElementType", 'IFC4X3_ADD2', '01'), 
    ("fail", "IfcCivilElement", 'IFC4X3_ADD2', '01'),
    ("fail", "IfcPostalAddress", 'IFC4X3_ADD2', '01'),
    ("fail", "IfcTelecomAddress", 'IFC4X3_ADD2', '01'),
    ("fail", "IfcConnectionPortGeometry", 'IFC2X3', '04'),
    ("fail", "IfcElectricalElement", 'IFC2X3', '04'),
    ("pass", "IfcWall", 'IFC4', '08'),
    ("fail", "IfcProxy", 'IFC4', '08'),
    ("fail", "IfcWindowStyle", 'IFC4', '08'),
    ("fail", "IfcRelCoversSpaces", 'IFC4', '08'),
    ("fail", "IfcWallStandardCase", 'IFC4', '08')]:

    f = ifcopenshell.template.create(schema_identifier=schema_identifier)
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"       

    f.create_entity(elem)

    f.write(f"{os.path.dirname(__file__)}/{validity}-{rule_code}-scenario{scenario_num}-{schema_identifier}_{elem}_present.ifc")


for elem, attribute, schema_identifier, scenario_num in [
    ('IfcBuilding', 'BuildingAddress', 'IFC4X3_ADD2', '02'),
    ('IfcBuilding', 'ElevationOfRefHeight', 'IFC4X3_ADD2', '02'),
    ('IfcBuilding', 'ElevationOfTerrain', 'IFC4X3_ADD2', '02'),
    ('IfcBuildingStorey', 'Elevation', 'IFC4X3_ADD2', '02'),
    ('IfcOrganization', 'Addresses', 'IFC4X3_ADD2', '02'),
    ('IfcPerson', 'Addresses', 'IFC4X3_ADD2', '02'),
    ('IfcSite', 'LandTitleNumber', 'IFC4X3_ADD2', '02'),
    ('IfcSite', 'SiteAddress', 'IFC4X3_ADD2', '02'),
    ('IfcFillAreaStyleHatching', 'PointOfReferenceHatchLine', 'IFC2X3', '05')
]:
    
    if attribute == 'Addresses':
        v = [f.createIfcAddress()]
    elif attribute in ['SiteAddress', 'BuildingAddress']:
        v = f.createIfcPostalAddress()
    else:
        v = 'test_value'
    f = ifcopenshell.template.create(schema_identifier=schema_identifier)
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"  

    f.create_entity(
        elem,
        **{attribute : 1}
    )
    f.write(f"{dir}/fail-{rule_code}-scenario{scenario_num}-{schema_identifier}_element-{elem}_attribute_{attribute}.ifc")


for i, (elem, value, schema_identifier, scenario_num) in enumerate([
    ('IfcFireSuppressionTerminal', 'SPRINKLERDEFLECTOR', 'IFC4X3_ADD2', '03'),
    ('IfcFireSuppressionTerminal', 'SPRINKLER', 'IFC4X3_ADD2', '03'),
    ('IfcCableCarrierFitting', 'CROSS', 'IFC4X3_ADD2', '03'),
    ('IfcCableCarrierFitting', 'JUNCTION', 'IFC4X3_ADD2', '03'),
    ('IfcCableCarrierFittingType', 'TEE', 'IFC4X3_ADD2', '03'),
    ('IfcCableCarrierFittingType', 'TRANSITION', 'IFC4X3_ADD2', '03'),
    ('IfcGeographicElement', 'SOIL_BORING_POINT', 'IFC4X3_ADD2', '03'),
    ('IfcGeographicElement', 'TERRAIN', 'IFC4X3_ADD2', '03'),
    ('IfcUtilityResource', "MODIFIEDADDED", 'IFC2X3', '06'),
    ('IfcUtilityResource', 'NOCHANGE', 'IFC2X3', '06')
]):

    f = ifcopenshell.template.create(schema_identifier=schema_identifier)
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    try:
        f.create_entity(
            elem, 
            ifcopenshell.guid.new(),
            PredefinedType = value
        ) 
    except:
        continue
    pass_or_fail = 'fail' if i % 2 == 0 else 'pass'

    f.write(f"{dir}/{pass_or_fail}-{rule_code}-scenario{scenario_num}-{schema_identifier}_{elem}_enum_type_value_{value}.ifc")


pass_fail_map = {0: 'fail', 1: 'pass'}
implicit_explicit_map = {0: 'explicit', 1: 'implicit'}

for (explicit, implicit) in [
    ('IfcRelAssociates', 'IfcRelAssociatesMaterial'),
    ('IfcProductRepresentation', 'IfcProductDefinitionShape'),
]:
    for i, elem in enumerate([explicit, implicit]):
        f = ifcopenshell.template.create(schema_identifier='IFC2X3')
        f.create_entity(elem)
        pass_or_fail = pass_fail_map[i % 2]
        implicit_or_explicit = implicit_explicit_map[i % 2]

        f.write(f'{pass_or_fail}-ifc102-scenario06-IFC2X3_{implicit_or_explicit}_{explicit}.ifc')