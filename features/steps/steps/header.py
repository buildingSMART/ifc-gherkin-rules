"""Then steps for the Model View Definition (MVD) declared in FILE_DESCRIPTION."""
from validation_handling import gherkin_ifc
from utils import ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Exactly one base Model View Definition must be declared")
def step_impl(context, inst):
    base_views = ifc.get_base_view_definitions(context.model)
    if len(base_views) != 1:
        yield ValidationOutcome(
            inst=inst,
            expected="one base Model View Definition",
            observed=", ".join(base_views) or "none",
            severity=OutcomeSeverity.ERROR,
        )


@gherkin_ifc.step("Add-on views must only be declared together with '{mvd}'")
def step_impl(context, inst, mvd):
    views = ifc.get_view_definitions(context.model)
    add_on_views = [view for view in views if ifc.is_add_on_view(view)]
    if add_on_views and mvd not in views:
        yield ValidationOutcome(
            inst=inst,
            expected=f"{', '.join(add_on_views)} only together with {mvd}",
            observed=", ".join(views),
            severity=OutcomeSeverity.ERROR,
        )


@gherkin_ifc.step("Add-on views must not be declared")
def step_impl(context, inst):
    add_on_views = [view for view in ifc.get_view_definitions(context.model) if ifc.is_add_on_view(view)]
    if add_on_views:
        yield ValidationOutcome(
            inst=inst,
            expected="no add-on views",
            observed=", ".join(add_on_views),
            severity=OutcomeSeverity.ERROR,
        )
