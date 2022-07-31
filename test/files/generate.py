import itertools
import ifcopenshell
import ifcopenshell.template
from regex import F

for num_sites, num_buildings, assign_to_site in itertools.product(range(3), range(3), (0, 1)):
    if num_sites == 0 and assign_to_site == 1:
        continue

    f = ifcopenshell.template.create(schema_identifier="IFC2X3")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    
    sites = [f.createIfcSite(
        ifcopenshell.guid.new(),
        owner,
    ) for _i in range(num_sites)]

    if sites:
        f.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner,
            RelatingObject=proj,
            RelatedObjects=sites
        )

        if assign_to_site:
            building_parent = sites[0]

    buildings = [f.createIfcBuilding(
        ifcopenshell.guid.new(),
        owner,
    ) for _i in range(num_buildings)]

    if buildings:
        f.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner,
            RelatingObject=building_parent,
            RelatedObjects=buildings
        )

    ok = num_sites <= 1 and num_buildings >= 1 and (not num_sites or assign_to_site)

    fail_or_pass = "pass" if ok else "fail"

    f.write(f"{fail_or_pass}-{num_sites}-sites-{num_buildings}-buildings-variant-{assign_to_site}.ifc")
