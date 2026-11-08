"""WS-03 body: a faceted wedge built from clean plan, side and section shapes taken from the base.stl silhouettes (old chassis
frame numbers), mapped to the 3WD frame, hollowed to a 2.4 mm wall with an open belly, windows cut where the front arms
swing. Output: out/mono3/body3.stl (and halves/pieces via split_body3)."""
import math
import os
import sys
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import MultiPoint, Polygon

import mono_build as MB
from w3_stretch import fx, back, pts as _pts, STRETCH, RAXLE_Z

from skin_cfg import CONCEPT, MONO
OUT = Path(MONO)
KX, KY, DZ, XOFF = 1.0, 1.0, 0.0, 0.0           # the profile below is already in the assembly frame
WALL = 2.4

# profile from the owner's sketch over the RT-1 sheet (assembly frame, mm): truncated nose, roof rising toward the rear, high rear hood
# with a scoop, open tail underside above the gearbox; wide mid body, narrow tail
NOSE_LOW = (-1.0, -26.0)                              # where the nose underside meets the chassis floor
NOSE_TH = math.atan2(53.0, 35.0)                      # underside slope (56.6 deg)
TAIL = _pts([(-299.0, 50.0), (-341.5, 66.4), (-348.1, 83.3)])                # new tail from the owner's markup: underside rising to the tail-light face, then the roof
WHEEL_C, WHEEL_R = (back(-360.0), RAXLE_Z), 62.0                                           # rear tyre (radius 56) plus 6 mm: the skin's rear edge follows this radius over the wheel
PEAK = (fx(-237.0), 100.4)                             # roof peak, moved forward along the tail's own descent line (z 97 at old x -259): one straight line from here to the tail light
ARC = [(WHEEL_C[0] + WHEEL_R * math.cos(math.radians(a_)), WHEEL_C[1] + WHEEL_R * math.sin(math.radians(a_))) for a_ in (math.degrees(math.asin(max(-1.0, min(1.0, (-26.0 - WHEEL_C[1]) / WHEEL_R)))), 12, 20, 30, 40, 50, 60, 70)]   # the arc starts where the radius meets the skin floor (z -26)
SIDE = [(34, 40), (34, 27), NOSE_LOW] + ARC + TAIL[1:] + [PEAK, (-70.0, 63.0)]   # straight roofline, flat vertical nose face, wheel-arch rear edge, short raked tail
HALF = [(30, 38), (20, 44), (-28, 44), (-73.5, 47), (-91.3, 60), (-122, 66), (-176, 86), (-293, 70), (-365, 76.5), (-382, 49), (-400, 44), (-438, 38.5)]   # plan: a side pod swelling to y 86 at x -176, tapering to the rear arch (traced from the owner's markup)
SECTION = [(-68, -40), (68, -40), (68, -9.3), (35, 110), (-35, 110), (-68, -9.3)]   # (y, z): flanks lean in toward the roof, with a 45-degree-ish shoulder bevel at z 50..58

SIDE_BASE = list(SIDE)                                  # the old roofline: top_z() keeps answering with it because the frame's roof tab nodes hang from it
TENT_K = 1.0 / 3.615                                    # flank lean (y per mm of z) of the section prism
SEC_TOP = (35.0, 110.0)                                 # (half width, z) of the section's flat top
if CONCEPT:                                           # rev 3: reference silhouette (drawings 54/55, tools_skin/ref_outline.py)
    DECK_DZ = 22.0                                      # the rear deck is this much higher than the old one (the wing is lifted with it)
    TAIL = _pts([(-299.0, 50.0), (-341.5, 66.4)]) + [(-438.1, 83.3 + DECK_DZ)]
    SIDE = [(55, 44), (55, 37), (34, 27), NOSE_LOW] + ARC + TAIL[1:] + [(-327.0, 100.4 + DECK_DZ), (-290.0, 130.0), (-151.0, 124.0), (-72.0, 84.0), (-5.0, 62.0)]   # low raked nose, raked windscreen, tall cabin roof, high hunched deck
    HALF = [(55, 18), (34, 26), (3.5, 52), (-52, 52), (-123, 60), (-150, 90), (-205, 92)] + HALF[7:]      # chisel nose, narrow hood over the arm sweep, shoulder flare behind it, flat wide pods
    TENT_K = 30.0 / 139.3                               # steeper flanks: 38 mm half width still at z 130
    SEC_TOP = (68.0 - TENT_K * 144.3, 135.0)
    SECTION = [(-68, -40), (68, -40), (68, -9.3), (SEC_TOP[0], SEC_TOP[1]), (-SEC_TOP[0], SEC_TOP[1]), (-68, -9.3)]


def to_new(pts, kind):
    out = []
    for a, b in pts:
        if kind == "side":
            out.append((KX * a + XOFF, b + DZ))
        elif kind == "plan":
            out.append((KX * a + XOFF, KY * b))
        else:
            out.append((KY * a, b + DZ))
    return out


def prism_yz(pts, x0, x1):
    m = trimesh.creation.extrude_polygon(Polygon(pts), x1 - x0)           # polygon in (y, z), extruded along local z
    m.apply_transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1.0]]))
    m.apply_translation((x0, 0, 0))
    return MB.man(m)


FENDER = [(back(-284.0), 47.0), (back(-304.0), 58.0), (back(-346.0), 50.0)]               # rear fender flare: (x, half width) stations; hulled, so plan edges are straight diagonals
FENDER_Z = (-20.0, 34.0, 58.0, 9.0)                                      # foot z, start of the top chamfer, top z, chamfer run in y


def hump(inset=0.0):
    """Canopy block: hull between (y, z) trapezoid stations along x, taller than the roof; the roof tabs, hood and nose stay on the old roofline."""
    yb, yt, zb = HUMP_Y
    polys = [Polygon([(-yb, zb), (yb, zb), (yt, zt), (-yt, zt)]).buffer(-inset, join_style=2) for _, zt in HUMP]
    return _hull_sections([x for x, _ in HUMP], polys)


def _plan_hw(x):
    xs = [p[0] for p in sorted(HALF)]
    ys = [p[1] for p in sorted(HALF)]
    return float(np.interp(x, xs, ys))


def _hull_sections(xs, polys):
    """Convex hull between consecutive (y, z) section polygons placed at x stations, mirrored to both flanks."""
    out = None
    for (xa, pa), (xb, pb) in zip(zip(xs, polys), list(zip(xs, polys))[1:]):
        for sgn in (1, -1):
            pts = [(x, sgn * y, z) for x, pl in ((xa, pa), (xb, pb)) for y, z in list(pl.exterior.coords)[:-1]]
            h = Manifold.hull_points(np.array(pts, float))
            out = h if out is None else out + h
    return out


POD = [(-122.0, 68.0, -9.3), (-176.0, 86.0, -9.0), (-293.0, 70.0, -11.0), (-365.0, 76.5, -15.0), (-382.0, 62.0, -15.0)]   # side pod stations (x, outer |y|, top z): the waist line peaks at x -176, flares out at the rear and tapers down
SHOULDER = dict(stations=[(-440.0, 1.0), (-300.0, 1.0), (-120.0, 0.25)], z0=50.0, z1=58.0, depth=6.0)
if CONCEPT:
    POD = [(-85.0, 66.0, 76.0), (-123.0, 84.0, 70.0), (-150.0, 92.0, 60.0), (-205.0, 92.0, 52.0), (-293.0, 92.0, 52.0), (-335.0, 86.0, 46.0), (-365.0, 76.5, -15.0), (-382.0, 62.0, -15.0)]   # rear pods with a shoulder plane stepping down from the cowl (arm arches are cut out of it by the window cut)

if CONCEPT:
    SHOULDER = dict(stations=[(-440.0, 1.0), (-250.0, 1.0), (-100.0, 0.3)], z0=50.0, z1=58.0, depth=6.0)   # shoulder crease: full at the rear, tapering to nothing toward the front


def _tent_y(z):
    return 68.0 - (max(z, -9.3) + 9.3) * TENT_K


def pods(inset=0.0):
    """Side pods below the shoulder: hull between stations of a (y, z) profile with a vertical outer face and an angled top returning into the flank."""
    polys = []
    for _, yo, zt in POD:
        yf = _tent_y(zt)
        zb = -26.0 - (30.0 if inset else 0.0)
        p = Polygon([(30.0, zb), (max(yo, yf + 0.5), zb), (max(yo, yf + 0.5), zt - 6.0), (yf, zt), (30.0, zt)])
        polys.append(p.buffer(-inset, join_style=2) if inset else p)
    return _hull_sections([x for x, _, _ in POD], polys)


def shoulder_cut(inset=0.0):
    """The shoulder crease: the thin triangle between the plain flank tent and a bevelled one, hulled between stations so it tapers out toward the front."""
    tent = Polygon(to_new(SECTION, "sec")).buffer(-inset, join_style=2)
    S = SHOULDER
    polys = []
    for _, k in S["stations"]:
        ap = _tent_y(S["z1"]) - S["depth"] * k
        bev = Polygon([(-68, -40), (68, -40), (68, -9.3), (_tent_y(S["z0"]), S["z0"]), (ap, S["z1"]), (SEC_TOP[0], SEC_TOP[1]), (-SEC_TOP[0], SEC_TOP[1]), (-ap, S["z1"]), (-_tent_y(S["z0"]), S["z0"]), (-68, -9.3)]).buffer(-inset, join_style=2)
        d = tent.difference(bev)
        d = max([g for g in d.geoms if g.geom_type == "Polygon" and g.centroid.x > 0.0], key=lambda g: g.area) if hasattr(d, "geoms") else d                      # drop numerical slivers
        pts = [c for c in d.buffer(0.3, join_style=2).exterior.coords if c[0] > 0.0]               # a hair past the tent: no coplanar faces
        polys.append(MultiPoint(pts).convex_hull)
    return _hull_sections([x for x, _ in S["stations"]], polys)


def fenders(inset=0.0):
    """Rear fender flare over the wheel arch: a hull between three plan stations, vertical outer face with a 45-degree-ish top chamfer."""
    zf, zc, zt, run = FENDER_Z
    polys = []
    for _, yo in FENDER:
        zb = zf - (30.0 if inset else 0.0)                                  # the cavity runs out through the bottom: an open skirt, no floor rim
        p = Polygon([(36.0, zb), (yo, zb), (yo, zc), (yo - run, zt), (36.0, zt)])
        polys.append(p.buffer(-inset, join_style=2) if inset else p)
    return _hull_sections([x for x, _ in FENDER], polys)


def solid(inset=0.0, belly=False):
    side = Polygon(to_new(SIDE, "side")).buffer(-inset, join_style=2)
    hp = to_new(HALF, "plan")
    plan_pts = hp + [(x, -y) for x, y in reversed(hp)]
    plan = Polygon(plan_pts).buffer(-inset, join_style=2)
    sec = Polygon(to_new(SECTION, "sec")).buffer(-inset, join_style=2)
    sidep = MB.prism_xz(list(side.exterior.coords)[:-1], -120.0, 120.0)
    s = MB.prism_xy(list(plan.exterior.coords)[:-1], -120.0, 140.0) ^ sidep ^ prism_yz(list(sec.exterior.coords)[:-1], -500.0, 100.0)
    s = s - shoulder_cut(inset) + ((fenders(inset) + pods(inset)) ^ sidep)
    if belly:                                        # open belly: remove the floor with a straight prism of the cavity's plan (no stepped sweep: the lower edge stays clean)
        floor = MB.prism_xy(list(plan.exterior.coords)[:-1], -80.0, -26.0 + inset + 0.01) ^ Manifold.cube((296.2 + STRETCH, 400.0, 100.0), center=False).translate((-296.6 - STRETCH, -200.0, -80.0))
        s = s + floor
    return s



from shapely.geometry import LineString


def _poly(kind, inset):
    if kind == "side":
        return Polygon(to_new(SIDE, "side")).buffer(-inset, join_style=2)
    hp = to_new(HALF, "plan")
    return Polygon(hp + [(x, -y) for x, y in reversed(hp)]).buffer(-inset, join_style=2)


def top_z(x, inset=0.0):
    """Old roofline (frame-facing: the roof tab nodes hang from it)."""
    g = LineString([(x, -500), (x, 500)]).intersection(Polygon(to_new(SIDE_BASE, "side")).buffer(-inset, join_style=2))
    return g.bounds[3]


def _tz(x, inset=0.0):
    """Actual skin top at the centre line."""
    g = LineString([(x, -500), (x, 500)]).intersection(_poly("side", inset))
    return g.bounds[3]


def hw_in(x, inset=WALL):
    g = LineString([(x, -500), (x, 500)]).intersection(_poly("plan", inset))
    return g.bounds[3]


def cyl_m(c, r, h, axis="z"):
    m = Manifold.cylinder(h, r, r, 32, True)
    if axis == "y":
        m = m.rotate((90.0, 0.0, 0.0))
    elif axis == "x":
        m = m.rotate((0.0, 90.0, 0.0))
    return m.translate(c)




def details(body):
    """Pads, posts, seam bosses, antenna boss, base-style details. Returns the body with them added."""
    import parts.w3_frame as FR
    for tx, ty, tz in FR._tab_pos()[3:]:                                   # hood boss over the frame's magnet pad (no screws: hinge + magnets hold the skin)
        ztop = 50.6 if not CONCEPT else _tz(tx, WALL) + 0.8                  # concept: posts reach up to the (taller) roof underside
        for s in (1, -1):
            zb = tz + FR.TAB_BOSS
            if CONCEPT:                                                      # foot of 4.5 mm radius round the magnet, a slimmer post up to the taller roof (kept inside the flank)
                rp = max(2.5, min(4.5, _tent_y(ztop) - abs(ty) - 1.0))
                body = body + cyl_m((tx, s * ty, zb + 4.0), 4.5, 8.0) + cyl_m((tx, s * ty, 0.5 * (zb + 4.0 + ztop)), rp, ztop - zb - 4.0)
            else:
                body = body + cyl_m((tx, s * ty, 0.5 * (zb + ztop)), 4.5, ztop - zb)
            body = body - cyl_m((tx, s * ty, zb + 0.95), FR.MAG_D / 2, 2.2)                      # matching pocket for the magnet
    scoop, cavity = flank_intake()
    body = body + scoop - cavity
    for k in (-1, 0, 1):                                              # nose light bar: 3 LED holes (3.2 mm) centred between the hinge ears, 7 mm pitch
        body = body - Manifold.cylinder(24.0, 1.6, 1.6, 24).rotate((0.0, 90.0, 0.0)).translate((20.0, 7.0 * k, 33.5))
    wedge, cav = hood_scoop()
    body = body + wedge - cav                                         # hood scoop, 50 % of the hood width
    # tail-light face: a 0.8 mm recess across the short vertical face at the end of the roof (painted red/black)
    (bx, bz), (cx_, cz_) = TAIL[2], TAIL[1]
    dvec = np.array([cx_ - bx, cz_ - bz]); dvec /= np.linalg.norm(dvec)
    nvec = np.array([-dvec[1], dvec[0]])
    if nvec[0] > 0:
        nvec = -nvec                                                      # outward = rearward
    p0, p1 = np.array([bx, bz]) + dvec * 3.0, np.array([cx_, cz_]) - dvec * 3.0
    quad = [tuple(p0 + nvec * 3.0), tuple(p1 + nvec * 3.0), tuple(p1 - nvec * 3.0), tuple(p0 - nvec * 3.0)]
    body = body - (MB.prism_xz(quad, -31.0, 31.0) - solid(0.8))
    body = body - canopy_cut() + canopy_cage()
    if CONCEPT:
        body = body - pink_grooves()
    # roof gills over the motor: slanted slats, openings facing the rear; the slats run across y so both sides are mirror images
    for s_ in (1, -1):
        rect = [(back(-237.0), s_ * 5.0), (back(-205.0), s_ * 5.0), (back(-205.0), s_ * 37.0), (back(-237.0), s_ * 37.0)]
        body = body - (MB.prism_xy(rect, -100.0, 200.0) - solid(0.8))                    # shallow pocket so the blades blend into the roof
    cuts, wedges, chans = roof_gills(back(-233.0), back(-209.0), 8.0, 34.0)
    body = body - cuts + wedges - chans
    import parts.w3_frame as _FR                                                           # hinge ears: the skin flips up on a pin through these and the frame's lugs
    for s in (1, -1):
        zt_ = top_z(_FR.HINGE_PIN[0], WALL) + 0.4
        y0, y1 = (_FR.HINGE_EAR[0], _FR.HINGE_EAR[1]) if s > 0 else (-_FR.HINGE_EAR[1], -_FR.HINGE_EAR[0])
        body = body + Manifold.cube((_FR.HINGE[0][1] - _FR.HINGE[0][0], y1 - y0, zt_ - 28.0), center=False).translate((_FR.HINGE[0][0], y0, 28.0))
        body = body - cyl_m((_FR.HINGE_PIN[0], s * 0.5 * (_FR.HINGE_EAR[0] + _FR.HINGE_EAR[1]), _FR.HINGE_PIN[1]), _FR.HINGE_D / 2, 8.0, 'y')
    _tl = __import__('parts.w3_tail', fromlist=['screw_holes'])
    body = body + _tl.screw_bosses() - _tl.screw_holes()                       # wing feet screw onto the hood from inside, so the wing flips up with the skin
    body = body - __import__('parts.w3_frame', fromlist=['relief']).relief()
    body.num_tri()                                                             # evaluate now: the lazily batched boolean chain leaves sliver triangles at the 4 deg rake
    _sw = __import__('w3_swing')
    env = _sw.rear_travel_channels()
    hp = MultiPoint([(float(x), float(z)) for x, y, z in MB.to_trimesh(env).vertices if abs(y) > 40.0]).convex_hull.simplify(1.0)
    body = body - MB.prism_xz(list(hp.exterior.coords)[:-1], 30.0, 100.0) - MB.prism_xz(list(hp.exterior.coords)[:-1], -100.0, -30.0)   # one straight-edged trim over the full wheel/arm travel envelope
    body.num_tri()
    body = body - env                                                          # wheel arch: the rear tyre and swing arm over their full travel (25 mm up, 20 mm down)
    body.num_tri()
    body = body - _sw.swing_channels().translate((0.0031, 0.0017, 0.0023))       # a few microns off: exact coincidence with the frame relief left a pinched edge; open-ended channels for the frame tubes
    return body


CX_WAIST, CX_K = -211.0, STRETCH / 360.0 + 1.0          # canopy centred at 52 % of the stretched body length, 1.25 x its old length
CANOPY_HALF = [(CX_WAIST + (x - -165.0) * CX_K, y) for x, y in [(-198, 18), (-189, 27), (-178, 27), (-165, 17), (-152, 27), (-141, 27), (-132, 18)]]   # hourglass opening (y > 0 side), pinched at the waist
CX_FRONT, CX_REAR = CANOPY_HALF[-1][0], CANOPY_HALF[0][0]
RIM = 3.0                                                                  # 45-degree rim chamfer width


def _cage_feet():
    """Where the canopy pillars meet the hull (x, |y|): rear outer, front outer, windscreen base; shared by the cut-out and the cage."""
    return dict(xo_r=CX_REAR - 20.0, yo_r=34.5, xo_f=CX_FRONT, yo_f=34.0, xs_b=CX_FRONT + 21.4, ys_b=12.6, xs_c=CX_FRONT + 28.0, ys_c=23.0)


def canopy_cut():
    """The opening under the canopy: a convex polygon through the pillar feet (rear outer, front outer, windscreen base), cut through the roof with a 45-degree rim."""
    f = _cage_feet()
    pts = [(f["xo_r"], f["yo_r"]), (f["xo_f"], f["yo_f"]), (f["xs_b"], f["ys_b"]), (f["xs_b"], -f["ys_b"]), (f["xo_f"], -f["yo_f"]), (f["xo_r"], -f["yo_r"])]
    cut = MB.prism_xy(pts, 45.0, 200.0)
    grown = Polygon(pts).buffer(RIM + 0.5, join_style=2)
    P = [(x, y, _tz(x, 0.0) - RIM) for x, y in pts]
    Q = [(x, y, _tz(x, 0.0) + 0.5) for x, y in list(grown.exterior.coords)[:-1]]
    return cut + Manifold.hull_points(np.array(P + Q, float))


def _strut(a, b, w=4.0):
    """Square-section strut between two points (hull of two small boxes)."""
    h = w / 2.0
    pts = [(x + dx, y + dy, z + dz) for (x, y, z) in (a, b) for dx in (-h, h) for dy in (-h, h) for dz in (-h, h)]
    return Manifold.hull_points(np.array(pts, float))


CAGE = dict(h=6.0 if CONCEPT else 16.0, t=3.0, yr=21.5, ro=34.5)


def canopy_cage():
    """Covered canopy as a cage: a flat roof slab (parallel to the roofline) held by diagonal pillars that run to the roof surface, with open side
    windows and an open windscreen between the pillars; low rails ring the foot of the screen.  Top view follows the owner's sketch."""
    c = CAGE
    zt = lambda x: _tz(x, 0.0)
    zr = lambda x: zt(x) + c["h"]
    xa, xb = CX_REAR - 8.0, CX_FRONT - 23.0                                 # roof slab rear and front edges
    f = _cage_feet()
    xo_r, xo_f, xs_c, xs_b = f["xo_r"], f["xo_f"], f["xs_c"], f["xs_b"]    # outer feet (rear, front), windscreen corner and base
    out = MB.prism_xz([(xa, zr(xa)), (xb, zr(xb)), (xb, zr(xb) + c["t"]), (xa, zr(xa) + c["t"])], -c["yr"] - 2.0, c["yr"] + 2.0)
    foot = lambda x, y: (x, y, zt(x) - 1.0)
    for s_ in (1, -1):
        top = lambda x: (x, s_ * c["yr"], zr(x))
        for p, q in ((top(xa), foot(xo_r, s_ * c["ro"])), (top(xb), foot(xo_f, s_ * 34.0)), (top(xb), foot(xs_b, s_ * 12.6))):
            out = out + _strut(p, q)
        ring = [foot(xo_f, s_ * 34.0), foot(xs_c, s_ * 23.0), foot(xs_b, s_ * 12.6)]       # low rails along the foot of the screen
        for p, q in zip(ring, ring[1:]):
            out = out + _strut((p[0], p[1], p[2] + 1.0), (q[0], q[1], q[2] + 1.0), 4.0)
    out = out + _strut((foot(xs_b, 12.6)[0], 12.6, zt(xs_b)), (xs_b, -12.6, zt(xs_b)), 4.0)
    return out


GROOVE_W, GROOVE_D = 1.4, 0.7                       # pink accent lines as engraved grooves (paint colour regions): 1.4 wide, 0.7 deep (wall stays >= 1.7)
FLANK_LINES = [((-60.0, -2.37), (-330.0, -2.37)), ((-215.0, -4.0), (-300.0, 40.0)), ((-30.0, 8.0), (-125.0, 56.0))]       # (x, z) polylines on the flanks
ROOF_LINES = [((-8.0, 30.0), (-64.0, 30.0)), ((-255.0, 31.0), (-335.0, 31.0))]                                           # (x, |y|) lines on the hood and engine deck


def _band(p, q, w):
    d = np.array(q, float) - np.array(p, float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * w / 2.0
    return [tuple(np.array(p) + n), tuple(np.array(q) + n), tuple(np.array(q) - n), tuple(np.array(p) - n)]


def pink_grooves():
    """Shallow engraved lines that follow the skin: the outer 0.7 mm layer intersected with thin straight bands (flank bands in x-z, roof bands in x-y)."""
    layer = solid(0.0) - solid(GROOVE_D)
    cut = None
    for p, q in FLANK_LINES:
        for y0, y1 in ((45.0, 120.0), (-120.0, -45.0)):
            c = MB.prism_xz(_band(p, q, GROOVE_W), y0, y1)
            cut = c if cut is None else cut + c
    for p, q in ROOF_LINES:
        for s_ in (1, -1):
            c = MB.prism_xy(_band((p[0], s_ * p[1]), (q[0], s_ * q[1]), GROOVE_W), 30.0, 200.0)
            cut = cut + c
    return layer ^ cut


def front_window():
    """Hull of the front mechanism over the lean range, projected to (x, z), grown by 4 mm: a clean polygon cut through the flanks."""
    import w3_scene as S
    pts = []
    for ph in range(-25, 26, 5):
        for n, m, k in S.scene(float(ph)):
            if n.startswith(("arm_", "pod_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod")):
                pts += [(float(x), float(z)) for x, y, z in m.vertices[::7]]
    hull = MultiPoint(pts).convex_hull.buffer(8.0 if CONCEPT else 5.5, join_style=2).simplify(2.0)
    return hull


INTAKE = dict(x_rear=-205.0, x_front=-140.0, z_top=40.0, z_bot=8.0, x_bot_in=14.0, h=9.0)   # flank air intake: trapezoid narrowing downward, grows out of the flank at its rear edge, mouth opens forward


def _intake_poly(inset=0.0):
    c = INTAKE
    poly = Polygon([(c["x_rear"], c["z_top"]), (c["x_front"], c["z_top"]), (c["x_front"] - c["x_bot_in"], c["z_bot"]), (c["x_rear"] + c["x_bot_in"], c["z_bot"])])
    return poly.buffer(-inset, join_style=2) if inset else poly


def _intake_h(x):
    c = INTAKE
    return c["h"] * (x - c["x_rear"]) / (c["x_front"] - c["x_rear"])


def flank_intake():
    """One big air intake per flank: a faceted scoop that is flush with the flank at its rear edge and stands c.h out at the front, where the mouth
    opens forward; its cavity cuts through the flank into the shell.  Returns (scoop, cavity)."""
    out = cav = None
    outer, inner = _intake_poly(0.0), _intake_poly(WALL)
    for s_ in (1, -1):
        po = []
        for x, z in list(outer.exterior.coords)[:-1]:
            po += [(x, s_ * (_tent_y(z) - 1.0), z), (x, s_ * (_tent_y(z) + _intake_h(x)), z)]
        pc = []
        for x, z in list(inner.exterior.coords)[:-1]:
            pc += [(x, s_ * (_tent_y(z) - 6.0), z), (x, s_ * (_tent_y(z) + _intake_h(x) - WALL), z)]
        for x, z in list(inner.exterior.coords)[:-1]:                      # out through the front wall
            if x > INTAKE["x_front"] - INTAKE["x_bot_in"] - 1.0:
                pc += [(x + 5.0, s_ * (_tent_y(z) - 6.0), z), (x + 5.0, s_ * (_tent_y(z) + INTAKE["h"] - WALL), z)]
        o, c_ = Manifold.hull_points(np.array(po, float)), Manifold.hull_points(np.array(pc, float))
        out = o if out is None else out + o
        cav = c_ if cav is None else cav + c_
    return out, cav


def hood_scoop(xf=-36.0, xr=-76.0, hw=22.0, h=10.0, lean=6.0):
    """Ram-air scoop on the hood: a raised wedge (height h at the mouth, flush with the hood at the rear), half the hood width, whose front wall leans
    forward by `lean` (a parallelogram, not a 90 degree bend).  The cavity opens through the leaning front wall and has a hole through the hood floor."""
    zt = lambda x: _tz(x, 0.0)
    xt = xf + lean
    wedge = MB.prism_xz([(xf, zt(xf) - 1.0), (xt, zt(xt) + h), (xr, zt(xr)), (xr, zt(xr) - 1.0)], -hw, hw)
    sl = (zt(xt) + h - zt(xr)) / (xt - xr)
    tl = lambda x: zt(xr) + sl * (x - xr)                                               # the wedge's top line, extended
    xc = xr + 8.0
    cav = MB.prism_xz([(xf - 2.0, zt(xf - 2.0) - WALL - 2.0), (xt + 2.0, tl(xt + 2.0) - WALL), (xc, tl(xc) - WALL), (xc, zt(xc) - WALL - 2.0)], -(hw - WALL), hw - WALL)
    return wedge, cav


def roof_gills(x0, x1, y0, y1, n=4, slat=3.0, shift=8.0, blade=3.6):
    """Roof exhaust over the motor: n slanted slots across y; each is covered by a wedge that grows out of the roof at its front edge and rises
    3.6 mm at the rear, with closed ends (1.2 mm cheeks): the only opening is a slot in the wedge's rear face.  Returns (cuts, wedges, channels)."""
    pitch = (x1 - x0 - slat) / (n - 1)
    cuts = wedges = chans = None
    for k in range(n):
        xa = x0 + k * pitch
        zs = _tz(xa + slat / 2, 0.0)
        xt, xb = xa - 0.4 * shift, xa + 0.6 * shift                          # the slanted slot crosses the roof surface exactly at [xa, xa + slat]
        quad = [(xt, zs + 4.0), (xt + slat, zs + 4.0), (xb + slat, zs - 6.0), (xb, zs - 6.0)]
        xf, xr = xa + slat + 1.0, xa - blade                               # +x is forward: the wedge grows out of the roof at its FRONT edge and opens to the rear
        wq = [(xf, zs - 2.2), (xr, zs - 2.2), (xr, zs + 4.2), (xf, zs + 0.6)]
        cq = [(xa + slat - 0.5, zs - 0.1), (xr - 1.0, zs - 0.1), (xr - 1.0, zs + 3.0), (xa + slat - 0.5, zs + 0.1)]
        for s in (1, -1):
            ya, yb = (y0, y1) if s > 0 else (-y1, -y0)
            c = MB.prism_xz(quad, ya + 2.0, yb - 2.0)                         # the skin slot is shorter than the wedge: no slanted slot face shows at the ends
            w = MB.prism_xz(wq, ya - 0.4, yb + 0.4)
            ch = MB.prism_xz(cq, ya + 2.5, yb - 2.5)
            cuts = c if cuts is None else cuts + c
            wedges = w if wedges is None else wedges + w
            chans = ch if chans is None else chans + ch
    return cuts, wedges, chans


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outer = solid(0.0)
    inner = solid(WALL, belly=True)
    body = outer - inner
    win = front_window()
    wpts = list(win.exterior.coords)[:-1]
    from shapely.geometry import box as sbox
    low = win.intersection(sbox(-500.0, -500.0, 500.0, 25.0))                 # inboard of the arms only the servo level needs clearing
    lpts = list(low.exterior.coords)[:-1]
    for s in (1, -1):
        y0, y1 = (52.0, 100.0) if s > 0 else (-100.0, -52.0)                  # arm level: everything out
        body = body - MB.prism_xz(wpts, y0, y1)
        y0, y1 = (30.0, 52.0) if s > 0 else (-52.0, -30.0)                    # servo level: leave the upper shoulder as the frame's top beam
        body = body - MB.prism_xz(lpts, y0, y1)
    # (the old rear-arm exit windows are gone: the wall is solid and only the arm's own swept volume is carved, in swing_channels)
    body = details(body)
    m = MB.to_trimesh(body)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    m.export(OUT / "body3.stl")
    print("body3", len(m.faces), m.is_watertight, round(m.volume), np.round(m.bounds, 1).tolist())


if __name__ == "__main__":
    main()
