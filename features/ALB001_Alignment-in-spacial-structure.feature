@implementer-agreement
@ALB

Feature: ALB001 - Alignment in spacial structure

  Scenario Outline: Agreement on each IfcAlignment being contained in an IfcSite

      Given A file with Schema Identifier "<schema_identifier>"
      And An IfcAlignment
      Then Each IfcAlignment must be contained in IfcSite

  Examples: Schema identifiers
    | schema_identifier |
    | IFC4x3 |
    | IFC4 |