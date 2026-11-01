"""Split the WS-03 body into left/right halves, then across x so every piece fits the 220 x 220 bed. Output: out/mono3/body3_{left,right}_{front,rear}.stl"""
import numpy as np, trimesh
from manifold3d import Manifold
import mono_build as MB, validate

body = MB.man(trimesh.load("out/mono3/body3.stl"))
for side, sg in (("left", 1), ("right", -1)):
    box = Manifold.cube((2000.0, 1000.0, 2000.0), center=True).translate((0, sg * 500.0 - sg * 0.013, 0))
    MB.to_trimesh(body ^ box).export(f"out/mono3/body3_{side}.stl")
XS = -150.0
for side in ("left", "right"):
    h = MB.man(trimesh.load(f"out/mono3/body3_{side}.stl"))
    for part, sgn in (("front", 1), ("rear", -1)):
        box = Manifold.cube((400.0, 400.0, 400.0), center=True).translate((XS + sgn * 200.0 - sgn * 0.1, 0, 0))
        m = MB.to_trimesh(h ^ box); m.merge_vertices()
        m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
        m.export(f"out/mono3/body3_{side}_{part}.stl")
        pm = m.copy(); pm.apply_translation((0, 0, -pm.bounds[0][2]))
        print(side, part, len(m.faces), m.is_watertight, np.round(m.extents, 1).tolist(), validate.check_bed(pm, 3.0))
