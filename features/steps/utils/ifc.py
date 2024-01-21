from .misc import do_try


def condition(inst, representation_id, representation_type):
    def is_valid(inst, representation_id, representation_type):
        representation_type = list(map(lambda s: s.strip(" ").strip("\""), representation_type.split(",")))
        return any([repre.RepresentationIdentifier in representation_id and repre.RepresentationType in representation_type for repre in do_try(lambda: inst.Representation.Representations, [])])

    if is_valid(inst, representation_id, representation_type):
        return any([repre.RepresentationIdentifier == representation_id and repre.RepresentationType in representation_type for repre in do_try(lambda: inst.Representation.Representations, [])])


def get_precision_from_contexts(entity_contexts, func_to_return=max, default_precision=1e-05):
    precisions = []
    if not entity_contexts:
        return default_precision
    for entity_context in entity_contexts:
        if entity_context.is_a('IfcGeometricRepresentationSubContext'):
            precision = get_precision_from_contexts([entity_context.ParentContext])
        elif entity_context.is_a('IfcGeometricRepresentationContext') and entity_context.Precision:
            return entity_context.Precision
        else:
            continue
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

def order_by_ifc_inheritance(instances, base_class_last):
    import ifcopenshell
    ifc = ifcopenshell.file(schema='IFC4X3')
    inheritance_nr = {}
    for instance in instances:
        ifc_instance = ifc.create_entity(instance)
        result = sum(1 for str_instance in instances if ifc_instance.is_a(str_instance))
        inheritance_nr[instance] = result
    inheritance_nr = dict(sorted(inheritance_nr.items(), key=lambda item: item[1], reverse=base_class_last))
    return list(inheritance_nr.keys())


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
