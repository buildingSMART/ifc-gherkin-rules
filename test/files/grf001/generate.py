import ifcopenshell
import ifcopenshell.template

import itertools


def create_ifc(filename, mapconversion=0, rigidoperation = 0):
    file = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD1")

    context = file.by_type("IfcGeometricRepresentationContext")[0]
    owner = file.by_type("IfcOwnerHistory")[0]
    site = file.createIfcSite(ifcopenshell.guid.new(), owner)


    WorldCoordinateSystem = file.by_type("IFCAXIS2PLACEMENT3D")[0]
    TrueNorth = file.by_type("IFCDirection")[-1]

    file.createIfcGeometricRepresentationContext(
        ContextType = 'Model',
        CoordinateSpaceDimension = 3,
        Precision = 10 ** -5,
        WorldCoordinateSystem = WorldCoordinateSystem,
        TrueNorth = TrueNorth 
    )
                                            
    if (mapconversion + rigidoperation) > 0:
        file.createIfcProjectedCrs(
            Name = 'EPSG:3857', # plz 04177
            GeodeticDatum = 'WGS84',
            MapProjection = 'WSG',
            MapZone = '3', # GausKrueger
            MapUnit = file.by_type("IFCSIUNIT")[0]
        )

    n = 0       
    for i in range(mapconversion):
        file.createIfcMapConversion(
            SourceCRS = file.by_type('IfcGeometricRepresentationContext')[i],
            TargetCRS = file.by_type('IfcProjectedCrs')[0],
            Northings = 5690966.11,
            Eastings = 316131.64,
            XAxisAbscissa = 1,
            XAxisOrdinate = 0
        )
        n += 1

    for i in range(rigidoperation):
        file.createIfcRigidOperation(
            SourceCRS = file.by_type('IfcGeometricRepresentationContext')[i + n],
            TargetCRS = file.by_type('IfcProjectedCrs')[0],
        )

    file.write(filename)

create_ifc('pass-grf001-2-none.ifc')

create_ifc('pass-grf001-2-mapconversion.ifc', mapconversion=2)

create_ifc('fail-grf001-1-mapconversion-1-rigidoperation.ifc', mapconversion = 1, rigidoperation = 1)

create_ifc('fail-grf001-1-rigidoperation-1-none.ifc', rigidoperation=1)