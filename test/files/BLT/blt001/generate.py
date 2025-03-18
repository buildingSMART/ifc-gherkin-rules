import ifcopenshell
import ifcopenshell.template


file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcDoor(ifcopenshell.guid.new())

file.write('pass-blt001-scenario01-no_user_defined_operation_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcDoor(ifcopenshell.guid.new(), 
                   UserDefinedOperationType = 'TestDoor',
                   OperationType = 'USERDEFINED')

file.write('pass-blt001-scenario01_correct_operation_type.ifc')


for i in ['swing_fixed_right', 'single_swing_right']:
    file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')
    file.createIfcDoor(ifcopenshell.guid.new(), 
                    file.createIfcDoor(ifcopenshell.guid.new(), 
                    UserDefinedOperationType = 'TestDoor',
                    OperationType = i.upper()))
    file.write(f'fail-blt001-scenario01-operation_type_{i}.ifc')



file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcDoorType(ifcopenshell.guid.new()),
    RelatedObjects = [file.createIfcDoor(
        ifcopenshell.guid.new(),
    )]
)

file.write('pass-blt001-scenario02-door_type_no_own_operation_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcDoorType(ifcopenshell.guid.new()),
    RelatedObjects = [file.createIfcDoor(
        ifcopenshell.guid.new(),
        OperationType = 'SLIDING_TO_RIGHT'
    )]
)

file.write('fail-blt001-scenario02-door_type_own_operation_type.ifc')
