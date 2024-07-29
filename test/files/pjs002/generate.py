import ifcopenshell
import ifcopenshell.template
import os

for rel_name, relating, related, i, description in [
    ('IfcRelAggregates', 'RelatingObject', 'RelatedObjects', 1, 'is_decomposed_by'),
    ('IfcRelDeclares', 'RelatingContext', 'RelatedDefinitions', 2, 'declares')
]:
    for validity, elem in [
        ("pass", 'IfcProjectLibrary'),
        ("pass", 'IfcPropertySetTemplate'),
        ("fail", 'IfcAlignment'),
        ("fail", "IfcElement"),
        ("fail", "IfcBeam")
    ]:

        f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
        building_parent = proj = f.by_type("IfcProject")[0]
        owner = f.by_type("IfcOwnerHistory")[0]
        owner.ChangeAction = "ADDED"

        f.create_entity(
            rel_name,
            ifcopenshell.guid.new(),
            owner,
            **{relating: proj, related:[f.create_entity(
            elem,
            ifcopenshell.guid.new(),
            owner
        )]}
        )

        f.write(f"{os.path.dirname(__file__)}/{validity}-pjs002-scenario0{i}-project_{description}_{elem}.ifc")