import re
import itertools

from pydantic import field_validator
from ..errors import ProtocolError

class ScenarioValidators:
    @field_validator('steps')
    def validate_steps(cls, value):

        """
        Check whether IFC versions mentioned in steps are all uppercases
        - IFC4X3_ADD2 and IFC2X3 are correct
        - IFC4x3_ADD2 or ifc4x3_add2 or Ifc2X3 are not
        """
        pattern = re.compile(r'\bIFC[A-Za-z]*\d+[A-Za-z0-9_]*\b', re.IGNORECASE)
        ifc_versions_in_steps = list(itertools.chain.from_iterable(pattern.findall(stmt['name']) for stmt in value))

        for version in ifc_versions_in_steps:
            if not ''.join(ch for ch in version if ch.isalpha()).isupper():
                raise ProtocolError(
                    value = version,
                    message = "{value} must be all upper cases"
                    )


        """Check only correct keywords are applied: 'Given', 'Then', 'And'"""
        if not all(d['keyword'] in ['Given', 'Then', 'And'] for d in value):
            raise ProtocolError(
                value=value,
                message=f"The expected keywords used in the feature file are 'Given', 'Then' and 'And'. Now {[d['keyword'] for d in value]} are used."
            )

        """Check that no punctuation at the end of the step"""
        if any(d['name'].endswith(tuple(r"""!#$%&()*+,-./:;<=>?@[\]^_`{|}~""")) for d in value):
            raise ProtocolError(
                value=value,
                message=f"The feature steps must not end with punctuation. Now the steps end with {[d['name'][-1] for d in value]}."
            )

        """Check that 'shall' is not used"""
        if any('shall' in d['name'].lower() for d in value):
            raise ProtocolError(
                value=value,
                message=f"The feature steps must not use the word 'shall', use 'must' instead."
            )

        """Check double spaces are not used"""
        if any('  ' in d['name'] for d in value):
            raise ProtocolError(
                value=value,
                message=f"Double spaces are not to be used in the step definition"
            )