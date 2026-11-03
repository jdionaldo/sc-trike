"""WS-03 skin swing-open check: the skin (both body pieces, welded in place) rotates about the nose hinge pin (axis along y at HINGE_PIN) so the rear lifts
and flips forward.  Reports, per angle, which fixed parts the skin would hit, and builds the channels (swept cut-outs) that let it open."""
import sys
import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
import parts.w3_frame as FR

XH, ZH = FR.HINGE_PIN
ANGLES = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0]


def rot(m, deg):
    """Rotate a Manifold about the hinge axis (positive = rear goes up)."""
    a = np.radians(deg)
    R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    T = np.array([XH - R[0, 0] * XH - R[0, 2] * ZH, 0.0, ZH - R[2, 0] * XH - R[2, 2] * ZH])
    return m.transform(np.hstack([R, T[:, None]]))


def load_body():
    bodies = [MB.man(trimesh.load(f"out/mono3/body3_{p}.stl")) for p in ("front", "mid", "rear")]
    import w3_assembly as A
    wing = [MB.man(m) for n, m, k in A.assembly(0.0, 0.0) if n.startswith("w3_tail")]
    out = bodies[0] + bodies[1] + bodies[2]
    for w in wing:
        out = out + w
    return out


def fixed_parts():
    import w3_assembly as A
    return [(n, MB.man(m)) for n, m, k in A.assembly(0.0, 0.0) if not n.startswith(("body3", "w3_tail"))]      # the wing is screwed to the skin and swings with it


def report():
    body = load_body()
    parts = fixed_parts()
    rows = []
    for ang in [0.0] + ANGLES:
        b = rot(body, ang)
        hits = []
        for n, p in parts:
            v = (b ^ p).volume()
            if v > 0.5:
                hits.append((n, round(v, 1)))
        rows.append((ang, hits))
        print(ang, hits[:12], flush=True)
    return rows


if __name__ == "__main__":
    report()


THETA_MAX = 35.0
STEP = 0.25


def swing_channels(theta_max=THETA_MAX, step=STEP):
    """Union, in the skin's frame, of the frame tubes (grown 0.8 mm, the same solids that give the static slots) over the whole opening: subtracting it from the
    skin leaves open-ended channels the tubes slide out of as the skin swings up."""
    rel = FR.relief() + FR.frame()                               # grown tubes plus the pads, lugs and plates (the real frame solid)
    for n, m in fixed_parts():                                   # inner printed parts the skin's lower rear (below the hinge axis it swings rearward) would also hit
        if n in ("w3_rbc_upper", "w3_rbc_lower", "w3_deck_front", "b_rear_shaft", "b_rear_shock"):
            rel = rel + m
    for n, m in fixed_parts():                                   # the rear arm lies against the wall's lower part: carve it (and a 0.4 mm margin) at rest and along the swing
        if n == "w3_rear_arm":
            for d in ((0, 0, 0), (0, .4, 0), (0, -.4, 0), (0, 0, .4), (0, 0, -.4), (.4, 0, 0), (-.4, 0, 0)):
                rel = rel + m.translate(d)
    acc = rel
    n = int(theta_max / step)
    for k in range(1, n + 1):
        acc = acc + rot(rel, -k * step)                       # the tubes seen from the skin rotate the other way
    return acc


def check_fine(body, parts, theta_max=THETA_MAX, step=1.0, names=("w3_frame",)):
    worst = []
    k = 0
    while k * step <= theta_max:
        b = rot(body, k * step)
        for n, p in parts:
            if n.startswith(names):
                v = (b ^ p).volume()
                if v > 0.5:
                    worst.append((k * step, n, round(v, 1)))
        k += 1
    return worst


from parts.w3_drive import XR as XP          # rear pivot (stretched)
ZP = 0.0              # rear swing-arm pivot (the rear bevel axis)


def rot_pivot(m, deg):
    """Rotate a Manifold about the rear arm pivot (axis along y); positive = the wheel goes up."""
    a = np.radians(deg)
    R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    T = np.array([XP - (R[0, 0] * XP + R[0, 2] * ZP), 0.0, ZP - (R[2, 0] * XP + R[2, 2] * ZP)])
    return m.transform(np.hstack([R, T[:, None]]))


def rear_travel_channels(up_mm=25.0, down_mm=20.0, margin=3.0):
    """Skin cut-out for the rear wheel's travel: the tyre (grown by `margin`) and the arm swept about the pivot from `down_mm` below to `up_mm` above rest."""
    import math
    tc = [m for n, m, k in __import__("w3_assembly").assembly(0.0, 0.0) if n == "mock_rear_tire_ring"][0]
    cx, cz = 0.5 * (tc.bounds[0][0] + tc.bounds[1][0]), 0.5 * (tc.bounds[0][2] + tc.bounds[1][2])
    rad = 0.5 * (tc.bounds[1][0] - tc.bounds[0][0]) + margin
    wid = tc.bounds[1][1] - tc.bounds[0][1] + 2 * margin
    env = Manifold.cylinder(wid, rad, rad, 64).rotate((-90.0, 0.0, 0.0)).translate((cx, tc.bounds[0][1] - margin, cz))
    arms = [MB.man(m) for n, m, k in __import__("w3_assembly").assembly(0.0, 0.0) if n == "w3_rear_arm"][0]
    arm_env = arms + arms.translate((0, 0.4, 0)) + arms.translate((0, -0.4, 0)) + arms.translate((0, 0, 0.4)) + arms.translate((0, 0, -0.4))
    r_arm = math.hypot(cx - XP, cz - ZP)
    a0, a1 = -math.degrees(math.asin(down_mm / r_arm)), math.degrees(math.asin(up_mm / r_arm))
    # the arm's inner face lies inside the skin wall at the pivot; clear the wall right through around the hub so no sliver of wall is left
    pad = Manifold.cylinder(42.0, 13.0, 13.0, 48).rotate((-90.0, 0.0, 0.0)).translate((XP, 38.0, ZP))
    arm_env = arm_env + pad
    for n, m, k in __import__("w3_assembly").assembly(0.0, 0.0):                                  # the belt and its pulleys move with the arm too
        if n in ("mock_rear_belt", "mock_rear_pulley_pivot", "mock_rear_pulley_axle"):
            bm = MB.man(m)
            arm_env = arm_env + bm + bm.translate((0, 0.4, 0)) + bm.translate((0, -0.4, 0))
    acc = None
    for k in range(int(a0), int(a1) + 2):
        for part in (env, arm_env):
            p = rot_pivot(part, float(k))
            acc = p if acc is None else acc + p
    from parts import w3_shock as SK                                           # the coilover's envelope over the travel (the shock is not rigid with the arm)
    for k in range(int(a0), int(a1) + 2):
        sh = SK.shock_manifold(float(k))
        acc = acc + sh + sh.translate((0, 0, 0.4)) + sh.translate((0, 0, -0.4))
    return acc
