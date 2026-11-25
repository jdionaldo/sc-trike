"""Which chassis solids sit near a point (final frame)? usage: probe_point.py x y z radius"""
import os, sys, cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
import types; f = types.ModuleType('soma'); f.param = lambda d, *a, **k: d; sys.modules['soma'] = f
from parts.params import CHASSIS_Y, CHASSIS_Z
x, y, z, r = [float(a) for a in sys.argv[1:5]]
p = cq.Vector(x, y - CHASSIS_Y, z - CHASSIS_Z)
for fn in ('parts/chassis_ref.step', 'parts/rear_ref.step', 'parts/frame_ref.step'):
    for s in cq.importers.importStep(fn).solids().vals():
        b = s.BoundingBox()
        if b.xmin - r <= p.x <= b.xmax + r and b.ymin - r <= p.y <= b.ymax + r and b.zmin - r <= p.z <= b.zmax + r:
            d = s.distance(cq.Solid.makeSphere(0.1, p)) if hasattr(s, 'distance') else -1
            if d < r: print(fn.split('/')[-1], 'dist %.1f' % d, 'bbox x %.0f..%.0f y %.0f..%.0f z %.0f..%.0f (final frame)' % (b.xmin, b.xmax, b.ymin + CHASSIS_Y, b.ymax + CHASSIS_Y, b.zmin + CHASSIS_Z, b.zmax + CHASSIS_Z), 'vol %.0f' % s.Volume())
