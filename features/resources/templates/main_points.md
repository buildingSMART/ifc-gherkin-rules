Alignment Main Points
=====================


```
concept {
    IfcLinearElement:IsNestedBy -> IfcRelNests:RelatingObject
    IfcRelNests:RelatedObjects -> IfcReferent
    IfcReferent:Name -> IfcLabel_0
    IfcReferent:PredefinedType -> IfcReferentTypeEnum
    IfcReferent:ObjectType -> IfcLabel_5
    IfcReferent:Positions -> IfcRelPositions:RelatingPositioningElement
    IfcRelPositions:Name -> IfcLabel_1
    IfcRelPositions:RelatedProducts -> IfcAlignmentSegment
    IfcAlignmentSegment:DesignParameters -> IfcAlignmentParameterSegment
    IfcAlignmentSegment:Name -> IfcLabel_4
    IfcAlignmentParameterSegment:StartTag -> IfcLabel_2
    IfcAlignmentParameterSegment:EndTag -> IfcLabel_3
    IfcRelNests:RelatedObjects[binding="Referent"]
    IfcReferent:Name[binding="ReferentName"]
    IfcReferent:PredefinedType[binding="ReferentPredefinedType"]
    IfcReferent:ObjectType[binding="ReferentObjectType"]
    IfcReferent:Positions[binding="Positions"]
    IfcRelPositions:Name[binding="PositionsName"]
    IfcRelPositions:RelatedProducts[binding="RelatedProducts"]
    IfcAlignmentSegment:DesignParameters[binding="DesignParameters"]
    IfcAlignmentParameterSegment:StartTag[binding="StartTag"]
    IfcAlignmentParameterSegment:EndTag[binding="EndTag"]
    IfcAlignmentSegment:Name[binding="SegmentName"]
}
```
