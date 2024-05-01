# Segment Type Mapping for ALA003

## Horizontal Segment Types

| [Business Logic Segment PredefinedType][horiz_enums] | Representation Entity             | Reference                                                    |
|------------------------------------------------------|-----------------------------------|--------------------------------------------------------------|
| BLOSSCURVE                                           | `IfcThirdOrderPolynomialSpiral`   | [4.2.2.2.2 Bloss Transition Segment][bloss]                  |
| CIRCULARARC                                          | `IfcCircle`                       | [4.2.2.2.1 Arc Segment][arc]                                 |
| CLOTHOID                                             | `IfcClothoid`                     | [4.2.2.2.3 Clothoid Transition Segment][clothoid]            |
| COSINECURVE                                          | `IfcCosineSpiral`                 | [4.2.2.2.4 Cosine Spiral Transition Segment][cosine]         |
| CUBIC                                                | `IfcPolynomialCurve`              | [4.2.2.2.5 Cubic Transition Segment][cubic]                  |
| HELMERTCURVE                                         | `IfcSecondOrderPolynomialSpiral`  | [4.2.2.2.6 Helmert Transition Segment][helmert]              |
| LINE                                                 | `IfcLine` or `IfcPolyline`        | [4.2.2.2.7 Linear Segment][line]                             |
| SINECURVE                                            | `IfcSineSpiral`                   | [4.2.2.2.9 Sine Spiral Transition Segment][sine]             |
| VIENNESEBEND                                         | `IfcSeventhOrderPolynomialSpiral` | [4.2.2.2.10 Viennese Bent Transition Segment][viennese_bend] |

## Vertical Segment Types

| [Business Logic Segment PredefinedType][vertical_enums] | Representation Entity | Reference                                                 |
|---------------------------------------------------------|-----------------------|-----------------------------------------------------------|
| CIRCULARARC                                             | `IfcCircle`           | See [Horizontal Segment Types](#horizontal-segment-types) |
| CLOTHOID                                                | `IfcClothoid`         | See [Horizontal Segment Types](#horizontal-segment-types) |
| CONSTANTGRADIENT                                        | `IfcLine`             |                                                           |
| PARABOLICARC                                            | `IfcPolynomialCurve`  | [4.2.2.2.8 Parabolic Transition Segment][parabolic]       |

## Cant Segment Types

| [Business Logic Segment PredefinedType][cant_enums] | Representation Entity             | Reference                                                 |
|-----------------------------------------------------|-----------------------------------|-----------------------------------------------------------|
| BLOSSCURVE                                          | `IfcThirdOrderPolynomialSpiral`   | See [Horizontal Segment Types](#horizontal-segment-types) |
| CONSTANTCANT                                        | `IfcLine`                         |                                                           |
| COSINECURVE                                         | `IfcCosineSpiral`                 | See [Horizontal Segment Types](#horizontal-segment-types) |
| HELMERTCURVE                                        | `IfcSecondOrderPolynomialSpiral`  | See [Horizontal Segment Types](#horizontal-segment-types) |
| LINEARTRANSITION                                    | `IfcLine`                         | See [Horizontal Segment Types](#horizontal-segment-types) |
| SINECURVE                                           | `IfcSineSpiral`                   | See [Horizontal Segment Types](#horizontal-segment-types) |
| VIENNESEBEND                                        | `IfcSeventhOrderPolynomialSpiral` | see [Horizontal Segment Types](#horizontal-segment-types) |

### Special Note for Cant `LINEARTRANSITION`

The partial concept template addresses horizontal segment types only and is silent on
`PredefinedType` values that are specific to vertical and cant.
For a cant `LINEARTRANSITION`, this rule implementation will consider both `IfcLine` and `IfcClothoid` to be
valid representation entity types.
`IfcLine` seems correct from the author's perspective,
however sample models such as [linear-placement-of-signal][linear-placement-of-signal]
utilize `IfcClothoid` for this cant segment type.
The use of `IfcClothoid` is also consistent with reference code from the IFC-Rail room,
particularly the [EnrichIFC4x3][enrich_4x3] utility that can be used to generate
an alignment geometry representation from an IFC model that contains business logic only.

See additional discussion in IFC4.x Implementer Forum [Issue # 145][IFC4.x-IF#145].

[horiz_enums]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcAlignmentHorizontalSegmentTypeEnum.htm

[vertical_enums]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcAlignmentVerticalSegmentTypeEnum.htm

[cant_enums]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcAlignmentCantSegmentTypeEnum.htm

[arc]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Arc_Segment/content.html

[bloss]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Bloss_Transition_Segment/content.html

[clothoid]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Clothoid_Transition_Segment/content.html

[cosine]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Cosine_Spiral_Transition_Segment/content.html

[cubic]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Cubic_Transition_Segment/content.html

[helmert]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Helmert_Transition_Segment/content.html

[line]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Linear_Segment/content.html

[parabolic]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Parabolic_Transition_Segment/content.html

[sine]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Sine_Spiral_Transition_Segment/content.html

[viennese_bend]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Viennese_Bend_Transition_Segment/content.html

[linear-placement-of-signal]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/annex_e/alignment-geometries-and-linear-positioning/linear-placement-of-signal.html

[enrich_4x3]: https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/blob/6975595f84da8b78afb68f8ac97062732315aaf1/EnrichIFC4x3/EnrichIFC4x3/business2geometry/ifcalignmentcant.h#L428

[IFC4.x-IF#145]: https://github.com/buildingSMART/IFC4.x-IF/issues/145