"""WS-03 full assembly: every printed and bought part placed for a lean/steer pose, with a global interference check,
bed fit of every printed part and a mass estimate. Frame: x forward, y left, z up, z = 0 at the front axle height."""
import math
import itertools
import numpy as np
import trimesh
import manifold3d as m

import w3_scene as S
import w3_drive_scene as DS
import layout3wd as LY
from parts import w3_chassis as C, w3_drive as D, w3_front as W

STL = "out/stl"
MONO = "out/mono3"


def _t(path, mat=None, shift=None):
    t = trimesh.load(path)
    if mat is not None:
        t.apply_transform(mat)
    if shift is not None:
        t.apply_translation(shift)
    return t


def M(rows, t=(0, 0, 0)):
    m_ = np.eye(4)
    m_[:3, :3] = rows
    m_[:3, 3] = t
    return m_


def rear_arm_mats():
    px, pz = D.XR, 0.0
    ax, az = D.RAXLE
    L = math.hypot(ax - px, az - pz)
    dx, dz = (ax - px) / L, (az - pz) / L
    nx, nz = dz, -dx
    rows = [[dx, nx, 0], [0, 0, 1], [dz, nz, 0]]
    return rows, (px, 46.0, pz), L


def assembly(phi_deg=0.0, steer=None):
    items = []
    import w3_mock
    for n, mesh, k in S.scene(phi_deg, steer=steer):
        if n.startswith(("tub_wall", "front_diff", "tire_")):
            continue
        items.append((n, mesh, k))
    items += w3_mock.mock(phi_deg, steer)
    for n, mesh in DS.placed():
        items.append((n, mesh, "printed"))
    for n in ("w3_deck_front", "w3_deck_rear"):
        items.append((n, _t(f"{STL}/{n}.stl", shift=(0, 0, C.DECK_Z[0])), "printed"))
    for n, side in (("w3_wall_left", 1), ("w3_wall_right", -1)):
        mm = np.eye(4)
        if side > 0:
            mm[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; mm[1, 3] = 51.0 + W.YS
        else:
            mm[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; mm[1, 3] = -(51.0 + W.YS)
        items.append((n, _t(f"{STL}/{n}.stl", mm), "printed"))
    for s_ in (1, -1):
        items.append((f"w3_body_post_{s_}", _t(f"{STL}/w3_body_post.stl", shift=(-18.0, s_ * 16.0, -23.0)), "printed"))
    mp = M([[0, 0, -1], [1, 0, 0], [0, -1, 0]], (-236.0, 0, 0))
    items.append(("w3_motor_plate", _t(f"{STL}/w3_motor_plate.stl", mp), "printed"))
    items.append(("w3_skid", _t(f"{STL}/w3_skid.stl", shift=(-31.0, -36.0, -29.0)), "printed"))
    rows, t0, L = rear_arm_mats()
    items.append(("w3_rear_arm", _t(f"{STL}/w3_rear_arm.stl", M(rows, t0)), "printed"))
    cov = M(rows, (t0[0], 58.0, t0[2]))
    items.append(("w3_rear_arm_cover", _t(f"{STL}/w3_rear_arm_cover.stl", cov), "printed"))
    for f in ("lid3",):
        items.append((f, _t(f"{MONO}/{f}.stl"), "printed"))
    for side in ("left", "right"):
        for part in ("front", "rear"):
            items.append((f"body3_{side}_{part}", _t(f"{MONO}/body3_{side}_{part}.stl"), "printed"))
    b = LY.blocks()
    for k in ("battery", "esc", "motor", "front_ring", "rear_ring", "rear_shaft", "front_pinion_shaft", "motor_shaft"):
        items.append((f"b_{k}", b[k], "bought"))
    return items


def mass_g(items):
    dens = 1.27e-3
    tot = 0.0
    for n, mesh, k in items:
        if k == "printed":
            tot += abs(mesh.volume) * dens
    return tot


if __name__ == "__main__":
    it = assembly(0.0)
    print(len(it), "items, printed mass about", round(mass_g(it)), "g")


def check_global(items, min_mm3=0.5, skip_bought_pairs=True):
    man = lambda t: m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
    cache = {}
    bad = []
    for (an, am, ak), (bn, bm, bk) in itertools.combinations(items, 2):
        if ak == bk == "bought":
            continue
        if S.declared(an, bn):
            continue
        if np.any(am.bounds[1] < bm.bounds[0]) or np.any(bm.bounds[1] < am.bounds[0]):
            continue
        for n, mesh in ((an, am), (bn, bm)):
            if n not in cache:
                cache[n] = man(mesh)
        v = (cache[an] ^ cache[bn]).volume()
        if v > min_mm3:
            bad.append((an, bn, round(v, 1)))
    return bad
