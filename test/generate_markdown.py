import os
import re
import pandas as pd
from typing import NewType
import sys
import argparse

try:
    from ..main import run, ExecutionMode, do_try
    from .utils import collect_test_files
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import run, ExecutionMode, do_try
    from test.utils import collect_test_files


MarkdownTableStr = NewType('MarkdownTableStr', str)

def handle_markdown_table(markdown_table: MarkdownTableStr) -> pd.DataFrame:
    """
    Handling in case the already existing file is in non-html markdown format
    """
    lines = [line.strip() for line in markdown_table.split("\n")]
    headers = [header.strip()for header in lines[0].split("|") if header.strip()]

    data = {header: [] for header in headers}
    for line in lines[2:]:
        values = [value.strip() if value.strip() != '' else ' ' for value in line.split("|")][1:]
        for header, value in zip(headers, values):
            data[header].append(value)
    return pd.DataFrame(data)


def rearrange_column(df: pd.DataFrame, column_to_move: str, relative_column: str, place_before=True) -> pd.DataFrame:
    """
    Move a column in the dataframe before or after another column.
    """
    cols = df.columns.tolist()

    if column_to_move in cols:
        cols.remove(column_to_move)
        idx = cols.index(relative_column) + (not place_before)
        cols.insert(idx, column_to_move)

    return df[cols]

def update_html_markdown(df: pd.DataFrame, content_testfile: dict) -> pd.DataFrame:
    drop_unnamed = df.columns[df.columns.str.contains('Unnamed')]
    df.drop(drop_unnamed, axis=1, inplace=True) # remove index being rendered as new column
    df.loc[len(df)] = content_testfile
    df = df.sort_values(by='Expected result', ascending=False)
    mask = df.index.duplicated(keep=False)

    return rearrange_column(df = df, column_to_move="Error no.", relative_column="Error", place_before=True)


def generate(file_desc_list = False, testfile_filter = False):
    """
    Usage:
    ------
    Combine with a rule_code: 
        python3 generate_markdown.py sys001
    To combine markdown generation with custom descriptions:
        python3 generate_markdown.py alb002 --file-desc 'testfile1.ifc' 'this is a sample file' --file-desc 'testfile2.ifc' 'this is another sample file'
    
    "The value provided with the --file-desc argument will populate the 'Description' column in the markdown (converted to HTML) table."
    "The script allows specification of designated parameters for a particular rule_code or a distinct filename.
    The etnries will be integrated into the pre-existing table. For example, the following command can be used:
    python3 generate_markdown.py 'testfile_new.ifc' --file-desc 'testfile_new' 'This is a new testfile'"
    """
    test_files = collect_test_files(top_order_string='pass', insert_args=testfile_filter) 
    file_desc_dict = {}
    if file_desc_list:
        for fd in file_desc_list:
            file_desc_dict[fd[0]] = fd[1]

    for filename in test_files:
        results = list(run(filename, execution_mode=ExecutionMode.TESTING))
        base = os.path.basename(filename)
        rule_code = re.search(r'(fail|pass)-([a-z]{3}[0-9]{3})-', base).group(2)
        readme_path = os.path.join(os.path.dirname(__file__), 'files', rule_code, 'README.md')


        description = file_desc_dict.get(base, " NA / Automatically generated markdown ")

        if not description == " NA / Automatically generated markdown ":
            pass

        behave_output_patterns = {
            'Instance_id': r"Instance_id=(\d+)",
            'Expected': r"Expected=({.*?})",
            'Observed': r"Observed=({.*?})"
        }


        def extract_value(pattern, text):
            """ Utility function to apply regex search and return the matching group. """
            match = re.search(pattern, text)
            return match.group(1) if match else ''
        
        def get_parsed_behave_output(results):
            formatted_results = []
            for e, result in enumerate(results):
                extracted_values = {key: extract_value(pattern, result[4][1]) for key, pattern in behave_output_patterns.items()}  
                result_str = f"Result {e+1}: {extracted_values}"
                formatted_results.append(result_str)

            return str(" . ".join(formatted_results))
        

        content_testfile = {
                        "File name" : base,
                        "Expected result" : "pass" if base.startswith("pass-") else "fail",
                        "Description": do_try(lambda: get_parsed_behave_output(results), "NA / Automatically generated markdown")
                    }

        if os.path.exists(readme_path) and os.path.getsize(readme_path) > 0:
            with open(readme_path, 'r+') as file:
                content = file.read()
                file.seek(0)

                markdown_table_pattern = re.compile(r'\|.*?\|\n\|[-:]+\|[-:]+', re.DOTALL)
                has_markdown_table = bool(markdown_table_pattern.search(content))

                html_table_pattern = re.compile(r'<table.*?>.*?</table>', re.DOTALL)
                has_html_table = bool(html_table_pattern.search(content))

                if has_markdown_table:
                    df = handle_markdown_table(content)
                elif has_html_table:
                    df = pd.read_html(content)[0]
                else:
                    raise ValueError(f"The file '{readme_path}' does not contain a recognized HTML or Markdown table. Please ensure the file adheres to the expected format.")

                if base not in df['File name'].values:
                    df = update_html_markdown(df, content_testfile)

                    file.write(df.to_html(index=False))
                else: # check for an updated description
                    description_in_df = df[df['File name'] == base]['Description'].values[0]
                    if description != description_in_df:
                        df.loc[df['File name'] == base, 'Description'] = description
                        file.write(df.to_html(index=False))
                        print('readme for rule code {rule_code} has been updated')
        else: # create new README.md markdown file
            with open(readme_path, 'w') as file:
                assert base.startswith('pass-'), f'file must contain at least one file that passes the rule {rule_code}'
                file.write(pd.DataFrame([content_testfile]).to_html(index=False))
                print(f'readme for rule code {rule_code} has been created')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description about your script")
    parser.add_argument('testfile_filter', nargs='*', help="All arguments before --file-desc")
    parser.add_argument('--file-desc', nargs=2, action='append', help="File and its description")

    args = parser.parse_args()

    generate(args.file_desc, args.testfile_filter)