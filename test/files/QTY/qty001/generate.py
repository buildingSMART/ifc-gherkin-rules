"""
Sample model comes from:

IFC 4X3_ADD2 Documentation - Example E.4.8 - reinforcing assembly
Ref: https://github.com/buildingSMART/IFC4.3.x-sample-models/blob/main/models/building-elements/reinforcing-assembly/reinforcing-assembly.ifc
"""
from enum import StrEnum, auto
from typing import Dict


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


def write_fail_file(file: ifcopenshell.file, index: int, description: str, qto_def_type: QtoDefinitionType) -> None:
    out_file = f"{FAIL_FILE_PREFIX}{index}-{description}_on_{qto_def_type.value.lower()}.ifc"
    print(f"[INFO] writing {out_file} to file...")
    file.write(out_file)


def generate(model: ifcopenshell.file, qty_defined_on: QtoDefinitionType):
    """
    Generate two sets of unit test files:
    1. Qto defined on IfcBeam occurrence
    2. Qto defined on IfcBeamType
    """
    add_units_defs(model)

    match qty_defined_on:
        case QtoDefinitionType.OCCURRENCE:
            add_quantity_info(file=model, product=model.by_type("IfcBeam")[0])
        case QtoDefinitionType.TYPE:
            # the previous run added the occurrence-driven qto def
            # delete it first
            beam_type = create_entity(model, "IfcBeamType")
            beam = model.by_type("IfcBeam")[0]

            assign_type(
                file=model, related_objects=[beam], relating_type=beam_type,
                should_map_representations=True)

            add_quantity_info(file=model, product=beam_type)

    qty_inst = get_qty_instance(model)
    qty_inst.MethodOfMeasurement = "BaseQuantities"
    print("[INFO] writing passing model to file...")
    pass_file = PASS_FILE_PREFIX + f"{qty_defined_on.value.lower()}.ifc"
    model.write(pass_file)

    idx = 1
    model = ifcopenshell.open(pass_file)
    qty_inst = get_qty_instance(model)
    qty_inst.Name = "Qto_DefinitelyNotStandard"
    write_fail_file(model, idx, description="invalid_element_quantity_name", qto_def_type=qty_defined_on)

    idx = 2
    model = ifcopenshell.open(pass_file)
    qty_inst = get_qty_instance(model)
    qty_to_edit = qty_inst.Quantities[2]
    qty_to_edit.Name = "still Volume but no longer a standard name"
    write_fail_file(model, idx, description="invalid_physical_quantity_name", qto_def_type=qty_defined_on)

    idx = 3
    model = ifcopenshell.open(pass_file)
    pile = create_entity(model, "IfcPile")
    rel_to_edit = model.by_type("IfcBeam")[0].IsDefinedBy[0]
    rel_to_edit.RelatedObjects = (pile,)
    write_fail_file(model, idx, description="invalid_related_entity_type", qto_def_type=qty_defined_on)

    idx = 4
    model = ifcopenshell.open(pass_file)
    qty_inst = get_qty_instance(model)
    invalid_qty_to_add = model.create_entity(
        type="IfcQuantityCount",
        Name="Length",
        CountValue=1000,
    )
    qty_props = list(qty_inst.Quantities)[0:]
    qty_props.append(invalid_qty_to_add)
    qty_inst.Quantities = qty_props
    write_fail_file(model, idx, description="invalid_quantity_prop_entity_type", qto_def_type=qty_defined_on)

    idx = 5
    model = ifcopenshell.open(pass_file)
    qty_inst = get_qty_instance(model)
    qty_inst.MethodOfMeasurement = "Calculated by an intern on an HP 42 calculator"
    write_fail_file(model, idx, description="incorrect_method_of_measurement", qto_def_type=qty_defined_on)


if __name__ == "__main__":
    print("[INFO] opening sample model...")
    in_file = ifcopenshell.open("reinforcing-assembly.txt")

    # generate files for two scenarios: Qto defined on type and Qto defined on occurrence
    for defined_on in QtoDefinitionType:
        generate(in_file, qty_defined_on=defined_on)

    print("[INFO] Done.")
