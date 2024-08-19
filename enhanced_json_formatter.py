"""
Enhanced JSON Formatter for clearer activation checks in CI/CD pipeline
===================================

This file provides an `EnhancedJSONFormatter` for Behave, which extends the
functionality of the default JSON formatter. This custom formatter includes additional
information in the output JSON, specifically the results of passed steps, which can
be useful for activation checks..

File: enhanced_json_formatter.py

Example:
--------
To use the `EnhancedJSONFormatter` in a Behave test run:

    behave --format=enhanced_json -o enhanced_output.json features/

The output will be saved to `enhanced_output.json` in JSON format, including
additional details about passed results.
"""
from behave.formatter.json import JSONFormatter

class EnhancedJSONFormatter(JSONFormatter):
    name = 'enhanced_json'

    def feature(self, feature):
        super().feature(feature) 
        self.current_feature_data.setdefault("activated", False)

    def result(self, step):
        super().result(step)
        if getattr(step, 'activating_feature', False):
            self.current_feature_data["activated"] = True