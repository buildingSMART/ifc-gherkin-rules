from behave import register_type
import itertools
from typing import Dict
from typing import List
from typing import Union

import ifcopenshell.entity_instance

from utils import ifc43x_alignment_validation as ifc43
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

from parse_type import TypeBuilder

register_type(absence_or_presence=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("presence", "absence")))))


def is_3d(entity: ifcopenshell.entity_instance) -> bool:
    """
    Determines whether the geometry described by an entity
    is 3D (e.g. X, Y, Z) or not.

    This function is scoped only to entity types that are valid representations
    of IfcAlignment.

    @param entity: The entity_instance to be tested.
    """
    entity_type = entity.is_a().upper()

    if entity_type == "IFCCOMPOSITECURVE":
        return False
    elif (entity_type == "IFCGRADIENTCURVE") or (
            entity_type == "IFCSEGMENTEDREFERENCECURVE"
    ):
        return True
    elif entity_type == "IFCPOLYLINE":
        dim = entity.Dim
        if dim == 3:
            return True
        elif dim == 2:
            return False
        else:
            raise IndexError("Cartesian points require 2 or 3 dimensions.")
    elif entity_type == "IFCINDEXEDPOLYCURVE":
        points_type = entity.Points.is_a().upper()
        if points_type == "IFCCARTESIANPOINTLIST3D":
            return True
        if points_type == "IFCCARTESIANPOINTLIST2D":
            return False
        else:
            raise TypeError(
                f"Invalid type '{entity_type}' used for 'Points' attribute on entity #{entity.id()}."
            )
    else:
        raise TypeError(
            f"Invalid type '{entity_type}' used for alignment representation."
        )


def count_segments(logic, representation):
    """
    Used in ALA002 to return count of segments for business logic
    and geometry representation.
    """
    if logic is not None:
        expected_count = 0
        for seg in logic.segments:
            if seg.PredefinedType == "HELMERTCURVE":
                expected_count += 2
            else:
                expected_count += 1
    else:
        expected_count = None
    if representation is not None:
        rep_count = len(representation.segments)
    else:
        rep_count = None

    return expected_count, rep_count


def check_segment_geometry_type(exp_type: Dict, obs_type: str) -> bool:
    k, v = exp_type.keys(), exp_type.values()

    def fn_exactly():
        if obs_type in v:
            return True

    if "OneOf" in k:
        # there is more than one valid representation type for this logic segment PredefinedType
        if obs_type in exp_type["OneOf"]:
            return True
    elif "Exactly" in k:
        return fn_exactly()
    elif "multiple" in k:
        opts = exp_type["multiple"]
        for opt in opts:
            k, v = opt.keys(), opt.values()
            if "Exactly" in k:
                return fn_exactly()

    return False


def check_segment_geometry_types(expected_types: List[Dict], observed_types: List[str]) -> List[bool]:
    """
    Used in ALA003 to confirm agreement of segment geometry types between business logic
    and geometry representation.

    :param expected_types: The expected segment geometry types based on the segments in the alignment business logic
    :param observed_types: The observed segment geometry types based on the segment(s) in the shape representation
    """
    is_valid = list()

    # confirm that both lists have the same number of items
    if len(expected_types) != len(observed_types):
        return [False]
    else:
        for expected_type, observed_type in zip(expected_types, observed_types):
            is_valid.append(check_segment_geometry_type(expected_type, observed_type))

        return is_valid


def pretty_print_expected_geometry_type(spec: Dict, pretty: List[str]) -> List[str]:
    """
    Format the expected geometry types
    """

    pairs = [(k, v) for (k, v) in spec.items()]

    def fn_exactly():
        pretty.append(v)

    for k, v in pairs:
        match k:
            case "Exactly":
                fn_exactly()
            case "OneOf":
                opts = spec[k]
                pretty.append(" or ".join(opts))
            case "multiple":
                opts = spec[k]
                for o in opts:
                    k, v = o.keys(), o.values()
                    if k == "Exactly":
                        fn_exactly()
            case _:
                pass

    return pretty


def pretty_print_expected_geometry_types(exp: List[Dict]) -> str:
    """
    Format the expected list of geometry types
    """
    pretty = list()

    for d in exp:
        pretty = pretty_print_expected_geometry_type(spec=d, pretty=pretty)

    return ", ".join(pretty)


def ala003_activation_inst(inst, context) -> Union[ifcopenshell.entity_instance | None]:
    """
    Used in ALA003 as reverse traversal of graph to locate the correct business logic entity
    """
    for candidate in context._stack[2]["instances"]:
        if candidate is None:
            return None
        else:
            for rep in candidate.Representations:
                for item in rep.Items:
                    if item.id() == inst[0][0].id():
                        return candidate.ShapeOfProduct[0]

@gherkin_ifc.step(
    'A representation by {ifc_rep_criteria} requires the {existence:absence_or_presence} of {entities} in the business logic')
def step_impl(context, inst, ifc_rep_criteria, existence, entities):
    for align_ent in context.instances:
        align = ifc43.entities.Alignment().from_entity(align_ent)
        match (ifc_rep_criteria, existence, entities):
            case ("IfcSegmentedReferenceCurve", "presence", "IfcAlignmentCant"):
                if align.segmented_reference_curve is not None:
                    if align.cant is None:
                        yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "presence", "IfcAlignmentVertical"):
                if align.gradient_curve is not None:
                    if align.vertical is None:
                        yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("3D IfcIndexedPolyCurve", "presence", "IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCINDEXEDPOLYCURVE") and (is_3d(item)):
                            if align.vertical is None:
                                yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("3D IfcPolyline", "presence", "IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCPOLYLINE") and (is_3d(item)):
                            if align.vertical is None:
                                yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcCompositeCurve as Axis", "absence", "IfcAlignmentVertical and IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCCOMPOSITECURVE") and (
                                shape_rep.RepresentationIdentifier == "Axis"):
                            if (align.vertical is not None) or (align.cant is not None):
                                yield ValidationOutcome(inst=inst, expected=None,
                                                        observed="', '".join(entities.split(" and ")),
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "absence", "IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if item.is_a().upper() == "IFCGRADIENTCURVE":
                            if align.cant is not None:
                                yield ValidationOutcome(inst=inst, expected=None,
                                                        observed=entities,
                                                        severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    'The representation must have the correct number of segments indicated by the layout')
def step_impl(context, inst):
    for rel in inst.Nests:
        ent = rel.RelatingObject
        if ent.is_a() == "IfcAlignment":
            align = ifc43.entities.Alignment().from_entity(ent)

            match inst.is_a():
                case "IfcAlignmentHorizontal":
                    expected_count, rep_count = count_segments(
                        logic=align.horizontal,
                        representation=align.composite_curve,
                    )
                case "IfcAlignmentVertical":
                    expected_count, rep_count = count_segments(
                        logic=align.vertical,
                        representation=align.gradient_curve,
                    )
                case "IfcAlignmentCant":
                    expected_count, rep_count = count_segments(
                        logic=align.cant,
                        representation=align.segmented_reference_curve,
                    )
                case _:
                    msg = f"Invalid type '{inst.is_a()}'. "
                    msg += "Should be 'IfcAlignmentHorizontal', 'IfcAlignmentVertical', or 'IfcAlignmentCant'."

                    raise NameError(msg)

            if expected_count != rep_count:
                # account for alignment that has business logic only
                # or contains representation only
                logic_only = (expected_count is not None) and (rep_count is None)
                rep_only = (expected_count is None) and (rep_count is not None)
                if not (logic_only or rep_only):
                    observed_msg = f"{expected_count} segments in business logic and "
                    observed_msg += f"{rep_count} segments in representation"
                    yield ValidationOutcome(inst=inst, expected="same count of segments",
                                            observed=observed_msg,
                                            severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step('Each segment must have the same geometry type as its corresponding {activation_phrase}')
def step_impl(context, inst, activation_phrase):
    if inst is not None:
        # flatten the tuple of tuples and turn in to a list so that gradient curve can be added if necessary
        instances = list(tuple(itertools.chain(*inst)))

        # retrieve activation instance entity from the attribute stack
        activation_ent = ala003_activation_inst(inst, context)
        if activation_ent is not None:

            if activation_ent.is_a().upper() == "IFCALIGNMENT":
                # ensure that all three representation types will be validated
                for i in instances:
                    if i.is_a().upper() in ["IFCSEGMENTEDREFERENCECURVE", "IFCGRADIENTCURVE"]:
                        instances.append(i.BaseCurve)
                # remove any duplicate entities
                instances = set(instances)

            for rep in instances:
                match activation_phrase:
                    case "segment in the applicable IfcAlignment layout":
                        align = ifc43.entities.Alignment().from_entity(activation_ent)
                        match rep.is_a().upper():
                            case "IFCCOMPOSITECURVE":
                                logic = align.horizontal
                                representation = ifc43.entities.CompositeCurve().from_entity(rep)
                            case "IFCGRADIENTCURVE":
                                logic = align.vertical
                                representation = ifc43.entities.GradientCurve().from_entity(rep)
                            case "IFCSEGMENTEDREFERENCECURVE":
                                logic = align.cant
                                representation = ifc43.entities.SegmentedReferenceCurve().from_entity(rep)
                            case _:
                                logic = None
                                representation = None

                    case "segment in the horizontal layout":
                        logic = ifc43.entities.AlignmentHorizontal().from_entity(activation_ent)
                        representation = ifc43.entities.CompositeCurve().from_entity(rep)

                    case "segment in the vertical layout":
                        logic = ifc43.entities.AlignmentVertical().from_entity(activation_ent)
                        representation = ifc43.entities.GradientCurve().from_entity(rep)

                    case "segment in the cant layout":
                        logic = ifc43.entities.AlignmentCant().from_entity(activation_ent)
                        representation = ifc43.entities.SegmentedReferenceCurve().from_entity(rep)

                    case "alignment segment":
                        logic = ifc43.entities.AlignmentSegment().from_entity(activation_ent)
                        representation = ifc43.entities.CurveSegment().from_entity(rep)

                    case _:
                        logic = None
                        representation = None

                if (logic is not None) & (representation is not None):
                    if activation_ent.is_a().upper() == "IFCALIGNMENTSEGMENT":
                        # validating a single segment
                        exp = logic.expected_segment_geometry_type
                        obs = representation.segment_type

                        valid = check_segment_geometry_type(exp, obs)
                        expected_msg = "".join(pretty_print_expected_geometry_type(exp, pretty=list()))
                        observed_msg = obs

                    else:
                        # validating a list of segments
                        exp = logic.expected_segment_geometry_types
                        obs = representation.segment_types

                        checks = check_segment_geometry_types(exp, obs)
                        expected_msg = pretty_print_expected_geometry_types(exp)
                        observed_msg = ", ".join(representation.segment_types)
                        if False in checks:
                            valid = False
                        else:
                            valid = True

                    if not valid:
                        yield ValidationOutcome(
                            inst=rep,
                            expected=expected_msg,
                            observed=observed_msg,
                            severity=OutcomeSeverity.ERROR,
                        )
