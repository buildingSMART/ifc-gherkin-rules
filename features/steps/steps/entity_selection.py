from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("An .{entity_opt_stmt}.")
@gherkin_ifc.step("An .{entity_opt_stmt}. ^{subtype_handling}^ [{additional_prose_matching}]")
def step_impl(context, entity_opt_stmt, subtype_handling=None, additional_prose_matching=None,):
    """
    Generic step, typically used as an initial or second Given statement to select entities.
    
    Examples:
        Given an .IfcAlignment.
        Given an .IfcRoot. ^with subtypes^
        Given an .entity instance.
        Given an .IfcAlignment. [with business logic and geometric representation]
        
    The last example returns everything in the model.
    """

    if entity_opt_stmt == "entity instance":
        original_instances = list(context.model)
    else:
        entity = entity_opt_stmt

        match subtype_handling:
            case "without subtypes":
                include_subtypes = False
            case "with subtypes":
                include_subtypes = True
            case _:
                include_subtypes = True

        original_instances = context.model.by_type(entity, include_subtypes) or []
        filtered_instances = []

        if (entity == 'IfcAlignment') and (additional_prose_matching is not None):
            from utils import ifc43x_alignment_validation as ifc43

            for align_inst in original_instances:
                align = ifc43.entities.Alignment().from_entity(align_inst)
                if (align.horizontal is not None) and (align.has_representation):
                    filtered_instances.append(align_inst)
                    print(align)

            applicable_instances = filtered_instances
        else:
            applicable_instances = original_instances


    if applicable_instances:
        context.applicable = getattr(context, 'applicable', True)
    else:
        context.applicable = False

    # yield instances
    for inst in applicable_instances:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
