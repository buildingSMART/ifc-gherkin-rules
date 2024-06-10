import requests
import yaml
import re
from packaging import version
import ifcopenshell

def recent_ifcopenshell_version():
    branches = requests.get("https://api.github.com/repos/IfcOpenBot/IfcOpenShell/branches").json()
    versions = [branch['name'] for branch in branches if re.compile(r'^v\d+\.\d+\.\d+$').match(branch['name'])]
    versions.sort(key=version.parse)
    return versions[-1]

def latest_ifcopenshell_build_commit():
    try:
        ifcopenshell_version = recent_ifcopenshell_version()
    except:
        return None # e.g. maximum api requests reached
    url = f"https://api.github.com/repos/IfcOpenBot/IfcOpenShell/commits?sha={ifcopenshell_version}"
    response = requests.get(url)
    commits = response.json()

    for commit in commits:
        for comment in  requests.get(commit['comments_url']).json():
            if 'ifcopenshell-builds' in comment['body'] and 'IfcOpenBot' in comment['user']['login']:
                commit_hash = commit['sha'][:7]
                return f"{ifcopenshell_version}-{commit_hash}"
            
def get_commit_hash_from_ci_yml(file_path):
    with open(file_path, 'r') as file:
        ci_config = yaml.safe_load(file)

    steps = ci_config['jobs']['build-linux']['steps']
    wget_command = None
    for step in steps:
        if 'run' in step and 'wget' in step['run']:
            wget_command = step['run']
            break

    match = re.search(r'ifcopenshell-python-[^/]+-v([0-9]+\.[0-9]+\.[0-9]+)-([a-f0-9]+)-linux64.zip', wget_command)
    if match:
        return f"v{match.group(1)}-{match.group(2)}"
    else:
        return None

def update_ci_yml_with_latest_hash(file_path, latest_version):
    with open(file_path, 'r') as file:
        ci_content = file.read()

    updated_content = re.sub(
        r'(ifcopenshell-python-[^/]+-v)([0-9]+\.[0-9]+\.[0-9]+)-([a-f0-9]+)(-linux64.zip)',
        rf'\g<1>{latest_version[1:]}\g<4>',
        ci_content
    )

    with open(file_path, 'w') as file:
        file.write(updated_content)


def update_ifcopenshell_version():
    ci_yml_path = '.github/workflows/ci.yml'
    ifcopenshell_build_hash = {
        'latest_build' : latest_ifcopenshell_build_commit(),
        'local': ifcopenshell.version[:7],
        'ci_cd': get_commit_hash_from_ci_yml(ci_yml_path)
    }

    if ifcopenshell_build_hash['latest_build'] != ifcopenshell_build_hash['ci_cd']:
        if ifcopenshell_build_hash['ci_cd'] and ifcopenshell_build_hash['latest_build']: # only update version once every test
            update_ci_yml_with_latest_hash(ci_yml_path, ifcopenshell_build_hash['latest_build'])
            print('ifcopenshell version updated')

if __name__ == '__main__':
    update_ifcopenshell_version()