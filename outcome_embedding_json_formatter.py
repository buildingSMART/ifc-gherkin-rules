"""
Enhanced JSON Formatter for clearer activation checks in CI/CD pipeline
embeds the ValidationOutcome to the JSON output.

Example:
--------
To use the `EnhancedJSONFormatter` in a Behave test run:

    behave --format=outcome_embedding_json -o output.json features/

The output will be saved to `enhanced_output.json`.
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
