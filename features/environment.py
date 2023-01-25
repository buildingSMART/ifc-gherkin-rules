import ifcopenshell

from behave.model import Scenario

def before_feature(context, feature):
    context.model = ifcopenshell.open(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step