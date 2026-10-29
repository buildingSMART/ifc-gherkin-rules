import ast
import operator

from utils import misc
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

from utils.ifc import check_entity_type

@gherkin_ifc.step(".{attribute}. ^{comparison_operator:equal_or_not_equal}^ ^null^")
def step_impl_null(context, inst, comparison_operator, attribute):
    """
    .Attribute. ^is^ ^null^      -> the attribute is not provided: '$' in the exchange structure (ISO 10303-21, 12.2.2),
                                    None in IfcOpenShell
    .Attribute. ^is not^ ^null^  -> the attribute has a value

    Unlike 'empty' below, an empty string '' and falsy values such as 0., 0 or .F. are values, not null.
    Registered before the generic comparison so that ^null^ is not parsed as a literal {value}.
    """
    observed_v = getattr(inst, attribute, None)
    is_null = observed_v is None
    expect_null = comparison_operator in {"is", "="}
    if is_null == expect_null:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst,
                                expected='null' if expect_null else 'not null',
                                observed='null' if is_null else observed_v,
                                severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("[{attribute}] ^{comparison_operator:equal_or_not_equal}^ {value}")
@gherkin_ifc.step("[{attribute}] ^{comparison_operator:equal_or_not_equal}^ {value} ^{subtype_handling:include_or_exclude_subtypes}^")
@gherkin_ifc.step(".{attribute}. ^{comparison_operator:equal_or_not_equal}^ {value}")
@gherkin_ifc.step(".{attribute}. ^{comparison_operator:equal_or_not_equal}^ {value} ^{subtype_handling:include_or_exclude_subtypes}^")
def step_impl(context, inst, comparison_operator, attribute, value, subtype_handling="excluding subtypes"):
    """
    Note that the following statements are acceptable:
    - Attribute = empty
    - Attribute = not empty
    - Attribute is empty

    However, please avoid using:
    - Attribute is not empty
    """
    start_value = value
    pred = operator.eq

    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne
    else:
        try:
            value = ast.literal_eval(value)
        except ValueError:
            # Check for multiple values, for example `PredefinedType = 'POSITION' or 'STATION'`.
            value = set(map(ast.literal_eval, map(str.strip, value.split(' or '))))
            pred = operator.contains

    if comparison_operator in {"is not", "!="}: # avoid using != together with (not)empty stmt
        pred = misc.negate(pred)

    observed_v = ()
    if attribute.lower() in ['its type', 'its entity type']: # it's entity type is a special case using ifcopenshell 'is_a()' func
        observed_v = misc.do_try(lambda : inst.is_a(), ())
        if isinstance(value, set):
            values = [check_entity_type(inst, v, subtype_handling) for v in value]
        else:
            values = check_entity_type(inst, value, subtype_handling)
        entity_is_applicable = pred(values, True)
    else:
        observed_v = getattr(inst, attribute, ()) or ()
        entity_is_applicable = pred(value, observed_v)

    if entity_is_applicable:
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASSED)
    else: # in case of a Then statement
        yield ValidationOutcome(inst=inst,
                                expected = f"{'not ' if comparison_operator in {'is not', '!='} or 'not' in start_value else ''}{'empty' if value == () else value}",
                                observed = 'empty' if observed_v == () else observed_v, severity = OutcomeSeverity.ERROR)
