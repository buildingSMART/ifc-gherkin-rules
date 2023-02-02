import json
import operator
import os
import re
import subprocess
import sys
import tempfile
import functools
from enum import Flag, auto

class RuleType(Flag):
    INFORMAL_PROPOSITION = auto()
    IMPLEMENTER_AGREEMENT = auto()
    ALL = INFORMAL_PROPOSITION | IMPLEMENTER_AGREEMENT

    @staticmethod
    def from_argv(argv):
        try:
            return functools.reduce(operator.or_, (v for nm, v in RuleType.__members__.items() if "--" + nm.lower().replace("_", "-") in argv))
        except:
            return RuleType.ALL

@functools.lru_cache(maxsize=16)
def get_remote(cwd):
    return subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=cwd).decode('ascii').split('\n')[0]

@functools.lru_cache(maxsize=16)
def get_commits(cwd, feature_file):
    return subprocess.check_output(['git', 'log', '--pretty=format:%h', feature_file], cwd=cwd).decode('ascii').split('\n')

def do_try(fn, default=None):
    try:
        return fn()
    except:
        import traceback
        traceback.print_exc()
        return default

def run(filename, instance_as_str=True, rule_type=RuleType.ALL):
    cwd = os.path.dirname(__file__)
    remote = get_remote(cwd)

    fd, jsonfn = tempfile.mkstemp("pytest.json")

    tag_filter = []
    if rule_type != RuleType.ALL:
        tag_filter.append(
            '--tags=' + ' and '.join(['@'+nm.lower().replace("_", "-") for nm, v in RuleType.__members__.items() if v in rule_type])
        )
    else:
        tag_filter.append('--tags=-disabled' )

    # If this is a test file from the repository filter only the relevant scenarios
    feature_filter = []
    try:    
        rule_code = os.path.basename(filename).split('-')[1].strip().upper()
        if re.match(r'[A-Z]{3}[0-9]{3}', rule_code):
            feature_filter = ["-i", rule_code]
    except Exception as e:
        print(e)

    proc = subprocess.run([sys.executable, "-m", "behave", *feature_filter, *tag_filter, "--define", f"input={os.path.abspath(filename)}", "-f", "json", "-o", jsonfn], cwd=cwd, capture_output=True)
    
    with open(jsonfn) as f:
        try:
            log = json.load(f)
        except json.JSONDecodeError:
            f.seek(0)
            print("Error invoking behave:", file=sys.stderr)
            print(proc.stderr.decode('utf-8'), file=sys.stderr)
            print(f.read(), file=sys.stderr)
            exit(1)
        for item in log:
            feature_name = item['name']
            feature_file = item['location'].split(':')[0]
            shas = get_commits(cwd, feature_file)
            version = len(shas)
            check_disabled = 'disabled' in item['tags']
            if check_disabled:
                yield f"{feature_name}/.v{version}", f"{remote}/blob/{shas[0]}/{feature_file}", "Rule disabled", "Rule disabled", "Rule disabled"
            item['status'] == 'passed'
            for el in item['elements']:
                scenario_name = el['name']
                for step in el['steps']:
                    step_name = step['name']
                    step_status = step.get('result', {}).get('status')
                    if step_status and step_status != 'passed':
                        for occurence in do_try(lambda: list(map(json.loads, step['result']['error_message'][1:])), ()):
                            inst = occurence.get("inst") if instance_as_str else ((occurence["inst_id"], occurence["inst_type"]) if "inst_id" in occurence else None)
                            yield f"{feature_name}/{scenario_name}.v{version}", f"{remote}/blob/{shas[0]}/{feature_file}", f"{step_name}", inst, occurence["message"]

            
    os.close(fd)
    os.unlink(jsonfn)
