import glob
import os
import re
import sys
from pyparsing import Word, Literal, alphas, nums, Combine, StringEnd, ParseException


def collect_test_files(top_order_string = False, insert_args = False):
    """
    Option -> Example
    Test files for a rule -> 'python3 test_main.py alb001'
    Also applies for multiple rules -> 'python3 test_main.py alb001 alb002'
    Test files for a single file -> 'python3 test_main.py <path>.ifc
    Also applies for multiple files -> 'python3 test_main.py <path1>.ifc <path2>.ifc'
    Codes and rules can also be combined -> 'python3 test_main.py alb001 <path>.ifc'
    """

    args = insert_args or [a for a in sys.argv[1:] if not a.startswith('-')]

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

    # Sort the file_paths list to ensure 'pass' entries come before 'fail' entries.
    # This ordering is essential for the automated generation of markdown files.
    if top_order_string:
        test_files = sorted(test_files, key=lambda x: top_order_string not in x)
    return test_files


def check_filename_structure(filename):
    """
    This function checks if the provided filename follows a strict structure:
    1. Starts with 'na', 'pass', or 'fail'.
    2. Followed by a hyphen ('-').
    3. Followed by a combination of three letters and three digits (i.e. the rulecodes).
    4. Followed by another hyphen ('-') and a remainder that may not be strictly validated here.
    
    If any of the rules above are violated, the function will print an error .
    """

    start_keywords = Word("na" + "pass" + "fail")

    hyphen = Literal("-")

    three_letters = Word(alphas, exact=3)
    three_digits = Word(nums, exact=3)
    letters_digits_combination = Combine(three_letters + three_digits)

    remainder = Word(alphas + nums + "_.-")

    filename_structure = (
        (start_keywords + hyphen + letters_digits_combination + hyphen + remainder)
        + StringEnd() 
    )

    try:
        filename_structure.parseString(filename)
    except ParseException as pe:
        print(f"'{filename}' is invalid. Error: {pe}")