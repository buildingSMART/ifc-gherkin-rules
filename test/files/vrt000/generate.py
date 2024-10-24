import ifcopenshell
import ifcopenshell.template
import uuid

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

file = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
building_parent = proj = file.by_type("IfcProject")[0]
owner = file.by_type("IfcOwnerHistory")[0]
         
file.write('na-vrt000-no_virtual_element.ifc')

file.createIfcVirtualElement(create_guid(), owner)

file.write('pass-vrt000-virtual_element_present.ifc')
