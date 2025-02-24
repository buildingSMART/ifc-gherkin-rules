"""
This module provides a single location for the definition of all modifier enumerations.

A modifier is a choice between two or more mutually exclusive options that are used to add specificity to gherkin steps.
"""
from behave import register_type
from enum import Enum

def register_enum_type(cls):
    """
    Use this decorator to register an enum type for behave, e.g.
    @register_enum_type
    class SubtypeHandling(Enum):
        INCLUDE = "including subtypes"
        EXCLUDE = "excluding subtypes"
    """
    register_type(**{cls.__name__: cls})
    return cls


@register_enum_type
class PrefixCondition(Enum):
    STARTS = "starts"
    DOES_NOT_START = "does not start"


@register_enum_type
class SubTypeHandling(Enum):
    INCLUDE = 'including subtypes'
    EXCLUDE = 'excluding subtypes'
    

@register_enum_type
class FirstOrFinal(Enum):
    FINAL = "final"
    FIRST = "first"
    