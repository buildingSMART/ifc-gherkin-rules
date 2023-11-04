import json
import operator
import os
import re
import subprocess
import sys
import tempfile
import functools
from enum import Flag, auto

from typing import Type, TypeVar, Union
from validation_results import ValidationResult, Scenario, Feature
from test.protocol.config import ConfiguredBaseModel


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
def get_commits(cwd, feature_filename):
    return subprocess.check_output(['git', 'log', '--pretty=format:%h', feature_filename], cwd=cwd).decode('ascii').split('\n')


def do_try(fn, default=None):
    try:
        return fn()
    except:
        import traceback
        traceback.print_exc()
        return default


def run(filename, instance_as_str=True, rule_type=RuleType.ALL, with_console_output=False, ci_cd=False):
    cwd = os.path.dirname(__file__)
    remote = get_remote(cwd)

    fd, jsonfn = tempfile.mkstemp("pytest.json")

    tag_filter = []
    if rule_type != RuleType.ALL:
        tag_filter.append(
            '--tags=' + ' and '.join(['@' + nm.lower().replace("_", "-") for nm, v in RuleType.__members__.items() if v in rule_type])
        )
    else:
        tag_filter.append('--tags=-disabled')

    # If this is a test file from the repository filter only the relevant scenarios
    feature_filter = []
    try:
        rule_code = os.path.basename(filename).split('-')[1].strip().upper()
        if re.match(r'[A-Z]{3}[0-9]{3}', rule_code):
            feature_filter = ["-i", rule_code]
    except Exception as e:
        print(e)

    if with_console_output:
        # Sometimes it's easier to see what happens exactly on the console output
        print('>',*[sys.executable, "-m", "behave", *feature_filter, *tag_filter, "--define", f"input={os.path.abspath(filename)}"])
        subprocess.run([sys.executable, "-m", "behave", *feature_filter, *tag_filter, "--define", f"input={os.path.abspath(filename)}"], cwd=cwd)

    proc = subprocess.run([sys.executable, "-m", "behave", *feature_filter, *tag_filter, "--define", f"input={os.path.abspath(filename)}", "--define", "error_on_passed_rule=yes", "-f", "json", "-o", jsonfn], cwd=cwd, capture_output=True)

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
            feature_filename = item['location'].split(':')[0]
            shas = get_commits(cwd, feature_filename)
            f = {
                'name' : item['name'],
                'description' : '\n'.join(item.get('description', [])), 
                'filename' : item['location'].split(':')[0],
                'location' : item['location'],
                'github_source_location' : f"{remote}/blob/{shas[0]}/{feature_filename}",
                'version' : len(shas),
                'tags' : item['tags'] 
            }
            feature = Feature(**f) if not ci_cd else Feature.model_construct(**f)
            try:
                el_list = item['elements']
            except KeyError:
                el_list = []
            check_disabled = 'disabled' in feature.tags
            for el in el_list:
                s = {'name': el['name'], 'feature': feature}
                scenario = Scenario(**s) if not ci_cd else Scenario.model_construct(**s)
                for step in el['steps']:
                    scenario.steps.append(step)
                    scenario.latest_step = step['name']
                    step_status = step.get('result', {}).get('status')
                    if step_status and step['step_type'] == 'then' and not check_disabled:
                        try:
                            results = list(map(json.loads, step['result']['error_message'][1:]))
                        except KeyError:  # THEN not checked
                            results = []
                        except json.decoder.JSONDecodeError:  # THEN not checked
                            results = []
                        passed = [result for result in results if result['rule_passed']]
                        failed = [result for result in results if not result['rule_passed']]

                        for occurence in failed:
                            v = {
                                "passed_failed": "failed",
                                "message": occurence["message"],
                                "feature": feature,
                                "scenario": scenario,
                                "ifc_filepath": filename,
                                "inst": occurence.get("inst") if instance_as_str else ((occurence["inst_id"], occurence["inst_type"]) if "inst_id" in occurence else None),
                            }
                            yield ValidationResult(**v) if not ci_cd else ValidationResult.model_construct(**v)
                        for occurence in passed:
                            v = {
                                "passed_failed": "passed",
                                "message": "Rule passed",
                                "feature": feature,
                                "scenario": scenario,
                                "ifc_filepath": filename,
                                "inst": occurence.get("inst") if instance_as_str else ((occurence["inst_id"], occurence["inst_type"]) if "inst_id" in occurence else None)
                            }
                            try:
                                yield ValidationResult(**v) if not ci_cd else ValidationResult.model_construct(**v)
                            except:
                                pass
                # feature.scenario_list.append(scenario)
            if check_disabled:
                v = {
                    'disabled' : True,
                    'message': 'Rule disabled',
                    'feature': feature,
                    'ifc_filepath': filename
                }
                yield ValidationResult(**v) if not ci_cd else ValidationResult.model_construct(**v)

    os.close(fd)
    os.unlink(jsonfn)