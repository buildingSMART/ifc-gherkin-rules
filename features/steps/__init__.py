import json
from pathlib import Path
from behave import register_type
from parse_type import TypeBuilder

json_file = Path(__file__).parent / "registered_type_definitions.json"
with open(json_file, "r", encoding="utf-8") as file:
    type_definitions = json.load(file)

for name, values in type_definitions.items():
    register_type(**{name: TypeBuilder.make_enum({v: v for v in values})})