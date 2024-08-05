import ifcopenshell
import ifcopenshell.template
import os

rule_code = "cls000"

abs_path = os.path.join(os.getcwd(), "test", "files", rule_code)
save_ifc_file = lambda file, filename: file.write(os.path.join(abs_path, filename))

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

save_ifc_file(f, 'pass-cls000-not_activated_no_reference.ifc')

ref = f.createIfcClassificationReference()
annotation = f.createIfcAnnotation()

save_ifc_file(f, 'pass-cls000-not_activated_no_relating_classification_project.ifc')

c = f.createIfcRelAssociatesClassification(
    RelatedObjects = [annotation],
    RelatingClassification = ref
    )

save_ifc_file(f, 'pass-cls000-passing_valid_classification_association.ifc')