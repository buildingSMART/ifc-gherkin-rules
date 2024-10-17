import ifcopenshell
import ifcopenshell.template
import os

cwd = os.path.dirname(os.path.abspath(__file__))

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')
owner = file.by_type("IfcOwnerHistory")[0]

file.createIfcWindow(ifcopenshell.guid.new())

def write(fn):
    file.write(os.path.join(cwd, fn))

write('na-blt002-scenario01-no_user_defined_Partitioning_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcWindow(ifcopenshell.guid.new(), 
                    OwnerHistory = owner,
                   UserDefinedPartitioningType = 'TestWindow',
                   PartitioningType = 'USERDEFINED')

write('pass-blt002-scenario01_correct_Partitioning_type.ifc')


for i in ['double_panel_horizontal', 'triple_panel_left']:
    file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')
    file.createIfcWindow(
                    ifcopenshell.guid.new(), 
                    OwnerHistory = owner,
                    UserDefinedPartitioningType = 'TestWindow',
                    PartitioningType = i.upper())
    write(f'fail-blt002-scenario01-Partitioning_type_{i}.ifc')


file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcWindowType(ifcopenshell.guid.new(),
                                            Name = 'TestWindowType',
                                            OwnerHistory = owner,
                                            PredefinedType = 'WINDOW',
                                            PartitioningType = 'DOUBLE_PANEL_HORIZONTAL'
                                            ),
    RelatedObjects = [file.createIfcWindow(
        ifcopenshell.guid.new(),
        OwnerHistory = owner,
    )]
)

write('pass-blt002-scenario02-window_type_no_own_Partitioning_type.ifc')

file = ifcopenshell.template.create(schema_identifier='IFC4X3_ADD2')

file.createIfcRelDefinesByType(
    ifcopenshell.guid.new(),
    RelatingType = file.createIfcWindowType(ifcopenshell.guid.new(),
                                            Name = 'TestWindowType',
                                            OwnerHistory = owner,
                                            PredefinedType = 'WINDOW',
                                            PartitioningType = 'DOUBLE_PANEL_HORIZONTAL'),
    RelatedObjects = [file.createIfcWindow(
        ifcopenshell.guid.new(),
        OwnerHistory = owner,
        PartitioningType = 'TRIPLE_PANEL_VERTICAL', 
        PredefinedType = 'WINDOW'
    )]
)

write('fail-blt002-scenario02-Window_type_own_Partitioning_type.ifc')
