import os
import sys, numpy, ifcopenshell, ifcopenshell.geom
import matplotlib
import matplotlib.pyplot as plt

f = ifcopenshell.open(sys.argv[1])
p = f.by_type('IfcProfileDef')[0][2]
try:
    st = ifcopenshell.geom.settings(INCLUDE_CURVES=True)
except:
    st = ifcopenshell.geom.settings(DIMENSIONALITY=ifcopenshell.ifcopenshell_wrapper.CURVES)

shp = ifcopenshell.geom.create_shape(st, p)
print(ifcopenshell.get_log())
vs = numpy.array(shp.verts).reshape((-1, 3))
ed = numpy.array(shp.edges).reshape((-1, 2))[:,0]
ed = numpy.concatenate((ed, [ed[0]]))
cs = vs[ed][:,0:2]
plt.figure()

fn = os.path.basename(sys.argv[1])

if fn.startswith('fail-'):
    for axis in ['top','bottom','left','right']:
        plt.gca().spines[axis].set_linewidth(4)
        plt.gca().spines[axis].set_color('#ff0000')

plt.plot(*cs.T)
plt.title(' '.join(fn.split('-')[3:])[:-4].replace('_', ' '))

try:
    plt.savefig(sys.argv[2])
except:
    plt.show()
