import unittest

from pydantic import ValidationError

from .protocol import RuleCreationConventions
from .errors import ProtocolError


    
class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.test_base_case = {
            'feature': {
                'name': 'ALB001 - Alignment in spatial structure',
                "valid_first_separator": '-',
                'valid_separators': ' '
            },
            'dotfeature_file': {
                'name': 'ALB001_Alignment-in-spatial-structure.feature',
                "valid_first_separator": '_',
                'valid_separators': '-'
            },
            'ifc_input': {
                'name': 'fail-grf001-none-ifcmapconversion.ifc',
                'valid_separators': '-'
            },
            'tags': ['disabled', 'implementer-agreement', 'ALB'],
            'desciption' : ['This rule verifies that this and that such and so']
        }

    def test_tag(self):
        """Feature file must start with a tag to the functional part
        """
        invalid = self.test_base_case.copy()
        invalid['tags'] = ['BBB', 'disabled'] # wrong tag
        with self.assertRaises(ProtocolError):
            RuleCreationConventions(**invalid)
            
        invalid ['tags'] = ['AL', 'disabled'] #only the first two letters of a functional part
        with self.assertRaises(ProtocolError):
            RuleCreationConventions(**invalid) 

        invalid ['tags'] = [] #no tag linking to a rule
        with self.assertRaises(ProtocolError):
            RuleCreationConventions(**invalid) 
    
    def test_description(self):
        """The Feature must include a description of the rule that start with "The rule verifies that..."""""
        invalid = self.test_base_case.copy() 
        invalid['description'] = []
        with self.assertRaises(ValidationError): # Feature has no description
            RuleCreationConventions(**invalid)

        invalid['description'] = ['Some other description']
        with self.assertRaises(ProtocolError):
            RuleCreationConventions(**invalid)
        
            

if __name__ == '__main__':
    unittest.main()

    # feature_obj_invalid = feature_obj.copy()
    # feature_obj_invalid['tags'] = ['BEC']
        # with pytest.raises(ValueError, match="Tags should contain 'ALB'"):
        # RuleCreationConventions(**feature_obj_invalid)