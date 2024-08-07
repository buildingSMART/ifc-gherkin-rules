import ifcopenshell

from enum import Enum, auto

class SubTypeHandling (Enum):
    INCLUDE = auto()
    EXCLUDE = auto()

def check_entity_type(inst: ifcopenshell.entity_instance, entity_type: str, handling: SubTypeHandling) -> bool:
    """
    Check if the instance is of a specific entity type or its subtype.
    INCLUDE will evaluate to True if inst is a subtype of entity_type while the second function for EXCLUDE will evaluate to True only for an exact type match

    Parameters:
    inst (ifcopenshell.entity_instance): The instance to check.
    entity_type (str): The entity type to check against.
    handling (SubTypeHandling): Determines whether to include subtypes or not.

    Returns:
    bool: True if the instance matches the entity type criteria, False otherwise.
    """
    handling_functions = {
        SubTypeHandling.INCLUDE: lambda inst, entity_type: inst.is_a(entity_type),
        SubTypeHandling.EXCLUDE: lambda inst, entity_type: inst.is_a() == entity_type,
    }
    return handling_functions[handling](inst, entity_type)