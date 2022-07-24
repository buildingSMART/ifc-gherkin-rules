import json
import os
import subprocess
import sys
import tempfile
import functools

@functools.lru_cache(maxsize=16)
def get_remote(cwd):
    return subprocess.check_output(['git', 'remote'], cwd=cwd).decode('ascii').split('\n')[0]

@functools.lru_cache(maxsize=16)
def get_commits(cwd, feature_file):
    return subprocess.check_output(['git', 'log', '--pretty=format:%h', feature_file], cwd=cwd).decode('ascii').split('\n')

def run(filename):
    cwd = os.path.dirname(__file__)
    remote = get_remote(cwd)

    fd, jsonfn = tempfile.mkstemp("pytest.json")
    
    subprocess.call([sys.executable, "-m", "behave", "--define", f"input={os.path.abspath(filename)}", "-f", "json", "-o", jsonfn], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(jsonfn) as f:
        log = json.load(f)
        for item in log:
            feature_name = item['name']
            feature_file = item['location'].split(':')[0]
            shas = get_commits(cwd, feature_file)
            version = len(shas)
            item['status'] == 'passed'
            for el in item['elements']:
                scenario_name = el['name']
                for step in el['steps']:
                    step_name = step['name']
                    step_status = step.get('result', {}).get('status')
                    if step_status and step_status != 'passed':
                        for occurence in list(map(json.loads, step['result']['error_message'][1:])):
                            yield f"{feature_name}/{scenario_name}.v{version}", f"{remote}/blob/{shas[0]}/{feature_file}", f"{step_name}", occurence["inst"], occurence["message"]

            
    os.close(fd)
    os.unlink(jsonfn)
