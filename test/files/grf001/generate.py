import ifcopenshell
import ifcopenshell.template

import itertools


def create_ifc(filename, mapconversion=0):
    file = ifcopenshell.template.create(schema_identifier="IFC4X1")

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
                                            
    if mapconversion > 0:
        file.createIfcProjectedCrs(
            Name = 'EPSG:31467',
            MapZone = '3', # GausKrueger
            MapUnit = file.by_type("IFCSIUNIT")[0]
        )
            
    for i in range(mapconversion):
        file.createIfcMapConversion(
            file.by_type('IfcGeometricRepresentationContext')[i],
            file.by_type('IfcProjectedCrs')[0]
        )
    file.write(filename)

create_ifc('pass-grf001-2-None.ifc')

create_ifc('pass-grf001-2-Mapconversion.ifc', mapconversion=2)