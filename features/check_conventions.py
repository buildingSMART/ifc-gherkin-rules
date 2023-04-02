import re
import typing

from dataclasses import dataclass, field

from pyparsing import Word, alphas, nums, Group, OneOrMore, And


documentation_src = 'https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features'

"""
Checks whether conventions of creating rules in documentations are met : https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features

- The file name is rule code_rule title
- The rule code is made of 3 digits capital letters (taken from the list of Functional parts) + 3 digits number
- The rule title must have no space and must use - as separator
- The naming convention for the Feature in the is the following: rule code - rule title (the same used for the file name). For the rule title blank spaces must be used instead of -
- The rule code, and rule title, must be unique
"""


def get_separators(s):
    return [' ' if char == ' ' else char for char in s if char in ['-', '.', '_'] or char == ' ']

def parse_pattern():
    rule_code = Group(Word(alphas, exact=3)('category') + Word(nums, exact=3)('number'))('rule_code')
    special_character = Word("-_.", exact=1)('special_character')
    rule_title = OneOrMore(Word(alphas + '-. '))('rule_title').setParseAction(lambda i: i[0].replace('.feature', ''))
    return rule_code + special_character + rule_title

@dataclass 
class NameValidator:
    source : str
    name : str
    validated_items_list: typing.ClassVar[typing.Sequence[typing.Any]] = []
    documentation_statement : str = field(default=f'Further information can be found at {documentation_src}')
    parse_pattern : And = field(default_factory=parse_pattern)

    def parse(self):
        self.parsed = self.parse_pattern.parseString(self.source)
        self.code = self.parsed.rule_code.category + self.parsed.rule_code.number
        self.first_seperator = self.parsed.special_character
        self.rule_title = self.parsed.rule_title
        self.seperators = get_separators(self.rule_title)

        NameValidator.update_validated_items_list(self)
    
    def self_validation(self, valid_first_seperator, valid_seperator):
        code_pattern = re.compile(r'^[A-Z]{3}\d{3}$')
        assert code_pattern.match(self.code), f"{self.code} is not a valid rule code."

        # Check separator between rule code and rule title
        assert self.first_seperator == valid_first_seperator, f"The standard format for {self.name}s is to use the pattern 'code{valid_first_seperator} \
                                                                rule title' with the symbol ({valid_first_seperator}) as the separator.\
                                                                {self.documentation_statement} "
        
        # Check seperators within rule title
        assert not any(sym in self.seperators for sym in list(filter(lambda x: x != valid_seperator, ['-', '.', '_']))), f"The rule {self.code} title can only contain the symbol '{valid_seperator}' as the separator. \
        {self.documentation_statement}"

        # after internal validating, remove seperator for the purpose of further validation
        self.rule_title = self.rule_title.replace(valid_seperator, '').lower()

    def compatibility_check(self, other):
        assert self.code == other.code, f"Please ensure that the code used in the {self.name} matches the code used in the {other.name}. \
                                         {self.documentation_statement}"
        assert self.rule_title == other.rule_title, f"For rule {self.code}, the rule title in the {self.name} does not match the one in the {other.name}. \
                                                      {self.documentation_statement}"

    @classmethod
    def update_validated_items_list(cls, validated_item):
        assert validated_item not in cls.validated_items_list, f'Either the code or title of {validated_item.code} is not unique. Please verify. {validated_item.documentation_statement}'
        cls.validated_items_list.append(validated_item)
        return cls.validated_items_list
    
    def __eq__(self, other):
        #'The rule code, and rule title, must be unique'
        return ((self.code, self.rule_title.lower()) == (other.code, other.rule_title.lower()))
    
    def __hash__(self):
        return hash((self.code, self.rule_title.lower()))
    
def validate(filename, feature_name, context):
    file, feature = NameValidator(filename, 'file name'), NameValidator(feature_name, 'feature name')
    file.parse(), feature.parse()
    file.self_validation('_', '-'), feature.self_validation('-', ' ')
    NameValidator.compatibility_check(file, feature)