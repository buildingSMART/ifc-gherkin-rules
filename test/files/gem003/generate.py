# see toturial Kianwee Chen at https://academy.ifcopenshell.org/posts/creating-a-simple-wall-with-property-set-and-quantity-information/

import ifcopenshell
import ifcopenshell.template
import itertools

for num_body_identifier, num_axis_identifier in itertools.product(range(4), range(4)):
    num_representations = num_body_identifier+num_axis_identifier
    if not 1 <= num_body_identifier+num_axis_identifier <= 4:
        continue
    if num_axis_identifier > 2:
        continue


    file = ifcopenshell.template.create(schema_identifier="IFC2X3")
    context = file.by_type("IfcGeometricRepresentationContext")[0]
    owner = file.by_type("IfcOwnerHistory")[0]
    building_parent = proj = file.by_type("IfcProject")[0]
    site = file.createIfcSite(ifcopenshell.guid.new(), owner)

    building = file.createIfcBuilding(
                    ifcopenshell.guid.new(), owner
                )

    file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner,
            RelatingObject=site,
            RelatedObjects = [building]
        )

    create_ifcpolyline = lambda point_list : file.createIfcPolyLine([file.createIfcCartesianPoint(point) for point in point_list])
    polyline = create_ifcpolyline([(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])

    identifiers = ['Body' for i in range(num_body_identifier)] + ['Axis' for i in range(num_axis_identifier)]

    representations = [file.createIfcShapeRepresentation(context, i, "Curve2D", [polyline]
                      ) for i in identifiers]

    shape = file.createIfcProductDefinitionShape(None, None, representations)
    from collections import Counter

    duplicates = [value for (value,count) in Counter(identifiers).items() if count > 1]

    fail_or_pass = "fail" if len(duplicates) else "pass"
    file.write(f"{fail_or_pass}-gem003-{num_body_identifier}-body-{num_axis_identifier}-axis-as-identifiers.ifc")