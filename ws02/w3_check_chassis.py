"""Build, print-check and interference-check the WS-03 deck and walls."""
import numpy as np, trimesh, manifold3d as m
import build, validate
from params import P
from parts import w3_chassis as C
import w3_scene as S, w3_drive_scene as DS, layout3wd as LY
for part in C.build(P):
    build.run_part(part)
    r = validate.validate_part(part.name, part.walls, part.supports)
    bad = {k: v[1] for k, v in r.items() if not v[0]}
    print(part.name, "OK" if not bad else bad)
man = lambda t: m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
items = {}
for n in ("w3_deck_front", "w3_deck_rear"):
    t = trimesh.load(f"out/stl/{n}.stl"); t.apply_translation((0, 0, C.DECK_Z[0])); items[n] = t
for n, side in (("w3_wall_left", 1), ("w3_wall_right", -1)):
    t = trimesh.load(f"out/stl/{n}.stl"); mm = np.eye(4)
    if side > 0: mm[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; mm[1, 3] = 51.0 + C.YS
    else: mm[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; mm[1, 3] = -(51.0 + C.YS)
    t.apply_transform(mm); items[n] = t
others = dict(DS.placed()); b = LY.blocks()
for k in ("battery", "esc", "motor", "center_diff", "front_diff", "front_ring", "rear_shaft", "front_pinion_shaft"):
    others[k] = b[k]
for ph in (-25.0, 0.0, 25.0):
    for n, mesh, k in S.scene(ph):
        if n.startswith(("lean_servo", "steer_servo", "uplink", "arm_", "cover_", "diff_out", "lean_horn", "steer_horn", "tie_rod", "lean_rod")):
            others[f"{n}@{ph:+.0f}"] = mesh
bad = []
for a, ta in items.items():
    for k, tb in others.items():
        if np.any(ta.bounds[1] < tb.bounds[0]) or np.any(tb.bounds[1] < ta.bounds[0]):
            continue
        v = (man(ta) ^ man(tb)).volume()
        if v > 0.5:
            bad.append((a, k, round(v, 1)))
print("chassis clashes:", bad)
# servos and horns against the gear housings
hous = dict(DS.placed())
bad2 = []
for n, mesh, k in S.scene(0.0):
    if n.startswith(("lean_servo", "steer_servo", "lean_horn", "steer_horn")):
        for hn, hm in hous.items():
            if np.any(mesh.bounds[1] < hm.bounds[0]) or np.any(hm.bounds[1] < mesh.bounds[0]):
                continue
            v = (man(mesh) ^ man(hm)).volume()
            if v > 0.5:
                bad2.append((n, hn, round(v, 1)))
print("servo vs housing:", bad2)
