from datetime import datetime, timezone
from enum import StrEnum, auto
from pathlib import Path

import ifcopenshell
import ifcopenshell.guid

import ifcopenshell.api.aggregate
import ifcopenshell.api.attribute
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.owner
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.representation


class PassFailEnum(StrEnum):
    PASS = auto()
    FAIL = auto()


def clean_directory():
    """
    Delete all .ifc files in the current directory using pathlib.
    """
    current_dir = Path(__file__).resolve().parent
    ifc_files = list(current_dir.glob('*.ifc'))

    if ifc_files:
        print(f"[INFO] Deleting {len(ifc_files)} IFC files from {current_dir.as_posix()}...")
        for file_path in ifc_files:
            file_path.unlink()
    else:
        print(f"[INFO] No IFC files found in {current_dir.as_posix()}.")


def save_model(file: ifcopenshell.file, pass_fail: PassFailEnum, entity_type: str, scenario: int = None) -> None:
    prefix = pass_fail.value.lower()
    match prefix:
        case "fail":
            suffix = "with_representation.ifc"
        case "pass":
            suffix = "no_representation.ifc"
        case _:
            suffix = "na"

    base = f"{prefix}-sps008"
    if scenario:
        base += f"-scenario{str(scenario).zfill(2)}"
    filename = f"{base}-{entity_type.lower()}_{suffix}"
    print(f"[INFO] Writing {filename} to disk...")
    file.wrapped_data.header.file_name.name = filename
    file.wrapped_data.header.file_name.preprocessor_version = "IfcOpenShell 0.8.3"
    file.wrapped_data.header.file_name.originating_system = "IfcOpenShell contributors - IfcOpenShell - 0.8.3"
    current_time = datetime.now(timezone.utc).astimezone()
    iso_time = current_time.isoformat(timespec="seconds")
    file.wrapped_data.header.file_name.time_stamp = iso_time
    match file.schema_identifier:
        case "IFC2X3":
            mvd = "ViewDefinition [CoordinationView_V2.0]"
        case "IFC4":
            mvd = "ViewDefinition [ReferenceView_V1.2]"
        case "IFC4X3_ADD2":
            mvd = "ViewDefinition [ReferenceView]"

    file.wrapped_data.header.file_description.description = (mvd, )

    file.write(filename)


def create_model(schema_identifier: str = 'IFC2X3') -> ifcopenshell.file:
    """
    Creates a new ifc file with basic units, geometric context, etc.
    """
    f = ifcopenshell.api.project.create_file(version=schema_identifier)

    person = ifcopenshell.api.owner.add_person(f, family_name="Smith", given_name="John", identification="john.smith")
    org = ifcopenshell.api.owner.add_organisation(f, identification="ACME", name="ACME Corp")
    application = ifcopenshell.api.owner.add_application(f, application_developer=org)
    user = ifcopenshell.api.owner.add_person_and_organisation(f, person=person, organisation=org)

    ifcopenshell.api.owner.settings.get_user = lambda x: user
    ifcopenshell.api.owner.settings.get_application = lambda x: application

    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Validation Unit Test")
    ifcopenshell.api.unit.assign_unit(f)
    model_context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW",
                                         parent=model_context)

    return f


def add_representation(file: ifcopenshell.file, product: ifcopenshell.entity_instance) -> None:
    rect = file.create_entity(type="IfcRectangleProfileDef", ProfileType="AREA", XDim=4500, YDim=4500)
    direction = file.create_entity(type="IfcDirection", DirectionRatios=[0., 0., 1.])
    extrusion = file.create_entity(type="IfcExtrudedAreaSolid", SweptArea=rect, ExtrudedDirection=direction, Depth=4500)
    model_context = ifcopenshell.util.representation.get_context(file, "Model", "Body", "MODEL_VIEW")
    rep = file.create_entity(type="IfcShapeRepresentation", ContextOfItems=model_context,
                             RepresentationIdentifier="Body",
                             RepresentationType="SweptSolid", Items=[extrusion])
    ifcopenshell.api.geometry.assign_representation(file,product=product, representation=rep)

    if file.schema_identifier == "IFC2X3":
        origin2 = file.create_entity(type="IfcCartesianPoint", Coordinates=(0., 0.))
        ref_dir2 = file.create_entity(type="IfcDirection", DirectionRatios=(1., 0.))
        placement2 = file.create_entity(type="IfcAxis2Placement2D", Location=origin2, RefDirection=ref_dir2)

        origin3 = file.create_entity(type="IfcCartesianPoint", Coordinates=(0., 0., 0.))
        placement3 = file.create_entity(type="IfcAxis2Placement3D", Location=origin3)
        rect.Position = placement2
        extrusion.Position = placement3


def create_tests2x3() -> None:
    model = create_model(schema_identifier="IFC2X3")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")
    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
    project = model.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[building])
    ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])

    save_model(file=model, pass_fail=PassFailEnum.PASS, entity_type="IfcBuildingStorey")

    # add default placement
    ifcopenshell.api.geometry.edit_object_placement(model, product=storey)
    # give the storey a basic representation - so that it fails
    add_representation(file=model, product=storey)
    save_model(file=model, pass_fail=PassFailEnum.FAIL, scenario=1, entity_type="IfcBuildingStorey")


def create_tests4() -> None:
    model = create_model(schema_identifier="IFC4")
    inst_type = "IfcSite"
    site = ifcopenshell.api.root.create_entity(model, ifc_class=inst_type)
    ifcopenshell.api.aggregate.assign_object(model, relating_object=model.by_type("IfcProject")[0], products=[site])
    save_model(file=model, pass_fail=PassFailEnum.PASS, entity_type=inst_type)

    # add default placement
    ifcopenshell.api.geometry.edit_object_placement(model, product=site)
    # give the storey a basic representation - so that it fails
    add_representation(file=model, product=site)
    save_model(file=model, pass_fail=PassFailEnum.FAIL, scenario=2, entity_type=inst_type)

def create_tests4x3() -> None:
    facility_types = ["IfcBridge", "IfcMarineFacility", "IfcRailway", "IfcRoad"]
    for facility_type in facility_types:
        model = create_model(schema_identifier="IFC4X3_ADD2")
        facility = ifcopenshell.api.root.create_entity(model, facility_type)
        ifcopenshell.api.aggregate.assign_object(model, relating_object=model.by_type("IfcProject")[0], products=[facility])
        save_model(file=model, pass_fail=PassFailEnum.PASS, entity_type=facility_type)

        # add default placement
        ifcopenshell.api.geometry.edit_object_placement(model, product=facility)
        # give the storey a basic representation - so that it fails
        add_representation(file=model, product=facility)
        save_model(file=model, pass_fail=PassFailEnum.FAIL, scenario=3, entity_type=facility_type)

if __name__ == "__main__":
    clean_directory()
    create_tests2x3()
    create_tests4()
    create_tests4x3()
