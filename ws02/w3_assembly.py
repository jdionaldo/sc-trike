"""WS-03 full assembly: every printed and bought part placed for a lean/steer pose, with a global interference check,
bed fit of every printed part and a mass estimate. Frame: x forward, y left, z up, z = 0 at the front axle height."""
import math
import os
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
    from parts import w3_shock as SK
    return rows, (px, 46.0 - SK.WOFF, pz), L


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
    for n in ("w3_deck_front", "w3_deck_rear", "w3_deck_tail"):
        items.append((n, _t(f"{STL}/{n}.stl", shift=(0, 0, C.DECK_Z[0] - (C.SERVO_DROP if n == "w3_deck_front" else 0.0))), "printed"))
    import parts.w3_frame as FR
    for n, mesh in FR.placed():
        items.append((n, mesh, "printed"))
    import parts.w3_tail as TL
    for n, mesh in TL.placed():
        items.append((n, mesh, "printed"))
    for s_ in (1, -1):                                                       # upper-link standoff on the pivot pin, between the wall and the link
        rows = [[1, 0, 0], [0, 0, 1], [0, -1, 0]] if s_ > 0 else [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
        items.append((f"w3_uplink_standoff_{s_}", _t(f"{STL}/w3_uplink_standoff.stl", M(rows, (-100.0, s_ * 57.6, 40.0))), "printed"))
    mp = M([[0, 0, -1], [1, 0, 0], [0, -1, 0]], (LY.MOTOR_C[0] - 29.05, 0, 0))
    items.append(("w3_motor_plate", _t(f"{STL}/w3_motor_plate.stl", mp), "printed"))
    from body3_build import NOSE_TH as th, NOSE_LOW
    sk = M([[math.cos(th), 0, math.sin(th)], [0, -1, 0], [math.sin(th), 0, -math.cos(th)]], (NOSE_LOW[0], 0.0, NOSE_LOW[1]))
    import json
    sm = trimesh.load(f"{STL}/w3_skid.stl")
    sm.apply_translation((0.0, 0.0, -json.loads(open(f"{STL}/w3_skid_lift.json").read())))
    sm.apply_transform(sk)
    items.append(("w3_skid", sm, "printed"))
    rows, t0, L = rear_arm_mats()
    items.append(("w3_rear_arm", _t(f"{STL}/w3_rear_arm.stl", M(rows, t0)), "printed"))
    for part in ("front", "mid", "rear"):
        if os.path.exists(f"{MONO}/body3_{part}.stl"):                          # absent while the body is being rebuilt (the body build itself calls the assembly)
            items.append((f"body3_{part}", _t(f"{MONO}/body3_{part}.stl"), "printed"))
    b = LY.blocks()
    for k in ("battery", "motor", "front_ring", "rear_ring", "rear_shaft", "front_pinion_shaft", "motor_shaft"):
        items.append((f"b_{k}", b[k], "bought"))
    import mono_build as MB
    from parts import w3_shock as SK
    items.append(("b_rear_shock", MB.to_trimesh(SK.shock_manifold(0.0)), "bought"))     # stock 1/10 coilover, left side, at rest
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
