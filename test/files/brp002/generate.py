import ifcopenshell
import numpy as np

vs = np.array([[-1., -1., -1.],
       [-1., -1.,  1.],
       [-1.,  1., -1.],
       [-1.,  1.,  1.],
       [ 1., -1., -1.],
       [ 1., -1.,  1.],
       [ 1.,  1., -1.],
       [ 1.,  1.,  1.]])

faces = np.array([[0, 1, 3, 2],
       [2, 3, 7, 6],
       [6, 7, 5, 4],
       [4, 5, 1, 0],
       [2, 6, 4, 0],
       [7, 3, 1, 5]])

tris = np.array([[1, 2, 0],
       [3, 6, 2],
       [7, 4, 6],
       [5, 0, 4],
       [6, 0, 2],
       [3, 5, 7],
       [1, 3, 2],
       [3, 7, 6],
       [7, 5, 4],
       [5, 1, 0],
       [6, 4, 0],
       [3, 1, 5]])

for nc, pass_or_fail in enumerate(['pass', 'fail'], start=1):

    f = ifcopenshell.file()
    ps = [f.createIfcCartesianPoint(v.tolist()) for v in vs]
    f.createIfcOpenShell([f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([ps[i] for i in b]), True)]) for b in faces.reshape((-1, 6, 4))[:,0]])
    f.write(f'{pass_or_fail}-brp002-open_shell_reused_points_{nc}_components.ifc')

    f = ifcopenshell.file()
    f.createIfcOpenShell([f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([f.createIfcCartesianPoint(vs[i].tolist()) for i in b]), True)]) for b in faces.reshape((-1, 6, 4))[:,0]])
    f.write(f'{pass_or_fail}-brp002-open_shell_non_reused_points_{nc}_components.ifc')

    f = ifcopenshell.file()
    ps = [f.createIfcCartesianPoint(v.tolist()) for v in vs]
    f.createIfcClosedShell([f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([ps[i] for i in b]), True)]) for b in faces])
    f.write(f'{pass_or_fail}-brp002-closed_shell_reused_points_{nc}_components.ifc')

    f = ifcopenshell.file()
    f.createIfcClosedShell([f.createIfcFace([f.createIfcFaceOuterBound(f.createIfcPolyLoop([f.createIfcCartesianPoint(vs[i].tolist()) for i in b]), True)]) for b in faces])
    f.write(f'{pass_or_fail}-brp002-closed_shell_non_reused_points_{nc}_components.ifc')

    f = ifcopenshell.file()
    ps = f.createIfcCartesianPointList3D(vs.tolist())
    fs = [f.createIfcIndexedPolygonalFace(fa.tolist()) for fa in faces + 1]
    f.createIfcPolygonalFaceSet(
        ps, True, fs
    )
    f.write(f'{pass_or_fail}-tas002-polygonal_faceset_{nc}_components.ifc')

    f = ifcopenshell.file()
    ps = f.createIfcCartesianPointList3D(vs.tolist())
    f.createIfcTriangulatedFaceSet(
        ps, None, True, (faces + 1).tolist()
    )
    f.write(f'{pass_or_fail}-tas002-triangulated_faceset_{nc}_components.ifc')

    # create 2nd cube
    faces = np.concatenate((faces, faces + len(vs)), axis=0)
    tris = np.concatenate((tris, tris + len(vs)), axis=0)
    vs = np.concatenate((vs, vs+(3.,0.,0.)), axis=0)

