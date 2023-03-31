import ifcopenshell
import os

from behave.model import Scenario

import check_conventions

"""
Checks whether conditions in documentations are met : https://github.com/buildingSMART/ifc-gherkin-rules/tree/main/features

- The file name is rule code_rule title
- The rule code is made of 3 digits capital letters (taken from the list of Functional parts) + 3 digits number
- The rule title shall have no space and shall use - as separator
- The naming convention for the Feature in the is the following: rule code - rule title (the same used for the file name). For the rule title blank spaces must be used instead of -

"""

model_cache = {}
def read_model(fn):
    if cached := model_cache.get(fn):
        return cached
    model_cache[fn] = ifcopenshell.open(fn)
    return model_cache[fn]

def before_feature(context, feature):
    filename = os.path.basename(context.feature.filename)
    feature_name = feature.name
    check_conventions.validate(filename, feature_name, context)

    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.
    context._stack = context._stack[-2:]
    
    context.model = read_model(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step
