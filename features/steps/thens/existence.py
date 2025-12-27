from dataclasses import dataclass, field
from enum import StrEnum
import operator

import ifcopenshell
from utils import misc
from validation_handling import gherkin_ifc, global_rule

from . import ValidationOutcome, OutcomeSeverity

class NestedAlignmentInstanceAbbreviation(StrEnum):
    IFCALIGNMENTHORIZONTAL = "H"
    IFCALIGNMENTVERTICAL = "V"
    IFCALIGNMENTCANT = "C"
    IFCREFERENT = "R"
    
@dataclass
class ObservedNestedAlignmentInstances:
    horizontal_layouts: list = field(default_factory=list)
    vertical_layouts: list = field(default_factory=list)
    cant_layouts: list = field(default_factory=list)
    referents: list = field(default_factory=list)
    other: list = field(default_factory=list)


@gherkin_ifc.step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(
            operator.attrgetter("RepresentationIdentifier"),
            inst.Representation.Representations,
        )
        if not present:
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)


def get_entities_in_model(context, constraint, entity, include_or_exclude_subtypes):
    # the @global_rule decorator doesn't work with in combination with multiple decorators, hence the helper function
    return misc.do_try(
        lambda: (
            context.model.by_type(entity)
            if include_or_exclude_subtypes == "including subtypes"
            else context.model.by_type(entity, include_subtypes=False)
        ),
        (),  # return empty tuple for deleted entities, e.g. in IFC102
    )


@gherkin_ifc.step(
    "There must be {constraint} {num:d} instance(s) of .{entity}. ^{subtype_handling:include_or_exclude_subtypes}^"
)
@global_rule
def step_impl(context, inst, constraint, num, entity, subtype_handling="including subtypes"):
    op = misc.stmt_to_op(constraint)
    instances_in_model = get_entities_in_model(context, constraint, entity, subtype_handling)
    if not op(len(instances_in_model), num):
        yield ValidationOutcome(
            inst=inst, observed=instances_in_model, severity=OutcomeSeverity.ERROR
        )


@gherkin_ifc.step("There must be {constraint} {num:d} instance(s) of .{entity}.")
@global_rule
def step_impl(context, inst, constraint, num, entity, include_or_exclude_subtypes="including subtypes"):
    """
    The Given step_impl in combination with 'at least 1' is the equivalent of 'Given an IfcEntity', but without setting new applicable instances. 
    For example: 
    Given an IfcWall -> insts = [IfcWall, IfcWall]
    Given an IfcRoof -> inst = [IfcRoof, IfcRoof]
    
    However, 
    Given an IfcWall -> insts = [IfcWall, IfcWall]
    Given there must be at least 1 instance(s) of IfcRoof -> inst = [IfcWall, IfcWall]
    """
    op = misc.stmt_to_op(constraint)
    instances_in_model = get_entities_in_model(context, constraint, entity, include_or_exclude_subtypes)
    if not op(len(instances_in_model), num):
        yield ValidationOutcome(
            inst=inst, observed=instances_in_model, severity=OutcomeSeverity.ERROR
        )
    else: 
        yield ValidationOutcome(
                inst=inst, severity=OutcomeSeverity.PASSED
            )

@gherkin_ifc.step(
    "A representation must have 2 items for PredefinedType of HELMERTCURVE and 1 item for all other values of PredefinedType"
)
def step_impl(context, inst):
    if inst is not None:
        predefined_type = inst.DesignParameters.PredefinedType
        prod_def = inst.Representation
        if prod_def is not None:
            for shape_rep in prod_def.Representations:
                rep_items = list()
                for itm in shape_rep.Items:
                    rep_items.append(itm)

                if predefined_type == "HELMERTCURVE":
                    expected_count = 2
                else:
                    expected_count = 1

                observed_count = len(rep_items)

                if observed_count != expected_count:
                    yield ValidationOutcome(
                        inst=inst,
                        observed=observed_count,
                        expected=expected_count,
                        severity=OutcomeSeverity.ERROR,
                    )


def get_previous_step(context):
    for i, step in enumerate(context.scenario.steps):
        if step.name.lower() == context.step.name.lower() and i > 0:
            return context.scenario.steps[i - 1].name


@gherkin_ifc.step("the alignment layouts must include [{prose_matching}]")
def step_impl(context, inst, prose_matching):
    """
    This implementation is specific to the ALB functional part and validates the proper usage of nesting for alignment layouts.
    It must be preceded by a 'Given its attribute .IsNestedBy.' step so that all RelatedObjects are passed as a single object.
    """

    valid_combos = misc.strip_split(stmt=prose_matching, strp=" ", splt="] or [")

    preceding_step_name = get_previous_step(context).upper()
    assert preceding_step_name == "A RELATIONSHIP .IFCRELNESTS. FROM .IFCALIGNMENT. TO .IFCOBJECT."

    related = inst.IsNestedBy[0].RelatedObjects
    observed_nested_insts = ObservedNestedAlignmentInstances()
    for nested_inst in related:
        match nested_inst.is_a().upper():
            case "IFCALIGNMENTHORIZONTAL":
                observed_nested_insts.horizontal_layouts.append(nested_inst)
            case "IFCALIGNMENTVERTICAL":
                observed_nested_insts.vertical_layouts.append(nested_inst)
            case "IFCALIGNMENTCANT":
                observed_nested_insts.cant_layouts.append(nested_inst)
            case "IFCREFERENT":
                observed_nested_insts.referents.append(nested_inst)
            case _:
                observed_nested_insts.other.append(nested_inst)

    observed_combo = str()
    observed_counts = {
        "horiz": len(observed_nested_insts.horizontal_layouts),
        "vert": len(observed_nested_insts.vertical_layouts),
        "cant": len(observed_nested_insts.cant_layouts),
    }

    for abbr in ["horiz", "vert", "cant"]:
        if observed_counts[abbr] > 0:
            if len(observed_combo) > 0:
                observed_combo += " and "
            observed_combo += f"{observed_counts[abbr]} {abbr.lower()}"

    if observed_combo == "":
        observed_combo = "no alignment layouts"

    if observed_combo not in valid_combos:
        yield ValidationOutcome(
            inst=inst,
            observed={'value': observed_combo},
            expected=valid_combos,
            severity=OutcomeSeverity.ERROR,
        )


@gherkin_ifc.step("Assert existence")
@global_rule
def step_impl(context, inst):

    not_empty = [item for item in misc.recursive_flatten(inst) if item is not None]

    if len(not_empty) == 0:
        expected = get_previous_step(context)
        yield ValidationOutcome(
            inst=inst,
            expected=expected,
            observed="Nonexistent",
            severity=OutcomeSeverity.ERROR,
        )


@gherkin_ifc.step("The IFC model contains information on {functional_part_description}")
def step_impl(context, inst, functional_part_description):
    # This rule is designed to always pass and is used solely to trigger the activation of the rule
    # if an instance linked to the functional part is present.
    pass
