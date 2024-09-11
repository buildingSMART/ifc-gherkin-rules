import os
import ifcopenshell
import ifcopenshell.template

import networkx as nx

for validity, chain_length, topology in [
    ("pass", 1, 'path'),
    ("pass", 3, 'path'),
    ("fail", 1, 'cycle'),
    ("fail", 3, 'cycle'),
]:

    f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    G = nx.DiGraph()
    getattr(nx, f'add_{topology}')(G, list(range(chain_length)))

    N = dict(map(lambda n: (n, f.createIfcGroup(ifcopenshell.guid.new(), Name='group-%d' % n)), G.nodes))

    for ab in G.edges:
        a, b = map(N.__getitem__, ab)
        f.createIfcRelAssignsToGroup(ifcopenshell.guid.new(), RelatedObjects=[a], RelatingGroup=b)

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"

    f.write(f"{validity}-{os.path.basename(os.path.dirname(__file__))}-{failing_scenario}{topology}-of-length-{chain_length}.ifc")
