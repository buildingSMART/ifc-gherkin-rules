@implementer-agreement
@QTY
@version1
@E00020
Feature: QTY001 - Quantity method of measurement
The rule verifies that an IfcElementQuantity has the correct method of measurement as per the general agreements
for IfcElementQuantity documented at:
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcElementQuantity.htm

  Scenario: Agreement on value for method of measurement

    Given An .IfcElementQuantity.

    Then The value of attribute .MethodOfMeasurement. must be 'BaseQuantities'