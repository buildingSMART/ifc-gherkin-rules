import re
import os

from pydantic import field_validator
from ..errors import ProtocolError

class ResultValidators:
    
    @field_validator('ifc_filepath')
    def validate_test_filename(cls, value):

        normalized_path = os.path.normpath(value)
        """Check if test file is located in the ifc-gherkin-rules\\test\\files directory"""
        if not (('ifc-gherkin-rules\\test\\files\\' in normalized_path) or ('ifc-gherkin-rules/test/files/' in normalized_path)):
            raise ProtocolError(
                value=value,
                message=f"The test files are to be placed in the ifc-gherkin-rules/test/files/ directory. Currently it's placed: {normalized_path}"
            )

        """Check if path rule folder is using the valid rule directory name"""
        rule_folder = re.split(r'[\\/]', normalized_path)[-2]
        if not re.match(r'^[a-z]{3}\d{3}$', rule_folder):
            raise ProtocolError(
                value=value,
                message=f"The rule directory is supposed to be a valid rule code name, but is {rule_folder} instead"
            )

        file_path = os.path.basename(value)
        result, rule, *rest = file_path.split('-')
        if len(rest) == 1:
            rest = rest[0]
            scenario = ''
        elif len(rest) == 2:
            scenario, rest = rest
        else:
            raise ProtocolError(
                value=value,
                message=f"Test file {value} does not fit the naming convention. Expected two '-' separators for pass file and three for fail file. Got {len(file_path.split('-')) - 1} instead"
            )

        rest, extension = rest.split('.')

        """Check if test file start with pass or fail"""
        if result not in ('pass', 'fail'):
            raise ProtocolError(
                value=value,
                message=f"Name of the result file must start with 'pass' or 'fail'. In that case name starts with: {result}"
            )

        """Check if a second part of the test file is a rule code"""
        if not re.match(r'^[a-z]{3}\d{3}$', rule):
            raise ProtocolError(
                value=value,
                message=f"The second part of the test file name must be a valid rule code. In that case it's: {rule}"
            )

        """Check if scenario is found in the third part of the test file (for fail files)"""
        if scenario and not re.match(r'^scenario\d{2}$', scenario):
            raise ProtocolError(
                value=value,
                message=f"The third part of the fail test file name must be a valid scenario number. In that case it's: {scenario}"
            )

        """Check if the only separator used in the file description is underscore"""
        separators = [match.group(0) for match in re.finditer(r'[^a-zA-Z0-9]+', rest)]
        if any(separator != '_' for separator in separators):
            raise ProtocolError(
                value=value,
                message=f"The expected separator in the short_informative_description of the test file name is _. For file {value} found {separators}"
            )

        """Check if extension is ifc"""
        if extension.lower() != 'ifc':
            raise ProtocolError(
                value=value,
                message=f"The expected test file extension is .ifc, found: {extension} instead"
            )
        
        """Check if readme file is located in test file directory"""
        test_file_directory = os.path.dirname(normalized_path)
        readme_path = os.path.join(test_file_directory, 'readme.md')
        if not set(f for f in os.listdir(test_file_directory) if f.lower() == 'readme.md'):
            raise ProtocolError(
                value=value,
                message=f"README.ME file not found in the test file directory: {readme_path}")