import ifcopenshell
import sys
from behave.model import Scenario

model_cache = {}
def read_model(fn):
    if cached := model_cache.get(fn):
        return cached
    model_cache[fn] = ifcopenshell.open(fn)
    return model_cache[fn]

def before_feature(context, feature):
    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.
    context._stack = context._stack[-2:]
    if "error_on_passed_rule" in context.config.userdata:
        context.error_on_passed_rule = context.config.userdata["error_on_passed_rule"] == 'yes'
    else:
        context.error_on_passed_rule = False
    context.model = read_model(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step
