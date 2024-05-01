import os
import subprocess
import re

def find_disabled_feature_codes(features_path):
    disabled_tag_pattern = re.compile(r'@disabled')
    code_pattern = re.compile(r'^[a-zA-Z]{3}\d{3}')
    disabled_feature_codes = set()

    for root, _, files in os.walk(features_path):
        for file in files:
            if file.endswith('.feature'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    if disabled_tag_pattern.search(f.read()):
                        match = code_pattern.search(file)
                        if match:
                            disabled_feature_codes.add(match.group())

    return list(disabled_feature_codes)


def main():
    disabled_rule_codes = find_disabled_feature_codes(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'features')))
    directory_path = os.path.join(os.path.dirname(__file__), 'files')

    folders = [name for name in os.listdir(directory_path)
               if os.path.isdir(os.path.join(directory_path, name)) 
               and re.match(r'^[a-zA-Z]{3}\d{3}$', name)
               and name.upper() not in disabled_rule_codes] 

    subprocess.run(['python', 'generate_markdown.py'] + folders, cwd=os.path.dirname(__file__))

if __name__ == '__main__':
    main()
