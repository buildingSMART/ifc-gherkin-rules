import ifcopenshell

file = ifcopenshell.open('fail-alb002-scenario02-two_alignments.ifc')

instances = file.by_type('IfcAlignmentHorizontal')

def get_attributes(instances, nesting_type, object_type, expected_value):
    for inst in instances:
        print(inst.Nests[0].RelatingObject.is_a(expected_value))
    filter(lambda inst: inst.Nests[0].RelatingObject.is_a(expected_value), instances)
    x1 = list(
        map(lambda inst: getattr(inst, 'Nests')[0].RelatingObject.is_a(expected_value), instances)
    )
    print('x1', x1)
    x2 = list(
        filter(lambda inst: not getattr(inst, 'Nests')[0].RelatingObject.is_a(expected_value), instances)
    )   
    print('x2', x2)
    return x1, x2

get_attributes(instances, 'Nests', 'RelatingObject', 'IfcAlignment')

import pdb; pdb.set_trace()