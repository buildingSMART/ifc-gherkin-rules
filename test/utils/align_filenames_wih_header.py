import glob
import os
import ifcopenshell
source_dir = "../files"
# change with local src
alt_dir = "/home/geert/Documents/gherkin/development/v2/ifc-gherkin-rules/test/files"

ifc_files = glob.glob(f"{source_dir}/**/*.ifc", recursive=True)

for file_path in ifc_files:
    filename = os.path.basename(file_path)
    f = ifcopenshell.open(file_path)
    f.header.file_name.name = filename
    f.write(file_path)

source_dir = "../files"

# change with local src
alt_dir = "/home/geert/Documents/gherkin/development/v2/ifc-gherkin-rules/test/files"

for file1_path in ifc_files:
    filename = os.path.basename(file1_path)
    file2_path = None

    for root, _, files in os.walk(alt_dir):
        if filename in files:
            file2_path = os.path.join(root, filename)
            break
    if not file2_path:
        continue
    
    with open(file1_path, "r", encoding="utf-8") as f1, open(file2_path, "r", encoding="utf-8") as f2:
        content1 = f1.read()
        content2 = f2.read()
        
    header_part = content1.split("ENDSEC;")[0] + "ENDSEC;\n"

    data_part = content2.split("ENDSEC;")[1].strip()

    if data_part.endswith("END-ISO-10303-21;"):
        data_part = data_part.rsplit("ENDSEC;", 1)[0].strip()
    merged_content = header_part + data_part.strip() + "\nENDSEC;\nEND-ISO-10303-21;\n"

    with open(file1_path, "w", encoding="utf-8") as f_out:
        f_out.write(merged_content)

    print(f"✅ Updated {filename}")
