import os
import glob
import sys
import re
import pandas as pd

import pytest
import tabulate

try:
    from ..main import run
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run

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

def handle_testfile_markdown(results, base):
    """
    Usage:
    ------
    To generate markdown files:
        python3 test_main.py --generate-markdown

    To combine markdown generation with testing for a specific rule code:
        python3 test_main.py --generate-markdown grf001

    Explanation:
    ------------
    The '--generate-markdown' flag tells the script to create markdown files based on the tests.

    The 'grf001' in the second example represents a specific rule code. You can replace it with any valid rule code to test.

    The markdown generation process will take into account the specified rule code, if provided.
    """
    rule_code = re.search(r'(fail|pass)-([a-z]{3}[0-9]{3})-', base).group(2)
    readme_path = os.path.join(os.path.dirname(
        __file__), f'files/{rule_code}/README.md')
    markdown_result_testfile = {
                    "File name" : base,
                    "Expected result" : "pass" if base.startswith("pass-") else "fail",
                    "Error" : results[0][4] if results else " ",
                    "Description": " "
                }
    
    if os.path.exists(readme_path) and os.path.getsize(readme_path) > 0:
        with open(readme_path, 'r+') as file:
            content = file.read()
            lines = [line.strip() for line in content.split("\n")]
            headers = [header.strip()for header in lines[0].split("|") if header.strip()]

            data = {header: [] for header in headers}
            # Parse each line and populate the data lists
            for line in lines[2:]:
                values = [value.strip() if value.strip() != '' else ' ' for value in line.split("|")][1:]
                for header, value in zip(headers, values):
                    data[header].append(value)

            df = pd.DataFrame(data)
            if base not in df['File name'].values:
                df.loc[len(df)] = markdown_result_testfile
                file.seek(0)
                file.write(df.to_markdown(index=False))
    else:
        with open(readme_path, 'w') as file:
            file.write(pd.DataFrame([markdown_result_testfile]).to_markdown(index=False))


@pytest.mark.parametrize("filename", get_test_files())
def test_invocation(filename):
    results = list(run(filename))
    base = os.path.basename(filename)

    if '--generate-markdown' in sys.argv:
        handle_testfile_markdown(results, base)

    # if base.startswith("pass-"):
    results = [result for result in results if result[4] != 'Rule disabled']
    results = [result for result in results if 'Rule passed' not in result[4]]
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
    if base.startswith("fail-"):
        assert len(results) > 0
    elif base.startswith("pass-"):
        assert len(results) == 0

if __name__ == "__main__":
    pytest.main(["-s", __file__])
