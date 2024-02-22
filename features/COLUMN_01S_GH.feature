@COLUMN01S
@version1
@N00010
Feature: COLUMN01S

  Scenario: Spatial Containment | Product Local Placement

        Given an IfcBuilding 
        Given A relationship IfcRelAggregates from IfcBuilding to IfcSite and following that
        Given Its attribute Name

        Then The value must be "ColumnBuilding_1"


    Scenario Outline: Quantity Sets for COLUMN_1-01

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_ColumnBaseQuantities
        Given Its Property <Property>

        Then <Statement>

        Examples: 
            | Property | Statement |
            | NetVolume | The volume must be 0.04655 or 0.0463785 cubic metre |
            | OuterSurfaceArea | It must be given and exported |
    

    Scenario Outline: Property Set for Objects Column_01-01

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ColumnCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value            |  
            | FireRating            | F60                       |
            | IsExternal            | False                     |
            | LoadBearing           | True                      |
            | Status                | NEW             |
            |ThermalTransmittance| given and exported |
            | Reference              | contains the substring L 250x250x28 |

    
    Scenario Outline: Property Set for Objects Column_01-07

        Given An IfcColumn
        Given Name = Column_1-07
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ColumnCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value            |  
            | Roll            | 0                       |
            | Slope            | 80                     |
    