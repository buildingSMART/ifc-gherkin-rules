import pandas as pd
import glob
import csv
import re
import ast

for fn in glob.glob('**/pset_definitions.csv', recursive=True):
    def check_whitespaces_in_string(s):
        if re.search(r'\s', s):
            return True
        return False

    def check_whitespace(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                check_whitespace(key, f"{path}.{key} (key)" if path else f"{key} (key)")
                check_whitespace(value, f"{path}.{key}" if path else key)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                check_whitespace(item, f"{path}[{index}]")
        else:
            if isinstance(data, str) and check_whitespaces_in_string(data):
                print(f"Whitespace found in {path}: '{data}'")

    def safe_eval(expr):
        try:
            return ast.literal_eval(expr)
        except (ValueError, SyntaxError):
            return expr

    with open(fn, 'r') as file:
        reader = csv.DictReader(file)
        for row_num, row in enumerate(reader):
            for key, value in row.items():
                parsed_value = safe_eval(value) 
                check_whitespace(parsed_value, f"row[{row_num + 1}].{key}")

