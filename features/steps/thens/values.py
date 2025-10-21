import csv
import operator
import re
import ifcopenshell
import os
from pyproj.database import query_crs_info
from pyproj import CRS

from pathlib import Path

from validation_handling import full_stack_rule, gherkin_ifc

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
