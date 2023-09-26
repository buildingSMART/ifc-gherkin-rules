import os
import ifcopenshell
import ifcopenshell.template

for validity, do_contain, do_aggregate in [
    ("pass", True, False),
    ("pass", False, True),
    ("fail", True, True),
]:

    f = ifcopenshell.template.create(schema_identifier="IFC2X3")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    site = f.createIfcSite(
        ifcopenshell.guid.new(),
        owner,
        CompositionType="ELEMENT",
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[site]
    )

    building = f.createIfcBuilding(
        ifcopenshell.guid.new(),
        owner,
        CompositionType="ELEMENT",
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=site, RelatedObjects=[building]
    )

    wall = f.createIfcWall(
        ifcopenshell.guid.new(),
        owner,
    )

    part = f.createIfcBuildingElementPart(
        ifcopenshell.guid.new(),
        owner,
    )
    
    f.createIfcRelContainedInSpatialStructure(
        ifcopenshell.guid.new(), owner, None, None, [wall], building
    )

    if do_contain:
        f.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(), owner, None, None, [part], building
        )
    if do_aggregate:
        f.createIfcRelAggregates(
            ifcopenshell.guid.new(), owner, RelatingObject=wall, RelatedObjects=[part]
        )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    def fmt(x):
        if isinstance(x, str):
            return x
        else:
            return 'with' if x else 'without'
    case = '_'.join(map(fmt, (do_aggregate, 'aggregate', do_contain, 'contain')))
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{case}.ifc")
