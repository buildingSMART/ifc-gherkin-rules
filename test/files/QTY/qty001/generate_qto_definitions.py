import csv
from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from pathlib import Path
from typing import List
import sys

import ifcopenshell


# property sets for Quantity Takeoff (Qto) are not present in IFC2X3
class SchemaVersions(Enum):
    IFC4X3 = "IFC4X3"
    IFC4_ADD2 = "IFC4_ADD2"


RESOURCE_PATH_PREFIX = Path("features", "resources")


@dataclass
class PropertyDef:
    property_name: str
    property_type: str


@dataclass
class QtoDef:
    property_set_name: str
    template_type: str
    applicable_entities: List[str]
    applicable_type_value: str
    property_definitions: List[PropertyDef]


def property_template_type_to_entity_type(template_type: str) -> str:
    match template_type:
        case "Q_AREA":
            return "IfcQuantityArea"
        case "Q_COUNT":
            return "IfcQuantityCount"
        case "Q_LENGTH":
            return "IfcQuantityLength"
        case "Q_NUMBER":
            return "IfcQuantityNumber"
        case "Q_TIME":
            return "IfcQuantityTime"
        case "Q_VOLUME":
            return "IfcQuantityVolume"
        case "Q_WEIGHT":
            return "IfcQuantityWeight"
        case _:
            raise ValueError(f"Unknown template type: {template_type}")


def get_site_packages_path():
    venv_path = Path(sys.prefix)
    site_packages = venv_path / "Lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if site_packages.exists():
        return site_packages
    else:
        raise FileNotFoundError(f"Site-packages directory not found at {site_packages}")


def qto_def_from_entity(inst: ifcopenshell.entity_instance) -> QtoDef:
    prop_defs = inst.HasPropertyTemplates
    applicable_entitites = inst.ApplicableEntity.split(",")
    property_def_info = list()
    for prop_def in prop_defs:
        property_def_info.append({
            "property_name": prop_def.Name,
            "property_type": property_template_type_to_entity_type(prop_def.TemplateType)
        })

    qto = QtoDef(
        property_set_name=inst.Name,
        template_type=inst.TemplateType,
        applicable_entities=applicable_entitites,
        applicable_type_value=inst.ApplicableEntity,
        property_definitions=property_def_info,
    )
    return qto


def create_definitions(library_path: Path, schema_version: SchemaVersions) -> List[QtoDef]:
    qto_defs = list()
    in_file = library_path / f"Pset_{schema_version.value}.ifc"
    model = ifcopenshell.open(in_file.as_posix())
    print(f"[INFO] opened {in_file}...")

    psets = model.by_type("IfcPropertySetTemplate")
    for pset in psets:
        name = pset.Name
        if name.startswith("Qto_"):
            print(f"Creating definition for {name}...")
            qto_defs.append(qto_def_from_entity(pset))

    return qto_defs


def write_csv(schema_version: SchemaVersions, qto_defs: List[QtoDef]):
    cur_path = Path(__file__).resolve()
    parents = cur_path.parents
    out_path = parents[4] / RESOURCE_PATH_PREFIX / schema_version.value
    if schema_version == SchemaVersions.IFC4_ADD2:
        out_path = parents[4] / RESOURCE_PATH_PREFIX / "IFC4"
    out_file = out_path / "qto_definitions.csv"

    with open(out_file.as_posix(), "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["property_set_name", "template_type", "applicable_entities", "applicable_type_value",
                         "property_definitions"])
        for qto in qto_defs:
            print(f"[INFO] Writing definition for {qto.property_set_name} to {out_file.as_posix()}...")
            writer.writerow(
                [
                    qto.property_set_name,
                    qto.template_type,
                    qto.applicable_entities,
                    qto.applicable_type_value,
                    qto.property_definitions,
                ]
            )


def main():
    print("[INFO] Generating QTO definitions...")
    print("[INFO] Getting path to property set definitions...")
    site_packages = get_site_packages_path()
    library_path = site_packages / "ifcopenshell" / "util" / "schema"

    for schema_enum in SchemaVersions:
        print(f"[INFO] Getting {schema_enum.value} quantity definitions...")
        qto_defs = create_definitions(library_path, schema_enum)
        write_csv(schema_enum, qto_defs)


if __name__ == "__main__":
    main()
