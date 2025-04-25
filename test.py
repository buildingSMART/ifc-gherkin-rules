import os
import ifcopenshell

base_path = "/home/geert/Documents/gherkin/development/ifc-gherkin-rules/test/files"
paths = []

# Recursively walk through all subdirectories and collect .ifc files
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.lower().endswith(".ifc"):
            full_path = os.path.join(root, file)
            paths.append(full_path)

# Check for IfcBuiltElement or IfcBuildingElement
for path in paths:
    try:
        f = ifcopenshell.open(path)
        if f.schema == 'IFC4X3':
            elements = f.by_type("IfcBuiltElement")
            # if elements:
            #     # import pdb; pdb.set_trace()
            #     print(f"Found IfcBuiltElement in: {path}")
        elif f.schema == 'IFC2X3':
            elements = f.by_type("IfcBoundingBox")
            if elements:
                print(f"Found IfcBuildingElement in: {path}")
        elif f.schema == 'IFC4':
            elements = f.by_type("IfcBuildingElement")
            # if elements:
            #     print(f"Found IfcBuildingElement in: {path}")
        else: 
            pass
    except Exception as e:
        print(f"Failed to open {path}: {e}")
