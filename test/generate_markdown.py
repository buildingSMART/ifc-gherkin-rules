import os
import re
import pandas as pd
import sys

try:
    from ..main import run
    from .utils import collect_test_files
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run
    from test.utils import collect_test_files

def generate():
    """
    Usage:
    ------
    To combine markdown generation with testing for a specific rule code:
        python3 generate_markdown.py grf001

    Explanation:
    ------------
    The '--generate-markdown' flag tells the script to create markdown files based on the tests.

    The 'grf001' in the second example represents a specific rule code. You can replace it with any valid rule code to test.

    The markdown generation process will take into account the specified rule code, if provided.
    """
    test_files = collect_test_files()
    for filename in test_files:
        results = list(run(filename))
        base = os.path.basename(filename)
        rule_code = re.search(r'(fail|pass)-([a-z]{3}[0-9]{3})-', base).group(2)
        readme_path = os.path.join(os.path.dirname(
            __file__), f'files/{rule_code}/README.md')
        
        def errors_to_markdown(errors):
            markdown_errors = ','.join([error[4] for error in errors if not error[4] == "Rule passed"])
            markdown_errors = markdown_errors.replace('(', '').replace(')', '') # avoid default markdown handling of '(' and ')' symbols
            return markdown_errors

        
        markdown_result_testfile = {
                        "File name" : base,
                        "Expected result" : "pass" if base.startswith("pass-") else "fail",
                        "Error" : "Rules passed" if base.startswith("pass-") else errors_to_markdown(results),
                        "Description": " NA / Automatically generated markdown "
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
                    df = df.sort_values(by='Expected result', ascending=False)
                    file.seek(0)
                    file.write(df.to_markdown(index=False))
        else:
            with open(readme_path, 'w') as file:
                file.write(pd.DataFrame([markdown_result_testfile]).to_markdown(index=False))

if __name__ == "__main__":
    generate()
