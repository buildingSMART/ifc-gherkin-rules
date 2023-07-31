import typing
import os
import argparse
import re

from pydantic import BaseModel, model_validator, field_validator, Field, conlist

from rule_creation_protocol.validation_helper import ValidatorHelper, ParsePattern
# from .validation_helper import ValidatorHelper, ParsePattern
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
    feature: Naming  # feature as in .feature file
    dotfeature_file: Naming  # either user input or test file
    ifc_input: dict
    tags: list
    description : conlist(str, min_length=1) # fails if no description is provided

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
        pass

    @field_validator('description')
    def validate_description(cls, value = list) -> list:
        """must include a description of the rule that start with "The rule verifies that..."""
        first_sentence = value[0]
        cleaned_value = ' '.join(re.sub(r'[^\w\s]', '', first_sentence).split()[:4]) # allow for comma's
        if not cleaned_value.lower() in ['the rule verifies that', 'this rule verifies that']: # allow 'this'
            raise ProtocolError(
                value = value,
                message = f"The description must start with 'The rule verifies that', it now starts with {value}"
            )
        return value
    

def enforce(context=False, feature=False, testing=False) -> bool:
    """Main function to validate feature and tagging conventions.

    This function creates and validates a `RuleCreationConventions` instance based on the provided parameters. 
    It can work in a testing mode when a testing dictionary is provided.
    """
    if testing:
        feature_obj = testing
    else:
        feature_obj = {
            'feature': {
                'name': feature.name,  # e.g. 'ALB001 - Alignment in spatial structure
                'valid_first_separator': '-',
                'valid_separators': ' '
            },
            'dotfeature_file': {
                # e.g. 'ALB001_Alignment-in-spatial-structure.feature'
                'name': os.path.basename(context.feature.filename),
                'valid_first_separator': '_',
                'valid_separators': '-'
            },
            'ifc_input': {
                # if testfile : 'fail-alb001-scenario01-contained_relation_not_directed_to_ifcsite.ifc'
                'name': os.path.basename(context.config.userdata["input"]),
                'valid_separators': '-'
            },
            'tags': feature.tags,
            'description': feature.description
        }

    feature = RuleCreationConventions(**feature_obj)

    return True


if __name__ == "__main__":
    # @todo Write proper unit tests
    enforce(
        testing={
            'feature': {
                'name': 'ALB001 - Alignment in spatial structure',
                "valid_first_separator": '-',
                'valid_separators': ' '
            },
            'dotfeature_file': {
                'name': 'ALB001_Alignment-in-spatial-structure.feature',
                "valid_first_separator": '_',
                'valid_separators': '-'
            },
            'ifc_input': {
                'name': 'fail-grf001-none-ifcmapconversion.ifc',
                'valid_separators': '-'
            },
            'tags': ['disabled', 'implementer-agreement', 'ALB']
        }
    )