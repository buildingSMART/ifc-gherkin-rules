import ifcopenshell

from behave.model import Scenario

def before_feature(context, feature):
    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.
    context._stack = context._stack[-2:]
    
    context.model = ifcopenshell.open(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step