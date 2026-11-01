"""WS-03 front end scene: places the printed parts and bought blocks for a lean angle and checks interference."""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import brentq

import front3wd as F
import layout3wd as LY
from parts import w3_front as W

STL = Path("out/stl")
from params import P as _P
RODT = _P.rod_t
R_H, LR_LEAN = 28.0, None                      # lean horn length
STEER_MAX = 17.0
LEAN_MAX = 25.0
SH_LEAN = np.array([-71.4, -18.8])     # lean horn shaft (x, z), from the horn scan (worst horn angle 29 deg)
LR = 30.0
R_S = 12.0
I0 = np.array([F.P[0] + W.ARM_A[0], W.ARM_A[2]])                     # steer rod inner point at rest (x, z)
SIGN = -1.0                                   # +1: steer horn shaft below the rod inner point, -1: above
SH_STEER = np.array([I0[0], I0[1] - SIGN * R_S])
HORN_Y = (54.7 + W.YS, 57.0 + W.YS)
SERVO_Y = (28.7 + W.YS, 48.0 + W.YS)


def solve_psi(f):
    g = np.linspace(-1.6, 1.6, 321)
    v = [f(x) for x in g]
    roots = [g[i] for i in range(len(g)) if abs(v[i]) < 1e-9] + [brentq(f, g[i], g[i + 1]) for i in range(len(g) - 1) if v[i] * v[i + 1] < 0]
    if not roots:
        raise ValueError("no horn solution")
    return min(roots, key=abs)


def T(*d):
    m = np.eye(4)
    m[:3, 3] = d
    return m


def Ry(theta, about):
    """Rotate in the x-z plane by theta (up positive) about the point (x, z)."""
    c, s = math.cos(theta), math.sin(theta)
    m = np.eye(4)
    m[:3, :3] = [[c, 0, -s], [0, 1, 0], [s, 0, c]]
    return T(about[0], 0, about[1]) @ m @ T(-about[0], 0, -about[1])


def Rz(a, about):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    return T(about[0], about[1], 0) @ m @ T(-about[0], -about[1], 0)


def load(name, m):
    t = trimesh.load(STL / f"{name}.stl")
    t.apply_transform(m)
    return t


def flat_box(c, size):
    b = trimesh.creation.box(extents=size)
    b.apply_translation(c)
    return b


def rod_mesh(name, p0, p1, up):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    e1 = (p1 - p0) / np.linalg.norm(p1 - p0)
    e3 = np.asarray(up, float) - e1 * (np.asarray(up, float) @ e1)
    e3 /= np.linalg.norm(e3)
    e2 = np.cross(e3, e1)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = e1, e2, e3
    m[:3, 3] = p0 - e3 * RODT / 2
    return load(name, m)


def horn_mesh(shaft_xz, tip_xz, y):
    a = np.array([shaft_xz[0], y[0], shaft_xz[1]]); b = np.array([tip_xz[0], y[1], tip_xz[1]])
    L = np.linalg.norm(tip_xz - shaft_xz)
    box = trimesh.creation.box(extents=(L + 6.0, y[1] - y[0], 7.0))
    box.apply_translation(((L) / 2, 0, 0))
    ang = math.atan2(tip_xz[1] - shaft_xz[1], tip_xz[0] - shaft_xz[0])
    c, s = math.cos(ang), math.sin(ang)
    r = np.eye(4); r[:3, :3] = [[c, 0, -s], [0, 1, 0], [s, 0, c]]
    box.apply_transform(r)
    box.apply_translation((shaft_xz[0], (y[0] + y[1]) / 2, shaft_xz[1]))
    return box


def tip_at(shaft, r, psi, rest, sign=1.0):
    q = psi + rest
    return shaft + r * np.array([-math.sin(q) * sign, math.cos(q)])


def scene(phi_deg, steer=None):
    phi = math.radians(phi_deg)
    th = dict(zip((1, -1), F.arm_angles(phi)))
    delta = math.radians(max(-STEER_MAX, min(STEER_MAX, phi_deg * STEER_MAX / LEAN_MAX))) if steer is None else math.radians(steer)
    items = []
    lug0 = F.P + np.array(W.LUG)
    # rest geometry for the lean rod: horn at rest angle -40 deg, rod length fixed by the rest pose
    rest = math.radians(-40.0)
    lr = LR
    for s in (1, -1):
        t = th[s]
        kx, kz = F.P[0] + F.LA * math.cos(t), F.LA * math.sin(t)
        ma = Ry(t, F.P) @ W.mats(s, W.ARM_Y[0])
        items.append((f"arm_{s}", load(f"w3_arm_{'left' if s > 0 else 'right'}", ma), "printed"))
        mc = Ry(t, F.P) @ W.mats(s, W.COVER_Y[0])
        items.append((f"cover_{s}", load(f"w3_arm_cover_{'left' if s > 0 else 'right'}", mc), "printed"))
        mu = Ry(t, (F.P[0], W.ZU)) @ W.mats(s, W.UP_Y[0])
        items.append((f"uplink_{s}", load(f"w3_uplink_{'left' if s > 0 else 'right'}", mu), "printed"))
        car = T(kx, 0, kz) @ W.mats(s, W.CAR_Y[0])
        items.append((f"carrier_{s}", load(f"w3_carrier_{'left' if s > 0 else 'right'}", car), "printed"))
        wm = np.eye(4)
        wm[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, 1, 0]]                       # print (u, v, w) = (x, z + 4, |y| - 99); flat plate, so the mirror is the same part flipped
        if s < 0:
            wm[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
        wm[1, 3] = s * (W.CAR_Y[0] - 3.0)
        wm[2, 3] = -4.0
        wing = load("w3_wing_left", T(kx, 0, kz) @ wm)
        items.append((f"wing_{s}", wing, "printed"))
        km = np.eye(4)
        if s > 0:
            km[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; km[1, 3] = W.KN_Y[1]
        else:
            km[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; km[1, 3] = -W.KN_Y[1]
        kn = T(kx, 0, kz) @ Rz(delta, (0.0, s * W.KP_Y)) @ km
        items.append((f"knuckle_{s}", load(f"w3_knuckle_{'left' if s > 0 else 'right'}", kn), "printed"))
        # wheel (bought), steered with the knuckle
        wheel = LY.cyl((0, s * (F.T), 0), F.R, F.W, "y")
        wheel.apply_transform(T(kx, 0, kz) @ Rz(delta, (0.0, s * W.KP_Y)))
        items.append((f"tire_{s}", wheel, "bought"))
        # lean servo, horn and rod (horn angle solved for this arm angle)
        a = math.atan2(W.LUG[1], W.LUG[0]); rho = math.hypot(*W.LUG)
        lug = F.P + rho * np.array([math.cos(a + t), math.sin(a + t)])
        f = lambda psi: np.linalg.norm(tip_at(SH_LEAN, R_H, psi, rest) - lug) - lr
        psi = solve_psi(f)
        tip = tip_at(SH_LEAN, R_H, psi, rest)
        yh = (s * HORN_Y[0], s * HORN_Y[1]) if s > 0 else (s * HORN_Y[1], s * HORN_Y[0])
        items.append((f"lean_horn_{s}", horn_mesh(SH_LEAN, tip, tuple(sorted((s * HORN_Y[0], s * HORN_Y[1])))), "bought"))
        items.append((f"lean_servo_{s}", flat_box(((SH_LEAN[0] + 11.4), s * (SERVO_Y[0] + SERVO_Y[1]) / 2, SH_LEAN[1]),
                                                  (40.0, SERVO_Y[1] - SERVO_Y[0], 20.0)), "bought"))
        # steer: tie rod from the knuckle arm point to the steer horn tip
        kp = np.array([kx, s * W.KP_Y, kz])
        a_pt = kp + Rz(delta, (0, 0))[:3, :3] @ np.array([W.ARM_A[0], s * W.ARM_A[1], W.ARM_A[2]])
        tip_y = 56.0 + W.YS
        L_t = float(np.linalg.norm(np.array([W.ARM_A[0], W.KP_Y + W.ARM_A[1], W.ARM_A[2]]) - np.array([I0[0], tip_y, I0[1]])))
        g = lambda ps: np.linalg.norm(np.array([SH_STEER[0] + R_S * math.sin(ps), s * tip_y, SH_STEER[1] + SIGN * R_S * math.cos(ps)]) - a_pt) - L_t
        try:
            ps = solve_psi(g)
        except ValueError:
            ps = float("nan")
        ts = np.array([SH_STEER[0] + R_S * math.sin(ps), SH_STEER[1] + SIGN * R_S * math.cos(ps)])
        items.append((f"steer_horn_{s}", horn_mesh(SH_STEER, ts, tuple(sorted((s * HORN_Y[0], s * HORN_Y[1])))), "bought"))
        items.append((f"steer_servo_{s}", flat_box((SH_STEER[0] - 11.4, s * (SERVO_Y[0] + SERVO_Y[1]) / 2, SH_STEER[1]),
                                                   (40.0, SERVO_Y[1] - SERVO_Y[0], 20.0)), "bought"))
        items.append((f"tub_wall_{s}", flat_box((-105, s * (49.0 + W.YS), -5), (170.0, 2.0, 78.0)), "bought"))
        items.append((f"diff_out_{s}", LY.cyl((F.P[0], s * (33.0 + W.YS / 2), 0), 2.5, 66.0 + W.YS, "y"), "bought"))
        items.append((f"tip_shaft_{s}", LY.cyl((kx, s * (86.0 + W.YS / 2), kz), 2.0, 74.0 - W.YS, "y"), "bought"))
        if not math.isnan(ps):
            items.append((f"tie_rod_{s}", rod_mesh("w3_tie_rod", [ts[0], s * tip_y, ts[1]], [a_pt[0], a_pt[1], a_pt[2]], (0, 0, 1)), "printed"))
        items.append((f"lean_rod_{s}", rod_mesh("w3_lean_rod", [tip[0], s * (55.0 + W.YS), tip[1]], [lug[0], s * (55.0 + W.YS), lug[1]], (0, 1, 0)), "printed"))
    items.append(("front_diff", LY.cyl((F.P[0], 0, 0), 19, 38, "y"), "bought"))
    return items


OK_PAIRS = [("mock_axle", "knuckle"), ("mock_joint", "knuckle"), ("mock_joint", "carrier"), ("mock_hub", "knuckle"), ("mock_rimdisc", "knuckle"), ("mock_tire", "knuckle"), ("mock_rim", "knuckle"), ("wing", "tip_shaft"), ("wing", "carrier"), ("tip_shaft", "carrier"), ("tip_shaft", "knuckle"), ("tip_shaft", "tire"), ("tip_shaft", "arm"), ("tip_shaft", "cover"),
            ("diff_out", "arm"), ("diff_out", "tub_wall"), ("diff_out", "front_diff"), ("diff_out", "cover"),
            ("tire", "knuckle"), ("lean_rod", "lean_horn"), ("tie_rod", "steer_horn"), ("lean_rod", "arm"),
            ("tie_rod", "knuckle"), ("tire", "carrier")]


def declared(a, b):
    n = lambda x: x.rsplit("_", 1)[0]
    return any({n(a), n(b)} == {p, q} for p, q in OK_PAIRS)


def check(items):
    import manifold3d as m

    def man(t):
        return m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))

    bad = []
    for (an, am, ak), (bn, bm, bk) in itertools.combinations(items, 2):
        if ak == bk == "bought" or declared(an, bn):
            continue
        if np.any(am.bounds[1] < bm.bounds[0]) or np.any(bm.bounds[1] < am.bounds[0]):
            continue
        v = (man(am) ^ man(bm)).volume()
        if v > 0.5:
            bad.append((an, bn, round(v, 1)))
    return bad


if __name__ == "__main__":
    for ph in ([float(a) for a in sys.argv[1:]] or [0.0, 15.0, 30.0, -30.0]):
        print("lean", ph, check(scene(ph)))
