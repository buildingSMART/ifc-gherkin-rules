import csv
import re
import requests

repository_url = "https://api.github.com/repos/buildingSMART/ifc-gherkin-rules/contents/features"

response = requests.get(repository_url)
if response.status_code == 200:
    directory_data = response.json()
    information_about_features = []
    for item in directory_data:
        if item["type"] == "file" and item["name"].endswith(".feature"):
            information_about_feature = {}
            file_content = requests.get(item["download_url"]).text

            information_about_feature["code"] = item["name"][0:6]
            information_about_feature["name"] = item["name"][7:].replace('.feature', '')


            match = re.search(r"Feature: (.+?)\n\s*Scenario:", file_content, re.DOTALL)

            if match:
                feature_desc = match.group(1).strip()
                information_about_feature["rule_description"] = "".join(
                    feature_desc.split("\n")[1:]
                )
            else:
                information_about_feature["rule_description"] = ""

            lines = file_content.split("\n")
            at_lines = [line.lower() for line in lines if line.startswith("@")]

            tags = ["@disabled", "@implementer-agreement", "@informal-proposition"]
            for tag in tags:
                information_about_feature[tag[1:]] = tag in at_lines

            rule_tag = [item for item in at_lines if (item not in tags and len(item)==4)]
            information_about_feature["rule_tag"] = rule_tag[0].upper()[1:]

            information_about_features.append(information_about_feature)

    print(information_about_features)

    csv_file = "rules_overview.csv"

    with open(csv_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=information_about_features[0].keys())
        writer.writeheader()
        writer.writerows(information_about_features)
    print(f"Data has been written to {csv_file}")

else:
    print("Failed to list directory contents. Status code:", response.status_code)
