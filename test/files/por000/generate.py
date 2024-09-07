import ifcopenshell
import ifcopenshell.template
import os

rule_code = "por000"

abs_path = os.path.join(os.getcwd(), "test", "files", rule_code)
save_ifc_file = lambda file, filename: file.write(os.path.join(abs_path, filename))

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

save_ifc_file(f, 'pass-por000-not_activated_no_port.ifc')

port2 = f.createIfcDistributionPort()
port = f.createIfcDistributionPort()

save_ifc_file(f, 'pass-por000-not_activated_no_relating_port.ifc')

c = f.createIfcRelConnectsPorts(
    RelatedPort = port,
    RelatingPort = port2
    )

save_ifc_file(f, 'pass-por000-passing_valid_port_connectivity.ifc')