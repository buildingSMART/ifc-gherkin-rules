import ifcopenshell
import ifcopenshell.template


file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcWindow(ifcopenshell.guid.new())

file.write('na-blt002-scenario01-no_user_defined_Partitioning_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcWindow(ifcopenshell.guid.new(), 
                   UserDefinedPartitioningType = 'TestWindow',
                   PartitioningType = 'USERDEFINED')

file.write('pass-blt002-scenario01_correct_Partitioning_type.ifc')


for i in ['double_panel_horizontal', 'triple_panel_left']:
    file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')
    file.createIfcWindow(ifcopenshell.guid.new(), 
                    file.createIfcWindow(ifcopenshell.guid.new(), 
                    UserDefinedPartitioningType = 'TestWindow',
                    PartitioningType = i.upper()))
    file.write(f'fail-blt002-scenario01-Partitioning_type_{i}.ifc')



file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcWindowType(ifcopenshell.guid.new()),
    RelatedObjects = [file.createIfcWindow(
        ifcopenshell.guid.new(),
    )]
)

file.write('pass-blt002-scenario02-window_type_no_own_Partitioning_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcWindowType(ifcopenshell.guid.new()),
    RelatedObjects = [file.createIfcWindow(
        ifcopenshell.guid.new(),
        PartitioningType = 'TRIPLE_PANEL_VERTICAL'
    )]
)

file.write('fail-blt002-scenario02-Window_type_own_Partitioning_type.ifc')
