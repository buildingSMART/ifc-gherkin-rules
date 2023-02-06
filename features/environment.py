import ifcopenshell

from behave.model import Scenario

from pyparsing import Word, alphas, alphanums, delimitedList, OneOrMore

def before_feature(context, feature):
    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.

    # parse filename
    tree = delimitedList(Word(alphas + '/'), '/')
    rulecode = Word(alphanums) + "_"
    file_feature_name = delimitedList(Word(alphas + '-'), '-', combine=True)('file_feature_name')
    grammar = tree + rulecode + file_feature_name
    parse = grammar.parseString(context.feature.filename)
    file_feature_name = parse['file_feature_name'].replace('-', ' ')

    # parse name of feature used for gherkin
    feature_word = "<" + Word(alphas) + '"'
    rulecode = Word(alphanums) + "-"
    gherkin_feature_name = OneOrMore(Word(alphas))('gherkin_feature_name')
    grammar = feature_word + rulecode + gherkin_feature_name
    parse_description = grammar.parseString(str(feature))
    gherkin_feature_name = ' '.join(parse_description['gherkin_feature_name'])

    # still allow for typo between lowercase and uppercase?
    assert(file_feature_name.lower() == gherkin_feature_name.lower(), 'filename and feature name are not the same, please check')

    context._stack = context._stack[-2:]
    
    context.model = ifcopenshell.open(context.config.userdata["input"])
    Scenario.continue_after_failed_step = True

def before_step(context, step):
    context.step = step