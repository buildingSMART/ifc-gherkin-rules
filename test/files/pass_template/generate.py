# for commit: 462daf5

import ifcopenshell
import ifcopenshell.template
import itertools


file = ifcopenshell.template.create(schema_identifier="IFC2X3")
context = file.by_type("IfcGeometricRepresentationContext")[0]
owner = file.by_type("IfcOwnerHistory")[0]
building_parent = proj = file.by_type("IfcProject")[0]
site = file.createIfcSite(ifcopenshell.guid.new(), owner)

building = file.createIfcBuilding(
                ifcopenshell.guid.new(), owner
            )

file.createIfcRelAggregates(
        ifcopenshell.guid.new(),
        owner,
        RelatingObject=site,
        RelatedObjects = [building]
    )

file.createIfcSpace(ifcopenshell.guid.new(), Name='My Wall')
file.write('pass-gem002-no-space2.ifc')