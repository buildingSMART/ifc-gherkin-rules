@implementer-agreement
@PSE
@version1
@E00020
Feature: PSE001 - Standard properties and property sets validation
The rule verifies that each IfcPropertySet starting with Pset is defined correctly.
  
  Background:
   Given An IfcPropertySet
   Given its Name attribute starts with Pset

    Scenario Outline: IfcPropertySet Name
     
      Given a file with Schema "<schema>"

      Then The IfcPropertySet Name attribute value must use predefined values according to the <csv_table> table

      Examples:
        | schema  | csv_table |
        | IFC2X3  | IFC2x3_definitions.csv |
        | IFC4    | IFC4_definitions.csv |
        | IFC4X3  | IFC4X3_definitions.csv |

    
    Scenario Outline: Property Name

        Given a file with Schema "<schema>"

        Then Each associated IfcProperty must be named according to the property set definitions table <csv_table>

        Examples:
          | schema  | csv_table |
          | IFC2X3  | IFC2x3_definitions.csv |
          | IFC4    | IFC4_definitions.csv |
          | IFC4X3  | IFC4X3_definitions.csv |

      
      Scenario Outline: PropertySet definitions

        Given a file with Schema "<schema>"

        Then The IfcPropertySet must be assigned according to the property set definitions table <csv_table>

        Examples:
          | schema  | csv_table |
          | IFC2X3  | IFC2x3_definitions.csv |
          | IFC4    | IFC4_definitions.csv |
          | IFC4X3  | IFC4X3_definitions.csv |


    Scenario Outline: Property Type

        Given a file with Schema "<schema>"

        Then Each associated IfcProperty must be of type according to the property set definitions table <csv_table>

        Examples:
          | schema  | csv_table |
          | IFC2X3  | IFC2x3_definitions.csv |
          | IFC4    | IFC4_definitions.csv |
          | IFC4X3  | IFC4X3_definitions.csv |

      
    Scenario Outline: Property Data Type
      
          Given a file with Schema "<schema>"
  
          Then Each associated IfcProperty value must be of data type according to the property set definitions table <csv_table>
  
          Examples:
            | schema  | csv_table |
            | IFC2X3  | IFC2x3_definitions.csv |
            | IFC4    | IFC4_definitions.csv |
            | IFC4X3  | IFC4X3_definitions.csv |
