import os
import sys

import re
from pyparsing import Word, alphas, nums, Group, OneOrMore
from .utils import replace_substrings

try:
    from ...features.steps.utils import system
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '...'))
    from features.steps.utils import system

class ValidatorHelper():
    """
    Perform various types of validations.
    Provides methods for performing various validation tasks such as validating functional parts and rule codes, and checking tags.
    """

    def __init__(self):
        """
        Get list of valid functional parts. 
        For example, can be used to validate the rule code or check the validity of a present tag
        """
        self.filename_functional_parts = system.get_abs_path(
            f"resources/**/functional_parts.csv")
        self.valid_functional_parts = [item.lower() for sublist in system.get_csv(
            self.filename_functional_parts) for item in sublist]

    def valid_functional_part(self, functional_part):
        if functional_part.lower() not in self.valid_functional_parts:
            return {
                'value': self.rule_code,
                'message': f"{self.rule_code} not in list of functional parts, please check /n\
                https://github.com/buildingSMART/ifc-gherkin-rules/blob/main/features/Functional-parts.md"
            }
        return None

    def validate_rule_code(self, code) -> dict:
        "- The rule code is made of 3 digits capital letters (taken from the list of Functional parts) + 3 digits number"
        self.rule_code = code['functional_part'] + code['number']

        # Rule code pattern check
        valid_pattern = re.compile(r'^[A-Z]{3}\d{3}$')
        if not valid_pattern.match(self.rule_code):
            return {
                'value': self.rule_code,
                'message': f"rule code '{self.rule_code}' must consist of three digital capital letters plus three digit numbers"
            }
        # Functional part validity check
        return self.valid_functional_part(code['functional_part'])

    def validate_tags(self, tags):
        if (rule_type_tags := [t for t in tags if t.lower() in ['implementer-agreement', 'informal-proposition', 'industry-practice', 'critical']]) and len(rule_type_tags) > 1: 
            return { 
                'value': rule_type_tags, 
                'message' : "The tags must contain only one tag with a reference to the rule type: normative (ia ip), industry-practice and critical"
            }
        functional_part_tags = [tag for tag in tags if tag.isalpha() and len(tag) == 3 and tag.isupper()]
        if not any(value.lower() in self.valid_functional_parts for value in functional_part_tags):
            current_tags = ''.join(functional_part_tags)
            return {
                'value': current_tags,
                'message': 'The tags must contain one tag with a reference to a valid functional part'
            }
        return 'passed'
    
    
class ParsePattern():
    """Define and parse a feature name pattern.

    Defines a rule for parsing the name of a feature and provides a method to perform the parsing.
    """

    def __init__(self):
        self.rule_code = Group(Word(alphas, exact=3)(
            'functional_part') + Word(nums, exact=3)('number'))('rule_code')
        self.special_character = Word("-_.", exact=1)('special_character')
        # self.rule_title = OneOrMore(Word(
        #     alphas + '-. '))('rule_title').setParseAction(lambda i: i[0].replace('.feature', ''))
        self.rule_title = OneOrMore(Word(alphas + '-._ '))('rule_title').setParseAction(lambda i: replace_substrings(i[0]))


    def parse_feature_name(self, name) -> dict:
        """
        This function breaks down and analyzes the structure of a naming. 

        First, it defines a pattern to parse the feature name, which is a combination of 'rule code', a 'special character', and the 'rule title'.
        Next, it uses this pattern to break down the provided feature name into its component parts.

        After successfully parsing the name, the function then extracts and returns these parts in a dictionary. The dictionary includes:

        - 'rule_code': It is further divided into 'functional_part' and 'number'.
        - 'first_separator': The first special character that appears in the feature name.
        - 'rule_title': The main title of the feature.
        - 'separators': A list of all separators that appear in the rule title. These can be a space, hyphen, period, or underscore.
        """

        self.feature_name_pattern = self.rule_code + \
            self.special_character + self.rule_title
        try:
            self.feature_name_parsed = self.feature_name_pattern.parseString(name)
        except:
            pass
        try:
            return {
                'rule_code': {
                    'functional_part': self.feature_name_parsed.rule_code.functional_part,
                    'number': self.feature_name_parsed.rule_code.number
                },
                'first_separator': self.feature_name_parsed.special_character,
                'rule_title': self.feature_name_parsed.rule_title,
                'separators': [' ' if char == ' ' else char for char in self.feature_name_parsed.rule_title if char in ['-', '.', '_'] or char == ' ']
            }
        except:
            return {}
