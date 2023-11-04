import os
import glob
import sys
import re

import pytest
import tabulate

try:
    from ..main import run
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run

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


def get_test_files():
    """
    Option -> Example
    Test files for a rule -> 'python3 test_main.py alb001'
    Also applies for multiple rules -> 'python3 test_main.py alb001 alb002'
    Test files for a single file -> 'python3 test_main.py <path>.ifc
    Also applies for multiple files -> 'python3 test_main.py <path1>.ifc <path2>.ifc'
    Codes and rules can also be combined -> 'python3 test_main.py alb001 <path>.ifc'
    """
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    rule_code_pattern = re.compile(r"^[a-zA-Z]{3}\d{3}$")
    rule_codes = list(filter(lambda arg: rule_code_pattern.match(arg), args))

    test_files = []
    for code in rule_codes:
        paths = glob.glob(os.path.join(os.path.dirname(__file__), "files/", code.lower(), "*.ifc"))
        if not paths:
            print(f"No IFC files were found for the following rule code: {code}. Please provide test files or verify the input.")
        elif rule_disabled(code):
            print(f"The rule identified by code '{code}' is currently marked as 'disabled'. Any associated test files will not be taken into consideration")
            continue
        test_files.extend(paths)

    file_pattern =  r".*\.ifc(\')?$" #matches ".ifc" and "ifc'"
    test_files.extend([s.strip("'") for s in args if re.match(file_pattern, s)])

    if not args: # for example, with 'pytest -sv'
        test_files = glob.glob(os.path.join(os.path.dirname(__file__), "files/**/*.ifc"), recursive=True)
    return test_files

@pytest.mark.parametrize("filename", get_test_files())
def test_invocation(filename):
    gherkin_results = list(run(filename))
    base = os.path.basename(filename)

    filtered_results = [result for result in gherkin_results if result.passed_failed != 'passed' and not result.disabled]
    print()
    print(base)
    print()
    print(f"{len(filtered_results)} errors")

    if filtered_results:
        table_data = [
        [
            f"{result.feature.name}/{result.scenario.name}.v{result.feature.version}" if result.passed_failed == 'failed' and result.scenario else f"{result.feature.name}.v{result.feature.version}",
            result.feature.github_source_location,
            result.scenario.latest_step if result.scenario else '',
            result.inst if result.inst is not None else '',
            result.message
        ]
        for result in gherkin_results]
        print(tabulate.tabulate(
            table_data,
            maxcolwidths=[30] * len(table_data),
            tablefmt="simple_grid"
        ))

    if base.startswith("fail-") and not any(result.disabled for result in gherkin_results):
        assert len(filtered_results) > 0
    elif base.startswith("pass-"):
        assert len(filtered_results) == 0

if __name__ == "__main__":
    pytest.main(["-s", __file__])
