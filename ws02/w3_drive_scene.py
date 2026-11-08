"""Place the WS-03 drivetrain housings and check them against the gear and shaft blocks."""
import itertools
import numpy as np
import trimesh
import layout3wd as LY
from parts import w3_drive as D

STL = "out/stl"
HOUS = {"w3_fdc": (-22.0, 22.0), "w3_cdc": (-22.0, 52.0), "w3_rbc": (-21.0, 21.0), "w3_pillow": (-21.0, 21.0)}


def placed():
    items = []
    for n, (z0, z1) in HOUS.items():
        lo = trimesh.load(f"{STL}/{n}_lower.stl"); lo.apply_translation((0, 0, z0))
        up = trimesh.load(f"{STL}/{n}_upper.stl"); m = np.diag([1.0, -1.0, -1.0, 1.0]); m[2, 3] = z1; up.apply_transform(m)
        items += [(f"{n}_lower", lo), (f"{n}_upper", up)]
    import math
    import w3_stock as K

    def put(name, rot, t):
        h = trimesh.load(f"{STL}/{name}.stl")
        m = np.eye(4); m[:3, :3] = rot; m[:3, 3] = t
        h.apply_transform(m)
        items.append((name, h))
    # ring hubs: print frame z up from the flange; flange at the gear, spigot into it.  Rear ring hub: axis +y, flange on the ring's back face.
    put("w3_rring_hub", np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float), (K.XR, K.RRING_Y[1] + 3.0, 0.0))
    put("w3_cring_hub", np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float), (K.C_FACE_F, K.SY, 0.0))
    return items


def check():
    import manifold3d as m
    man = lambda t: m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
    b = LY.blocks()
    gear = ["front_diff", "front_ring", "front_pinion_shaft", "center_diff", "rear_shaft", "motor_shaft", "rear_ring", "rear_out",
            "diff_out_L", "diff_out_R", "motor"]
    bad = []
    for hn, hm in placed():
        for gn in gear:
            gm = b[gn]
            if np.any(hm.bounds[1] < gm.bounds[0]) or np.any(gm.bounds[1] < hm.bounds[0]):
                continue
            v = (man(hm) ^ man(gm)).volume()
            if v > 1.0:
                bad.append((hn, gn, round(v, 1)))
    return bad


if __name__ == "__main__":
    for r in check():
        print(r)
    print("done")
