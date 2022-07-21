from pathlib import Path

import ifcopenshell


def before_feature(context, feature):
    context.model = ifcopenshell.open(context.config.userdata["input"])
