import ifcopenshell
import ifcopenshell.template
import uuid
import random

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

file = ifcopenshell.template.create(schema_identifier="IFC4X3")
building_parent = proj = file.by_type("IfcProject")[0]
owner = file.by_type("IfcOwnerHistory")[0]

site = file.createIfcSite(ifcopenshell.guid.new(), owner)

buildings = file.createIfcBuilding(ifcopenshell.guid.new(), owner)

alignment = file.createIfcAlignment(create_guid(), owner, Name='A1')

alignment_horizontal_instance = file.createIfcAlignmentHorizontal(create_guid(), owner, Name='AV3')
alignment_vertical_instance = file.createIfcAlignmentVertical(create_guid(), owner, Name='AV3')
alignment_cant_instance = file.createIfcAlignmentCant(create_guid(), owner, Name='AV3')

directions = [alignment_horizontal_instance, alignment_vertical_instance, alignment_cant_instance]

file.createIfcRelNests(create_guid(), owner, RelatingObject = file.by_type("IfcAlignment")[0], RelatedObjects = [d for d in directions])

file.createIfcRelNests( create_guid(), owner, RelatingObject = alignment_horizontal_instance,
                        RelatedObjects = [ file.createIfcAlignmentSegment(create_guid(),
                            DesignParameters = file.createIfcAlignmentHorizontalSegment(create_guid())
                        ) for i in range(random.randint(5,10))
                        ]
                      )
file.createIfcRelNests( create_guid(), owner, RelatingObject = alignment_vertical_instance,
                        RelatedObjects = [ file.createIfcAlignmentSegment(create_guid(),
                            DesignParameters = file.createIfcAlignmentVerticalSegment(create_guid())
                        ) for i in range(random.randint(5,10))
                        ]
                      )
file.createIfcRelNests( create_guid(), owner, RelatingObject = alignment_cant_instance,
                        RelatedObjects = [ file.createIfcAlignmentSegment(create_guid(),
                            DesignParameters = file.createIfcAlignmentCantSegment(create_guid())
                        ) for i in range(random.randint(5,10))
                        ]
                      )

                    
file.write('pass-alb002-manually_created_file.ifc')