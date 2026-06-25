import csv
import functools
import operator
import re
from typing import Tuple
import ifcopenshell
import os

from pathlib import Path

from validation_handling import full_stack_rule, gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity
from utils import misc
from utils import geometry

def apply_is_a(inst):
    if isinstance(inst, (list, tuple)):
        return [i.is_a() for i in inst]
    else:
        return inst.is_a()

@functools.cache
def read_csv_values(schema, csv_file):
    dirname = os.path.dirname(__file__)
    filename =  Path(dirname).parent.parent / "resources" / f"{schema}" /f"{csv_file}.csv"
    return [row[0] for row in csv.reader(open(filename))]

@gherkin_ifc.step("The {i:value_or_type} must be in '{csv_file}.csv'")
@gherkin_ifc.step("The {i:values_or_types} must be in '{csv_file}.csv'")
def step_impl(context, inst, i, csv_file):
    """
    This implementation supports basic reading from CSV resources that have a single field and no header.
    It validates a value against a single field, but does not support CSV resources with multiple fields per row.
    """
    if not inst:
        return []

    valid_values = read_csv_values(context.model.schema, csv_file)

    def is_valid_instance(instance):
        if isinstance(instance, ifcopenshell.entity_instance):
            return any(instance.is_a(valid_value) for valid_value in valid_values)
        else:
            return instance in valid_values

    if not is_valid_instance(inst):
        yield ValidationOutcome(inst=inst, expected=valid_values, observed=inst, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("At least '{num:d}' value must {constraint}")
@gherkin_ifc.step("At least '{num:d}' values must {constraint}")
def step_impl(context, inst, constraint, num):
    stack_tree = list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

    values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

    if stack_tree:
        num_valid = 0
        for i in range(len(stack_tree[0])):
            path = [l[i] for l in stack_tree]
            if path[0] in values:
                num_valid += 1
        if num_valid < num:
            yield ValidationOutcome(inst=inst, expected= constraint, observed = f"Not {constraint}", severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The values must be {unique_or_identical:unique_or_identical} at depth {depth_level:d}")
def step_impl(context, inst, unique_or_identical, depth_level=None):
    """
    NOTE: depth_level is not processed via this step implementation but it does affect instance selection
    within the @gherkin_ifc.step decorator.
    see validation_handling.py:299
    """
    if not inst:
        return

    if unique_or_identical == 'identical':
        if not all([inst[0] == i for i in inst]):
            yield ValidationOutcome(inst=inst, expected= unique_or_identical, observed = inst, severity=OutcomeSeverity.ERROR)

    if unique_or_identical == 'unique':
        seen = set()
        duplicates = [x for x in inst if x in seen or seen.add(x)]
        if duplicates:
            yield ValidationOutcome(inst=inst, expected= unique_or_identical, observed = inst, severity=OutcomeSeverity.ERROR)


def recursive_unpack_value(item):
    """Unpacks a tuple recursively, returning the first non-empty item
    For instance, (,'Body') will return 'Axis'
    and (((IfcEntityInstance.)),) will return IfcEntityInstance

    Note that it will only work for a single value. E.g. not values for statements like 
    "The values must be X"
    as ('Axis', 'Body') will return 'Axis' 
    """
    if isinstance(item, tuple):
        if len(item) == 0:
            return None
        elif len(item) == 1 or not item[0]:
            return recursive_unpack_value(item[1]) if len(item) > 1 else recursive_unpack_value(item[0])
        else:
            return item[0]
    return item


@gherkin_ifc.step("The {i:value_or_type} must be '{value}'")
def step_impl(context, inst, i, value):
    values = [v.lower() for v in misc.strip_split(value, strp='"', splt=' or ')]
    inst = recursive_unpack_value(inst)
    if isinstance(inst, ifcopenshell.entity_instance): # redundant due to the statement 'Its entity type must be X; see e.g. ALS007 & ALS008'. This also allows to check for inheritance
        inst = inst.is_a()  

    if inst.lower() not in values:
        yield ValidationOutcome(inst=inst, expected= value, observed = inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("All {i:values_or_types} must be '{value}.")
def step_impl(context, inst, i, value):
    number_of_unique_values = len(set(inst))
    if number_of_unique_values > 1: # if there are more than 1 values, the 'All' predicament is impossible to fulfill
        yield ValidationOutcome(inst=inst, expected= value, observed=f"{number_of_unique_values} unique values", severity=OutcomeSeverity.ERROR)
    else:
        inst = recursive_unpack_value(inst)
        if isinstance(inst, ifcopenshell.entity_instance):
            inst = misc.do_try(lambda: inst.is_a(), inst)
        if inst != value:
            yield ValidationOutcome(inst=inst, expected= value, observed = inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("the value '{varname1}' must be ^{op}^ the value '{varname2}'")
@full_stack_rule
def step_impl(context, inst, path, npath, varname1, op, varname2):
    """Compares the value in variable v1 to the value in variable v2

    Args:
        varname1 (_type_): Left-hand-side variable reference
        op (_type_): 'equal to' / 'not equal to' / 'greater than' / 'less than' / 'greater than or equal to' / 'less than or equal to'
        varname2 (_type_): Right-hand-side variable reference
    """

    binary_operators = {
        'equal to' : operator.eq,
        'not equal to' : operator.ne,
        'greater than' : operator.gt,
        'less than' : operator.lt,
        'greater than or equal to' : operator.ge,
        'less than or equal to' : operator.le,
    }
    
    steps = [l.get('step') for l in context._stack]
    var_lists = [re.findall(r"\[stored as '(\w+)'\]", s.name) if s else None for s in steps]
    varnames = [l[0] if l else None for l in var_lists]

    tree = misc.get_stack_tree(context)
    def get_value(varname):
        # look up layer in tree based on variable name matched to step text
        val = tree[varnames.index(varname) - 1]
        # while numeric path is not depleted, use indices to peek into the appropriate slot
        p = list(npath)
        while isinstance(val, (list, tuple)) and p:
            val = val[p.pop(0)]
        return val

    v1, v2 = map(get_value, (varname1, varname2))
    passed = binary_operators[op](v1, v2)
    yield ValidationOutcome(inst=inst, expected=v2, observed=v1, severity=OutcomeSeverity.PASSED if passed else OutcomeSeverity.ERROR)

@full_stack_rule
@gherkin_ifc.step('the profiles must have the same number of points and edges')
def step_impl(context, inst):
    def count_edges_in_segment(indexed_segment_inst):
        if indexed_segment_inst.is_a("IfcArcIndex"):
            return 1
        elif indexed_segment_inst.is_a("IfcLineIndex"):
            return len(indexed_segment_inst.wrappedValue) - 1
        else:
            return 0

    def handle_curves(curr_crv, next_crv):
        curr_crv_type = curr_crv.is_a().upper()
        next_crv_type = next_crv.is_a().upper()
        if curr_crv_type == next_crv_type:
            match curr_crv_type:
                case "IFCPOLYLINE":
                    # num_edges always == (num_points - 1)
                    # therefore just test number of points in profile definition curve
                    curr_crv_pt_count = len(curr_crv.Points)
                    next_crv_pt_count = len(next_crv.Points)
                    if curr_crv_pt_count != next_crv_pt_count:
                        expected_msg = f"{curr_crv_pt_count} points in profile definition curve"
                        observed_msg = f"{next_crv_pt_count} points in profile definition curve"
                        yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                severity=OutcomeSeverity.ERROR)

                case "IFCINDEXEDPOLYCURVE":
                    # check overall number of points
                    curr_crv_pt_count = len(geometry.get_points(curr_crv))
                    next_crv_pt_count = len(geometry.get_points(curr_crv))
                    if curr_crv_pt_count != next_crv_pt_count:
                        expected_msg = f"{curr_crv_pt_count} points in profile definition curve"
                        observed_msg = f"{next_crv_pt_count} points in profile definition curve"
                        yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                severity=OutcomeSeverity.ERROR)

                    # check overall number of segments
                    if curr_crv.Segments and next_crv.Segments:
                        curr_crv_seg_count = len(curr_crv.Segments)
                        next_crv_seg_count = len(next_crv.Segments)
                        if curr_crv_seg_count != next_crv_seg_count:
                            expected_msg = f"{curr_crv_seg_count} segments in profile definition curve"
                            observed_msg = f"{next_crv_seg_count} segments in profile definition curve"
                            yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                    severity=OutcomeSeverity.ERROR)

                    # iterate segments and confirm same number of points and edges in each
                    for seg_in_curr, seg_in_next in zip(curr_crv.Segments, next_crv.Segments):
                        # segment will be either IfcLineIndex or IfcArcIndex
                        # the two segment types don't necessarily have to be the same - e.g. could sweep between polyline of three points and an arc
                        curr_seg_pt_count = len(seg_in_curr.wrappedValue)
                        next_seg_pt_count = len(seg_in_next.wrappedValue)
                        if curr_seg_pt_count != next_seg_pt_count:
                            expected_msg = f"{curr_seg_pt_count} points in {seg_in_curr.is_a()}"
                            observed_msg = f"{next_seg_pt_count} points in {seg_in_next.is_a()}"
                            yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                    severity=OutcomeSeverity.ERROR)

                        curr_seg_edge_count = count_edges_in_segment(seg_in_curr)
                        next_seg_edge_count = count_edges_in_segment(seg_in_next)
                        if curr_seg_edge_count != next_seg_edge_count:
                            expected_msg = f"{curr_seg_edge_count} edges in {seg_in_curr.is_a()}"
                            observed_msg = f"{next_seg_edge_count} edges in {seg_in_next.is_a()}"
                            yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                    severity=OutcomeSeverity.ERROR)

                    else:
                        # IndexedPolyCurve is just a polyline if Segments are not provided
                        curr_polycrv_pt_count = len(curr_crv.Points.CoordList)
                        next_polycrv_pt_count = len(next_crv.Points.CoordList)
                        if curr_polycrv_pt_count != next_polycrv_pt_count:
                            expected_msg = f"{curr_polycrv_pt_count} points in profile definition curve"
                            observed_msg = f"{next_polycrv_pt_count} points in profile definition curve"
                            yield ValidationOutcome(inst=next_crv, expected=expected_msg, observed=observed_msg,
                                                    severity=OutcomeSeverity.ERROR)

                case _:
                    pass

        else:
            # NOTE: consider enforcing cross section curves to be of the same type.
            # this is not explicitly called for in the IfcSectionedSolidHorizontal docs,
            # so it is not implemented for SWE003.
            # There may be value in a future additional rule in the SWE functional part.
            # Ref: https://github.com/buildingSMART/ifc-gherkin-rules/pull/523
           pass


    for pair_of_profiles in inst:
        curr_profile, next_profile = pair_of_profiles
        if (curr_profile is not None) & (next_profile is not None):
            curr_profile, next_profile = misc.iflatten(curr_profile), misc.iflatten(next_profile)

            for cp, np in zip(curr_profile, next_profile):

                # NOTE: Currently this step implementation is only used in SWE003 which explicitly selects only IfcArbitraryClosedProfileDef.
                # To be potentially expanded in case of other scenarios.
                assert curr_profile.is_a('IfcArbitraryClosedProfileDef') and next_profile.is_a(
                    'IfcArbitraryClosedProfileDef')

                curr_curve, next_curve = cp.OuterCurve, np.OuterCurve
                yield from handle_curves(curr_curve, next_curve)

