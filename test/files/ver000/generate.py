import ifcopenshell
import ifcopenshell.template
import uuid

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
owner = f.by_type("IfcOwnerHistory")[0]

f.write('na-ver000-owner_without_versioning.ifc')

f.write('pass-ver000-owner_with_change_action.ifc')

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
f.by_type("IfcOwnerHistory")[0].LastModifiedDate = 1320688800

f.write('pass-ver000-owner_with_last_modify_date.ifc')