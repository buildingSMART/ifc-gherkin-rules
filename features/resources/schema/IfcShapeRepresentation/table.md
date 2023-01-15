|Identifier|Description|
|--- |--- |
|CoG|Point to identify the center of gravity of an element. This value can be used for validation purposes.|
|Box|Bounding box as simplified 3D box geometry of an element|
|Annotation|3D annotations not representing elements|
|Axis|2D or 3D Axis, or single line, representation of an element|
|FootPrint|2D Foot print, or double line, representation of an element, projected to ground view|
|Profile|3D line representation of a profile being planar, e.g. used for door and window outlines|
|Surface|3D Surface representation, e.g. of an analytical surface, of an elementplane)|
|Reference|3D representation that is not part of the Body representation. This is used, e.g., for opening geometries, if there are to be excluded from an implicit Boolean operation.|
|Body|3D Body representation, e.g. as wireframe, surface, or solid model, of an element|
|Body-FallBack|3D Body representation, e.g. as tessellation, or other surface, or boundary representation, added in addition to the solid model (potentially involving Boolean operations) of an element|
|Clearance|3D clearance volume of the element. Such clearance region indicates space that should not intersect with the 'Body' representation of other elements, though may intersect with the 'Clearance' representation of other elements.|
|Lighting|Representation of emitting light as a light source within a shape representation|