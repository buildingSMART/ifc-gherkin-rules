from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("An .{entity_opt_stmt}.")
@gherkin_ifc.step("An .{entity_opt_stmt}. ^{subtype_handling}^")
def step_impl(context, entity_opt_stmt, subtype_handling=None):
    """
    Generic step, typically used as an initial or second Given statement to select entities.
    
    Examples:
        Given an .IfcAlignment.
        Given an .IfcRoot. with subtypes
        Given an .entity instance.

    The last example returns everything in the model.
    """

    if entity_opt_stmt == "entity instance":
        instances = context.model
    else:
        entity = entity_opt_stmt

        match subtype_handling:
            case "without subtypes":
                include_subtypes = False
            case "with subtypes":
                include_subtypes = True
            case _:
                include_subtypes = True

        instances = context.model.by_type(entity, include_subtypes) or []

    if instances:
        context.applicable = getattr(context, 'applicable', True)
    else:
        context.applicable = False

    # yield instances
    for inst in instances:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
