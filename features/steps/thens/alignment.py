import operator

from utils import ifc43x_alignment_validation

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step('A representation by {ifc_rep_entity} requires an {ifc_layout_entity} in the business logic')
def step_impl(context, inst, ifc_rep_entity, ifc_layout_entity):
    if ifc_layout_entity in ["IfcAlignmentCant", "IfcAlignmentVertical"]:
        for align_ent in context.instances:
            align = ifc43x_alignment_validation.entities.Alignment().from_entity(align_ent)
            if align.segmented_reference_curve is not None:
                if align.cant is None:
                    yield ValidationOutcome(inst=inst, expected="IfcAlignmentCant", observed=None,
                                            severity=OutcomeSeverity.ERROR)
