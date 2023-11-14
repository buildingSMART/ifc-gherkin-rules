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

    context.feature = feature

def before_step(context, step):
    context.step = step
    context.instance_expected_results = []
    context.instance_observed_results = []

def after_step(context, step):
    if step.step_type == 'then':
        # print(dir(step))
        # print(help(step))
        # print(step.error_message)
        # print(step.filename)
        # print(context.feature)
        # print(help(context.feature))
        # print(context.feature.name)
        # print(context.feature.description)

        print(dir(step))
        #print(step.exception)
        print(step.filename)

        file = ''
        validated_on = ''
        reference = context.feature.name
        step_col = step.name
        description = context.feature.description
        severity = step.status
        code = ''
        expected = context.instance_expected_results
        observed = context.instance_observed_results
        query = f'INSERT INTO rule_results VALUES("{file}", "{validated_on}", "{reference}", "{step_col}", "{description}", "{severity}", "{code}", "{expected}", "{observed}")'
        print(query)
        context.cur.execute('Delete from rule_results') # TODO -> just to keep the db readable
        context.cur.execute(query) # TODO -> PoC, SQLAlchemy? + injection unsafe

        context.con.commit()
def before_all(context):



    import sqlite3
    con = sqlite3.connect("poc.db")
    context.con = con

    cur = con.cursor()
    context.cur = cur

    try:
        #TODO -> are the checks on the feature or on the step level?
        #TODO -> are the checks on the instance level?
        query = """CREATE TABLE "rule_results" (
                    "file"	TEXT,
                    "validated_on"	TEXT,
                    "reference"	TEXT,
                    "step"	TEXT, 
                    "description"	TEXT,
                    "severity"	TEXT,
                    "code"	TEXT,
                    "expected"	TEXT,
                    "observed"	TEXT
                );"""
        cur.execute(query)
    except sqlite3.OperationalError:  # TODO table already_exists (PoC)
        pass

    context.cur = cur

