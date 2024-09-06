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
import base64

from enum import Enum
class AttachmentTarget(Enum):
    FEATURE = "feature"
    STEP = "step"

class OutcomeEmbeddingJSONFormatter(JSONFormatter):
    name = 'outcome_embedding_json'

    def embedding(self, mime_type, data, target=AttachmentTarget.STEP, attribute_name='embedded'):
        if isinstance(target, str):
            try:
                target = AttachmentTarget[target.upper()]
            except KeyError:
                raise ValueError(f"Invalid target string provided: '{target}'. Must be 'feature' or 'step'.")
            
        decoded_data = {
            "mime_type": mime_type,
            "data": base64.b64encode(data).decode(self.stream.encoding or "utf-8"),
        }

        if target == AttachmentTarget.FEATURE:
            self.current_feature_element.setdefault(attribute_name, []).append(decoded_data)
        elif target == AttachmentTarget.STEP:
            self.current_feature_element["steps"][-1].setdefault(attribute_name, []).append(decoded_data)
        else:
            raise ValueError(f"Unknown target for embedding: {target}")
