"""WS-03 tubular space frame under the skin (replaces the flat servo walls).

6 mm printed tubes on angled paths: a side ladder in the plane |y| = 57.5 (servo, diff-case ear and pivot-pin pads, in the same places the
walls had them), a pivot hoop over the top at x = -100, a swept rail back to a rear hoop under the hood, and a lower rail back to the rear.
Skin tabs: pads with M2.5 holes under bosses on the roof and hood.  Built in assembly coordinates (z = 0 at the front axle height) as one
mesh, split into four pieces (left/right, front/rear at x = -175) that fit the bed; every STL is shifted up in z (DZ) so z min is near the bed.
"""
import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart

R = 3.0                      # tube radius (6 mm OD)
Y0, Y1 = 54.6, 57.6          # ladder pad thickness (outer face of the servos / diff case ears at 54.5)
YT = 57.6                    # ladder tube centre
DZ = {"front": 30.0, "rear": 14.0}      # STL z shift per piece (print frame, z min near the bed)
XS = -175.0                  # split across x
HEAD = 3.0                   # screw-head clearance radius
PIVOT = (-100.0, 40.0)
SKIN_TABS = []               # (x, y, z of pad top) filled by build(); used by the body generator


def _zt(x):
    from body3_build import top_z, WALL
    return top_z(x, WALL)


def tube(a, b, r=R, trim_a=0.0, trim_b=0.0):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    u = d / L
    a2, b2 = a + u * trim_a, b - u * trim_b
    L2 = L - trim_a - trim_b
    T = trimesh.geometry.align_vectors([0.0, 0.0, 1.0], u)
    mat = np.array(T[:3, :4])
    mat[:, 3] = a2
    return Manifold.cylinder(L2, r, r, 28).transform(mat)


def ball(p, r=R):
    return Manifold.sphere(r, 28).translate(tuple(p))


def _disc(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2, d / 2, 40).rotate((-90.0, 0.0, 0.0)).translate((x, y0, z))


def _vcyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, 28).translate((x, y, z0))


def _stadium(x, z0, z1, y0, y1, r):
    return _disc(x, z0, y0, y1, 2 * r) + _disc(x, z1, y0, y1, 2 * r) + MB.prism_xz([(x - r, z0), (x + r, z0), (x + r, z1), (x - r, z1)], y0, y1)


def _tab_pos():
    """Skin tab stations (x, y, node z): hoop top, mid rail, hood.  Node z = skin underside - 12 (roof), 40.4 (hood)."""
    return [(-100.0, 30.0, _zt(-100.0) - 12.0), (-180.0, 36.0, _zt(-180.0) - 12.0), (-262.0, 38.0, 40.4)]


def frame():
    tabs = _tab_pos()
    (hx, hy, hz), (mx, my, mz), (rx, ry, rz) = tabs
    PE1, PS2, PM, PS1 = (-150.0, YT, -10.0), (-135.9, YT, -14.0), (-86.0, YT, -16.5), (-35.5, YT, -18.8)
    PL = (PIVOT[0], YT, PIVOT[1])
    FN = (-25.0, YT, 28.0)
    R1 = (-246.0, 52.0, -10.0)
    HT, MU, R2 = (hx, hy, hz), (mx, my, mz), (rx, ry, rz)
    PHe = (hx, 53.0, PIVOT[1])
    h = Manifold()
    parts = []
    # side ladder pads
    parts += [_disc(PE1[0], PE1[2], Y0, Y1, 15.0)]
    parts += [_stadium(PS2[0], -19.0, -9.0, Y0, Y1, 4.5), _stadium(PS1[0], -23.8, -13.8, Y0, Y1, 4.5)]
    parts += [MB.prism_xz([(-92.0, -29.0), (-79.0, -29.0), (-79.0, -5.0), (-92.0, -5.0)], Y0, Y1)]
    parts += [_disc(PL[0], PL[2], Y0, Y1, 16.0), _disc(PL[0], PL[2], 46.0, Y0, 16.0)]
    # ladder tubes (angular fan to the pivot pad)
    for a, b, ta, tb in ((PE1, PS2, 0, 0), (PS2, PM, 0, 0), (PM, PS1, 0, 0), (PS2, PL, 0, 6.0), (PS1, FN, 0, 0), (FN, PL, 0, 6.0)):
        parts.append(tube(a, b, R, ta, tb))
    # lower rail to the rear and the diagonal up to the hood tab
    B1 = (-200.0, YT, -10.0)
    parts += [ball(FN), tube(PE1, B1), ball(B1), tube(B1, R1), ball(R1), tube(R1, R2), ball(R2)]
    # hoop: leg to the pivot pad, shallow arch over the top, rail aft
    parts += [tube(HT, PHe, R, 0, 6.0), ball(HT), tube(HT, (hx, 0.0, hz)), tube(HT, MU), ball(MU), tube(MU, R2), tube(R2, (rx, 0.0, rz))]
    # skin tab pads (screw up into the bosses on the skin)
    for (x, y, z) in tabs:
        parts.append(_vcyl(x, y, z + 1.0, z + 5.0, 9.0))
    side = Manifold.batch_boolean(parts, 0) if hasattr(Manifold, "batch_boolean") else None
    if side is None:
        side = parts[0]
        for p in parts[1:]:
            side = side + p
    # holes
    cuts = []
    for x, z in ((-150.0, -10.0),):
        cuts.append(_disc(x, z, Y0 - 0.1, Y1 + 4.0, 2.7))
    for x, z in ((-135.9, -19.0), (-135.9, -9.0), (-35.5, -23.8), (-35.5, -13.8), (-86.9, -19.0), (-86.5, -9.5), (-84.5, -23.8), (-84.5, -13.8)):
        cuts.append(_disc(x, z, Y0 - 0.1, Y1 + 4.0, 2.4))
        cuts.append(_disc(x, z, Y1, Y1 + 4.0, 2 * HEAD))
    cuts.append(_disc(PL[0], PL[2], 45.0, Y1 + 0.1, 3.4))
    for (x, y, z) in tabs:
        cuts.append(_vcyl(x, y, z, z + 6.0, 2.7))
    for c in cuts:
        side = side - c
    both = side + side.mirror((0.0, 1.0, 0.0))
    return both


_CACHE = {}


def piece(name):
    if "f" not in _CACHE:
        _CACHE["f"] = frame()
    f = _CACHE["f"]
    sgn = 1 if "_left_" in name else -1
    sx = 1 if name.endswith("front") else -1
    ybox = Manifold.cube((2000.0, 1000.0, 2000.0), center=True).translate((0, sgn * 500.0 + sgn * 0.013, 0))
    xbox = Manifold.cube((400.0, 400.0, 400.0), center=True).translate((XS + sx * 200.0 + sx * 0.05, 0, 0))
    m = MB.to_trimesh(f ^ ybox ^ xbox)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    m.apply_translation((0.0, 0.0, DZ["front" if sx > 0 else "rear"]))
    return m


NAMES = ["w3_frame_left_front", "w3_frame_left_rear", "w3_frame_right_front", "w3_frame_right_rear"]


def build(p):
    return [MeshPart(n, (lambda n=n: piece(n)), walls=False, supports=True) for n in NAMES]


def placed():
    """Assembly-frame meshes of the four pieces: (name, mesh)."""
    out = []
    for n in NAMES:
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_translation((0.0, 0.0, -DZ["front" if n.endswith("front") else "rear"]))
        out.append((n, m))
    return out


def relief():
    """Tubes and nodes grown by 0.8 mm (no pads, no tab pads): subtracted from the skin where tubes pass through it."""
    tabs = _tab_pos()
    (hx, hy, hz), (mx, my, mz), (rx, ry, rz) = tabs
    rr = R + 0.8
    PE1, PS2, PM, PS1 = (-150.0, YT, -10.0), (-135.9, YT, -14.0), (-86.0, YT, -16.5), (-35.5, YT, -18.8)
    PL, FN, R1 = (PIVOT[0], YT, PIVOT[1]), (-25.0, YT, 28.0), (-246.0, 52.0, -10.0)
    HT, MU, R2, PHe = (hx, hy, hz), (mx, my, mz), (rx, ry, rz), (hx, 53.0, PIVOT[1])
    ts = [tube(PE1, PS2, rr), tube(PS2, PM, rr), tube(PM, PS1, rr), tube(PS2, PL, rr, 0, 6.0), tube(PS1, FN, rr), tube(FN, PL, rr, 0, 6.0),
          tube(PE1, (-200.0, YT, -10.0), rr), tube((-200.0, YT, -10.0), R1, rr), tube(R1, R2, rr), ball((-200.0, YT, -10.0), rr), tube(HT, PHe, rr, 0, 6.0), tube(HT, (hx, 0.0, hz), rr), tube(HT, MU, rr), tube(MU, R2, rr), tube(R2, (rx, 0.0, rz), rr),
          ball(R1, rr), ball(R2, rr), ball(HT, rr), ball(MU, rr), ball(FN, rr)]
    ts.append(_disc(PL[0], PL[2], 45.0, Y0, 17.6))
    h = ts[0]
    for t in ts[1:]:
        h = h + t
    return h + h.mirror((0.0, 1.0, 0.0))
