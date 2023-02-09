import typing
import ifcopenshell

from dataclasses import dataclass, field
from utils import *

@dataclass
class attribute_type_error:
    inst: ifcopenshell.entity_instance
    related: ifcopenshell.entity_instance
    attribute: str
    expected_entity_type: str

    def __str__(self):
        if len(self.related):
            return f"The instance {self.inst} expected type '{self.expected_entity_type}' for the attribute {self.attribute}, but found {fmt(self.related)}  "
        else:
            return f"This instance {self.inst} has no value for attribute {self.attribute}"

@dataclass
class duplicate_value_error:
    inst: ifcopenshell.entity_instance
    incorrect_values: typing.Sequence[typing.Any]
    attribute: str
    incorrect_insts: typing.Sequence[ifcopenshell.entity_instance]
    report_incorrect_insts: bool = field(default=True)

    def __str__(self):
        incorrect_insts_statement = f"on instance(s) {', '.join(map(fmt, self.incorrect_insts))}" if not self.report_incorrect_insts else ''
        return (
            f"On instance {fmt(self.inst)} , "
            f"the following duplicate value(s) for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.incorrect_values))} {incorrect_insts_statement}"
        )

@dataclass
class edge_use_error:
    inst: ifcopenshell.entity_instance
    edge: typing.Any
    count: int

    def __str__(self):
        return f"On instance {fmt(self.inst)} the edge {fmt(self.edge)} was referenced {fmt(self.count)} times"

@dataclass
class identical_values_error:
    insts: typing.Sequence[ifcopenshell.entity_instance]
    incorrect_values: typing.Sequence[typing.Any]
    attribute: str

    def __str__(self):
        return (
            f"On instance(s) {';'.join(map(fmt, self.insts))}, "
            f"the following non-identical values for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.incorrect_values))}"
        )

@dataclass
class instance_count_error:
    insts: ifcopenshell.entity_instance
    type_name: str

    def __str__(self):
        if len(self.insts):
            return f"The following {len(self.insts)} instances of type {self.type_name} were encountered: {';'.join(map(fmt, self.insts))}"
        else:
            return f"No instances of type {self.type_name} were encountered"

@dataclass
class instance_placement_error:
    entity: ifcopenshell.entity_instance
    placement: str
    container: ifcopenshell.entity_instance
    relationship: str
    container_obj_placement: ifcopenshell.entity_instance
    entity_obj_placement: ifcopenshell.entity_instance

    def __str__(self):
        if self.placement:
            return f"The placement of {fmt(self.entity)} is not defined by {fmt(self.placement)}, but with {fmt(self.entity.ObjectPlacement)}"
        elif all([self.container, self.relationship, self.container_obj_placement, self.entity_obj_placement]):
            return f"The entity {fmt(self.entity)} is contained in {fmt(self.container)} with the {fmt(self.relationship)} relationship. " \
                   f"The container points to {fmt(self.container_obj_placement)}, but the entity to {fmt(self.entity_obj_placement)}"

@dataclass
class instance_structure_error:
    # @todo reverse order to relating -> nest-relationship -> related
    related: ifcopenshell.entity_instance
    relating: ifcopenshell.entity_instance
    relationship_type: str
    optional_values: dict = field(default_factory=dict)

    def __str__(self):
        pos_neg = 'is not' if self.optional_values.get('condition', '') == 'must' else 'is'
        directness = self.optional_values.get('directness', '')

        if len(self.relating):
            return f"The instance {fmt(self.related)} {pos_neg} {directness} {self.relationship_type} (in) the following ({len(self.relating)}) instances: {';'.join(map(fmt, self.relating))}"
        else:
            return f"This instance {self.related} is not {self.relationship_type} anything"

@dataclass
class invalid_value_error:
    related: ifcopenshell.entity_instance
    attribute: str
    value: str

    def __str__(self):
        return f"On instance {fmt(self.related)} the following invalid value for {self.attribute} has been found: {self.value}"

@dataclass
class polyobject_duplicate_points_error:
    inst: ifcopenshell.entity_instance
    duplicates: set

    def __str__(self):
        points_desc = ''
        for duplicate in self.duplicates:
            point_desc = f'point {str(duplicate[0])} and point {str(duplicate[1])}; '
            points_desc = points_desc + point_desc
        return f"On instance {fmt(self.inst)} there are duplicate points: {points_desc}"

@dataclass
class polyobject_point_reference_error:
    inst: ifcopenshell.entity_instance
    points: list

    def __str__(self):
        return f"On instance {fmt(self.inst)} first point {self.points[0]} is the same as last point {self.points[-1]}, but not by reference"

@dataclass
class representation_shape_error:
    inst: ifcopenshell.entity_instance
    representation_id: str

    def __str__(self):
        return f"On instance {fmt(self.inst)} the instance should have one {self.representation_id} shape representation"

@dataclass
class representation_type_error:
    inst: ifcopenshell.entity_instance
    representation_id: str
    representation_type: str

    def __str__(self):
        return f"On instance {fmt(self.inst)} the {self.representation_id} shape representation does not have {self.representation_type} as RepresentationType"

