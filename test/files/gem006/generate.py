import ifcopenshell
import ifcopenshell.template

import itertools


def generate_representation_tree(file, value):
    representations = [file.createIfcShapeRepresentation(
        RepresentationIdentifier=value)]
    return file.createIfcProductDefinitionShape(Representations=representations)


def create_aggregates_relationship(filename, relating_value, related_value, n_related, empty=False):
    file = ifcopenshell.template.create(schema_identifier="IFC4")
    relating = file.createIfcRoof(
        ifcopenshell.guid.new(),
        Representation=generate_representation_tree(file, value=relating_value)
    )

    Representation = generate_representation_tree(
        file, value=related_value) if not empty else None

    related = [
        file.createIfcSlab(
            ifcopenshell.guid.new(),
            Representation=Representation
        ) for _ in range(n_related)
    ]

    file.createIfcRelAggregates(
        ifcopenshell.guid.new(),
        RelatingObject=relating,
        RelatedObjects=related
    )

    # file.write(filename)


for relating, related, num_relating in itertools.product(['Body', 'Axis'], ['Body', 'Axis', 'Box'], (0, 1)):
    if not relating == 'Body' and num_relating == 0:
        continue
    not_ok = relating == 'Body' and num_relating > 0
    fail_or_pass = "fail" if not_ok else "pass"

    filename = f"{fail_or_pass}-gem005-{num_relating}-relating-{relating.lower()}-2-related-{related.lower()}.ifc"

    create_aggregates_relationship(
        filename=filename, relating_value=relating, related_value=related, n_related=2)

# create_aggregates_relationship(filename='pass-1-relating-body-empty-related.ifc')
