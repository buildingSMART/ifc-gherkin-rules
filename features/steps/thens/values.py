import csv
import ifcopenshell
import os
from pyproj.database import query_crs_info

from pathlib import Path

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity
from utils import misc

def apply_is_a(inst):
    if isinstance(inst, (list, tuple)):
        return [i.is_a() for i in inst]
    else:
        return inst.is_a()

@gherkin_ifc.step("The {i:value_or_type} must be in '{csv_file}.csv'")
@gherkin_ifc.step("The {i:values_or_types} must be in '{csv_file}.csv'")
def step_impl(context, inst, i, csv_file):
    if not inst:
        return []

    dirname = os.path.dirname(__file__)
    filename =  Path(dirname).parent.parent / "resources" / f"{context.model.schema}" /f"{csv_file}.csv"
    valid_values = [row[0] for row in csv.reader(open(filename))]

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


@gherkin_ifc.step("The value must refer to a valid EPSG code")
@gherkin_ifc.step("The value refers to a valid EPSG code")
def step_impl(context, inst):
    valid_epsg_codes = {f"EPSG:{crs.code}" for crs in query_crs_info(auth_name="EPSG")}
    if inst not in valid_epsg_codes:
        yield ValidationOutcome(inst=inst, observed=inst, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASSED)
