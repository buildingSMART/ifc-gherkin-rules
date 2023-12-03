import datetime

def define_feature_version(context):
    version = next((tag for tag in context.tags if "version" in tag))  # e.g. version1
    return int(version.replace("version", ""))

def define_expected_value(context):
    try:
        return str(context.errors[0].expected_value)
    except IndexError:  # Passed Rule
        return None


def define_observed_value(context):
    try:
        return str(context.errors[0].observed_value)
    except IndexError:  # Passed Rule
        return None

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
