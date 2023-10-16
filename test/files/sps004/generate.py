import os
import ifcopenshell
import ifcopenshell.template

for validity, do_position, do_contain in [
    ("pass", True, False),
    ("pass", False, True),
    ("fail", True, True),
]:

    f = ifcopenshell.template.create(schema_identifier="'IFC4X3_ADD2")
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

    alignment = f.createIfcAlignment(
        ifcopenshell.guid.new(),
        owner,
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[alignment]
    )

    horizontal = f.createIfcAlignmentHorizontal(
        ifcopenshell.guid.new(),
        owner,
    )

    f.createIfcRelNests(
        ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[alignment]
    )

    referent = f.createIfcReferent(
        ifcopenshell.guid.new(),
        owner,
    )

    if do_contain:
        f.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(), owner, None, None, [referent], site
        )
    if do_position:
        f.createIfcRelPositions(
        ifcopenshell.guid.new(), owner, RelatingPositioningElement=alignment, RelatedProducts=[referent]
    )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    def fmt(x):
        if isinstance(x, str):
            return x
        else:
            return 'with' if x else 'without'
    case = '_'.join(map(fmt, (do_position, 'position', do_contain, 'contain')))
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{case}.ifc")
