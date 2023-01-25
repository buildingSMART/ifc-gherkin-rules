import ifcopenshell
import ifcopenshell.template
import itertools

entities = ['IfcMapConversion', 'None']
# @todo extent with IfcRigidOperation and IfcMapConversionScaled?
for ent_1, ent_2, variate in itertools.product(entities, entities, (0, 1)):
    if (ent_1 != ent_2) and variate == 1:
        continue
    if ent_1 == ent_2 == 'None' and variate == 1:
        continue
    print(ent_1, ent_2, variate)

    file = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD1")

    WorldCoordinateSystem = file.by_type("IFCAXIS2PLACEMENT3D")[0]
    TrueNorth = file.by_type("IFCDirection")[-1]

    context_1 = file.by_type("IfcGeometricRepresentationContext")[0]
    TargetCRS = file.createIfcProjectedCrs(
        Name='EPSG:3857',  # plz 04177
        GeodeticDatum='WGS84',
        MapProjection='WSG',
        MapZone='3',  # GausKrueger
        MapUnit=file.by_type("IFCSIUNIT")[0]
    )
    
    total_ifcmapconversion = 0
    total_rigidoperation = 0

    Northings=5690966.11
    Eastings=316131.64
    count = 0
    for i in [ent_1, ent_2]:
        count =+ 1
        if i == 'IfcMapConversion':
            if total_ifcmapconversion == 0:
                file.createIfcMapConversion(
                    SourceCRS=context_1,
                    TargetCRS=TargetCRS,
                    Northings=Northings,
                    Eastings=Eastings,
                    XAxisAbscissa=1,
                    XAxisOrdinate=0
                )
                total_ifcmapconversion =+ 1
            else:
                # change values Northings, Eastings
                file.createIfcMapConversion(
                    SourceCRS=file.createIfcGeometricRepresentationContext(
                        ContextType='Model',
                        CoordinateSpaceDimension=3,
                        Precision=10 ** -5,
                        WorldCoordinateSystem=WorldCoordinateSystem,
                        TrueNorth=TrueNorth
                    ),
                    TargetCRS=TargetCRS,
                    Northings=5201735.12 if variate == 1 else Northings,
                    Eastings=341613.64 if variate == 1 else Eastings,
                    XAxisAbscissa=1,
                    XAxisOrdinate=0
                )
        # if i == 'IfcRigidOperation':
        #     if total_rigidoperation == 0:
        #         file.createIfcRigidOperation(
        #             SourceCRS=context_1,
        #             TargetCRS=TargetCRS,
        #             FirstCoordinate=92.2
        #         )
        #         total_rigidoperation = + 1 if variate == 1 else 0
        #     else:
        #         values FirstCoordinate & SecondCoordinate change
        #         file.createIfcRigidOperation(
        #             SourceCRS=context_1,
        #             TargetCRS=TargetCRS
        #         )

    # create extra reprcontext, slightly non-identical compared to first
    if 'None' in [ent_1, ent_2]:
        file.createIfcGeometricRepresentationContext(
                        ContextType='Model',
                        CoordinateSpaceDimension=2,
                        Precision=10 ** -5,
                        WorldCoordinateSystem=WorldCoordinateSystem,
                        TrueNorth=TrueNorth
                    )



    ok = (ent_1 == ent_2) and variate == 0
    pass_or_fail = 'pass' if ok else 'fail'

    different_values = '-non-identical' if variate == 1 else ''

    file.write(f'{pass_or_fail}-{ent_1.lower()}-{ent_2.lower()}{different_values}.ifc')

count = 0
for i in range(2):
    count += 1
    file = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD1")

    WorldCoordinateSystem = file.by_type("IFCAXIS2PLACEMENT3D")[0]
    TrueNorth = file.by_type("IFCDirection")[-1]

    context_1 = file.by_type("IfcGeometricRepresentationContext")[0]
    TargetCRS = file.createIfcProjectedCrs(
        Name='EPSG:3857',  # plz 04177
        GeodeticDatum='WGS84',
        MapProjection='WSG',
        MapZone='3',  # GausKrueger
        MapUnit=file.by_type("IFCSIUNIT")[0]
    )

    file.createIfcRigidOperation(
                    SourceCRS=context_1,
                    TargetCRS=TargetCRS,
                    FirstCoordinate=92.2
                )
    
    file.createIfcRigidOpeation(
        SourceCRS = file.createIfcGeometricRepresentationContext(
                        ContextType='Model',
                        CoordinateSpaceDimension=3,
                        Precision=10 ** -5,
                        WorldCoordinateSystem=WorldCoordinateSystem,
                        TrueNorth=TrueNorth
                    ),
        TargetCRS = Target
    )
    
