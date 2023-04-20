from .misc import do_try, map_state
from .system import list_renamed_entities

from dataclasses import dataclass, field

import typing


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
        precisions.append(precision)
    return func_to_return(precisions)


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


@dataclass
class IfcEntity:
    entity : str
    instances : typing.List = field(default_factory=lambda: [])
    renamed_entities : typing.List = field(default_factory=lambda : list_renamed_entities())

    def search(self, num):
        tup = next((t for t in self.renamed_entities if t[num] == self.entity), None)
        if tup:
            idx = 1 if num == 0 else 0
            return tup[idx]
    
    def get_alternative_name(self):
        # If the entity is renamed, such as in the case of 'IfcBuildingElement' being changed to 'IfcBuiltElement'
        self.alternative_name = next(filter(None, map(self.search, [0, 1])), None)
        return self.alternative_name
    
    def get_entity_instances(self, context):
        try:
            return context.model.by_type(self.entity)
        except:
            try:
                return context.model.by_type(self.get_alternative_name())
            except:
                return []
    
    def is_entity_instance(self, entity):
        '''
        Checks whether input is a subtype of ifcopenshell_entity_instance or it's alternative name
        '''
        return any([entity.is_a(i) for i in [self.entity, self.get_alternative_name()]])

@dataclass
class ContinuingInstances:
    """
Extracts `ifcopenshell.entity_instance` objects from a filtered stack tree.

Args:
    filtered_stack_tree. Lists that represent the presence of
        `ifcopenshell.entity_instance` objects, where the first list contains the objects 
        and the second list (optional) contains boolean values

    instances (List[ifcopenshell.entity_instance], optional): Additional `ifcopenshell.entity_instance`
        objects to include in the output.

Returns:
    List[ifcopenshell.entity_instance]: The `ifcopenshell.entity_instance` objects extracted from the
    filtered stack tree, i n the order that they appear in the second list.
    """
    instances: typing.List = field(default_factory=lambda: [])

    def check_applicability(self, i):
        self.local_appl = i is True

    def build(self, num):
        """
        Take into consideration the case in which order of bool-entity_instances are reversed
        """
        idx = 1 if num == 0 else 1
        map_state(self.item_pair[num], self.check_applicability)
        if self.local_appl:
            self.instances.append(self.item_pair[idx])

    def collect_applicable_instances(self, filtered_stack_tree):
        if len(filtered_stack_tree) == 2:
            self.pairs = list(
                zip(filtered_stack_tree[0], filtered_stack_tree[1]))
            for pair in self.pairs:
                self.item_pair = pair
                [self.build(i) for i in range(2)]
        else:
            self.instances = filtered_stack_tree[0]