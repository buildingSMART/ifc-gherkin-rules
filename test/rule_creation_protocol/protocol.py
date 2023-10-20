import os
import re
import typing
from pydantic import BaseModel, model_validator, field_validator, Field, conlist

from .validation_helper import ValidatorHelper, ParsePattern
from .duplicate_registry import Registry
from .errors import ProtocolError
from .utils import replace_substrings
from .config import ConfiguredBaseModel

documentation_src = 'https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features'

class Naming(ConfiguredBaseModel):
    """Parse and validate feature naming conventions.

    Parses a given name according to a specific pattern and validates its rule code.
    """
    name: str

    valid_first_separator: str
    valid_separators: str

    # Parsed values from naming
    rule_code: typing.Optional[dict] = Field(default_factory=dict, parsed_value=True)
    first_separator: str = Field(" ", parsed_value=True)
    rule_title: str = Field(" ", parsed_value=True)
    separators: typing.Optional[list] = Field(default_factory=list, parsed_value=True)

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
            raise ValueError('Name is required')

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
                message = f"expected {valid_separators} but found the following unvalid seperators {unvalid_separators}"
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
        if any(d['name'].endswith(tuple(r"""!#$%&()*+,-./:;<=>?@[\]^_`{|}~""")) for d in value):
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
        rule_folder = normalized_path.split('\\')[-2]
        if not re.match(r'^[a-z]{3}\d{3}$', rule_folder):
            raise ProtocolError(
                value=value,
                message=f"The rule directory is supposed to be a valid rule code name, but is {rule_folder} instead"
            )

        file_path = os.path.basename(value)
        result, rule, *rest = file_path.split('-')
        if len(rest) == 1:
            rest = rest[0]
            scenario = ''
        elif len(rest) == 2:
            scenario, rest = rest
        else:
            raise ProtocolError(
                value=value,
                message=f"Test file {value} does not fit the naming convention. Expected two '-' separators for pass file and three for fail file. Got {len(file_path.split('-')) - 1} instead"
            )

        rest, extension = rest.split('.')

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

        """Check if scenario is found in the third part of the test file (for fail files)"""
        if scenario and not re.match(r'^scenario\d{2}$', scenario):
            raise ProtocolError(
                value=value,
                message=f"The third part of the fail test file name must be a valid scenario number. In that case it's: {scenario}"
            )

        """Check if the only separator used in the file description is underscore"""
        separators = [match.group(0) for match in re.finditer(r'[^a-zA-Z0-9]+', rest)]
        if any(separator != '_' for separator in separators):
            raise ProtocolError(
                value=value,
                message=f"The expected separator in the short_informative_description of the test file name is _. For file {value} found {separators}"
            )

        """Check if extension is ifc"""
        if extension.lower() != 'ifc':
            raise ProtocolError(
                value=value,
                message=f"The expected test file extension is .ifc, found: {extension} instead"
            )

    @field_validator('readme')
    def validate_readme_presence(cls, value):
        """Check if readme file is located in test file directory"""
        normalized_path = os.path.normpath(value)
        test_file_directory = os.path.dirname(normalized_path)
        readme_path = os.path.join(test_file_directory, 'readme.md')
        if not os.path.exists(readme_path):
            raise ProtocolError(
                value=value,
                message=f"README.ME file not found in the test file directory: {readme_path}"
            )

def enforce(convention_attrs : dict = {}, testing_attrs : dict = {}) -> bool:
    """Main function to validate feature and tagging conventions.

    This function creates and validates a `RuleCreationConventions` instance based on the provided parameters. 
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
        'tags': attrs['tags'],
        'description': attrs['description'],
        'steps': attrs['steps'],
        'filename': attrs['filename'], # e.g. ifc-gherkin-rules\test\files\alb002\pass-alb002-generated_file.ifc
        'readme': attrs['filename'],  # e.g. ifc-gherkin-rules\test\files\alb002\pass-alb002-generated_file.ifc
    }

    RuleCreationConventions(**feature_obj)


if __name__ == "__main__":
    # @todo Write proper unit tests
    enforce(
        testing={
            'feature': {
                'name': 'ALB001 - Alignment in spatial structure',
                "valid_first_separator": '-',
                'valid_separators': ' '
            },
            'feature_filename': {
                'name': 'ALB001_Alignment-in-spatial-structure.feature',
                "valid_first_separator": '_',
                'valid_separators': '-'
            },
            'ifc_input': {
                'name': 'fail-grf001-none-ifcmapconversion.ifc',
                'valid_separators': '-'
            },
            'tags': ['disabled', 'implementer-agreement', 'ALB'],
        }
    )