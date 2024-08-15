import os
import ifcopenshell
import ifcopenshell.template

for validity, do_position, do_reference in [
    ("pass", True, True),
    ("pass", False, False),
    ("pass", False, True),
    ("fail", True, False),
]:
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
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

    signal = f.createIfcSignal(
        ifcopenshell.guid.new(),
        owner,
    )

    if do_reference:
        f.createIfcRelReferencedInSpatialStructure(
            ifcopenshell.guid.new(), owner, None, None, [signal], site
        )
    if do_position:
        f.createIfcRelPositions(
        ifcopenshell.guid.new(), owner, RelatingPositioningElement=alignment, RelatedProducts=[signal]
    )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    def fmt(x):
        if isinstance(x, str):
            return x
        else:
            return 'with' if x else 'without'
    case = '_'.join(map(fmt, (do_position, 'position', do_reference, 'reference')))
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{case}.ifc")
