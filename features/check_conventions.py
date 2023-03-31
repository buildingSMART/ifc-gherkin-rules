from pyparsing import Word, alphas, nums, Group, OneOrMore
import pyparsing
import re
from dataclasses import dataclass, field

documentation_src = 'https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features'

"""
Checks whether conventions of creating rules in documentations are met : https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features

- The file name is rule code_rule title
- The rule code is made of 3 digits capital letters (taken from the list of Functional parts) + 3 digits number
- The rule title shall have no space and shall use - as separator
- The naming convention for the Feature in the is the following: rule code - rule title (the same used for the file name). For the rule title blank spaces must be used instead of -

"""

def get_seperators(s):
    return [' ' if char == ' ' else char for char in s if char in ['-', '.', '_'] or char == ' ']

def parse_pattern():
    rule_code = Group(Word(alphas, exact=3)('category') + Word(nums, exact=3)('number'))('rule_code')
    special_character = Word("-_.", exact=1)('special_character')
    description = OneOrMore(Word(alphas + '-. '))('description').setParseAction(lambda i: i[0].replace('.feature', ''))
    return rule_code + special_character + description

@dataclass 
class NameValidator:
    source : str
    name : str
    documentation_statement : str = field(default=f'Further information can be found at {documentation_src}')
    parse_pattern : pyparsing.And = field(default_factory=parse_pattern)

    def parse(self):
        self.parsed = self.parse_pattern.parseString(self.source)
        self.code = self.parsed.rule_code.category + self.parsed.rule_code.number
        self.first_seperator = self.parsed.special_character
        self.description = self.parsed.description
        self.seperators = get_seperators(self.description)
    
    def self_validation(self, valid_first_seperator, valid_seperator):
        code_pattern = re.compile(r'^[A-Z]{3}\d{3}$')
        assert code_pattern.match(self.code), f"{self.code} is not a valid rule code."
        assert self.first_seperator == valid_first_seperator, f"The standard format for {self.name}s is to use the pattern 'code{valid_first_seperator} \
                                                                rule title' with the symbol ({valid_first_seperator}) as the separator.\
                                                                {self.documentation_statement} "
        assert not any(sym in self.seperators for sym in list(filter(lambda x: x != valid_seperator, ['-', '.', '_'])))
        self.description = self.description.replace(valid_seperator, '').lower() # after internal validating, remove seperator for the purpose of external validation

    def compatibility_check(self, other):
        assert self.code == other.code, f"Please ensure that the code used in the {self.name} matches the code used in the {other.name}. \
                                         {self.documentation_statement}"
        assert self.description == other.description, f"For rule {self.code}, the description in the {self.name} does not match the one in the {other.name}. \
                                                      {self.documentation_statement}"

    def __eq__(self, other):
        'The rule code, and rule title, must be unique'
        #@todo gh -> actually implement check for uniqueness. Do we use the context or database to save it globally?
        return ((self.code, self.description.lower()) == (other.code, other.description.lower()))
    
    def __hash__(self, other):
        return hash((self.code, self.description.lower()))
    
def validate(filename, feature_name, context):
    file, feature = NameValidator(filename, 'file name'), NameValidator(feature_name, 'feature name')
    file.parse(), feature.parse()
    file.self_validation('_', '-'), feature.self_validation('-', ' ')
    NameValidator.compatibility_check(file, feature)
