@MEMBER01A
@version1
@N00010
Feature: MEMBER01A

    Scenario: Material Single
    
        Given An IfcMember
        Given Name = Member_2-101
        Given Its Material 
        Given Its attribute Name

        Then The value must contain the substring stainless steel