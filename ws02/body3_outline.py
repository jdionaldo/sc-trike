"""Silhouettes of the base.stl body (old chassis frame, mm): plan (x, y), side (x, z) and half-width / height profiles."""
import json
import numpy as np, trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
import shell_from_base as SB

m = trimesh.load("base/base.stl")
main = max(m.split(only_watertight=False), key=lambda p: len(p.faces))
v = SB.to_chassis(main.vertices.copy())
main = trimesh.Trimesh(v, main.faces, process=False)
c = main.triangles_center
body = main.submesh([np.where((np.abs(c[:, 1]) < 62.0) & (c[:, 0] > -240.0) & (c[:, 0] < 40.0))[0]], append=True)
print("body faces", len(body.faces), body.bounds.round(0).tolist())

def sil(tri3, ax):
    polys = []
    for t in tri3:
        p = Polygon(t[:, ax])
        if p.area > 1e-6:
            polys.append(p.buffer(0.01))
    return unary_union(polys)

tri = body.triangles
side = sil(tri, [0, 2]).simplify(1.2)
plan = sil(tri, [0, 1]).simplify(1.2)
out = {"side": [list(map(float, p)) for p in (side.exterior.coords if side.geom_type == "Polygon" else max(side.geoms, key=lambda g: g.area).exterior.coords)],
       "plan": [list(map(float, p)) for p in (plan.exterior.coords if plan.geom_type == "Polygon" else max(plan.geoms, key=lambda g: g.area).exterior.coords)]}
json.dump(out, open("out/mono3/outline.json", "w"))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 1, figsize=(10, 7))
for a, k in zip(ax, ("side", "plan")):
    p = np.array(out[k]); a.plot(p[:, 0], p[:, 1], "-o", ms=2); a.set_aspect("equal"); a.set_title(k); a.grid(True)
fig.tight_layout(); fig.savefig("out/mono3/outline.png", dpi=80)
print(len(out["side"]), len(out["plan"]))
