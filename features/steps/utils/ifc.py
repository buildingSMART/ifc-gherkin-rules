import typing
from .misc import do_try
import ifcopenshell


def condition(inst, representation_id, representation_type):
    def is_valid(inst, representation_id, representation_type):
        representation_type = list(map(lambda s: s.strip(" ").strip("\""), representation_type.split(",")))
        return any([repre.RepresentationIdentifier in representation_id and repre.RepresentationType in representation_type for repre in do_try(lambda: inst.Representation.Representations, [])])

    if is_valid(inst, representation_id, representation_type):
        return any([repre.RepresentationIdentifier == representation_id and repre.RepresentationType in representation_type for repre in do_try(lambda: inst.Representation.Representations, [])])


def get_precision_from_contexts(entity_contexts : typing.Sequence[ifcopenshell.entity_instance], func_to_return : typing.Callable = max, default_precision : float = 1e-05, return_in_m : bool = False):
    """Determine the precision from a sequence of IfcGeometricRepresentationContext

    Args:
        entity_contexts (typing.Sequence[ifcopenshell.entity_instance]): Set of instances (typically returned by recurrently_get_entity_attr() to traverse upwards from a representation item to its context)
        func_to_return (typing.Callable, optional): The aggregate function to apply when multiple distinct precision values are found. Defaults to max().
        default_precision (float, optional): The default precision value when no values are found in the model. Defaults to 1e-05.
        return_in_m (bool, optional): Precision is a length measure so the length unit factor should be applied to it when comparing the value to values in meters (such as the ifcopenshell.geom defaults). Defaults to False.

    Returns:
        float: Precision value
    """
    precisions = []
    if not entity_contexts:
        return default_precision
    if return_in_m:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(next(iter(entity_contexts)).file)
    else:
        unit_scale = 1.
    for entity_context in entity_contexts:
        if entity_context.Precision is not None:
            precision = entity_context.Precision * unit_scale
            precisions.append(precision)
    if not precisions:
        return default_precision
    return func_to_return(precisions)

def get_relation(instance, attrs : list):
    relations = (
        getattr(instance, attr, [None])[0]
        for attr in attrs
    )
    return next((rel for rel in relations if rel is not None), None) # always len == 1

def get_mvd(ifc_file):
    try:
        detected_mvd = ifc_file.header.file_description.description[0].split(" ", 1)[1]
        detected_mvd = detected_mvd[1:-1]
    except:
        detected_mvd = None
    return detected_mvd


def instance_getter(i, representation_id, representation_type, negative=False):
    if negative:
        if not condition(i, representation_id, representation_type):
            return i
    else:
        if condition(i, representation_id, representation_type):
            return i


def recurrently_get_entity_attr(ifc_context, inst, entity_to_look_for, attr_to_get, attr_found=None):
    if attr_found is None:
        attr_found = set()
    if inst.is_a(entity_to_look_for):
        return getattr(inst, attr_to_get)
    else:
        for inv_item in ifc_context.model.get_inverse(inst):
            if inv_item.is_a(entity_to_look_for):
                attr_found.add((getattr(inv_item, attr_to_get)))
            else:
                recurrently_get_entity_attr(ifc_context, inv_item, entity_to_look_for, attr_to_get, attr_found)
    return attr_found

def check_entity_type(inst: ifcopenshell.entity_instance, entity_type: str, include_or_exclude_subtypes) -> bool:
    """
    Check if the instance is of a specific entity type or its subtype.
    INCLUDE will evaluate to True if inst is a subtype of entity_type while the second function for EXCLUDE will evaluate to True only for an exact type match

    Parameters:
    inst (ifcopenshell.entity_instance): The instance to check.
    entity_type (str): The entity type to check against.
    include_or_exclude_subtypes: Determines whether to include subtypes or not.

    Returns:
    bool: True if the instance matches the entity type criteria, False otherwise.
    """
    handling_functions = {
        "including subtypes": lambda inst, entity_type: inst.is_a(entity_type),
        "excluding subtypes": lambda inst, entity_type: inst.is_a() == entity_type,
    }
    return handling_functions[include_or_exclude_subtypes](inst, entity_type)
