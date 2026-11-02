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
    bodies = [MB.man(trimesh.load(f"out/mono3/body3_{p}.stl")) for p in ("front", "rear")]
    import w3_assembly as A
    wing = [MB.man(m) for n, m, k in A.assembly(0.0, 0.0) if n.startswith("w3_tail")]
    out = bodies[0] + bodies[1]
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
        if n in ("w3_rbc_upper", "w3_rbc_lower", "w3_deck_front", "b_rear_shaft"):
            rel = rel + m
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
