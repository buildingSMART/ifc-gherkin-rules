@MEMBER01A
@version1
@N00010
Feature: MEMBER01A

    Scenario: Site Attributes
    
        Given An IfcSite
        Then The value of attribute Name must be "LOT123"
        Then The value of attribute SiteAddress must be not empty

    

