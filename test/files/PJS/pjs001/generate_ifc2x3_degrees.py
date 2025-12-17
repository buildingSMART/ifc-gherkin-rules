import math

import ifcopenshell

import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.api.owner
import ifcopenshell.api.owner.settings


def main():
    # create new file with IFC 2X3 schema
    model = ifcopenshell.api.project.create_file(version="IFC2X3")

    application = ifcopenshell.api.owner.add_application(model)
    person = ifcopenshell.api.owner.add_person(model, identification="FWHAL", family_name="Whalbanger",
                                               given_name="Frank")
    org = ifcopenshell.api.owner.add_organisation(model, identification="MOE", name="tavern")
    user = ifcopenshell.api.owner.add_person_and_organisation(model, person=person, organisation=org)
    ifcopenshell.api.owner.settings.get_user = lambda x: user
    ifcopenshell.api.owner.settings.get_application = lambda x: application
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="PJS001 IFC2X3 Degrees")

    # create conversion-based planar angle unit for degrees
    degree = model.create_entity(
        type="IfcConversionBasedUnit",
        Name="degree",
        ConversionFactor=model.create_entity(
            type="IfcMeasureWithUnit",
            ValueComponent=model.create_entity("IfcPlaneAngleMeasure", math.pi / 180),
            UnitComponent=model.create_entity(
                type="IfcSIUnit",
                UnitType="PLANEANGLEUNIT",
                Name="RADIAN"
            ),
        ),
        UnitType="PLANEANGLEUNIT",
        Dimensions=model.create_entity("IfcDimensionalExponents", 0, 0, 0, 0, 0, 0, 0)
    )

    # assign project units
    ifcopenshell.api.unit.assign_unit(model, units=[degree])

    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(model, context_type="Model", context_identifier="Body",
                                                target_view="MODEL_VIEW", parent=context)

    # adjust header
    header = model.header
    out_file = "pass-pjs001-degree_ifc2x3.ifc"
    header.file_name.name = out_file
    header.file_name.originating_system = "IfcOpenShell Contributors - IfcOpenShell - 0.8.4"

    # save
    print("Writing to " + out_file)
    model.write(out_file)


if __name__ == "__main__":
    main()
