import os
import re

# Path to the directory containing the markdown files
repo_path = '/home/geert/Documents/IFC4.3.x-development/docs/schemas'

# Regex pattern to match deprecated attributes
deprecation_pattern = re.compile(r'DEPRECATION', re.IGNORECASE)

# List to store entities with deprecated attributes
entities_with_deprecation = []

for root, dirs, files in os.walk(repo_path):
    for file in files:
        if file.endswith('.md'):
            entity_name = file.replace('.md', '')
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if deprecation_pattern.search(content):
                    entities_with_deprecation.append(entity_name)

# Output the entities with deprecated attributes
print("Entities with deprecated attributes:")
for entity in entities_with_deprecation:
    print(entity)