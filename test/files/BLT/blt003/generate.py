import os
import ifcopenshell
import ifcopenshell.template

for validity, elem in [
    ("pass", 'IfcRailing'),
    ("pass", 'IfcSlab'),
    ("pass", 'IfcStairFlight'),
    ("pass", 'IfcBeam'),
    ("pass", 'IfcMember'),
    ("pass", 'IfcRoof'),
    ("pass", 'IfcWall'),
    ("pass", None),
    ("fail", "IfcCovering"), 
    ("fail", "IfcAlignment"), 
    ("fail", "IfcChimney"), 
    ("fail", "IfcCurtainWall"), 
    ("fail", "IfcDoor"), 
    ("fail", "IfcFooting"), 
    ("fail", "IfcPile"), 
    ("fail", "IfcPlate"), 
    ("fail", "IfcShadingDevice"), 
    ("fail", "IfcWindow"), 
    ("fail", "IfcChimney"), 
    ("fail", "IfcColumn"), 
    ("fail", "IfcCurtainWall"), 
    ("fail", "IfcFooting"), 
    ("fail", "IfcPile"), 
    ("fail", "IfcPlate"), 
    ("fail", "IfcRamp"), 
    ("fail", "IfcRampFlight") ]:

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"       

    stair = f.create_entity("IfcStair", ifcopenshell.guid.new(), owner)

    if elem:
        el = f.create_entity(
            elem,
            ifcopenshell.guid.new(),
            owner
        )

        f.createIfcRelAggregates(
            ifcopenshell.guid.new(), owner, RelatingObject=stair, RelatedObjects=[el]
        )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}IfcStair-aggregating-{elem}.ifc")

