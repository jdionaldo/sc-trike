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
LEG_Y, LEG_T = 28.0, 8.0           # foot centre |y| (kept inside the narrow hood)
WEB_T = 6.0                        # thickness of the hanger web plate (at y = +-LEG_Y)
FORK_SCREW_U = (-30.0, -44.0)      # chord positions of the two screws through each fork's lower prong into the blade
CH = 2.0                           # channel depth in the blade (top and bottom)
PR = 3.0                           # prong thickness: CH sits in the channel, the rest stands 1 mm proud of the blade surface
CLR = 0.15                         # prong-to-channel clearance
PROF_TOP = [(2.0, -0.5), (-8.0, 3.5), (-35.0, 5.5), (-72.0, 2.5)]
FORK_Y0 = LEG_Y - 5.0              # inner face of the hanger parts (print frame)
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


def topw(u):
    """Blade top-face height (local w) at chord position u."""
    us = [p[0] for p in PROF_TOP][::-1]
    ws = [p[1] for p in PROF_TOP][::-1]
    return float(np.interp(u, us, ws))


def _blade():
    prof = [(2.0, -3.0), (2.0, -0.5), (-8.0, 3.5), (-35.0, 5.5), (-CHORD, 2.5), (-CHORD, -3.0)]
    centre = MB.prism_xz(prof, -FLAT, FLAT)                           # plain blade centre (no raised cap)
    # snug channels for the fork prongs (top follows the blade profile, bottom is flat) and blind pilots for the prong screws
    ya, yb = LEG_Y - 5.3, LEG_Y + 5.3
    top_pts = [(3.0, topw(2.0) - CH), (2.0, topw(2.0) - CH), (-8.0, topw(-8.0) - CH), (-35.0, topw(-35.0) - CH), (-52.15, topw(-52.15) - CH),
               (-52.15, 30.0), (3.0, 30.0)]
    bot_pts = [(3.0, -3.5), (-52.15, -3.5), (-52.15, -3.0 + CH), (3.0, -3.0 + CH)]
    for sg in (1, -1):
        y0, y1 = (ya, yb) if sg > 0 else (-yb, -ya)
        centre = centre - MB.prism_xz(top_pts, y0, y1) - MB.prism_xz(bot_pts, y0, y1)
        for u in FORK_SCREW_U:
            centre = centre - Manifold.cylinder(4.0, 1.0, 1.0, 24).translate((u, sg * LEG_Y, -3.0 + CH - 0.1))
    body = centre.translate((0.0, 0.0, ARCH))
    for sg in (1, -1):
        y0, y1 = (FLAT - 0.05, SPAN) if sg > 0 else (-SPAN, -FLAT + 0.05)
        panel = MB.prism_xz(prof, y0, y1)
        fin = [(8.0, -3.0), (8.0, 3.5), (-30.0, 6.0), (-CHORD - 2.0, 5.0), (-CHORD - 2.0, -28.0), (-40.0, -20.0), (-12.0, -9.0)]   # swept fin that hangs DOWN from the blade's end
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
    if which == "main":                                                   # centre + left outer panel welded: 200 mm span fits the bed
        keep = _box(-200.0, 20.0, -SPLIT + 0.0125, 200.0, -60.0, 60.0)
    else:
        keep = _box(-200.0, 20.0, -200.0, -SPLIT - 0.0125, -60.0, 60.0)
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


def _centre_matrix():
    Mc = place_matrix().copy()
    Mc[:3, 3] += Mc[:3, :3] @ np.array([0.0, 0.0, ARCH])
    return Mc


def _lower_z(x):
    """Blade lower-face height at y = 0 (assembly) at chord position x."""
    a, b = blade_pt(-30.0, 0.0, -3.0), blade_pt(-60.0, 0.0, -3.0)
    return a[2] + (b[2] - a[2]) * (x - a[0]) / (b[0] - a[0])


def _chamfered(poly, y0, y1, c=1.2):
    """Convex (x, z) polygon extruded across y with 45-degree edge chamfers of size c on both faces."""
    from shapely.geometry import Polygon
    p = Polygon(poly)
    inner = list(p.buffer(-c, join_style=2).exterior.coords)[:-1]
    full = list(p.exterior.coords)[:-1]
    pts = [(x, y0 + c, z) for x, z in full] + [(x, y1 - c, z) for x, z in full] + [(x, y0, z) for x, z in inner] + [(x, y1, z) for x, z in inner]
    return Manifold.hull_points(np.array(pts, float))


def _hanger_left():
    """Fork hanger for y > 0, in assembly coordinates.  A web from the hood feet up to a nose cap that wraps the blade's leading edge; two prongs
    (1.2-style flush bands, 2 mm) follow the blade's top profile and its flat underside inside channels in the blade, and end in chamfers
    (down on top, up underneath).  The blade slides in from the rear; two screws from below go through the lower prong into the blade.
    Everything is chamfered."""
    Mc = _centre_matrix()
    A = lambda u, y, w: (Mc @ np.array([u, y, w, 1.0]))[:3]
    y0f, y1f = LEG_Y - 5.0, LEG_Y + 5.0
    c = CLR
    us = [2.0, -8.0, -35.0, -52.0]
    pd = PR - CH                                                          # proud height
    fl = lambda u: topw(u) - CH + c                                       # channel floor under the prong
    upper = [(2.5, topw(2.0) + pd)] + [(u, topw(u) + pd) for u in us] + [(u, fl(u)) for u in reversed(us)] + [(2.5, fl(2.0))]          # square end at u = -52: no wedge
    lower = [(2.5, -3.0 - pd), (-52.0, -3.0 - pd), (-52.0, -3.0 + CH - c), (2.5, -3.0 + CH - c)]
    prongs = MB.prism_xz(upper, y0f, y1f) + MB.prism_xz(lower, y0f, y1f)           # bands (not convex): plain prisms, the end chamfers are in the outline
    cap = _chamfered_prism_uw([(2.2, -3.0), (6.4, -3.0), (6.4, 0.6), (2.2, 0.6)], y0f, y1f)
    fork = prongs + cap
    for u in FORK_SCREW_U:
        fork = fork - Manifold.cylinder(CH + 2.0, 1.35, 1.35, 24).translate((u, LEG_Y, -3.5))              # clear hole through the lower prong
    fork = fork.transform(Mc[:3, :4])
    xf, xr = -300.0, -314.0
    h = lambda x: hood_top(x) + 0.4
    rl = A(3.2, LEG_Y, -2.0)                                           # web tips run into the cap so the hanger is one body
    rh = A(5.6, LEG_Y, -0.2)
    poly = [(xf, h(xf)), (xr, h(xr)), (rl[0], rl[2]), (rh[0], rh[2])]
    web = _chamfered(poly, LEG_Y - WEB_T / 2, LEG_Y + WEB_T / 2, 1.2)
    zf = foot_z()
    x0, x1 = FOOT_X
    foot = _box(x0, x1, y0f, y1f, zf, zf + 0.5)
    top = _box(x0, x1, y0f, y1f, hood_top(x1) + 0.2, hood_top(x1) + 2.0)
    body = fork + web + Manifold.batch_hull([foot, top])
    body = body - Manifold.cylinder(9.0, 1.0, 1.0, 24).translate((HOLE_X, LEG_Y, zf - 0.1))                 # pilot, screw from below through the frame pad
    return body


def _chamfered_prism_uw(poly, y0, y1, c=0.5):
    """(u, w) polygon extruded across y with small chamfers on the outer faces; used for the prongs and the nose cap in the blade's local frame."""
    from shapely.geometry import Polygon
    p = Polygon(poly)
    inner = p.buffer(-c, join_style=2)
    if inner.is_empty:
        return MB.prism_xz(poly, y0, y1)
    full = list(p.exterior.coords)[:-1]
    ins = list(inner.exterior.coords)[:-1]
    pts = [(x, y0 + c, z) for x, z in full] + [(x, y1 - c, z) for x, z in full] + [(x, y0, z) for x, z in ins] + [(x, y1, z) for x, z in ins]
    return Manifold.hull_points(np.array(pts, float))


def _hanger_part(side):
    from parts.w3_style import _to_print
    def fn():
        b = _hanger_left()
        if side < 0:
            b = b.mirror((0.0, 1.0, 0.0))
        return _to_print(b, side, FORK_Y0)
    return MeshPart("w3_tail_hanger_left" if side > 0 else "w3_tail_hanger_right", fn, walls=False, supports=True)


def slot_cutters():
    """Hood-skin slots for the two feet (grown 0.5 mm) and the access holes in the hood underside for their screws."""
    zf = foot_z()
    x0, x1 = FOOT_X
    g = 0.5
    out = None
    for sg in (1, -1):
        y0, y1 = sg * LEG_Y - 5.0 - g, sg * LEG_Y + 5.0 + g
        foot = _box(x0 - g, x1 + g, y0, y1, zf - 1.0, zf + 0.5)
        top = _box(x0 - g, x1 + g, y0, y1, hood_top(x1) + 1.0, hood_top(x1) + 2.0)
        cut = Manifold.batch_hull([foot, top])
        acc = Manifold.cylinder(24.0, 4.5, 4.5, 32).translate((HOLE_X, sg * LEG_Y, 44.0))
        out = cut + acc if out is None else out + cut + acc
    return out


def build(p):
    return [MeshPart("w3_tail_main", lambda: _piece("main"), walls=False, supports=True),
            MeshPart("w3_tail_right", lambda: _piece("right"), walls=False, supports=True),
            _hanger_part(1), _hanger_part(-1)]


def placed():
    import json
    from parts import w3_front as W
    LIFT = json.loads(open('out/stl/w3_tail_lift.json').read())
    out = []
    M = place_matrix()
    for n in ("w3_tail_main", "w3_tail_right"):
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_translation((0.0, 0.0, -LIFT[n.split('_')[-1]]))
        m.apply_transform(M)
        out.append((n, m))
    for s, n in ((1, "w3_tail_hanger_left"), (-1, "w3_tail_hanger_right")):
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_transform(W.mats(s, FORK_Y0))
        out.append((n, m))
    return out
