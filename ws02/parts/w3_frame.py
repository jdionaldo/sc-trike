"""WS-03 tubular space frame under the skin (replaces the flat servo walls).

6 mm printed tubes on angled paths: a side ladder in the plane |y| = 57.5 (servo, diff-case ear and pivot-pin pads, in the same places the
walls had them), a pivot hoop over the top at x = -100, a swept rail back to a rear hoop under the hood, and a lower rail back to the rear.
Skin tabs: pads with M2.5 holes under bosses on the roof and hood.  Built in assembly coordinates (z = 0 at the front axle height) as one
mesh, split into four pieces (left/right, front/rear at x = -175) that fit the bed; every STL is shifted up in z (DZ) so z min is near the bed.
"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart
from w3_stretch import fx, back, pv

R = 3.0                      # tube radius (6 mm OD)
Y0, Y1 = 54.6, 57.6          # ladder pad thickness (outer face of the servos / diff case ears at 54.5)
YT = 57.6                    # ladder tube centre
DZ = {"front": 30.0, "rear": 24.0}      # STL z shift per piece (print frame, z min near the bed)
XS = -175.0                  # split across x
HEAD = 2.9                   # screw-head clearance radius
PIVOT = (-100.0, 40.0)
HINGE = ((16.0, 26.8), (23.6, 33.0))      # lug plate extent (x range, z range)
HINGE_LUG = (9.5, 14.0)                   # lug plate |y| range (4.5 mm thick: the inboard face is free of the skin)
HINGE_EAR = (14.2, 17.2)                  # skin ear |y| range (beside the lug)
HINGE_PIN = (21.4, 29.5)                  # pin axis (x, z), along y
HINGE_D = 3.2
RELIEF_G = 0.35                           # clearance around tubes where they pass through the skin (tight: the skin is sealed around them)
MAG_D = 6.3                               # magnet pocket diameter (6 mm disc, 2 mm thick)
FOOT_Z = -23.0               # top of the base plate
TAB_PAD = (2.5, 6.5)         # skin-tab pad z range above the node z
TAB_PAD_D = 10.4             # hood-tab pad diameter (1.05 mm of wall round the 6.3 mm magnet pocket would be too thin at 9)
TAB_BOSS = 6.8               # boss on the skin starts this far above the node z


def _zt(x):
    from body3_build import top_z, WALL
    return top_z(x, WALL)


def tube(a, b, r=R, trim_a=0.0, trim_b=0.0):
    """Round tube with spherical ends (except where an end is trimmed back to a pad), so no joint is ever open."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    u = d / L
    a2, b2 = a + u * trim_a, b - u * trim_b
    L2 = L - trim_a - trim_b
    T = trimesh.geometry.align_vectors([0.0, 0.0, 1.0], u)
    mat = np.array(T[:3, :4])
    mat[:, 3] = a2
    m = Manifold.cylinder(L2, r, r, 40).transform(mat)
    if trim_a == 0.0:
        m = m + Manifold.sphere(r, 36).translate(tuple(a2))
    if trim_b == 0.0:
        m = m + Manifold.sphere(r, 36).translate(tuple(b2))
    return m


def ball(p, r=R):
    return Manifold.sphere(r, 36).translate(tuple(p))


def _disc(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2, d / 2, 40).rotate((-90.0, 0.0, 0.0)).translate((x, y0, z))


def _vcyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, 28).translate((x, y, z0))


def _rrect_xz(x0, x1, z0, z1, r, y0, y1):
    """Plate in the x-z plane with rounded corners (radius r), y0..y1."""
    return Manifold.batch_hull([_disc(x, z, y0, y1, 2 * r) for x in (x0 + r, x1 - r) for z in (z0 + r, z1 - r)])


def _tab_pos():
    """Skin tab stations (x, y, node z): front roof, hoop top, mid rail, hood.  Node z = skin underside - 13.5 (roof), 39.4 (hood)."""
    return [(-29.0, 28.0, _zt(-29.0) - 13.5), (-100.0, 30.0, _zt(-100.0) - 13.5), (-180.0, 36.0, _zt(-180.0) - 13.5), (back(-262.0), 38.0, 39.4)]


def nodes():
    """Node coordinates for the +y half (the other half is the mirror image); y = 0 nodes are shared."""
    (fx, fy, fz), (hx, hy, hz), (mx, my, mz), (rx, ry, rz) = _tab_pos()
    Y = YT
    from body3_build import NOSE_TH, NOSE_LOW
    inw = np.array([-math.sin(NOSE_TH), math.cos(NOSE_TH)])                  # inward normal of the nose underside
    def nose(u):
        px, pz = NOSE_LOW[0] + u * math.cos(NOSE_TH) + inw[0] * 4.2, NOSE_LOW[1] + u * math.sin(NOSE_TH) + inw[1] * 4.2
        return (px, 22.0, pz)
    return {"BT": (24.0, 28.0, 22.0), "CBT": (24.0, 0.0, 22.0), "NA": nose(10.0), "NB": nose(28.0), "FS": (-8.0, 22.0, -19.5), "PE1": (-150.0, Y, -10.0), "PS2": (-135.9, Y, -14.0), "PM": (-86.0, Y, -16.5), "PS1": (-35.5, Y, -18.8), "PL": (PIVOT[0], Y, PIVOT[1]), "FN": (-25.0, Y, 28.0),
            "B1": (-200.0, 59.0, -10.0), "R1": (pv(-246.0), 52.0, -10.0), "HT": (hx, hy, hz), "PH": (hx, 53.0, PIVOT[1]), "MU": (mx, my, mz), "R2": (rx, ry, rz),
            "C100": (hx, 0.0, hz), "C262": (rx, 0.0, rz), "FT": (fx, fy, fz), "C29": (fx, 0.0, fz), "XN": (0.5 * (mx + rx), 0.0, 0.5 * (mz + rz) + 0.5 * 0.0 + 0.0),
            "RW": (pv(-262.0), 40.5, 30.0), "R2m": (rx, -ry, rz), "PHm": (hx, -53.0, PIVOT[1]), "C40": (hx, 0.0, PIVOT[1]), "XH": (hx, 0.0, hz - (30.0 / 83.0) * (hz - PIVOT[1])),
            "HT2": (-135.9, hy + (my - hy) * 0.449, hz + (mz - hz) * 0.449), "K1": (-135.9, 38.5, 25.0),
            "R3": (-200.0, my + (ry - my) * 0.244, mz + (rz - mz) * 0.244), "K2": (-200.0, 52.0, 28.0),
            "FP1": (-135.9, 44.0, -20.0), "FPB": (-200.0, 52.5, -19.0), "FPR": (pv(-250.0), 41.5, -19.0), "FPF": (-35.5, 28.0, -19.5)}


# (a, b, tube radius, trim at a, trim at b): angled tubes only; the roof members are thicker (inboard, no clearance problem)
EDGES = [("PE1", "PS2", 4.5, 0, 0), ("PS2", "PM", 4.5, 0, 0), ("PM", "PS1", 4.5, 0, 0), ("PS2", "PL", 4.5, 0, 6.0), ("PE1", "PL", 4.5, 0, 6.0),
         ("PS1", "FN", 4.5, 0, 0), ("FN", "PL", 4.5, 0, 6.0),
         ("PS2", "FP1", 3.0, 0, 0), ("B1", "FPB", 5.5, 0, 0), ("R1", "FPR", 5.5, 0, 0), ("PS1", "FPF", 3.5, 0, 0),
         ("PE1", "B1", 5.5, 7.0, 0), ("B1", "R1", 5.5, 0, 0), ("R1", "RW", 4.5, 0, 0), ("RW", "R2", 4.5, 0, 0),
         ("HT", "PH", 5.5, 0, 6.0), ("PH", "PL", 6.0, 0, 0), ("HT", "C100", 5.5, 0, 0), ("HT", "HT2", 5.5, 0, 0), ("HT2", "MU", 5.5, 0, 0), ("MU", "R3", 5.5, 0, 0), ("R3", "R2", 5.5, 0, 0), ("R2", "C262", 5.5, 0, 0),
         ("MU", "XN", 4.5, 0, 0), ("XN", "R2m", 4.5, 0, 0),
         ("PH", "C40", 4.5, 6.0, 0), ("HT", "XH", 3.5, 0, 0), ("XH", "PHm", 3.5, 0, 6.0),
         ("FT", "C29", 5.5, 0, 0), ("FT", "HT", 5.5, 0, 0), ("FT", "FN", 4.5, 0, 0),
         ("NB", "BT", 3.5, 0, 0), ("FN", "BT", 4.0, 0, 0), ("FT", "BT", 4.5, 0, 0), ("BT", "CBT", 5.5, 0, 0), ("FS", "NA", 3.5, 0, 0), ("NA", "NB", 3.0, 0, 0), ("FP1", "K1", 3.0, 0, 0), ("K1", "HT2", 3.0, 0, 0), ("R3", "K2", 5.5, 0, 0), ("K2", "FPB", 5.5, 0, 0)]
BALLS = {"BT": 5.5, "FS": 3.5, "XH": 3.5, "C40": 4.5, "R1": 5.5, "RW": 4.5, "R2": 5.5, "HT": 5.5, "MU": 5.5, "FN": 4.5, "B1": 5.5, "FT": 5.5, "XN": 4.5, "FP1": 3.0, "FPB": 5.5, "FPR": 5.5, "FPF": 3.5, "HT2": 5.5, "K1": 3.0, "R3": 5.5, "K2": 5.5}
FEET = {"FS": 8.0, "FP1": 7.0, "FPB": 11.5, "FPR": 11.5, "FPF": 10.0}      # foot pad diameters, screwed down into the base plate


def frame(relief=False):
    N = nodes()
    g = RELIEF_G if relief else 0.0
    parts = []
    for a, b, r, ta, tb in EDGES:
        nc = (a, b) == ("PH", "PL")                                              # the pivot pad stack: a plain cylinder, no rounded ends
        parts.append(tube(N[a], N[b], r + g, ta + (1e-6 if nc else 0.0), tb + (1e-6 if nc else 0.0)))
    for k, r in BALLS.items():
        parts.append(ball(N[k], r + g))
    if relief:
        parts.append(_disc(PIVOT[0], PIVOT[1], 45.0, Y0, 17.6))
    else:
        PL = N["PL"]
        parts += [_rrect_xz(-92.0, -79.0, -29.0, -5.0, 2.0, Y0, Y1)]                 # servo-ear plate (both servos' inner ears and the front diff case's rear ear)
        parts += [_disc(PL[0], PL[2], Y0, Y1, 16.0), _disc(PL[0], PL[2], 46.0, Y0, 16.0)]
        for (x, y, z) in _tab_pos()[3:]:                                          # only the hood tab remains: a pad with a magnet pocket (the skin is held by hinge + magnets)
            pad = _vcyl(x, y, z + TAB_PAD[0], z + TAB_PAD[1], TAB_PAD_D)
            parts += [pad, Manifold.batch_hull([pad, Manifold.sphere(BALLS["R2"], 32).translate((x, y, z))])]      # flared from the node ball up to the pad
        for k, d in FEET.items():
            x, y, z = N[k]
            disc = _vcyl(x, y, FOOT_Z, FOOT_Z + 3.0, d)
            parts.append(disc)
            parts.append(Manifold.batch_hull([disc, Manifold.sphere(BALLS.get(k, 4.0), 32).translate((x, y, z))]))      # flared fillet from the node's ball down to the foot disc: no abrupt tube-to-pad step
        parts.append(Manifold.cube((HINGE[0][1] - HINGE[0][0], HINGE_LUG[1] - HINGE_LUG[0], HINGE[1][1] - HINGE[1][0]), center=False).translate((HINGE[0][0], HINGE_LUG[0], HINGE[1][0])))   # hinge lug plate on the bumper cross bar
        _lug = Manifold.cube((HINGE[0][1] - HINGE[0][0], HINGE_LUG[1] - HINGE_LUG[0], 3.0), center=False)
        parts.append(Manifold.batch_hull([_lug.translate((HINGE[0][0], HINGE_LUG[0], HINGE[1][1] - 3.0)), Manifold.cube((17.0, HINGE_LUG[1] - HINGE_LUG[0], 3.0), center=False).translate((HINGE[0][0] - 4.0, HINGE_LUG[0], 21.0))]))   # gusset web: lug plate flared down onto the cross bar
        from body3_build import NOSE_TH
        ax = np.array([-math.sin(NOSE_TH), 0.0, math.cos(NOSE_TH)])
        for k in ("NA", "NB"):                                                         # skid pads: 3 mm discs on the nose-skin inner face
            c = np.array(N[k])
            parts.append(tube(c - ax * 1.5, c + ax * 1.5, 4.5, 1e-6, 1e-6))                  # plain disc (no rounded ends: they would reach the skid)
    side = parts[0]
    for p in parts[1:]:
        side = side + p
    if relief:
        return side + side.mirror((0.0, 1.0, 0.0))
    cuts = []
    for x, z in ((-86.9, -19.0), (-86.5, -9.5), (-84.5, -23.8), (-84.5, -13.8)):
        cuts.append(_disc(x, z, Y0 - 0.1, Y1 + 4.0, 2.4))
        cuts.append(_disc(x, z, Y1, Y1 + 4.0, 2 * HEAD))
    cuts.append(_disc(PIVOT[0], PIVOT[1], 45.0, Y1 + 0.1, 3.4))
    for (x, y, z) in _tab_pos()[3:]:
        cuts.append(_vcyl(x, y, z + TAB_PAD[1] - 2.1, z + TAB_PAD[1] + 0.1, MAG_D))                  # pocket for a 6 x 2 mm neodymium disc
    for k in FEET:
        x, y, z = N[k]
        cuts.append(_vcyl(x, y, FOOT_Z - 0.1, FOOT_Z + 2.0, 2.2))                 # self-tapping pilot for the base-plate screw
    cuts.append(Manifold.cylinder(8.0, HINGE_D / 2, HINGE_D / 2, 28).rotate((-90.0, 0.0, 0.0)).translate((HINGE_PIN[0], HINGE_LUG[0] - 2.0, HINGE_PIN[1])))   # hinge pin hole through the lug
    for c in cuts:
        side = side - c
    both = side + side.mirror((0.0, 1.0, 0.0))
    PE1 = N["PE1"]          # the front diff case has its rear-ear screw on the +y side only: the pad and its pilot exist there alone (the tube end on -y is a plain ball)
    ear = _disc(PE1[0], PE1[2], Y0, Y1, 15.0) + Manifold.batch_hull([_disc(PE1[0], PE1[2], Y0, Y1, 15.0), ball(PE1, R)])
    return both + ear - _disc(PE1[0], PE1[2], Y0 - 0.1, Y1 + 4.0, 2.7) + shock_tab() - motor_envelope()


def shock_tab():
    """Left side only: the coilover's upper bolt lug, a plate hulled from the eye position back onto the rear hoop's cross tube (R2 - C262), with a boss on its centre side.
    Inside the skin, so it needs no relief."""
    from parts import w3_shock as SK
    tx, tz = SK.tab_xz()
    rx, _, rz = nodes()["R2"]
    y0, y1 = SK.PLATE_Y
    plate = Manifold.batch_hull([_disc(tx, tz, y0, y1, 2 * SK.HOOP_R), _disc(rx, rz, y0, y1, 2 * SK.HOOP_R)])
    m = plate + _disc(tx, tz, SK.BOSS_Y[0], y0 + 0.1, 2 * SK.BOSS_R)
    return m - _disc(tx, tz, SK.BOSS_Y[0] - 0.5, y1 + 0.5, SK.PIN_D)


def motor_envelope():
    """The motor can (36 x 58.1) plus its rear plate, grown 2.5 mm: nothing of the frame runs through it (the left half of the pivot hoop is open there)."""
    from layout3wd import MOTOR_C
    x, y, z = MOTOR_C
    can = Manifold.cylinder(58.1 + 2.5 + 10.5, 18.0 + 2.5, 18.0 + 2.5, 48).rotate((0.0, 90.0, 0.0)).translate((x - 29.05 - 10.5, y, z))
    plate = Manifold.cube((12.0, 48.0, 34.0), center=False).translate((x - 29.05 - 12.0, y - 24.0, z - 17.0))
    return can + plate


def relief():
    """Tubes and nodes grown by 0.8 mm (no pads, no tab pads): subtracted from the skin where tubes pass through it."""
    return frame(relief=True)


def feet_xy():
    N = nodes()
    return [(N[k][0], N[k][1]) for k in FEET]


_CACHE = {}


def piece(name):
    if "f" not in _CACHE:
        _CACHE["f"] = frame()
    f = _CACHE["f"]
    sx = 1 if name.endswith("front") else -1
    xbox = Manifold.cube((400.0, 400.0, 400.0), center=True).translate((XS + sx * 200.0 + sx * 0.0125, 0, 0))
    m = MB.to_trimesh(f ^ xbox)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    m.apply_translation((0.0, 0.0, DZ["front" if sx > 0 else "rear"]))
    m.vertices = np.asarray(m.vertices, np.float32).astype(np.float64)          # what the STL will hold
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    m.merge_vertices()
    return m


NAMES = ["w3_frame_front", "w3_frame_rear"]


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
