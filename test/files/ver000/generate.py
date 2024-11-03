import ifcopenshell
import ifcopenshell.template
import uuid
from importlib.metadata import version

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
owner = f.by_type("IfcOwnerHistory")[0]
user = f.by_type("IfcPersonAndOrganization")[0]
organization = f.by_type("IfcOrganization")[0]
person = f.by_type("IfcPerson")
application = f.by_type("IfcApplication")[0]

organization.Name = 'Validation Service Team'

f.write('na-ver000-owner_without_versioning.ifc')

f.write('na-ver000-owner_with_change_action.ifc')

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
owner.LastModifiedDate = 1320688800

f.write('na-ver000-owner_with_last_modify_date.ifc')

owner.LastModifyingUser = user
owner.LastModifyingApplication = application

f.write('pass-ver000-versioning_attributes_present.ifc')