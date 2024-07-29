import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.template


def make_id():
    return ifcopenshell.guid.new()

def generate_01():
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    project = f.createIfcProject(make_id())
    site = f.createIfcSite(make_id())
    building = f.createIfcBuilding(make_id())
    storey = f.createIfcBuildingStorey(make_id())

    # f.createIfcRelAggregates(make_id(), RelatingObject=project, RelatedObjects=[site])
    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=site, RelatedElements=[building])
    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=building, RelatedElements=[storey])

    annotation = f.createIfcAnnotation(make_id())
    grid = f.createIfcGrid(make_id())

    f.write('fail-sps007-scenario01-no_required_spatial_relationship.ifc')

    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=storey, RelatedElements=[annotation, grid])

    f.write("pass-sps007-scenario01-compliant_annotation_grid_wall.ifc")


def generate_02():
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    project = f.createIfcProject(make_id())
    site = f.createIfcSite(make_id())
    building = f.createIfcBuilding(make_id())
    storey = f.createIfcBuildingStorey(make_id())

    wall = f.createIfcWall(GlobalId = make_id())

    f.write('fail-sps007-scenario02_element_not_in_spatial_containment')

    spatial_structure = f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=storey, RelatedElements=[wall])

    f.write('pass-sps007-scenario03-element_part_of_spatial_structure.ifc')

    opening_element = f.createIfcOpeningElement(make_id())

    f.write('pass-sps007-scenario02-opening_element_not_contained_in_spatial_containment')

    spatial_structure.RelatedElements = [wall, opening_element]

    f.write('pass-sps007-scenario02-opening_elemenent_in_spatial_containment')

def generate_03():
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    project = f.createIfcProject(make_id())
    site = f.createIfcSite(make_id())
    building = f.createIfcBuilding(make_id())
    storey = f.createIfcBuildingStorey(make_id())

    wall = f.createIfcWall(GlobalId = make_id())

    element_assembly = f.createIfcElementAssembly(make_id())

    spatial_structure = f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=storey, RelatedElements=[wall, element_assembly])

    f.createIfcRelAggregates(make_id(), RelatingObject=element_assembly, RelatedObjects=[wall])

    f.write('fail-sps007-scenario03-aggregated_part_in_spatial_containment.ifc')

    spatial_structure.RelatedElements = [wall]

    f.write('pass-sps007-scenario03-aggregated_part_not_in_spatial_containment.ifc')


def generate_04():
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    project = f.createIfcProject(make_id())
    site = f.createIfcSite(make_id())
    building = f.createIfcBuilding(make_id())
    storey = f.createIfcBuildingStorey(make_id())

    # f.createIfcRelAggregates(make_id(), RelatingObject=project, RelatedObjects=[site])
    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=site, RelatedElements=[building])
    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=building, RelatedElements=[storey])

    opening_element = f.createIfcOpeningElement(make_id())
    f.write('fail-sps007-scenario04-ifc_opening_not_part_of_spatial_containment.ifc')

    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=storey, RelatedElements=[opening_element])

    f.write("pass-sps007-scenario04-opening_part_of_spatial_containment.ifc")


def generate_05():
    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    site = f.createIfcSite(make_id())
    building = f.createIfcBuilding(make_id())
    storey = f.createIfcBuildingStorey(make_id())

    alignment = f.createIfcAlignment(make_id())

    f.write('pass-sps007-scenario05-alignment_not_in_spatial_containment.ifc')

    f.createIfcRelContainedInSpatialStructure(make_id(), RelatingStructure=storey, RelatedElements=[alignment])

    f.write('fail-sps007-scenario05-alignment_in_spatial_structure.ic')




generate_01()
generate_02()
generate_03()
generate_04()
generate_05()

