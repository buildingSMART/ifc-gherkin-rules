import ast
import csv
import glob
import os
import ifcopenshell
w = ifcopenshell.ifcopenshell_wrapper

known_ptype_issues = ('IfcAnnotation', 'IfcDiscreteAccessory', 'IfcMaterial')

for fn in glob.glob('**/pset_definitions.csv', recursive=True):
    schema = fn.split(os.sep)[0].lower()
    S = w.schema_by_name({'ifc4x3': 'ifc4x3_add2'}.get(schema, schema))
    
    with open(fn, newline='') as csvfile:
        items = list(csv.DictReader(csvfile, delimiter=','))

    for item in items:
        for ent in ast.literal_eval(item['applicable_entities']):
            ptype = None
            if '/' in ent:
                ent, ptype = ent.split('/')
            assert S.declaration_by_name(ent)
            if ptype and ent not in known_ptype_issues:
                assert ptype in [a for a in S.declaration_by_name(ent).all_attributes() if a.name() == 'PredefinedType'][0].type_of_attribute().declared_type().enumeration_items()