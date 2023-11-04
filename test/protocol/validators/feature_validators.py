from pydantic import field_validator

from ..parser import ParseValidator
from ..errors import ProtocolError

class FeatureValidators:
    @field_validator('tags')
    def do_validate_tags(cls, value) -> dict:
        validator = ParseValidator()
        validated_tags = validator.validate_tags(value)
        if validated_tags != 'passed':
            raise ProtocolError(
                value=validated_tags['value'],
                message=validated_tags['message']
            )
        return value
    
    @field_validator('description')
    def validate_description(cls, value=list) -> list:
        """must include a description of the rule that start with "The rule verifies that..."""  # allow for comma's
        if not any(value.startswith(f"{prefix} rule verifies{optional_comma} that") for prefix in ("This", "The") for optional_comma in ("", ",")):
            raise ProtocolError(
                value=value,
                message=f"The description must start with 'The rule verifies that', it now starts with {value}"
            )
        return value