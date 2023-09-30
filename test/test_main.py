import os
import glob
import sys
import re

import pytest
import tabulate

try:
    from ..main import run
    from ..test.rule_creation_protocol import protocol
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run
    from test.rule_creation_protocol import protocol

rule_code_pattern = re.compile(r"^[a-zA-Z]{3}\d{3}$")
rule_codes = list(filter(lambda arg: rule_code_pattern.match(arg), sys.argv[1:]))

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
        test_files.extend(paths)

    file_pattern =  r".*\.ifc(\')?$" #matches ".ifc" and "ifc'"
    test_files.extend([s.strip("'") for s in args if re.match(file_pattern, s)])

    if not args: # for example, with 'pytest -sv'
        test_files = glob.glob(os.path.join(os.path.dirname(__file__), "files/**/*.ifc"), recursive=True)
    return test_files



@pytest.mark.parametrize("filename", get_test_files())
def test_invocation(request, filename):

    def step_attrs_to_file(*attrs): 
        def get_nested_item(d, keys):
            for key in keys:
                d = d.get(key, {})
            return d
        return list({get_nested_item(item, attrs) for item in behave_results})[0]

    behave_results = list(run(filename))
    base = os.path.basename(filename)
    results = [
        result['display_testresult']
        for result in behave_results
        if result['display_testresult'][4] != 'Rule disabled' and 'Rule passed' not in result['display_testresult'][4]
    ]
    print()
    print(base)
    print()
    print(f"{len(results)} errors")
    if results:
        print(tabulate.tabulate(
            [[c or '' for c in r] for r in results],
            maxcolwidths=[30] * len(results[0]),
            tablefmt="simple_grid"
        ))

    if '--validate-dev' in sys.argv or request.config.getoption("--validate-dev"):
        try:
            protocol.enforce(convention_attrs={
                'ifc_filename' : base,
                'feature_name' : step_attrs_to_file('convention_check_attrs', 'feature_name'),
                'feature_file' : step_attrs_to_file('convention_check_attrs', 'feature_file'),
                'description' :step_attrs_to_file('convention_check_attrs', 'description'),
                'tags': [item['convention_check_attrs']['tags'] for item in behave_results][0]
            })
        except IndexError:
            pass #@todo check for 'pass' testfiles that don't have any results. For instance 'pass-alb005-IfcReferent-NOTDEFINED_with_position.ifc'

    if base.startswith("fail-"):
        assert len(results) > 0
    elif base.startswith("pass-"):
        assert len(results) == 0

if __name__ == "__main__":
    pytest.main(["-s", __file__])
