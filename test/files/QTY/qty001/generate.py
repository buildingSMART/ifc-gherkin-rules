"""
Sample model comes from:

IFC 4X3_ADD2 Documentation - Example E.4.8 - reinforcing assembly
Ref: https://github.com/buildingSMART/IFC4.3.x-sample-models/blob/main/models/building-elements/reinforcing-assembly/reinforcing-assembly.ifc
"""
from typing import Dict

import ifcopenshell
from ifcopenshell.api.unit import add_si_unit
from ifcopenshell.api.pset import add_qto
from ifcopenshell.api.pset import edit_qto

PASS_FILE = "pass-qty001-correct_method_of_measurement.ifc"
FAIL_FILE_PREFIX = "fail-qty001-scenario0"


def get_qty_instance(file: ifcopenshell.file) -> ifcopenshell.entity_instance:
    return file.by_type("IfcElementQuantity")[0]


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


def add_quantity_info(file: ifcopenshell.file):
    print("[INFO] adding quantity information...")
    qto = add_qto(file, product=file.by_type("IfcBeam")[0], name="Qto_BeamBaseQuantities")
    edit_qto(file, qto=qto, properties={
        'Length': 5000.,
        'CrossSectionArea': 0.08,
        'GrossVolume': 0.40,
        'GrossWeight': 960.,
    })


def write_fail_file(file: ifcopenshell.file, index: int, description: str) -> None:
    out_file = f"{FAIL_FILE_PREFIX}{index}-{description}.ifc"
    print(f"[INFO] writing {out_file} to file...")
    file.write(out_file)


def generate(model: ifcopenshell.file):
    add_units_defs(model)
    add_quantity_info(model)

    qty_inst = get_qty_instance(model)
    qty_inst.MethodOfMeasurement = "BaseQuantities"
    print("[INFO] writing passing model to file...")
    model.write(PASS_FILE)

    idx = 1
    model = ifcopenshell.open(PASS_FILE)
    qty_inst = get_qty_instance(model)
    qty_inst.Name = "Qto_DefinitelyNotStandard"
    write_fail_file(model, idx, description="non_standard_qto_name")

    idx = 5
    model = ifcopenshell.open(PASS_FILE)
    qty_inst = get_qty_instance(model)
    qty_inst.MethodOfMeasurement = "Calculated by an intern on an HP 42 calculator"
    write_fail_file(model, idx, description="incorrect_method_of_measurement")


if __name__ == "__main__":
    print("[INFO] opening sample model...")
    in_file = ifcopenshell.open("reinforcing-assembly.txt")

    generate(in_file)

    print("[INFO] Done.")
