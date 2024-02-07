"""""
Output Type : Outcome must be one of mentioned types/values

if the observed value is a type of ifcopenshell.entity_instance obj, include the id
Applicable rules : ALB003, ALB005, ALB002, ALS006
"""""

#ALB002
expected = {"value": {"OneOf": {"entity_type": ['IfcElementA', "IfcElementB"], "relationship": {'ifc_relationship': 'nesting'}}}} #alb002
observed = {"value": {"entity_type": "IfcElementC", "id": 123}, "relationship": {'ifc_relationship': 'nesting'}}

# ALB002
expected = {"value": {"List": {"entity_type": 'IfcAlignmentCant', "relationship": {'ifc_relationship': 'nesting'}}}}
observed = {"value": {"entity_type": "IfcAlignment", "id": 123}, "relationship": {'ifc_relationship': 'nesting'}}

# ALB005
expected = {"value": {"OneOf": {"string": ['POSITION', "STATION"], "relationship": {"attribute" : "PreDefinedType"}}}}
observed = {"value": {"string": "BUILDING"}, "relationship": {"attribute" : "PreDefinedType"}} 


# ALS006, ALS005
expected = {"value": {"OneOf": {"entity_type": ['IfcCompositeCurve', "IfcIndexedPolyCurve", "IfcPolyLine"], "relationship": {"attribute" : "Items"}}}}
observed = {"value": {"entity_type": "IfcAlignment", "id": 123}, "relationship": {'attribute': 'Items'}}

# IFC001
expected = {"value": {"OneOf": {"schema": ['IFC4X3_ADD2', "IFC2X3"]}}}
observed = {"value": {"schema": "IFC4X3_ADD1"}} 


"""
Output type : Predicate followed by num 

'At most 1, exactly 2, only 1' 

Applicable rules : ALB002, GEM001
"""
#ALB002, GEM001, #SYS001
expected = {"value": {"count": 1}, "relationship": {"pred": 'at most'}} 
observed = {"value": {"count": 2}, "relationship": {"pred": 'at most'}}

#other_example
expected = {"value": {"count": 2}, "relationship": {"pred": 'at least'}} #example
observed = {"value": {"count": 1}, "relationship": {"pred": 'at most'}}

#ALS010
expected = {"value": {"count": 1}, "relationship": {"pred": 'exactly', 'attribute': 'Items'}} 
observed = {"value": {"count": 2}, "relationship": {"pred": 'exactly', 'attribute': 'Items'}}

#GEM002
expected = {"value": {"count": 1}, "relationship": {"pred": 'exactly', 'attribute': 'FootPrint'}} 
observed = {"value": {"count": 0}, "relationship": {"pred": 'exactly', 'attribute': 'FootPrint'}}

""""
Output: Equality check to value/types 

Applicable rules : ALB002, ALB005, ALS015

"""""

#ALB002, OJP001
#SPS001 (Assigned -> IfcProject)
#SPS003 (ContainedInStructure -> Empty)
#SPS004
expected = {"value": {"entity_type": "IfcAlignmentHorizontalSegment"}, "relationship": {"attribute": "DesignParameters"}} 
observed = {"value": {"entity_type": "IfcRoof"}, "relationship": {"attribute": "DesignParamters"}}

#ALS015, GEM005
expected = {"value": {"string": "DISCONTINUOUS"}, "relationship": {"attribute": "Transition"}} 
observed = {"value": {"string": "None"}, "relationship": {"attribute": "Transition"}}

#ALB015, ALS015
expected = {"value": {"attribute": "SegmentLength", "value": 0}, "relationship": {"attribute": "DesignParameters"}} 
observed = {"value": {"attribute": "SegmentLength", "value" : 1}, "relationship": {"attribute": "DesignParamters"}}

#ALB004
expected = {"value": {"entity_type": "IfcAlignmentHorizontalSegment"}, "relationship": {"ifc_relationship": "aggregates"}} 
observed = {"value": {"entity_type": "IfcRoof"}, "relationship": {"ifc_relationship": "aggregates"}}

#ALB005 / ALB001
expected = {"value": {"entity_type": "IfcAlignment"}, "relationship": {'value': "aggregated", "directly_or_indirectly": "directly"}} 
expected = {"value": {"entity_type": "IfcAlignment"}, "relationship": {'value': "aggregated", "directly_or_indirectly": "indirectly"}}

#ALS004, ALS008, ALS007, ALS010
expected = {"value": {"string": "Axis"}, "relationship": {"all": True, 'attribute': "Representationidentifier"}} 
observed = {"value": {"string": "Axis"}, "relationship": {"all": False, 'attribute': "Representationidentifier"}} 

#ALS005/ALS006
observed = {"value": {"string": "Axis"}, "relationship": {"attribute" : "Representationidentifier"}} 
observed = {"value": {"string": "Curve3D"}, "relationship": {"attribute" : "Representationidentifier"}} 

#GEM004, IBP001, PSE001, SPS002
expected = {"value": {"bool": True}, "relationship": {"resources": 'valid_RepresentationType.csv'}} 
observed = {"value": {"bool": False}, "relationship": {"resources": 'valid_RepresentationType.csv'}} 

#GEM111/GEM003/GRF001
expected = {"value": {"unique/identical/duplicate": True/False}, "relationship": {"attribute": "RepresentationIdentifier"}} #rel is optional here
expected = {"value": {"unique/identical/duplicate": False/True}, "relationship": {"attribute": "RepresentationIdentifier"}}



