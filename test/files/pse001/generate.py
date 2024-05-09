import ifcopenshell
w = ifcopenshell.ifcopenshell_wrapper

configs = [(True, 'ELECTRICACTUATOR'), (False, 'HANDOPERATEDACTUATOR')]

for schema in ['ifc2x3', 'ifc4', 'ifc4x3_add2']:
    entity_names = {e.name() for e in w.schema_by_name(schema).entities()}
    for create_type in [None, True, 'HasPropertySets']:
        for is_valid, ptype in configs:
            f = ifcopenshell.file(schema=schema)
            entity = 'IfcActuator' + ('Type' if create_type else '')
            if entity not in entity_names:
                # ifc2x3: "Usage of IfcActuatorType defines the parameters for one or more occurrences of IfcDistributionControlElement ..."
                entity = 'IfcDistributionControlElement'
            act = f.create_entity(entity, ifcopenshell.guid.new())
            act_type = act
            attr_names = {a.name() for a in w.schema_by_name(schema).declaration_by_name(entity).all_attributes()}
            if 'PredefinedType' in attr_names:
                act.PredefinedType = ptype
            else:
                act_type = f.createIfcActuatorType(ifcopenshell.guid.new(), PredefinedType=ptype)
                f.createIfcRelDefinesByType(
                    ifcopenshell.guid.new(),
                    RelatedObjects=[act],
                    RelatingType = act_type
                )
                if schema == 'ifc2x3':
                    # ifc2x3 does not have type driven override yet
                    act = act_type
            pset = f.createIfcPropertySet(
                ifcopenshell.guid.new(),
                Name='Pset_ActuatorTypeElectricActuator',
                HasProperties=[
                    f.createIfcPropertySingleValue(Name='ActuatorInputPower', NominalValue=f.createIfcPowerMeasure(1.0))
                ]
            )
            if create_type == 'HasPsets':
                act_type.HasPropertySets = (pset,)
            else:
                f.createIfcRelDefinesByProperties(
                    ifcopenshell.guid.new(),
                    RelatedObjects = [act],
                    RelatingPropertyDefinition = pset
                )
            
            f.write(f'{"pass" if is_valid else "fail"}-pse001-{schema}-{"on-type-forward-attr" if create_type == "HasPropertySets" else "on-type" if create_type else "on-occurence"}-electric-actuator-pset.ifc')
