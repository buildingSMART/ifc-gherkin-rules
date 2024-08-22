import os
import glob
import sys
import re

import pytest
import tabulate

try:
    from ..main import run, ExecutionMode
    from .utils import collect_test_files
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run, ExecutionMode
    from test.utils import collect_test_files

rule_code_pattern = re.compile(r"^[a-zA-Z]{3}\d{3}$")
rule_codes = list(filter(lambda arg: rule_code_pattern.match(arg), sys.argv[1:]))

    
def exclude_disabled_rules(filepath):
    tags = []
    
    with open(filepath, 'r') as file:
        for line in file:
            stripped_line = line.strip()  # Remove any leading or trailing whitespace
            if stripped_line.startswith("@"):
                tags_on_line = stripped_line.split()
                tags.extend(tags_on_line)
    return '@disabled' in tags

def rule_disabled(code: str) -> bool:
    feature_paths = glob.glob(os.path.join(os.path.dirname(__file__), "../features/**/*.feature"), recursive=True)
    return next((exclude_disabled_rules(path) for path in feature_paths if os.path.basename(path).lower().startswith(code)), False)


@pytest.mark.parametrize("filename", collect_test_files())
def test_invocation(filename):
    #results are all the results without considering the disabled rules and is the sum of the failing and passing results
    gherkin_results = list(run(filename, execution_mode=ExecutionMode.TESTING))
    results, failing_results, passing_results = [], [], []
    rule_is_disabled = any(description == 'Rule disabled' for description in [result[5] for result in gherkin_results])

    for result in gherkin_results:
        if result[5] != 'Rule disabled':
            results.append(result)
            (passing_results if result[5] == 'Rule passed' else failing_results).append(result)
    base = os.path.basename(filename)

    print()
    print(base)
    print()
    print(f"{len(results)} result(s)")

    if results:
        print(tabulate.tabulate(
                [[c or '' for c in r] for r in gherkin_results],
                headers = ["Rule", "Location", "Last step", "Scenario", "Instance", "Result"],
                maxcolwidths=[30] * len(gherkin_results[0]),
                tablefmt="simple_grid"
            ))
    elif rule_is_disabled:
        # Because we only run unit-testfiles on the feature they are created for,
        # it means that if there is one mention of a disabled rule it applies to the
        # testfile as well and nothing needs to be printed.
        print("Rule is disabled")
    else: 
        print("Rule not activated by test file")
        

    if not rule_is_disabled:
        if base.startswith("fail-"):
            assert len(failing_results) > 0
        elif base.startswith("na-"):
            assert len(results) == 0
        elif base.startswith("pass-"):
            assert len(passing_results) > 0
    
if __name__ == "__main__":
    pytest.main(["-s", __file__])
