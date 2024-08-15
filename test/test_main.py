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


def contains_outcome_code(data, code='P00010'):
    """
    Recursively checks if the given outcome code exists in the data.
    """
    if isinstance(data, str):
        return code in data
    elif isinstance(data, (list, tuple)):
        return any(contains_outcome_code(item, f'Outcome={code}') for item in data)
    return False


@pytest.mark.parametrize("filename", collect_test_files())
def test_invocation(filename):
    gherkin_results = list(run(filename, execution_mode=ExecutionMode.TESTING))
    base = os.path.basename(filename)
    results = [result for result in gherkin_results if result[4] != 'Rule disabled']
    print()
    print(base)
    print()
    print(f"{len(results)} errors")

    def print_tabulate(gherkin_results):
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in gherkin_results],
            maxcolwidths=[30] * len(gherkin_results[0]),
            tablefmt="simple_grid"
        ))
    
    if gherkin_results and not base.startswith("pass-"):
        print_tabulate(gherkin_results)

    rule_is_disabled = any(description == 'Rule disabled' for description in [result[4] for result in gherkin_results])

    if base.startswith("fail-") and not rule_is_disabled:
        assert len(results) > 0
    elif base.startswith("na-"):
        assert len(results) == 0
    elif base.startswith("pass-") and not rule_is_disabled:
        # check whether every result has a P00010 (PASSED) outcome code
        assert len(results) > 0 and [item for item in results if not contains_outcome_code(item, 'P00010')] == results
        for result in results:
            result[4][0] = 'Testfile activated and no validation error found'
            result[4][1] = 'Outcome=P00010'
        print_tabulate(results)

if __name__ == "__main__":
    pytest.main(["-s", __file__])
