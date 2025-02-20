"""
This module provides a single location for the definition of all modifier enumerations.

A modifier is a choice between two mutually exclusive options that are used to add specificity to gherkin steps.
"""
from enum import Enum, StrEnum, auto

class SubtypeHandlingModifier(StrEnum):
    INCLUDING_SUBTYPES = auto()
    EXCLUDING_SUBTYPES = auto()



