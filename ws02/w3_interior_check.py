"""Interior parts against the WS-03 shell: nothing inside should poke through the skin."""
import numpy as np, trimesh, manifold3d as m
import layout3wd as LY, w3_drive_scene as DS
man = lambda t: m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
sh = man(trimesh.load("out/mono3/body3.stl"))
b = LY.blocks()
items = dict(DS.placed())
for k in ("battery", "esc", "motor", "center_diff", "front_diff", "front_ring", "rear_ring", "rear_shaft", "front_pinion_shaft"):
    items[k] = b[k]
bad = []
for k, t in items.items():
    v = (man(t) ^ sh).volume()
    if v > 1.0:
        bad.append((k, round(v, 1)))
print("poking through the shell:", bad)
