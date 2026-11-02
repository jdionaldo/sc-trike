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
LEG_Y, LEG_T = 38.0, 8.0           # leg centre |y| and thickness
FOOT_X = (-311.0, -295.0)          # leg foot (assembly x)
STRUT_XY = (-303.0, 31.0)          # frame strut pad (x, |y|), beside the leg
TZ = {"center": 3.0, "left": 36.0, "right": 36.0}     # STL lift per piece (end plates hang 34 mm below the blade's lower face)
LEG_Y0 = LEG_Y - 14.0              # leg print frame: inner face of the foot flange on the bed



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
    return hood_top(STRUT_XY[0]) + 3.5                                # underside of the leg's foot flange


def strut_node():
    return np.array([STRUT_XY[0], STRUT_XY[1], foot_z()])


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
    for sg in (1, -1):                                                # leg screws: clear through blade and cap, counterbored from the top
        for x in LEG_SCREW_X:
            u = _u_at(x)
            centre = centre - Manifold.cylinder(20.0, 1.35, 1.35, 24).translate((u, sg * LEG_Y, -6.0))
            centre = centre - Manifold.cylinder(3.0, 2.6, 2.6, 28).translate((u, sg * LEG_Y, 8.5))
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


def _leg(side):
    """Tapered pylon (convex hull of a foot box and a top box that follows the warped blade underside), foot flange inboard with the screw."""
    s = side
    zf = foot_z()
    x0, x1 = FOOT_X
    tx0, tx1 = LEG_SCREW_X[0] + 12.0, LEG_SCREW_X[1] - 12.0
    def top_box(x):
        a = blade_pt(_u_at(x), s * LEG_Y, -3.0)
        return _box(x - 1.0, x + 1.0, min(s * (LEG_Y - 3.0), s * (LEG_Y + 3.0)), max(s * (LEG_Y - 3.0), s * (LEG_Y + 3.0)), a[2] - 1.2, a[2] - 0.6)
    foot = _box(x0, x1, min(s * (LEG_Y - 5.0), s * (LEG_Y + 5.0)), max(s * (LEG_Y - 5.0), s * (LEG_Y + 5.0)), zf, zf + 0.5)
    body = Manifold.batch_hull([foot, top_box(tx0), top_box(tx1)])
    fl_y0, fl_y1 = (LEG_Y - 14.0, LEG_Y + 5.0)
    body = body + _box(x0, x1, min(s * fl_y0, s * fl_y1), max(s * fl_y0, s * fl_y1), zf, zf + 4.0)
    sx, sy = STRUT_XY
    body = body - Manifold.cylinder(8.0, 1.35, 1.35, 24).translate((sx, s * sy, zf - 1.0))               # foot screw, from above
    body = body - Manifold.cylinder(4.0, 2.6, 2.6, 28).translate((sx, s * sy, zf + 2.0))
    n = place_matrix()[:3, :3] @ np.array([0.0, 0.0, 1.0])
    for x in LEG_SCREW_X:                                                  # pilots for the blade screws, along the blade normal
        a = blade_pt(_u_at(x), s * LEG_Y, -3.0)
        body = body - _tb(a - n * 8.0, a + n * 0.5, 1.0)
    return body


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
