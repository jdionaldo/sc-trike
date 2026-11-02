"""WS-03 GT wing: a 269 mm blade (as wide as the front track) on two swept-back legs, with big end plates.  The blade follows the FRONT roofline
(rises toward the rear at the roof's 11.3 deg); the legs start on the hood above the frame's strut pads and sweep rearward to the blade.

Pieces: blade centre, blade left and right (each with its end plate), leg left and right.  Blade print frame: u = chord (0 at the leading edge,
negative rearward), v = span (y), w = up from the blade's flat lower face; the STL is lifted by TZ for the end plates' lower part.
Legs are printed on their side (inner face on the bed) like the arms.
"""
import math

import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart, _clean, _tb

SPAN = 134.5                       # half span = half the front track (269 / 2)
X_LE = -325.0                      # leading edge (assembly x)
Z_LE = 120.0                       # lower-face height at the leading edge (set below so the blade top lies on the front roofline plane)
CHORD = 72.0
ROOF_P = (33.7, 40.4)              # front roofline: z = 40.4 + ROOF_K * (33.7 - x), from the nose top to the roof peak
ROOF_K = (97.0 - 40.4) / (33.7 + 259.0)
SLOPE = ROOF_K                     # the blade lies in the front roofline's plane
ALPHA = math.atan(SLOPE)
COS_A = math.cos(ALPHA)
PLATE_T = 3.0
SPLIT = 66.0
ARCH = 12.0
LEG_Y, LEG_T = 28.0, 8.0           # leg centre |y| and thickness (kept inside the narrow hood)
FOOT_X = (-314.0, -300.0)          # leg foot (assembly x): it passes through a slot in the hood and sits on the frame pad inside
HOLE_X = -307.0                    # foot screw, from below (the access hole is in the hood underside)
STRUT_XY = (-296.0, 28.0)          # frame strut node (x, |y|); the pad plate extends rearward to the screw
TZ = {"center": 3.0, "left": 36.0, "right": 36.0}     # STL lift per piece (end plates hang 34 mm below the blade's lower face)
LEG_Y0 = 14.0                      # leg print frame: inner face of the top flange on the bed



def _z_le_from_roof():
    """Z_LE such that the blade's top surface at the centre of the chord lies on the roofline plane extended rearward."""
    u, w = -35.0, 5.5 + 12.0                                       # mid-chord top of the blade at y = 0 (profile top 5.5 + arch 12)
    x = X_LE + u * math.cos(ALPHA) + w * math.sin(ALPHA)
    z_roof = ROOF_P[1] + ROOF_K * (ROOF_P[0] - x)
    return z_roof - (-u * math.sin(ALPHA) + w * math.cos(ALPHA))


Z_LE = _z_le_from_roof()


def hood_top(x):
    return 97.0 + (97.0 - 83.3) / 89.1 * (x + 259.0)


def foot_z():
    return hood_top(HOLE_X) - 6.0                                     # leg foot underside = pad top, 3.6 mm below the inner skin


def strut_node():
    return np.array([STRUT_XY[0], STRUT_XY[1], foot_z()])


def flange_screws():
    """Blade-underside pilots / leg flange holes: (u, y) pairs, beside the leg so the heads are reachable from below."""
    return [(_u_at(x), y) for x in LEG_SCREW_X for y in (LEG_Y - 8.5, LEG_Y + 8.5)]


def place_matrix():
    R = trimesh.transformations.rotation_matrix(ALPHA, [0, 1, 0])      # z' = -x sin(a) + z cos(a): rises toward the rear
    T = np.eye(4); T[:3, 3] = (X_LE, 0.0, Z_LE)
    return T @ R


def _u_at(x, w=-3.0):
    return (x - X_LE + (-w) * math.sin(ALPHA) * -1.0) / math.cos(ALPHA) if False else (x - X_LE - w * math.sin(ALPHA)) / math.cos(ALPHA)


LEG_SCREW_X = (-351.0, -369.0)


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


ARCH, SWEEP = 12.0, 8.0            # angular dihedral: flat centre |y| <= FLAT, outer panels slope down by ARCH and sweep rearward by SWEEP
FLAT = 50.0
FIN = 3.0


def _warp_pt(u, y, w):
    """Local point after the angular dihedral/sweep (flat centre, straight outer panels)."""
    t = max(0.0, (abs(y) - FLAT) / (SPAN - FLAT))
    return u - SWEEP * t, y, w + ARCH * (1.0 - t)


def blade_pt(u, y, w):
    p = place_matrix() @ np.array([*_warp_pt(u, y, w), 1.0])
    return p[:3]


def _panel_matrix(sgn):
    """Shear for an outer panel: z' = z + ARCH (SPAN-|y|)/(SPAN-FLAT), x' = x - SWEEP (|y|-FLAT)/(SPAN-FLAT)."""
    k = 1.0 / (SPAN - FLAT)
    return np.array([[1.0, -sgn * SWEEP * k, 0.0, sgn * SWEEP * k * FLAT * sgn * sgn],
                     [0.0, 1.0, 0.0, 0.0],
                     [0.0, -sgn * ARCH * k, 1.0, ARCH * (1.0 + FLAT * k)]]) if False else np.array(
        [[1.0, -SWEEP * k * sgn, 0.0, SWEEP * k * FLAT],
         [0.0, 1.0, 0.0, 0.0],
         [0.0, -ARCH * k * sgn, 1.0, ARCH * (1.0 + FLAT * k) - ARCH]])


def _blade():
    prof = [(2.0, -3.0), (2.0, -0.5), (-8.0, 3.5), (-35.0, 5.5), (-CHORD, 2.5), (-CHORD, -3.0)]
    # centre: flat blade plus a cap that wraps the blade (front lip, top, and down over the trailing edge), lifted by ARCH
    cap_prof = [(14.0, -3.0), (14.0, 7.5), (6.0, 11.0), (-10.0, 10.5), (-CHORD - 4.0, 8.0), (-CHORD - 4.0, -3.0)]
    from shapely.geometry import Polygon
    cap_plan = Polygon([(16.0, -52.0), (16.0, 52.0), (-CHORD - 6.0, 58.0), (-CHORD - 6.0, -58.0)]).buffer(-5.0).buffer(5.0)
    cap = MB.prism_xz(cap_prof, -60.0, 60.0) ^ MB.prism_xy(list(cap_plan.exterior.coords)[:-1], -20.0, 40.0)
    centre = MB.prism_xz(prof, -FLAT, FLAT) + cap
    for sg in (1, -1):                                                # pilots for the leg-flange screws, blind from the lower face (nothing shows on top)
        for u, y in flange_screws():
            centre = centre - Manifold.cylinder(9.0, 1.0, 1.0, 24).translate((u, sg * y, -3.2))
    body = centre.translate((0.0, 0.0, ARCH))
    for sg in (1, -1):
        y0, y1 = (FLAT - 0.05, SPAN) if sg > 0 else (-SPAN, -FLAT + 0.05)
        panel = MB.prism_xz(prof, y0, y1)
        fin = [(6.0, -3.0), (6.0, 4.0), (-25.0, 9.0), (-CHORD - 4.0, 20.0), (-CHORD - 4.0, -2.0), (-35.0, -5.0)]       # swept wedge fin, rising at the rear
        fy0, fy1 = (SPAN - FIN, SPAN) if sg > 0 else (-SPAN, -SPAN + FIN)
        panel = panel + MB.prism_xz(fin, fy0, fy1)
        k = 1.0 / (SPAN - FLAT)
        # |y|-dependent shear (y>0: t=(y-FLAT)k, y<0: t=(-y-FLAT)k)
        mat = np.array([[1.0, -sg * SWEEP * k, 0.0, SWEEP * k * FLAT],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, -sg * ARCH * k, 1.0, ARCH + ARCH * k * FLAT]])
        body = body + panel.transform(mat)
    return body


def _decimate(m):
    """Keep the first watertight single-body simplification (the cap and panels are flat: they collapse well)."""
    import fast_simplification
    for red in (0.9, 0.8, 0.6):
        v, f = fast_simplification.simplify(np.asarray(m.vertices), np.asarray(m.faces), target_reduction=red, agg=3)
        q = trimesh.Trimesh(v, f, process=True)
        q.merge_vertices()
        if q.is_watertight and len(q.split(only_watertight=False)) == 1:
            return q
    return m


def _piece(which):
    body = _blade()
    if which == "center":
        keep = _box(-200.0, 20.0, -SPLIT + 0.025, SPLIT - 0.025, -60.0, 60.0)
    elif which == "left":
        keep = _box(-200.0, 20.0, SPLIT + 0.025, 200.0, -60.0, 60.0)
    else:
        keep = _box(-200.0, 20.0, -200.0, -SPLIT - 0.025, -60.0, 60.0)
    m = MB.to_trimesh(body ^ keep)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    lift = -float(m.bounds[0][2]) + 0.5
    m.apply_translation((0.0, 0.0, lift))
    import json, pathlib
    p = pathlib.Path("out/stl/w3_tail_lift.json")
    d = json.loads(p.read_text()) if p.exists() else {}
    d[which] = lift
    p.write_text(json.dumps(d))
    return _clean(m)


def _leg_left():
    """Tapered pylon (hull of the foot box and two top boxes under the blade) with a top flange beside it for screws from below.
    Built for y > 0 in assembly coordinates."""
    zf = foot_z()
    x0, x1 = FOOT_X
    tx0, tx1 = LEG_SCREW_X[0] + 12.0, LEG_SCREW_X[1] - 12.0
    def top_box(x):
        a = blade_pt(_u_at(x), LEG_Y, -3.0)
        return _box(x - 1.0, x + 1.0, LEG_Y - 5.0, LEG_Y + 5.0, a[2] - 3.7, a[2] - 3.0)
    foot = _box(x0, x1, LEG_Y - 5.0, LEG_Y + 5.0, zf, zf + 0.5)
    body = Manifold.batch_hull([foot, top_box(tx0), top_box(tx1)])
    # flange under the blade: 3 mm thick in the blade's local frame, 0.3 mm below its lower face, spanning the screw positions
    us = [u for u, _ in flange_screws()]
    fl = Manifold.cube((max(us) - min(us) + 16.0, 2 * 8.5 + 11.0, 3.0), center=False).translate((min(us) - 8.0, LEG_Y - 8.5 - 5.5, -6.3))
    Mc = place_matrix() @ np.diag([1.0, 1.0, 1.0, 1.0])
    Mc = Mc.copy(); Mc[:3, 3] += Mc[:3, :3] @ np.array([0.0, 0.0, ARCH])
    body = body + fl.transform(Mc[:3, :4])
    for u, y in flange_screws():
        hole = Manifold.cylinder(6.0, 1.35, 1.35, 24).translate((u, y, -7.0))
        body = body - hole.transform(Mc[:3, :4])
    body = body - Manifold.cylinder(9.0, 1.0, 1.0, 24).translate((HOLE_X, LEG_Y, zf - 0.1))               # foot pilot, screw from below through the frame pad
    return body


def _leg(side):
    b = _leg_left()
    return b if side > 0 else b.mirror((0.0, 1.0, 0.0))


def slot_cutters():
    """Hood-skin slots for the leg feet: both legs, grown 0.5 mm in plan, plus the access holes in the hood underside for the screws."""
    zf = foot_z()
    x0, x1 = FOOT_X
    tops = []
    g = 0.5
    for tx in (LEG_SCREW_X[0] + 12.0, LEG_SCREW_X[1] - 12.0):
        a = blade_pt(_u_at(tx), LEG_Y, -3.0)
        tops.append(_box(tx - 1.0 - g, tx + 1.0 + g, LEG_Y - 5.0 - g, LEG_Y + 5.0 + g, a[2] - 3.7, a[2] - 3.0))
    foot = _box(x0 - g, x1 + g, LEG_Y - 5.0 - g, LEG_Y + 5.0 + g, zf - 1.0, zf + 0.5)
    cut = Manifold.batch_hull([foot] + tops)
    out = cut + cut.mirror((0.0, 1.0, 0.0))
    acc = Manifold.cylinder(24.0, 4.5, 4.5, 32).translate((HOLE_X, LEG_Y, 44.0))
    return out + acc + acc.mirror((0.0, 1.0, 0.0))


def _leg_part(side):
    from parts import w3_front as W
    from parts.w3_style import _to_print
    def fn():
        return _to_print(_leg(side), side, LEG_Y0)
    return MeshPart("w3_tail_leg_left" if side > 0 else "w3_tail_leg_right", fn, walls=False, supports=True)


def build(p):
    return [MeshPart("w3_tail_center", lambda: _piece("center"), walls=False, supports=True),
            MeshPart("w3_tail_left", lambda: _piece("left"), walls=False, supports=True),
            MeshPart("w3_tail_right", lambda: _piece("right"), walls=False, supports=True),
            _leg_part(1), _leg_part(-1)]


def placed():
    import json
    from parts import w3_front as W
    LIFT = json.loads(open('out/stl/w3_tail_lift.json').read())
    out = []
    M = place_matrix()
    for n in ("w3_tail_center", "w3_tail_left", "w3_tail_right"):
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_translation((0.0, 0.0, -LIFT[n.split('_')[-1]]))
        m.apply_transform(M)
        out.append((n, m))
    for s, n in ((1, "w3_tail_leg_left"), (-1, "w3_tail_leg_right")):
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_transform(W.mats(s, LEG_Y0))
        out.append((n, m))
    return out
