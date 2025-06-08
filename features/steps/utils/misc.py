import ifcopenshell
import operator
import pyparsing


def reverse_operands(fn):
    """
    Given a function `fn` that operates on two arguments, the returned function will
    swap the order of these arguments before applying `fn`.

    For instance, with the function operator.contains which expects argument in a specific order. 
        contains_reversed = reverse_operands(operator.contains)
        contains_reversed(3, [1, 2, 3, 4])  # True
        operator.contains([1,2,3,4], 3) # True

        However
        operator.contains(3, [1,2,3,4]) # Raises a TypeError
    """
    def inner(*args):
        return fn(*reversed(args))
    return inner

def negate(fn):
    """
    Returns a function that negates the result of the given predicate function.

    Example:
        >>> import operator
        >>> not_equal = negate(operator.eq)
        >>> not_equal(1, 2)
        True
        >>> not_equal(1, 1)
        False
    """
    def inner(*args):
        return not fn(*args)
    return inner


def recursive_flatten(lst):
    flattened_list = []
    for item in lst:
        if isinstance(item, (tuple, list)):
            flattened_list.extend(recursive_flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list


def iflatten(any):
    if isinstance(any, (tuple, list)):
        for v in any:
            yield from iflatten(v)
    else:
        yield any


def do_try(fn, default=None):
    try:
        return fn()
    except:
        return default

# @note dataclasses.asdict used deepcopy() which doesn't work on entity instance
asdict = lambda dc: dict(instance_converter(dc.__dict__.items()), message=str(dc), **dict(get_inst_attributes(dc)))


def get_inst_attributes(dc):
    if hasattr(dc, 'inst'):
        if isinstance(dc.inst, ifcopenshell.entity_instance):
            yield 'inst_guid', getattr(dc.inst, 'GlobalId', None)
            yield 'inst_type', dc.inst.is_a()
            yield 'inst_id', dc.inst.id()
        else:
            # apparently mostly for the rule passed logs...
            # @todo fix this
            yield 'inst_guid', None
            yield 'inst_type', type(dc.inst).__name__


def fmt(x):
    if isinstance(x, frozenset) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -- {}".format(*x)
    elif isinstance(x, tuple) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -> {}".format(*x)
    else:
        v = str(x)
        if len(v) > 35:
            return "...".join((v[:25], v[-7:]))
        return v

def include_subtypes(stmt):
    # todo replace by pyparsing?
    stmt = strip_split(stmt, strp='[]', splt=' ')
    excluding_statements = {'without', 'not', 'excluding', 'no'}
    return not set(stmt).intersection(set(excluding_statements))


def instance_converter(kv_pairs):
    def c(v):
        if isinstance(v, ifcopenshell.entity_instance):
            return str(v)
        else:
            return v
    return {k: c(v) for k, v in kv_pairs}


def is_a(s):
    return lambda inst: inst.is_a(s)

def make_aggregrated_dict(table, ent_tbl_header, relationship_tbl_header):
    aggregated_table = {}
    for d in table:
        applicable_entity = d[ent_tbl_header]
        tbl_relationship_object = d[relationship_tbl_header]
        if applicable_entity in aggregated_table:
            aggregated_table[applicable_entity].append(tbl_relationship_object)
        else:
            aggregated_table[applicable_entity] = [tbl_relationship_object]
    return aggregated_table


def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)


def rtrn_pyparse_obj(i):
    if isinstance(i, (pyparsing.core.LineEnd, pyparsing.core.NotAny)):
        return i
    elif isinstance(i, str):
        return pyparsing.CaselessKeyword(i)


def stmt_to_op(statement):
    statement = statement.replace('is', '').strip()
    statement = statement.lower()
    stmts_to_op = {
        '': operator.eq,  # a == b
        "equal to": operator.eq,  # a == b
        "exactly": operator.eq,  # a == b
        "not": operator.ne,  # a != b
        "at least": operator.ge,  # a >= b
        "more than": operator.gt,  # a > b
        "at most": operator.le,  # a <= b
        "less than": operator.lt  # a < b
    }
    assert statement in stmts_to_op
    return stmts_to_op[statement]


def strip_split(stmt, strp=' ', splt=',', lower=True):
    """
    Splits a string by a delimiter, strips unwanted characters from each part, 
    and optionally converts it to lowercase.

    Returns a tuple for efficient iteration and compatibility 
    with methods like `startswith()`, which accept tuples for multi-value checks.
    """
    return tuple(s.strip(strp) for s in (stmt.lower() if lower else stmt).split(splt))


def unpack_tuple(tup):
    for item in tup:
        if isinstance(item, tuple):
            unpack_tuple(item)
        else:
            return item

def define_feature_version(context):
    version = next((tag for tag in context.tags if "version" in tag))  # e.g. version1
    return int(version.replace("version", ""))


def recursive_unpack_value(item):
    """Unpacks a tuple recursively, returning the first non-empty item
    For instance, (,'Body') will return 'Axis'
    and (((IfcEntityInstance.)),) will return IfcEntityInstance

    Note that it will only work for a single value. E.g. not values for statements like 
    "The values must be X"
    as ('Axis', 'Body') will return 'Axis' 
    """
    if isinstance(item, (tuple, list)):
        if len(item) == 0:
            return None
        elif len(item) == 1 or not item[0]:
            return recursive_unpack_value(item[1]) if len(item) > 1 else recursive_unpack_value(item[0])
        else:
            return item[0]
    return item

def get_stack_tree(context):
    """Returns the stack tree of the current context. To be used for 'attribute stacking', e.g. in GEM004"""
    return list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
