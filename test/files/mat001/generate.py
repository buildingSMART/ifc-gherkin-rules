import itertools
import ifcopenshell
import ifcopenshell.template

entity_material_mapping = {
    'IfcLamp': 'IfcMaterialLayer',
    'IfcBeam': 'IfcMaterialProfile',
    'IfcPipeFitting': 'IfcMaterialConstituent'
}
names = ['Conductor', 'LoadBearing', 'Casing']

correct_names_mapping = {key: names[idx] for idx, key in enumerate(entity_material_mapping.keys())}

for mapping in [dict(zip(entity_material_mapping.keys(), perm)) for perm in itertools.permutations(names)]:
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    for entity, name in mapping.items():
        material_category = entity_material_mapping[entity][3:]  # e.g. 'MaterialLayer' for 'IfcMaterialLayer'
        f.createIfcRelAssociatesMaterial(
            ifcopenshell.guid.new(),
            owner,
            RelatedObjects=[f.create_entity(entity)],
            RelatingMaterial=f.create_entity(
                f'Ifc{material_category}Set',
                **{f'{material_category}s': [
                    f.create_entity(
                        f'Ifc{material_category}',
                        Name=name
                    )
                ]}
            )
        )
    if not mapping == correct_names_mapping:
        incorrect_categories = [entity_material_mapping[i[0]].replace('IfcMaterial', '').lower() for i in mapping.items() if correct_names_mapping[i[0]] != i[1]]
        f.write(f'fail-mat001-wrong_{"_and_".join(incorrect_categories)}_names.ifc')
    else:
        f.write('pass-mat001-correct_material_layer_profile_constituent_names')