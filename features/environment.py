import os
import ifcopenshell

from behave.model import Scenario

from pyparsing import Word, alphas, alphanums, delimitedList, OneOrMore

def before_feature(context, feature):
    file_feature_name = os.path.basename(context.feature.filename).replace('.feature', ' ')
    file_feature_name = ''.join(c for c in file_feature_name if c.isalnum())
    gherkin_feature_name = ''.join(c for c in feature.name if c.isalnum())

    assert file_feature_name.lower() == gherkin_feature_name.lower(), 'filename and feature name are not the same, please check'

    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.
    context._stack = context._stack[-2:]
    
    context.model = ifcopenshell.open(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step