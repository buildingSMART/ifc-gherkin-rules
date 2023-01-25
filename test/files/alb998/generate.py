import itertools
import os
import ifcopenshell
import ifcopenshell.template

G = ifcopenshell.guid.new

relate_to_rail = True

def make_file(refs, psets):

    file = ifcopenshell.template.create(schema_identifier="IFC4X3")
    owner = file.by_type("IfcOwnerHistory")[0]

    site = file.createIfcSite(G(), owner)
    alignment = file.createIfcAlignment(G(), owner, Name="A1")
    site_containees = [alignment]

    if relate_to_rail:
        rail = file.createIfcRailway(G(), owner)
        site_containees.append(rail)
        file.createIfcRelReferencedInSpatialStructure(
            G(), owner, RelatedElements=[alignment], RelatingStructure=rail
        )

    file.createIfcRelContainedInSpatialStructure(
        G(), owner, RelatedElements=site_containees, RelatingStructure=site
    )

    H = file.createIfcAlignmentHorizontal(G(), owner, Name="AH")

    Refs = []

    for r, wp in zip(refs, psets):
        R = file.createIfcReferent(G(), owner, PredefinedType=r)
        if wp:
            file.createIfcRelDefinesByProperties(
                G(),
                owner,
                RelatingPropertyDefinition=file.createIfcPropertySet(G(), owner, Name='Pset_Stationing', HasProperties=[
                    file.createIfcPropertySingleValue('Station', NominalValue=file.createIfcLengthMeasure(0.))
                ]),
                RelatedObjects=[R],
            )
        Refs.append(R)

    file.createIfcRelNests(G(), owner, RelatingObject=alignment, RelatedObjects=[H] + Refs)

    file.createIfcRelNests(
        G(),
        owner,
        RelatingObject=H,
        RelatedObjects=[
            file.createIfcAlignmentSegment(
                G(),
                DesignParameters=file.createIfcAlignmentHorizontalSegment(
                    G(), PredefinedType="LINE"
                ),
            )
        ],
    )
    
    valid = ("REFERENCEMARKER", True) in zip(refs, psets) or ("STATION", True) in zip(refs, psets)

    cfg = "-".join(f"{(pt or 'nil').lower()}-with{'' if wp else 'out'}-property" for pt, wp in zip(refs, psets)) or 'empty'

    file.write(f"{'pass' if valid else 'fail'}-{os.path.basename(os.path.dirname(__file__))}-{cfg}.ifc")

configs = [
    ([], []),
    ([None], [False]),
    (["KILOPOINT"],[True]),
    (["REFERENCEMARKER"],[False]),
    (["REFERENCEMARKER"],[True]),
    (["STATION"],[True]),
    (["REFERENCEMARKER", "STATION"],[False, True]),
    (["REFERENCEMARKER", "REFERENCEMARKER"],[True, False]),
    (["STATION", None],[False, True]),
]

for cfg in configs:
    make_file(*cfg)