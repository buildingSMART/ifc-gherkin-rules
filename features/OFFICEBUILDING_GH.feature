@OFFICEBUILDING
@version1
@N00010
Feature: OFFICEBUILDING

    Scenario Outline: Property Set for Objects - Controller

        Given An IfcController
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ControllerTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Reference             | chargecontroller     |
            | Status                | NEW                  |

    Scenario Outline: Property Set for Objects - Power Panel

        Given An IfcElectricDistributionBoard
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ElectricDistributionBoardTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Reference             | cunit                |
            | Status                | NEW                  |


    Scenario Outline: Body Geometry General

        Given An <Entity>
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attributes <geometric_attribute> for each

        Then The geometrical value must be "<Value>"

        Examples: 
            | Entity                          | geometric_attribute       | Value                                                                               |
            #
            | IfcController                   | RepresentationIdentifier  | Body                                                                                |
            | IfcController                   | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcController                   | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |
            | IfcElectricDistributionBoard    | RepresentationIdentifier  | Body                                                                                |  
            | IfcElectricDistributionBoard    | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcElectricDistributionBoard    | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |
            | IfcTransformer                  | RepresentationIdentifier  | Body                                                                                |
            | IfcTransformer                  | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcTransformer                  | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |