import ifcopenshell
import ifcopenshell.template
import os

rule_code = "mat000"

abs_path = os.path.join(os.getcwd(), "test", "files", rule_code)
save_ifc_file = lambda file, filename: file.write(os.path.join(abs_path, filename))

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

save_ifc_file(f, 'pass-mat000-not_activated_no_material.ifc')

material = f.createIfcMaterial()
wall = f.createIfcWall()

save_ifc_file(f, 'pass-mat000-not_activated_no_relationship_material_element.ifc')

c = f.createIfcRelAssociatesMaterial(
    RelatedObjects = [wall],
    RelatingMaterial = material
    )

save_ifc_file(f, 'pass-mat000-passing_valid_material_assigned_to_element.ifc')