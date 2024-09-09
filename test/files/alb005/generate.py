import os
import ifcopenshell
import ifcopenshell.template

for validity, do_position, predefined_type in [
    ("pass", True, None),
    ("pass", True, 'NOTDEFINED'),
    ("pass", True, 'POSITION'),
    ("fail", False, 'STATION')
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
        ifcopenshell.guid.new(), owner, RelatingObject=alignment, RelatedObjects=[horizontal]
    )

    referent = f.createIfcReferent(
        ifcopenshell.guid.new(),
        owner,
        PredefinedType=predefined_type
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
        elif x is None:
            return 'no_predefined_type'
        else:
            return 'with' if x else 'without'
    case = '_'.join(map(fmt, (predefined_type, do_position, 'position')))
    f.write(f"{validity}-IfcReferent-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{case}.ifc")
