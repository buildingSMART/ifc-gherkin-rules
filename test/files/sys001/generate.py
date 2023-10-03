import os
import ifcopenshell
import ifcopenshell.template

for validity, ports in [
    ("pass", ('SINK', 'SOURCE')),
    ("fail", ('SINK',)),
    ("fail", ('SOURCEANDSINK', 'SINK')),
    ("fail", ()),
    ("fail", ('SINK', 'SOURCE', 'SINK')),
]:

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD1")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    site = f.createIfcSite(
        ifcopenshell.guid.new(),
        owner,
        CompositionType="ELEMENT",
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[site]
    )

    cable = f.createIfcCableSegment(
        ifcopenshell.guid.new(), owner
    )

    f.createIfcRelContainedInSpatialStructure(
        ifcopenshell.guid.new(), owner, None, None, [cable], site
    )

    def create_port(lbl):
        return f.createIfcDistributionPort(
            ifcopenshell.guid.new(), owner,
            FlowDirection=lbl
        )
    
    if ports:
        f.createIfcRelNests(
            ifcopenshell.guid.new(), owner,
            RelatingObject=cable,
            RelatedObjects = list(map(create_port, ports))
        )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario0%d-" % (1 if len(ports) == 2 else 2)
    case = '_'.join(map(str.lower, ports))
    if not case:
        case = "no_ports"
    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{case}.ifc")
