@implementer-agreement
@POR
@version1

Feature: POR000 - Port Connectivity and Nesting
    The rule verifies the presence of IFC entities used to define ports (as means for an element to connect to other elements) and the relationship that is made between two ports.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Element_Connectivity/Port_Connectivity/content.html


    Scenario: Check for activation

    Given an .IfcDistributionPort.
    Given its attribute .ConnectedFrom.
    Given [its entity type] ^is^ 'IfcRelConnectsPorts'
    Given its attribute .RelatingPort.
    Given [its entity type] ^is^ 'IfcDistributionPort'

    Then The IFC model contains information on port connectivity and nesting

