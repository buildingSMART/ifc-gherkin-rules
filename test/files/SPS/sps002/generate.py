import os
import ifcopenshell
import ifcopenshell.template

for validity, elem in [
    ("pass", 'IfcBuilding'),
    ("pass", 'IfcSite'),
    ("pass", 'IfcAlignment'),
    ("pass", None),
    ("fail", "IfcBeam")
]:

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    if elem:
        el = f.create_entity(
            elem,
            ifcopenshell.guid.new(),
            owner
        )

        f.createIfcRelAggregates(
            ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[el]
        )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}IfcProject-aggregating-{elem}.ifc")
