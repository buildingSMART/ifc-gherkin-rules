import ifcopenshell
import ifcopenshell.template


def create_testfiles(schema, current_schema_identifiers):
    file = ifcopenshell.template.create(schema_identifier=schema)
    context = file.by_type("IfcGeometricRepresentationContext")[0]
    owner = file.by_type("IfcOwnerHistory")[0]
    building_parent = proj = file.by_type("IfcProject")[0]
    site = file.createIfcSite(ifcopenshell.guid.new(), owner)

    fail_or_pass = 'pass' if schema in current_schema_identifiers else 'fail'
    file.write(f"{fail_or_pass}-ifc001-{schema}.ifc")

current_schema_identifiers = ["IFC4X3_ADD2", "IFC2X3"]
all_identifiers = ['IFC4X3_ADD2', 'IFC2X3', 'IFC4X3', 'IFC4X3_ADD2', 'IFC2X3_ADD1', 'IFC4X3_TC1']

for schema_identifier in all_identifiers:
    create_testfiles(schema_identifier, current_schema_identifiers)