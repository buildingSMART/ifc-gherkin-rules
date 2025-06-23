"""
Sample model comes from:

IFC 4X3_ADD2 Documentation - Example E.4.8 - reinforcing assembly
Ref: https://github.com/buildingSMART/IFC4.3.x-sample-models/blob/main/models/building-elements/reinforcing-assembly/reinforcing-assembly.ifc
"""
from enum import StrEnum, auto

import ifcopenshell
from ifcopenshell.api.pset import add_qto
from ifcopenshell.api.pset import edit_qto
from ifcopenshell.api.root import create_entity, remove_product
from ifcopenshell.api.type.assign_type import assign_type
from ifcopenshell.api.unit import add_si_unit

PASS_FILE_PREFIX = "pass-qty001-correct_quantities_on_"
FAIL_FILE_PREFIX = "fail-qty001-scenario0"


class QtoDefinitionType(StrEnum):
    OCCURRENCE = auto()
    TYPE = auto()


def get_qty_instance(file: ifcopenshell.file) -> ifcopenshell.entity_instance:
    """
    Always returns the most-recently created IfcElementQuantity instance.
    """
    return file.by_type("IfcElementQuantity")[-1]


def add_units_defs(file: ifcopenshell.file) -> None:
    print("[INFO] adding units definitions...")
    area = add_si_unit(file, unit_type="AREAUNIT")
    volume = add_si_unit(file, unit_type="VOLUMEUNIT")
    mass = add_si_unit(file, unit_type="MASSUNIT")

    model_unit_def = file.by_type("IfcUnitAssignment")[0]
    model_units = list(model_unit_def.Units)
    model_units.append(area)
    model_units.append(volume)
    model_units.append(mass)
    model_unit_def.Units = model_units


def add_quantity_info(file: ifcopenshell.file, product: ifcopenshell.entity_instance) -> None:
    print("[INFO] adding quantity information...")
    qto = add_qto(file, product=product, name="Qto_BeamBaseQuantities")
    edit_qto(file, qto=qto, properties={
        'Length': 5000.,
        'CrossSectionArea': 0.08,
        'GrossVolume': 0.40,
        'GrossWeight': 960.,
    })


def setup_occurrence_qtys(model):
    add_units_defs(model)
    add_quantity_info(file=model, product=model.by_type("IfcBeam")[0])


def setup_type_qtys(model):
    add_units_defs(model)
    add_quantity_info(file=model, product=model.by_type("IfcBeamType")[0])


def write_pass_file(file: ifcopenshell.file, qty_defined_on: QtoDefinitionType) -> None:
    qty_inst = get_qty_instance(file)
    qty_inst.MethodOfMeasurement = "BaseQuantities"
    print("[INFO] writing passing model to file...")
    pass_file = PASS_FILE_PREFIX + f"{qty_defined_on.value.lower()}.ifc"
    file.wrapped_data.header.file_name.name = pass_file
    file.write(pass_file)


def write_fail_file(file: ifcopenshell.file, index: int, description: str, qto_def_type: QtoDefinitionType) -> None:
    out_file = f"{FAIL_FILE_PREFIX}{index}-{description}_on_{qto_def_type.value.lower()}.ifc"
    print(f"[INFO] writing {out_file} to file...")
    file.wrapped_data.header.file_name.name = out_file
    file.write(out_file)


def generate_passing(model: ifcopenshell.file, qty_defined_on: QtoDefinitionType):
    """
    Generate two sets of unit test files:
    1. Qto defined on IfcBeam occurrence
    2. Qto defined on IfcBeamType
    """

    match qty_defined_on:
        case QtoDefinitionType.OCCURRENCE:
            setup_occurrence_qtys(model)
            write_pass_file(model, qty_defined_on)

        case QtoDefinitionType.TYPE:
            # IfcBeamType is already in the model and associated to the beam
            setup_type_qtys(model)
            write_pass_file(model, qty_defined_on)


def generate_failing(model: ifcopenshell.file, qty_defined_on: QtoDefinitionType, index: int):
    """
    Generate two sets of unit test files:
    1. Qto defined on IfcBeam occurrence
    2. Qto defined on IfcBeamType
    """

    # use 1-based naming to match scenario numbers
    index += 1

    match qty_defined_on:
        case QtoDefinitionType.OCCURRENCE:
            setup_occurrence_qtys(model)
            qty_inst = get_qty_instance(model)
            if index != 5:
                qty_inst.MethodOfMeasurement = "BaseQuantities"

        case QtoDefinitionType.TYPE:
            if index != 3:
                setup_type_qtys(model)
                qty_inst = get_qty_instance(model)
                if index != 5:
                    qty_inst.MethodOfMeasurement = "BaseQuantities"

    match index:

        case 1:
            qty_inst.Name = "Qto_DefinitelyNotStandard"
            write_fail_file(model, index, description="invalid_element_quantity_name", qto_def_type=qty_defined_on)

        case 2:
            qty_to_edit = qty_inst.Quantities[2]
            qty_to_edit.Name = "still Volume but no longer a standard name"
            write_fail_file(model, index, description="invalid_physical_quantity_name", qto_def_type=qty_defined_on)

        case 3:
            pile = create_entity(model, "IfcPile")
            spatial_rel = model.by_type("IfcRelContainedInSpatialStructure")[0]
            cur_elements = list(spatial_rel.RelatedElements)
            cur_elements.append(pile)
            spatial_rel.RelatedElements = cur_elements
            if qty_defined_on == QtoDefinitionType.OCCURRENCE:
                qto_def_rel_to_edit = model.by_type("IfcBeam")[0].IsDefinedBy[0]
                qto_def_rel_to_edit.RelatedObjects = (pile,)
            elif qty_defined_on == QtoDefinitionType.TYPE:
                inst = model.by_type("IfcBeamType")[0]
                inst.HasPropertySets = None
                pile_type = create_entity(model, "IfcPileType")
                pile_type.Name = "PileType"
                add_units_defs(model)
                add_quantity_info(model, product=pile_type)
                qty_inst = get_qty_instance(model)
                qty_inst.MethodOfMeasurement = "BaseQuantities"

            write_fail_file(model, index, description="invalid_related_entity_type", qto_def_type=qty_defined_on)

        case 4:
            valid_qty_to_remove = model.by_type("IfcQuantityLength")[0]
            model.remove(valid_qty_to_remove)

            invalid_qty_to_add = model.create_entity(
                type="IfcQuantityCount",
                Name="Length",
                CountValue=1000,
            )
            qty_props = list(qty_inst.Quantities)[0:]
            qty_props.append(invalid_qty_to_add)
            qty_inst.Quantities = qty_props
            write_fail_file(model, index, description="invalid_quantity_prop_entity_type", qto_def_type=qty_defined_on)

        case 5:
            qty_inst.MethodOfMeasurement = "Calculated by an intern on an HP 42 calculator"
            write_fail_file(model, index, description="incorrect_method_of_measurement", qto_def_type=qty_defined_on)


if __name__ == "__main__":
    print("[INFO] opening sample model...")

    # generate files for two scenarios: Qto defined on type and Qto defined on occurrence
    for defined_on in QtoDefinitionType:
        generate_passing(model=ifcopenshell.open("reinforcing-assembly.txt"), qty_defined_on=defined_on)
        for i in range(5):
            generate_failing(model=ifcopenshell.open("reinforcing-assembly.txt"), qty_defined_on=defined_on, index=i)

    print("[INFO] Done.")
