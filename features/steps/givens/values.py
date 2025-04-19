import itertools

from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Its values")
@gherkin_ifc.step("Its values excluding {excluding}")
def step_impl(context, inst, excluding=None):
    yield ValidationOutcome(instance_id=inst.get_info(recursive=True, include_identifier=False, ignore=excluding),
                            severity=OutcomeSeverity.PASSED)


@gherkin_ifc.step("The values grouped pairwise at depth {ignored:d}")
def step_impl(context, inst, ignored=0):
    inst = itertools.pairwise(inst)
    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("The determinant of the placement matrix")
def step_impl(context, inst):
    import numpy as np
    import ifcopenshell.ifcopenshell_wrapper

    if inst.wrapped_data.file_pointer() == 0:
        # In some case we're processing operations on attributes that are 'derived in subtype', for
        # example the Operator on an IfcMirroredProfileDef. Derived attribute values are generated
        # on the fly and are not part of a file. Due to a limitation on the mapping expecting a file
        # object, such instances can also not be mapped. Therefore in such case we create a temporary
        # file to add the instance to.
        f = ifcopenshell.file(schema=context.model.schema_identifier)
        inst = f.add(inst)

    shp = ifcopenshell.ifcopenshell_wrapper.map_shape(ifcopenshell.geom.settings(), inst.wrapped_data)
    d = np.linalg.det(np.array(shp.components))
    yield ValidationOutcome(instance_id=d, severity=OutcomeSeverity.PASSED)
