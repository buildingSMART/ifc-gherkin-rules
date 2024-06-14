import os
import ifcopenshell
import ifcopenshell.template

dir = os.path.dirname(__file__)
rule_code = os.path.basename(dir)

for validity, elem in [
    ("pass", 'IfcRailing'),
    ("pass", 'IfcSlab'),
    ("pass", 'IfcStairFlight'),
    ("pass", 'IfcBeam'),
    ("pass", 'IfcWall'),
    ("fail", "IfcBuildingSystem"), 
    ("fail", "IfcCivilElementType"), 
    ("fail", "IfcPostalAddress"),
    ("fail", "IfcTelecomAddress") ]:

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"       

    try:
        f.create_entity(elem, ifcopenshell.guid.new())
    except RuntimeError:
        f.create_entity(elem)

    f.write(f"{validity}-")
    f.write(f"{os.path.dirname(__file__)}/{validity}-{rule_code}-scenario01-{elem}_present.ifc")


for elem, attribute in [
    ('IfcBuilding', 'BuildingAddress'),
    ('IfcBuilding', 'ElevationOfRefHeight'),
    ('IfcBuilding', 'ElevationOfTerrain'),
    ('IfcBuildingStorey', 'Elevation'),
    ('IfcOrganization', 'Addresses'),
    ('IfcPerson', 'Addresses'),
    ('IfcSite', 'LandTitleNumber'),
    ('IfcSite', 'SiteAddress')
]:
    
    if attribute == 'Addresses':
        v = [f.createIfcAddress()]
    elif attribute in ['SiteAddress', 'BuildingAddress']:
        v = f.createIfcPostalAddress()
    else:
        v = 'test_value'
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"  

    try:
        f.create_entity(
            elem, 
            ifcopenshell.guid.new(),
            **{attribute : v}
        )
    except:
        f.create_entity(
            elem, 
            ifcopenshell.guid.new(),
            **{attribute : 1}
        )

    f.write(f"{dir}/fail-{rule_code}-scenario02-element-{elem}_attribute_{attribute}.ifc")


for i, (elem, value) in enumerate([
    ('IfcFireSuppressionTerminal', 'SPRINKLERDEFLECTOR'),
    ('IfcFireSuppressionTerminal', 'SPRINKLER'),
    ('IfcCableCarrierFitting', 'CROSS'),
    ('IfcCableCarrierFitting', 'JUNCTION'),
    ('IfcCableCarrierFittingType', 'TEE'),
    ('IfcCableCarrierFittingType', 'TRANSITION'),
    ('IfcGeographicElement', 'SOIL_BORING_POINT'),
    ('IfcGeographicElement', 'TERRAIN')
]):

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
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

    f.write(f"{dir}/{pass_or_fail}-{rule_code}-scenario03-{elem}_enum_type_value_{value}.ifc")


