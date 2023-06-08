import ifcopenshell
import json
import operator
import pyparsing


def do_try(fn, default=None):
    try:
        return fn()
    except:
        return default

# @note dataclasses.asdict used deepcopy() which doesn't work on entity instance
asdict = lambda dc: dict(instance_converter(dc.__dict__.items()), message=str(dc), **dict(get_inst_attributes(dc)))


def get_inst_attributes(dc):
    if hasattr(dc, 'inst'):
        yield 'inst_guid', getattr(dc.inst, 'GlobalId', None)
        yield 'inst_type', dc.inst.is_a()
        yield 'inst_id', dc.inst.id()


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


def handle_errors(context, errors):
    error_formatter = (lambda dc: json.dumps(asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format(
        "\n".join(map(error_formatter, errors))
    )


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


def strip_split(stmt, strp=' ', splt=','):
    return list(
        map(lambda s: s.strip(strp), stmt.lower().split(splt))
    )


def unpack_sequence_of_entities(instances):
    # in case of [[inst1, inst2], [inst3, inst4]]
    return [do_try(lambda: unpack_tuple(inst), None) for inst in instances]


def unpack_tuple(tup):
    for item in tup:
        if isinstance(item, tuple):
            unpack_tuple(item)
        else:
            return item
