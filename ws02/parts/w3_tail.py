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
from w3_stretch import back, fx, STRETCH

STEP_Y, STEP_DZ, RISER = (92.0,), 6.0, 4.0     # step stations (|y|), height of each step, riser width (an angled step, about 56 degrees)
SPAN = 134.5                       # half span = half the front track (269 / 2)
X_LE = back(-325.0)                      # leading edge (assembly x)
Z_LE = 120.0                       # lower-face height at the leading edge (set below so the blade top lies on the front roofline plane)
CHORD = 72.0
ROOF_P = (33.7, 40.4)              # front roofline: z = 40.4 + ROOF_K * (33.7 - x), from the nose top to the roof peak
ROOF_K = (97.0 - 40.4) / (33.7 + 259.0)           # the pre-stretch roof slope: the wing keeps its old pitch and height
SLOPE = ROOF_K                     # the blade lies in the front roofline's plane
ALPHA = math.atan(SLOPE)
SPLIT = 66.0
ARCH = 12.0
LEG_Y = 28.0           # foot centre |y| (kept inside the narrow hood)
FORK_SCREW_U = (-30.0, -46.0, -58.0)      # chord positions of the two screws through each fork's lower prong into the blade
CH = 2.0                           # channel depth in the blade (top and bottom)
PR = 3.0                           # prong thickness: CH sits in the channel, the rest stands 1 mm proud of the blade surface
CLR = 0.15                         # prong-to-channel clearance
PROF_TOP = [(2.0, -0.5), (-8.0, 0.7), (-35.0, 4.0), (-55.0, 6.5), (-72.0, 11.5)]      # straight rise (about 7 deg over the blade pitch) then an upturned flick over the last 17 mm
FORK_Y0 = LEG_Y - 5.0              # inner face of the hanger parts (print frame)
FOOT_X = (back(-314.0), back(-300.0))          # leg foot (assembly x): it passes through a slot in the hood and sits on the frame pad inside
HOLE_X = back(-307.0)                    # foot screw, from below (the access hole is in the hood underside)
TZ = {"center": 3.0, "left": 36.0, "right": 36.0}     # STL lift per piece (end plates hang 34 mm below the blade's lower face)



def _z_le_from_roof():
    """Z_LE such that the blade's top surface at the centre of the chord lies on the roofline plane extended rearward."""
    u, w = -35.0, 4.0 + 12.0                                       # mid-chord top of the blade at y = 0 (profile top 5.5 + arch 12)
    x = X_LE + u * math.cos(ALPHA) + w * math.sin(ALPHA) + STRETCH           # evaluated at the pre-stretch x: same height as before the stretch
    z_roof = ROOF_P[1] + ROOF_K * (ROOF_P[0] - x)
    return z_roof - (-u * math.sin(ALPHA) + w * math.cos(ALPHA))


Z_LE = _z_le_from_roof()


def hood_top(x):
    return 97.0 + (97.0 - 83.3) / 89.1 * (x - fx(-259.0))


def foot_z():
    return hood_top(HOLE_X) - 6.0                                     # leg foot underside = pad top, 3.6 mm below the inner skin


def place_matrix():
    R = trimesh.transformations.rotation_matrix(ALPHA, [0, 1, 0])      # z' = -x sin(a) + z cos(a): rises toward the rear
    T = np.eye(4); T[:3, 3] = (X_LE, 0.0, Z_LE)
    return T @ R


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


ARCH, SWEEP = 12.0, -8.0           # angular dihedral: flat centre |y| <= FLAT, outer panels slope down by ARCH and sweep FORWARD by 8 mm (negative = forward)
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
    prof = [(2.0, -3.0)] + list(PROF_TOP) + [(-CHORD, -3.0)]
    centre = MB.prism_xz(prof, -FLAT, FLAT)                           # plain blade centre (no raised cap)
    # snug channels for the fork prongs (top follows the blade profile, bottom is flat) and blind pilots for the prong screws
    ya, yb = LEG_Y - 5.3, LEG_Y + 5.3
    top_pts = [(3.0, topw(2.0) - CH), (2.0, topw(2.0) - CH), (-8.0, topw(-8.0) - CH), (-35.0, topw(-35.0) - CH), (-55.0, topw(-55.0) - CH), (-66.15, topw(-66.15) - CH),
               (-66.15, 30.0), (3.0, 30.0)]
    bot_pts = [(3.0, -3.5), (-66.15, -3.5), (-66.15, -3.0 + CH), (3.0, -3.0 + CH)]
    for sg in (1, -1):
        y0, y1 = (ya, yb) if sg > 0 else (-yb, -ya)
        centre = centre - MB.prism_xz(top_pts, y0, y1) - MB.prism_xz(bot_pts, y0, y1)
        for u in FORK_SCREW_U:
            centre = centre - Manifold.cylinder(4.0, 1.0, 1.0, 24).translate((u, sg * LEG_Y, -3.0 + CH - 0.1))
    body = centre.translate((0.0, 0.0, ARCH))
    # stepped wing: the centre sits at +ARCH; each outer panel is flat and one STEP lower, joined by an angled riser (a ziggurat, no dihedral slope)
    k = 1.0 / (SPAN - FLAT)
    sweep = np.array([[1.0, -SWEEP * k, 0.0, SWEEP * k * FLAT], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
    slab = lambda y0, y1, z: MB.prism_xz(prof, y0, y1).translate((0.0, 0.0, z))
    fin = [(8.0, -3.0), (8.0, 3.5), (-30.0, 6.0), (-CHORD - 2.0, 5.0), (-CHORD - 2.0, -28.0), (-40.0, -20.0), (-12.0, -9.0)]   # swept fin that hangs DOWN from the blade's end
    side = None
    edges = [FLAT] + list(STEP_Y) + [SPAN]
    prev = ARCH
    for j in range(len(edges) - 1):                                          # panel j spans edges[j]..edges[j+1] at ARCH - dz (j + 1); an angled riser joins it to the level before
        ya, yb, z = edges[j], edges[j + 1], ARCH - STEP_DZ * (j + 1)
        part = slab(ya + RISER, yb, z) + Manifold.batch_hull([slab(ya - 0.05, ya + 0.01, prev), slab(ya + RISER - 0.01, ya + RISER, z)])
        side = part if side is None else side + part
        prev = z
    side = side + MB.prism_xz(fin, SPAN - FIN, SPAN).translate((0.0, 0.0, prev))
    side = side.transform(sweep)
    body = body + side + side.mirror((0.0, 1.0, 0.0))
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
    """One-piece fork hanger for y > 0 (assembly coordinates), no elbows: the web's front edge is the blade's own top-profile line (u -8 .. 2, 33 deg)
    carried straight down to the back slope, so the web and the upper strap are one straight edge.  Two 3 mm prongs (2 mm in channels, 1 mm proud)
    follow the blade's top and its flat underside and end in a 32 deg chamfer on the channel-end plane.  Screws from below through the lower prong."""
    Mc = _centre_matrix()
    A = lambda u, y, w: (Mc @ np.array([u, y, w, 1.0]))[:3]
    y0f, y1f = LEG_Y - 5.0, LEG_Y + 5.0
    c = CLR
    us = [2.0, -8.0, -35.0, -66.0]
    pd = PR - CH
    fl = lambda u: topw(u) - CH + c
    w_a, w_b = topw(-8.0) + pd, topw(2.0) + pd
    wl = lambda u: w_b + (w_b - w_a) / 10.0 * (u - 2.0)                     # the blade-top line, extended forward
    d = pd / np.tan(np.radians(32.0))
    ue = us[-1]
    uf = 2.9                                                              # prongs start inside the web face
    upper = [(uf, wl(uf)), (2.0, topw(2.0) + pd)] + [(u, topw(u) + pd) for u in us[1:-1]] + [(ue + d, topw(ue + d) + pd), (ue, topw(ue))] + [(u, fl(u)) for u in reversed(us)] + [(uf, fl(2.0))]
    lower = [(uf, -3.0 - pd), (ue + d, -3.0 - pd), (ue, -3.0), (ue, -3.0 + CH - c), (uf, -3.0 + CH - c)]
    fork = MB.prism_xz(upper, y0f, y1f) + MB.prism_xz(lower, y0f, y1f)
    for u in FORK_SCREW_U:
        fork = fork - Manifold.cylinder(CH + 2.0, 1.35, 1.35, 24).translate((u, LEG_Y, -3.5))              # clear hole through the lower prong
    fork = fork.transform(Mc[:3, :4])
    # web: front edge on the blade-top line down to the hood, rear edge straight to the lower prong's front
    a = A(-8.0, LEG_Y, w_a)[[0, 2]]
    b = A(2.0, LEG_Y, w_b)[[0, 2]]
    dv = (b - a) / np.linalg.norm(b - a)
    p = b.copy()
    h = lambda x: hood_top(x) + 0.4
    while p[1] > h(p[0]):
        p = p + dv * 0.05
    p0 = (float(p[0]), float(h(p[0])))
    p1 = (FOOT_X[0], float(h(FOOT_X[0])))
    rl = A(2.4, LEG_Y, -3.0)
    cc = A(2.4, LEG_Y, wl(2.4))
    web = _chamfered([p0, p1, (rl[0], rl[2]), (cc[0], cc[2])], y0f, y1f, 1.2)
    x0, x1 = FOOT_X
    sl = lambda x: hood_top(x) + 0.05                                                       # foot sits on the hood skin (the wing flips up with the skin)
    foot = Manifold.batch_hull([_box(x0, x0 + 0.01, y0f, y1f, sl(x0), sl(x0) + 0.5), _box(x1 - 0.01, x1, y0f, y1f, sl(x1), sl(x1) + 0.5)])
    top = _box(x0, x1, y0f, y1f, hood_top(x1) + 0.2, hood_top(x1) + 2.0)
    body = fork + web + Manifold.batch_hull([foot, top])
    body = body - Manifold.cylinder(9.0, 1.0, 1.0, 24).translate((HOLE_X, LEG_Y, sl(HOLE_X) - 0.1))        # pilot: screw from inside the skin up through the hood
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


def screw_holes():
    """Clearance holes through the hood for the foot screws (driven from inside the skin)."""
    out = None
    for sg in (1, -1):
        c = Manifold.cylinder(12.0, 1.6, 1.6, 24).translate((HOLE_X, sg * LEG_Y, hood_top(HOLE_X) - 8.0))
        out = c if out is None else out + c
    return out


def screw_bosses():
    """Bosses on the hood's inner face under each foot (seat for the screw head)."""
    out = None
    for sg in (1, -1):
        c = Manifold.cylinder(4.0, 4.5, 4.5, 32).translate((HOLE_X, sg * LEG_Y, hood_top(HOLE_X) - 6.0))
        out = c if out is None else out + c
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
