import os
import ifcopenshell
import ifcopenshell.template

cwd = os.path.dirname(os.path.abspath(__file__))
rule_code = os.path.basename(cwd)


def new_model(schema_identifier):
    f = ifcopenshell.template.create(schema_identifier=schema_identifier)
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "NOCHANGE"
    return f, owner


def properties(f, with_reference, reference_value="A-1"):
    props = []
    if with_reference:
        props.append(f.createIfcPropertySingleValue("Reference", None, f.createIfcIdentifier(reference_value), None))
    props.append(f.createIfcPropertySingleValue("IsExternal", None, f.createIfcBoolean(True), None))
    return props


def add_pset(f, owner, element, pset_name, with_reference):
    pset = f.createIfcPropertySet(ifcopenshell.guid.new(), owner, pset_name, None, properties(f, with_reference))
    f.createIfcRelDefinesByProperties(ifcopenshell.guid.new(), owner, None, None, [element], pset)
    return pset


def wall_with_pset(schema_identifier, pset_name, with_reference):
    f, owner = new_model(schema_identifier)
    wall = f.createIfcWall(ifcopenshell.guid.new(), owner)
    add_pset(f, owner, wall, pset_name, with_reference)
    return f, owner, wall


def write(f, validity, rest):
    filename = f"{validity}-{rule_code}-{rest}.ifc"
    f.header.file_name.name = filename
    f.write(os.path.join(cwd, filename))


# IFC4.3: 'Reference' is deprecated in every standard property set (Pset_*) that defines it
f, owner, wall = wall_with_pset("IFC4X3_ADD2", "Pset_WallCommon", with_reference=True)
write(f, "fail", "ifc4x3-reference_in_pset_wallcommon")

# ... also when the property set is attached to a type object via HasPropertySets
f, owner = new_model("IFC4X3_ADD2")
pset = f.createIfcPropertySet(ifcopenshell.guid.new(), owner, "Pset_DoorCommon", None, properties(f, True, "D-1"))
f.createIfcDoorType(ifcopenshell.guid.new(), owner, "Door type D-1", HasPropertySets=[pset],
                    PredefinedType="DOOR", OperationType="SINGLE_SWING_LEFT")
write(f, "fail", "ifc4x3-reference_in_pset_doorcommon_on_type")

# standard property set without the deprecated property
f, owner, wall = wall_with_pset("IFC4X3_ADD2", "Pset_WallCommon", with_reference=False)
write(f, "pass", "ifc4x3-pset_wallcommon_without_reference")

# 'Reference' in a custom (non Pset_) property set is ignored; the standard property set next to it is checked
f, owner, wall = wall_with_pset("IFC4X3_ADD2", "Pset_WallCommon", with_reference=False)
add_pset(f, owner, wall, "MyCompany_WallData", with_reference=True)
write(f, "pass", "ifc4x3-reference_in_custom_pset_next_to_pset_wallcommon")

# only a custom property set: nothing to check
f, owner, wall = wall_with_pset("IFC4X3_ADD2", "MyCompany_WallData", with_reference=True)
write(f, "na", "ifc4x3-reference_in_custom_pset_only")

# 'Reference' is not deprecated in IFC4 and IFC2X3
f, owner, wall = wall_with_pset("IFC4", "Pset_WallCommon", with_reference=True)
write(f, "na", "ifc4-reference_in_pset_wallcommon")
f, owner, wall = wall_with_pset("IFC2X3", "Pset_WallCommon", with_reference=True)
write(f, "na", "ifc2x3-reference_in_pset_wallcommon")

# no property sets at all
f, owner = new_model("IFC4X3_ADD2")
f.createIfcWall(ifcopenshell.guid.new(), owner)
write(f, "na", "ifc4x3-no_property_sets")
