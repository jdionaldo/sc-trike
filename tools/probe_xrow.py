"""Chassis tops along x at given y stations (final frame): where can the cage feet stand?"""
import os, sys, cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
from parts.params import CHASSIS_Y, CHASSIS_Z
solids = []
for f in ('parts/chassis_ref.step', 'parts/rear_ref.step'):
    solids += [s for s in cq.importers.importStep(f).solids().vals()]
for y in (-215, 95):
    for x in range(0, 80, 6):
        yy = y - CHASSIS_Y; iv = []
        for s in solids:
            b = s.BoundingBox()
            if not (b.xmin <= x <= b.xmax and b.ymin <= yy <= b.ymax): continue
            try: c = s.intersect(cq.Solid.makeBox(0.4, 0.4, 400, cq.Vector(x-0.2, yy-0.2, -100)))
            except Exception: continue
            iv += [(round(k.BoundingBox().zmin + CHASSIS_Z, 1), round(k.BoundingBox().zmax + CHASSIS_Z, 1)) for k in c.Solids()]
        print('y', y, 'x', x, sorted(iv)[:5], flush=True)
