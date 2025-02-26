import ifcopenshell
import ifcopenshell.template
import os

rule_code = "qty000"

abs_path = os.path.join(os.getcwd(), "test", "files", rule_code)
save_ifc_file = lambda file, filename: file.write(os.path.join(abs_path, filename))

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

save_ifc_file(f, 'pass-qty000-not_activated_no_quantity.ifc')

quantities = [
    f.createIFCQUANTITYLENGTH(
    Name="GrossArea", 
    LengthValue=0), 
    f.createIfcQuantityArea(
    Name="NetArea", 
    AreaValue=0,
    )
]

qt = qt = f.createIfcElementQuantity(
    GlobalId=ifcopenshell.guid.new(),
    Quantities=(quantities)
)

door = f.createIfcDoor(
    GlobalId=ifcopenshell.guid.new(),
)

save_ifc_file(f, 'pass-qty000-not_activated_no_relating_element.ifc')

c = f.createIfcRelDefinesByProperties(
    RelatedObjects = [door],
    RelatingPropertyDefinition = qt
    )

save_ifc_file(f, 'pass-qty000-passing_valid_quantity_relationship_to_object.ifc')