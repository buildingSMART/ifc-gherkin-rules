# import gc
# def count_entity_instances():
#     gc.collect()
#     return sum(1 for o in gc.get_objects()
#                if type(o).__name__ == "entity_instance"
#                and "ifcopenshell" in type(o).__module__)


import gc
from types import ModuleType

def is_ifc_entity(o):
    t = type(o)
    # looser but reliable: name + module prefix
    return (t.__name__ == "entity_instance"
            and isinstance(__import__(t.__module__.split('.')[0]), ModuleType)  # module exists
            and t.__module__.startswith("ifcopenshell"))

def count_entity_instances():
    gc.collect()
    objs = gc.get_objects()
    return sum(1 for o in objs if is_ifc_entity(o))

# sanity: do these wrappers appear in gc.get_objects?
def seen_in_gc(objs):
    gc.collect()
    ids_in_gc = {id(o) for o in gc.get_objects()}
    return sum(1 for o in objs if id(o) in ids_in_gc)