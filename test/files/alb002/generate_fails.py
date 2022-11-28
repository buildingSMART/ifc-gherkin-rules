import ifcopenshell
import uuid

create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)

def setup(file, create_alignment=False, *args, **kwargs):
    file = ifcopenshell.open(file)
    setup_variables = [file, file.by_type("IfcOwnerHistory")[0]]
    if create_alignment:
        setup_variables.append(file.createIfcAlignment(create_guid(), setup_variables[1], Name='dummy alignment'))
    return setup_variables

''''
Scenario 1: Agreement on nested attributes of IfcAlignment

This newly created file will fail for (at least) two reasons:
        (a) A new IfcAlignment is created without a nesting relationship and, instead of the required 1, will nests 0 instances of IfcAlignmentHorizontal
        (b) Three new directions of IfcAlignment are created and linked to an existing IfcAlignment. 
            This existing IfcAlignment will now match two instances of IfcAlignmentHorizontal, IfcAlignmentVertical and IfcAlignmentCant
'''
file, owner, extra_alignment = setup('pass-alb002-alignment-layout.ifc', create_alignment=True)

# Each IfcAlignmnet will nest more than 1 instance of IfcRelNests RelatedObjects (direction)
directions = set() #vertial, horizontal, cantilever
directions.add(file.createIfcAlignmentVertical(create_guid(), owner, Name='AV3')) 
directions.add(file.createIfcAlignmentHorizontal(create_guid(), owner, Name='AH3')) 
directions.add(file.createIfcAlignmentCant(create_guid(), owner, Name='AC3')) 
for d in directions:
    file.createIfcRelNests(create_guid(), owner, RelatingObject = file.by_type("IfcAlignment")[0], RelatedObjects = [d])
file.write('fail-alb002-scenario01.ifc')

''''
Scenario 2: Agreement on attributes being nested within a decomposition relationship

'Each entity must be be nested only by 1 other entity'

A new IfcAlignment instance is created and linked to an instance of IfcAlignmentHorizontal, IfcAlignmentVertical and IfcAlignmentCant
as a result, these three directions are linked to two instances of IfcAlignment 

For example, 'Each IfcAlignment must be nested only be 1 IfcAlignmentHorizontal'
'''
file, owner, extra_alignment = setup('pass-alb002-alignment-layout.ifc', create_alignment=True)

directions = ['IfcAlignmentHorizontal','IfcAlignmentVertical', 'IfcAlignmentCant']

new_relationships = list(map(lambda n: file.createIfcRelNests(create_guid(), owner, RelatingObject=extra_alignment, RelatedObjects=[file.by_type(n)[0]]), directions))

file.write('fail-alb002-scenario02-two_alignments.ifc')


''''
Scenario 3: Agreement on constraints of allowed attributes nesting nested attributes of IfcAlignment
      'Then Each IfcAlignment must nest only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent, IfcAlignments'

      A relationship is created between:
        (1) A newly created IfcAlignment
        (2) Three existing attributes (horizontal, vertical, cant) as well as a newly created attribute, IfcWall

        IfcWall is not in the list of allowed attributes, thereby leading to an error specific for this scenario

        Additionaly, the conditions for scenario two will fail as the three exisiting attributes are now related to two instances of IfcAlignment
'''
file, owner, extra_alignment = setup('pass-alb002-alignment-layout.ifc', create_alignment=True)

related_objects = list(map(lambda n: file.by_type(n)[0], ['IfcAlignmentHorizontal', 'IfcAlignmentVertical', 'IfcAlignmentCant']))
related_objects.append(file.createIfcWall(create_guid(), owner, Name='dummy wall')) #IfcWall is not one of the entities

file.createIfcRelNests(create_guid(), owner, RelatingObject = extra_alignment, RelatedObjects = related_objects)

file.write('fail-alb002-scenario03.ifc')


''''
Scenario 4: Agreement on structure of alignment segments
'''
file, owner = setup('pass-alb002-alignment-layout.ifc')

inst = file.by_type("IfcAlignmentHorizontal")[0]
file.remove(inst.IsNestedBy[0])

file.createIfcRelNests(create_guid(), owner, RelatingObject = inst, 
                        RelatedObjects = [file.createIfcWall(create_guid(), owner, Name='dummy wall')])

file.write('fail-alb002-scenario04.ifc')
# import pdb; pdb.set_trace()



# file.createIfcRelNests(ifcopenshell.guid.new(),'#1','Alignment Nesting',None,'#23',('#28','#510','#125'))
# create_guid = lambda: ifcopenshell.guid.compress(uuid.uuid1().hex)