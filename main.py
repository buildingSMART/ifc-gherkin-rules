import json
import operator
import os
import re
import subprocess
import sys
import tempfile
import functools
import base64
from enum import Flag, auto, Enum

class RuleType(Flag):
    INFORMAL_PROPOSITION = auto()
    IMPLEMENTER_AGREEMENT = auto()
    CRITICAL = auto()
    INDUSTRY_PRACTICE = auto()
    ALL = INFORMAL_PROPOSITION | IMPLEMENTER_AGREEMENT | CRITICAL | INDUSTRY_PRACTICE

    @staticmethod
    def from_argv(argv):
        try:
            return functools.reduce(operator.or_, (v for nm, v in RuleType.__members__.items() if "--" + nm.lower().replace("_", "-") in argv))
        except:
            return RuleType.ALL

class ExecutionMode(Enum):
    TESTING = 0
    PRODUCTION = 1


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


def run(filename, rule_type=RuleType.ALL, with_console_output=False, execution_mode = ExecutionMode.PRODUCTION, task_id = None):
    cwd = os.path.dirname(__file__)
    
    fd, jsonfn = tempfile.mkstemp("pytest.json")

    tag_filter = []
    if rule_type != RuleType.ALL:
        tag_filter.append(
            '--tags=' + ' and '.join(['@' + nm.lower().replace("_", "-") for nm, v in RuleType.__members__.items() if v in rule_type])
        )

    tag_filter.append('--tags=-disabled')

    # If this is a test file from the repository filter only the relevant scenarios
    feature_filter = []
    if execution_mode != ExecutionMode.PRODUCTION:
        bfn = os.path.basename(filename)
        parts = bfn.split('-')
        if len(parts) >= 2:
            rule_code = parts[1].strip().upper()
            if re.match(r'[A-Z]{3}[0-9]{3}', rule_code):
                feature_filter = ["-i", rule_code]

    if with_console_output:
        # Sometimes it's easier to see what happens exactly on the console output
        print('>',*[sys.executable, "-m", "behave", "--no-capture", "-v", *feature_filter, *tag_filter, "--define", f"input={os.path.abspath(filename)}"])
        subprocess.run(
            [
                sys.executable, "-m", "behave", "--no-capture", "-v",
                *feature_filter, *tag_filter,
                "--define", f"input={os.path.abspath(filename)}", 
                "--define", f"execution_mode={execution_mode}",
                *(["--define", f"task_id={task_id}"] if task_id is not None else []),
            ], 
        cwd=cwd
        )
        if task_id is None:
            exit()
      
    kwargs = {}
    if execution_mode == ExecutionMode.TESTING:
        # Only capture output in testing mode
        kwargs['capture_output'] = True

    proc = subprocess.run(
        [
            sys.executable, "-m", "behave",
            *feature_filter, *tag_filter, 
            "--define", f"input={os.path.abspath(filename)}",
            "--define", f"execution_mode={execution_mode}", 
            *(["--define", f"task_id={task_id}"] if task_id is not None else []),
            "-f", "outcome_embedding_json", "-o", jsonfn # save to json file
        ], 
        cwd=cwd, **kwargs)

    if execution_mode == ExecutionMode.TESTING:
        remote = get_remote(cwd)
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
                rule_is_disabled = 'disabled' in item['tags']
                yield { # add feature information, mainly to check disabled feature
                    'feature_name': f"{feature_name}.v{version}",
                    'rule_is_disabled': rule_is_disabled
                }
                try:
                    el_list = item['elements']
                except KeyError:
                    el_list = []
                for el in el_list:
                    scenario_validation_outcomes = json.loads(base64.b64decode(el.get('validation_outcomes', [{}])[0].get('data', '')).decode('utf-8')) if el.get('validation_outcomes') else []
                    scenario_info = {
                        'scenario_name': el['name'],
                        'step_names': [step['name'] for step in el['steps']]
                    }
                    for validation_outcome in scenario_validation_outcomes:
                        yield validation_outcome | scenario_info
    os.close(fd)
    os.unlink(jsonfn)
