import itertools
import os
import ifcopenshell
import ifcopenshell.template

G = ifcopenshell.guid.new

def make_file(relate_to_rail, use_valid_predefined_type):

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
    V = file.createIfcAlignmentVertical(G(), owner, Name="AV")
    C = file.createIfcAlignmentCant(G(), owner, Name="AC")

    file.createIfcRelNests(G(), owner, RelatingObject=alignment, RelatedObjects=[H, V, C])

    horizontal_ptypes = (
        ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4X3")
        .declaration_by_name("IfcAlignmentHorizontalSegment")
        .attributes()[-1]
        .type_of_attribute()
        .declared_type()
        .enumeration_items()
    )
    valid_horizontal_ptypes = "LINE", "CIRCULARARC", "CLOTHOID"

    file.createIfcRelNests(
        G(),
        owner,
        RelatingObject=H,
        RelatedObjects=[
            file.createIfcAlignmentSegment(
                G(),
                DesignParameters=file.createIfcAlignmentHorizontalSegment(
                    G(), PredefinedType=pt
                ),
            )
            for pt in (valid_horizontal_ptypes if use_valid_predefined_type else horizontal_ptypes)
        ],
    )
    file.createIfcRelNests(
        G(),
        owner,
        RelatingObject=V,
        RelatedObjects=[
            file.createIfcAlignmentSegment(
                G(), DesignParameters=file.createIfcAlignmentVerticalSegment(G())
            )
            for _ in range(3)
        ],
    )
    file.createIfcRelNests(
        G(),
        owner,
        RelatingObject=C,
        RelatedObjects=[
            file.createIfcAlignmentSegment(
                G(), DesignParameters=file.createIfcAlignmentCantSegment(G())
            )
            for _ in range(3)
        ],
    )

    valid = not relate_to_rail or use_valid_predefined_type

    file.write(f"{'pass' if valid else 'fail'}-{os.path.basename(os.path.dirname(__file__))}-{'in' if not use_valid_predefined_type else ''}valid-predefined-type-{'not-' if not relate_to_rail else ''}related-to-railway.ifc")

for params in itertools.product(range(2), range(2)):
    make_file(*params)