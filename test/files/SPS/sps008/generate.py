from enum import StrEnum, auto
from pathlib import Path

import ifcopenshell

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit


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
    file.write(filename)


def create_model(schema_identifier:str='IFC2X3') -> ifcopenshell.file:
    """
    Creates a new ifc file with basic units, geometric context, etc
    """
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Validation Unit Test")
    ifcopenshell.api.unit.assign_unit(f)
    model_context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_context)

    return f

def create_tests1() -> None:
    model = create_model(schema_identifier="IFC2X3")
    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
    project = model.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[storey])

    save_model(file=model, pass_fail=PassFailEnum.PASS, entity_type="IfcBuildingStorey")

    # give the storey a basic representation - so that it fails
    ifcopenshell.api.geometry.edit_object_placement(model, product=storey)
    rect = model.create_entity(type="IfcRectangleProfileDef", ProfileType="AREA", XDim=4500, YDim=4500)
    direction = model.create_entity(type="IfcDirection", DirectionRatios=[0., 0., 1.])
    extrusion = model.create_entity(type="IfcExtrudedAreaSolid", SweptArea=rect, ExtrudedDirection=direction, Depth=4500)
    model_context = ifcopenshell.util.representation.get_context(model, "Model", "Body", "MODEL_VIEW")
    rep = model.create_entity(type="IfcShapeRepresentation", ContextOfItems=model_context, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[extrusion])
    ifcopenshell.api.geometry.assign_representation(model, product=storey, representation=rep)

    save_model(file=model, pass_fail=PassFailEnum.FAIL, scenario=1, entity_type="IfcBuildingStorey")

def create_tests2() -> None:
    f = ifcopenshell.file(schema="IFC4")
    inst_type = "IfcSite"
    ifcopenshell.api.root.create_entity(f, inst_type)
    save_model(file=f, pass_fail=PassFailEnum.PASS, entity_type=inst_type)

    # give it a representation
    save_model(file=f, pass_fail=PassFailEnum.FAIL, scenario=2, entity_type=inst_type)


if __name__ == "__main__":
    clean_directory()
    create_tests1()
    # create_tests2()
