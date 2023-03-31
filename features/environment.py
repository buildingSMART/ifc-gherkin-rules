import ifcopenshell
import os

from behave.model import Scenario

import check_conventions

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
