"""Occupied z-intervals of chassis components on vertical lines near x=0 (shell frame incl. CHASSIS offsets), for placing the light connectors."""
import os, sys, cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
from parts.params import CHASSIS_Y, CHASSIS_Z
solids = []
for f in ('parts/chassis_ref.step', 'parts/rear_ref.step'):
    solids += [(f, s) for s in cq.importers.importStep(f).solids().vals()]
print(len(solids), 'solids', flush=True)
for y in range(-230, 111, 20):
    for x in (-8, 8):
        iv = []
        for f, s in solids:
            b = s.BoundingBox()
            yy, xx = y - CHASSIS_Y, x
            if not (b.xmin <= xx <= b.xmax and b.ymin <= yy <= b.ymax): continue
            try: c = s.intersect(cq.Solid.makeBox(0.4, 0.4, 400, cq.Vector(xx-0.2, yy-0.2, -100)))
            except Exception: continue
            for k in c.Solids():
                kb = k.BoundingBox(); iv.append((round(kb.zmin + CHASSIS_Z, 1), round(kb.zmax + CHASSIS_Z, 1)))
        iv.sort(); print('y', y, 'x', x, iv[:6], flush=True)
