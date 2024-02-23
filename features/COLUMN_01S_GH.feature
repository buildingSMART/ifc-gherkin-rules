@COLUMN01S
@version1
@N00010
Feature: COLUMN01S

  Scenario: Spatial Containment | Product Local Placement

        Given an IfcBuilding 
        Given A relationship IfcRelAggregates from IfcBuilding to IfcSite and following that
        Given Its attribute Name

        Then The value must be "ColumnBuilding_1"


    Scenario: Quantity Sets - COLUMN_1-01 - OuterSurfaceArea

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_ColumnBaseQuantities
        Given Its Property OuterSurfaceArea

        Then The property must be given and exported

    Scenario: Quantity Sets - COLUMN_01-01 - NetVolume

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_ColumnBaseQuantities
        Given Its Property NetVolume

        Then The volume must be 0.04655 or 0.0463785 cubic metre
    

    Scenario Outline: Property Set for Objects Column_01-01
        FireRating, IsExternal, LoadBearing, Status, ThermalTransmittance

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


    Scenario: Property Set for Objects Column_01-01 - Reference

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ColumnCommon
        Given Its Property Reference 
        
        Then The value must contain the substring L 250x250x28


    Scenario: Property Set for Objects Column_01-01 - ThermalTransmittance

        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ColumnCommon
        Given Its Property ThermalTransmittance 
        
        Then The property must be given and exported

    
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
    
    Scenario Outline: Body Geometry General

        Given An IfcColumn
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attributes <geometric_attribute> for each

        Then The geometrical value must be "<Value>"

        Examples: 
            | geometric_attribute       | Value                                                              |
            | RepresentationIdentifier  | Body                                                               |
            | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                 |
            | Items                     | IfcTessellateditem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |
    

    Scenario: Material Single
    
        Given An IfcColumn
        Given Name = Column_1-01
        Given Its Material 
        Given Its attribute Name

        Then The value must contain the substring steel