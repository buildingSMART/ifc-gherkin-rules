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
    gherkin_results = list(run(filename, execution_mode=ExecutionMode.TESTING))
    base = os.path.basename(filename)
    results = [result for result in gherkin_results if result[4] != 'Rule disabled']
    print()
    print(base)
    print()
    print(f"{len(results)} errors")

    if gherkin_results:
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in gherkin_results],
            maxcolwidths=[30] * len(gherkin_results[0]),
            tablefmt="simple_grid"
        ))

    if base.startswith("fail-") and not any(description == 'Rule disabled' for description in [result[4] for result in gherkin_results]):
        assert len(results) > 0
    elif base.startswith("pass-"):
        assert len(results) == 0

if __name__ == "__main__":
    pytest.main(["-s", __file__])
