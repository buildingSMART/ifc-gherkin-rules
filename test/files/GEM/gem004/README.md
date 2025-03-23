

| File name | Expected result | Description |
| --- | --- | --- |
| pass-gem004-ifc4-surface\_as\_identifiers.ifc | pass | NaN |
| pass-gem004-ifc4-boundingbox\_as\_type.ifc | pass | NaN |
| pass-gem004-ifc4x3-body\_axis\_as\_identifiers.ifc | pass | NaN |
| pass-gem004-2x3-sweptsolid\_as\_type.ifc | pass | NaN |
| pass-gem004-ifc4x3-surface\_as\_identifiers.ifc | pass | NaN |
| pass-gem004-ifc4x3-boundingbox\_as\_type.ifc | pass | NaN |
| pass-gem004-ifc4x3-axis\_as\_identifiers.ifc | pass | NaN |
| fail-gem004-ifc4x3-validationplan\_as\_identifiers.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: CoG Box Annotation Axis FootPrint Profile Surface Reference Body Body-Fallback Clearance Lighting', 'Observed': 'value: ValidationPlan'} |
| fail-gem004-ifc2x3-sweptsolidss\_as\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Curve2D GeometricSet GeometricCurveSet Annotation2D SurfaceModel SolidModel SweptSolid Brep CSG Clipping AdvancedSweptSolid BoundingBox SectionedSpine MappedRepresentation', 'Observed': 'value: SweptSolidss'} |
| fail-gem004-ifc4x3-axis\_validationplan\_as\_identifers.ifc | fail | Result (multiple/example): 'Instance\_id': '', 'Expected': 'oneOf: Point PointCloud Curve Curve2D Curve3D Surface Surface2D Surface3D SectionedSurface FillArea Text AdvancedSurface GeometricSet GeometricCurveSet Annotation2D SurfaceModel Tessellation Segment SolidModel SweptSolid AdvancedSweptSolid Brep AdvancedBrep CSG Clipping BoundingBox SectionedSpine LightSource MappedRepresentation', 'Observed': 'value: ValidationPlan |
| fail-gem004-ifc4-wrongelement-as-type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Point PointCloud Curve Curve2D Curve3D Surface Surface2D Surface3D FillArea Text AdvancedSurface GeometricSet GeometricCurveSet Annotation2D SurfaceModel Tessellation SolidModel SweptSolid AdvancedSweptSolid Brep AdvancedBrep CSG Clipping BoundingBox SectionedSpine LightSource MappedRepresentation', 'Observed': 'value: WrongElement'} |
| fail-gem004-ifc4x3-sweptsolid\_body\_as\_identifiers.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Point PointCloud Curve Curve2D Curve3D Surface Surface2D Surface3D SectionedSurface FillArea Text AdvancedSurface GeometricSet GeometricCurveSet Annotation2D SurfaceModel Tessellation Segment SolidModel SweptSolid AdvancedSweptSolid Brep AdvancedBrep CSG Clipping BoundingBox SectionedSpine LightSource MappedRepresentation', 'Observed': 'value: Body'} |
| fail-gem004-ifc4x3-validationplan\_mappedelement\_as\_identifiers.ifc | fail | Result (multiple/example): 'Instance\_id': '', 'Expected': 'oneOf: CoG Box Annotation Axis FootPrint Profile Surface Reference Body Body-Fallback Clearance Lighting', 'Observed': 'value: ValidationPlan|
| fail-gem004-ifc4x3-wrongelement-as-type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Point PointCloud Curve Curve2D Curve3D Surface Surface2D Surface3D SectionedSurface FillArea Text AdvancedSurface GeometricSet GeometricCurveSet Annotation2D SurfaceModel Tessellation Segment SolidModel SweptSolid AdvancedSweptSolid Brep AdvancedBrep CSG Clipping BoundingBox SectionedSpine LightSource MappedRepresentation', 'Observed': 'value: WrongElement'} |
| fail-gem004-ifc4x3-body\_as\_identifiers.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: CoG Box Annotation Axis FootPrint Profile Surface Reference Body Body-Fallback Clearance Lighting', 'Observed': 'value: Bodyy'} |
| fail-gem004-ifc4x3-body\_validationplan\_as\_identifiers.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: CoG Box Annotation Axis FootPrint Profile Surface Reference Body Body-Fallback Clearance Lighting', 'Observed': 'value: ValidationPlan'} |
| fail-gem004-ifc4-validationplan\_mappedelement\_as\_identifiers.ifc | fail | Result (multiple/example): {'Instance\_id': '', 'Expected': 'oneOf: CoG Box Annotation Axis FootPrint Profile Surface Reference Body Clearance Lighting', 'Observed': 'value: ValidationPlan |

