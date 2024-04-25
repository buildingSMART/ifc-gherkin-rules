import os
import re
import typing
from pydantic import model_validator, field_validator, Field, ValidationError
from pyparsing import Word, alphas, nums, Literal, Combine, StringEnd, alphanums, ParseException
import pyparsing


from .validation_helper import ValidatorHelper, ParsePattern
from .duplicate_registry import Registry
from .errors import ProtocolError
from .config import ConfiguredBaseModel

from typing import Any, Optional

documentation_src = 'https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features'

def parsed_field(default: Any = ..., *, default_factory: Optional[Any] = None, **extra) -> Any:
    return Field(default, default_factory=default_factory, json_schema_extra={"parsed_value": True, **extra})

class Naming(ConfiguredBaseModel):
    """Parse and validate feature naming conventions.

    Parses a given name according to a specific pattern and validates its rule code.
    """
    name: str

    valid_first_separator: str
    valid_separators: str

    # Parsed values from naming
    rule_code: typing.Optional[dict] = parsed_field(default_factory=dict)
    first_separator: str = parsed_field(" ")
    rule_title: str = parsed_field(" ")
    separators: list = parsed_field(default_factory=list)

    @classmethod
    def get_parsed_value_fields(cls, parsed_name) -> dict:
        return {
            field_name: parsed_name[field_name]
            for field_name, field_info in cls.model_fields.items()
            if getattr(field_info, 'json_schema_extra') and getattr(field_info, 'json_schema_extra').get('parsed_value', False)
        }

    @model_validator(mode='before')
    def parse_name(cls, values) -> dict:
        name = values.get('name')
        if name is None:
            raise ProtocolError(
                value = None,
                message = "The name is required"
            )

        parser = ParsePattern()
        parsed_name = parser.parse_feature_name(name)
        if not parsed_name:
            raise ProtocolError(
                value=name,
                message="Please check: the convention name for the name is: /n\
                    - A functional part (such as 'ALB') /n\
                    - A separator (e.g. a '-') /n\
                    - The rule title (e.g. 'Alignment in spatial structure /n\
                    - In between each single words, there must a separator"
            )
        values.update(cls.get_parsed_value_fields(parsed_name))
        # Rule code - Rule title to check for uniqueness
        # Registry.register_combination(f"{values['rule_code']['functional_part']}{values['rule_code']['number']}", re.sub('[-_.]', ' ', values['rule_title'])) s
        return values

    @field_validator('rule_code')
    def validate_rule_code(cls, value) -> dict:
        """ The rule code is made of 3 digits capital letters (taken from the list of Functional parts)
        + 3 digit numbers 
        e.g. 'ALB123', 'GEM391' and not 'AB14' or 'GKE9001'
        """
        validator_helper = ValidatorHelper()
        validation = validator_helper.validate_rule_code(value)
        if validation:
            raise ProtocolError(
                value=validation['value'],
                message=validation['message']
            )
        return value

    @field_validator('first_separator')
    def validate_first_separator(cls, value, values):
        valid_first_separator = values.data['valid_first_separator']
        if value != valid_first_separator:
            raise ProtocolError(
                value=value,
                message=f"expected separator {valid_first_separator} but instead found {value}"
            )
        return value, values

    @field_validator('separators')
    def validate_separators(cls, value, values):
        separators = value
        valid_separators = values.data['valid_separators']
        unvalid_separators = [separator for separator in separators if separator != valid_separators]
        if any(unvalid_separators):
            raise ProtocolError(
                value = separators,
                message = f"expected {valid_separators} but found the following unvalid seperators {unvalid_separators} for name {values.data['name']}"
            )
        return value, values


class RuleCreationConventions(ConfiguredBaseModel):
    """Validate feature conventions
    """
    feature: Naming  #  # e.g. 'ALB001 - Alignment in spatial structure
    feature_filename: Naming  # e.g. 'ALB001_Alignment-in-spatial-structure.feature'
    ifc_input: dict
    tags: list
    description: str
    steps: list
    filename: str
    readme: str

    @field_validator('feature_filename')
    def validate_feature_names(cls, value, values):
        def parse_f_names(f: str) -> str:
            return re.sub(r'[^a-zA-Z0-9\s]', '', f.split('.')[0]).lower().replace(' ', '')
        feature_filename = value.name # as in the .feature file
        feature_name = values.data['feature'].name # name after 'Feature' within the .feature file
        if parse_f_names(feature_name) != parse_f_names(feature_filename):
            raise ProtocolError(
                value = feature_name,
                message = f"Feature name {feature_name} and feature filename {feature_filename} should be the same"
            )

    @field_validator('tags')
    def do_validate_tags(cls, value) -> dict:
        validator = ValidatorHelper()
        validated_tags = validator.validate_tags(value)
        if validated_tags != 'passed':
            raise ProtocolError(
                value=validated_tags['value'],
                message=validated_tags['message']
            )
        return value

    @field_validator('ifc_input')
    def validate_ifc_input(cls, value):
        # @todo implement
        pass

    @field_validator('description')
    def validate_description(cls, value=list) -> list:
        """must include a description of the rule that start with "The rule verifies that..."""  # allow for comma's
        if not any(value.startswith(f"{prefix} rule verifies{optional_comma} that") for prefix in ("This", "The") for optional_comma in ("", ",")):
            raise ProtocolError(
                value=value,
                message=f"The description must start with 'The rule verifies that', it now starts with {value}"
            )
        return value

    @field_validator('steps')
    def validate_steps(cls, value):
        """Check only correct keywords are applied: 'Given', 'Then', 'And'"""
        if not all(d['keyword'] in ['Given', 'Then', 'And'] for d in value):
            raise ProtocolError(
                value=value,
                message=f"The expected keywords used in the feature file are 'Given', 'Then' and 'And'. Now {[d['keyword'] for d in value]} are used."
            )

        """Check that no punctuation at the end of the step"""
        if any(d['name'].endswith(tuple(r"""!#$%&(*+,-./:;<=>?@[\]^_`{|}~""")) for d in value):
            raise ProtocolError(
                value=value,
                message=f"The feature steps must not end with punctuation. Now the steps end with {[d['name'][-1] for d in value]}."
            )

        """Check that 'shall' is not used"""
        if any('shall' in d['name'].lower() for d in value):
            raise ProtocolError(
                value=value,
                message=f"The feature steps must not use the word 'shall', use 'must' instead."
            )

        """Check double spaces are not used"""
        if any('  ' in d['name'] for d in value):
            raise ProtocolError(
                value=value,
                message=f"Double spaces are not to be used in the step definition"
            )

    @field_validator('filename')
    def validate_test_filename(cls, value):

        normalized_path = os.path.normpath(value)
        """Check if test file is located in the ifc-gherkin-rules\\test\\files directory"""
        if not (('ifc-gherkin-rules\\test\\files\\' in normalized_path) or ('ifc-gherkin-rules/test/files/' in normalized_path)):
            raise ProtocolError(
                value=value,
                message=f"The test files are to be placed in the ifc-gherkin-rules/test/files/ directory. Currently it's placed: {normalized_path}"
            )

        """Check if path rule folder is using the valid rule directory name"""
        rule_folder = normalized_path.split(os.sep)[-2]
        if not re.match(r'^[a-z]{3}\d{3}$', rule_folder):
            raise ProtocolError(
                value=value,
                message=f"The rule directory is supposed to be a valid rule code name, but is {rule_folder} instead"
            )

        ifc_path = os.path.basename(value)
        result, rule, *rest = ifc_path.split('-') # result is either pass or fail

        

        """Check if test file start with pass or fail"""
        if result not in ('pass', 'fail'):
            raise ProtocolError(
                value=value,
                message=f"Name of the result file must start with 'pass' or 'fail'. In that case name starts with: {result}"
            )

        """Check if a second part of the test file is a rule code"""
        if not re.match(r'^[a-z]{3}\d{3}$', rule):
            raise ProtocolError(
                value=value,
                message=f"The second part of the test file name must be a valid rule code. In that case it's: {rule}"
            )
        
        """
        Naming convention for unit test files files
        Unit test files must follow this naming convention

        Expected result-rule code-rule scenario-short_informative_description`.ifc

        Or in case where a rule has no scenarios
        `Expected result`-`rule code`-`short_informative_description`.ifc

        Examples

        pass-alb001-short_informative_description.ifc
        fail-alb001-scenario01-short_informative_description.ifc
        fail-alb001-short_informative_description.ifc
        
        """
        ifc_path_errors = validate_ifc_path(ifc_path)
        if ifc_path_errors:
            if ifc_path != ifc_path_errors:
                os.rename(normalized_path, os.path.join(os.path.dirname(normalized_path), ifc_path_errors))
                msg = f"Error in the ifc file name: {ifc_path}. File name has been corrected to {ifc_path_errors}"
            else:
                msg = f"Error in the ifc file name: {ifc_path}"
                raise ProtocolError(
                    value=value,
                    message = msg
                )

    # @field_validator('readme')
    # def validate_readme_presence(cls, value):
    #     """Check if readme file is located in test file directory"""
    #     # normalized_path = os.path.normpath(value)
    #     # test_file_directory = os.path.dirname(normalized_path)
    #     # readme_path = os.path.join(test_file_directory, 'readme.md')
    #     if not os.path.exists(os.path.join(os.path.dirname(__file__), 'readme.md')):
    #         raise ProtocolError(
    #             value=value,
    #             message=f"README.ME file not found in the test file directory"
    #         )
        
def correct_character_use(file_name):
    """
    Corrects the use of '-' and '_' in the file name according to the rules.
    """
    parts = file_name.split('-')
    if len(parts) > 2:  # Expected format with scenario
        rule_code_and_scenario = '-'.join(parts[:3])  # Keep the first 3 parts intact
        description_parts = '-'.join(parts[3:]).split('_')  # Split the rest for correction
        corrected_description = '_'.join(description_parts)
        corrected_file_name = rule_code_and_scenario + '-' + corrected_description
    else:
        corrected_file_name = file_name.replace('_', '-')
    return corrected_file_name


def validate_ifc_path(file_name):
    expectedResult = Literal("pass") | Literal("fail")
    ruleCode = Combine(Word(alphas, exact=3) + Word(nums, exact=3))
    scenario = pyparsing.Optional(Literal("-") + Literal("scenario") + Word(nums, exact=2))
    description = Combine(Word(alphanums + "_+") + Literal(".ifc"))
    
    fileNameGrammar = expectedResult + Literal("-") + ruleCode + scenario + Literal("-") + description + StringEnd()
    

    attempts = 0
    max_attempts = 10 
    opposites = {'-': '_', '_': '-'}
    while attempts < max_attempts:
        try:
            fileNameGrammar.parseString(file_name)
        except ParseException as pe:
            if pe.loc < len(file_name) and file_name[pe.loc] in ['-', '_']:
                file_name = file_name[:pe.loc] + opposites.get(file_name[pe.loc]) + file_name[pe.loc+1:]
            else:
                return file_name
        attempts += 1

    pass


def enforce(convention_attrs : dict = {}, testing_attrs : dict = {}):
    """Main function to validate feature and tagging conventions.

    This function creates and validates a `RuleCreationConventions` instance based on the provided parameters. e
    It can work in a testing mode when a testing dictionary is provided.
    """
    attrs = convention_attrs or testing_attrs

    feature_obj = {
        'feature': {
            'name': attrs['feature_name'],  # e.g. 'ALB001 - Alignment in spatial structure
            'valid_first_separator': '-',
            'valid_separators': ' '
        },
        'feature_filename': {
            # e.g. 'ALB001_Alignment-in-spatial-structure.feature'
            'name': attrs['feature_filename'],
            'valid_first_separator': '_',
            'valid_separators': '-'
        },
        'ifc_input': {
            # if testfile : 'fail-alb001-scenario01-contained_relation_not_directed_to_ifcsite.ifc'
            'name': attrs['ifc_filename'],
            'valid_separators': '-'
        },
        'tags': list(attrs['tags']),
        'description': attrs['description'],
        'steps': attrs['steps'],
        'filename': attrs['filename'], # e.g. ifc-gherkin-rules\test\files\alb002\pass-alb002-generated_file.ifc
        'readme': attrs['filename'],  # e.g. ifc-gherkin-rules\test\files\alb002\pass-alb002-generated_file.ifc
    }

    try:
        RuleCreationConventions(**feature_obj)
    except ValidationError as convention_errors:
        print(convention_errors.json())
        for error in convention_errors.errors():
            yield error.get('msg')