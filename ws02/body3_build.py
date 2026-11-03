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

OUT = Path("out/mono3")
KX, KY, DZ, XOFF = 1.0, 1.0, 0.0, 0.0           # the profile below is already in the assembly frame
WALL = 2.4

# profile from the owner's sketch over the RT-1 sheet (assembly frame, mm): truncated nose, roof rising toward the rear, high rear hood
# with a scoop, open tail underside above the gearbox; wide mid body, narrow tail
NOSE_LOW = (-1.0, -26.0)                              # where the nose underside meets the chassis floor
NOSE_TH = math.atan2(53.0, 35.0)                      # underside slope (56.6 deg)
TAIL = _pts([(-299.0, 50.0), (-341.5, 66.4), (-348.1, 83.3)])                # new tail from the owner's markup: underside rising to the tail-light face, then the roof
WHEEL_C, WHEEL_R = (back(-360.0), RAXLE_Z), 62.0                                           # rear tyre (radius 56) plus 6 mm: the skin's rear edge follows this radius over the wheel
PEAK = (fx(-237.0), 100.4)                             # roof peak, moved forward along the tail's own descent line (z 97 at old x -259): one straight line from here to the tail light
ARC = [(WHEEL_C[0] + WHEEL_R * math.cos(math.radians(a_)), WHEEL_C[1] + WHEEL_R * math.sin(math.radians(a_))) for a_ in (-14, -7, 0, 10, 20, 30, 40, 50, 60, 70)]
SIDE = [(34, 40), (34, 27), NOSE_LOW] + ARC + TAIL[1:] + [PEAK, (-70.0, 63.0)]   # straight roofline, flat vertical nose face, wheel-arch rear edge, short raked tail   # straight roofline, flat vertical nose face, short raked tail
HALF = [(30, 38), (20, 44), (-28, 44), (-73.5, 47), (-91.3, 60), (-122, 66), (-176, 86), (-293, 70), (-365, 76.5), (-382, 49), (-400, 44), (-438, 38.5)]   # plan: a side pod swelling to y 86 at x -176, tapering to the rear arch (traced from the owner's markup)
SECTION = [(-68, -40), (68, -40), (68, -9.3), (35, 110), (-35, 110), (-68, -9.3)]   # (y, z): flanks lean in toward the roof, with a 45-degree-ish shoulder bevel at z 50..58


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
SHOULDER = dict(stations=[(-440.0, 1.0), (-300.0, 1.0), (-120.0, 0.25)], z0=50.0, z1=58.0, depth=6.0)   # shoulder crease: full at the rear, tapering to nothing toward the front


def _tent_y(z):
    return 68.0 - (max(z, -9.3) + 9.3) / 3.615


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
        bev = Polygon([(-68, -40), (68, -40), (68, -9.3), (_tent_y(S["z0"]), S["z0"]), (ap, S["z1"]), (35, 110), (-35, 110), (-ap, S["z1"]), (-_tent_y(S["z0"]), S["z0"]), (-68, -9.3)]).buffer(-inset, join_style=2)
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
        ztop = 50.6
        for s in (1, -1):
            zb = tz + FR.TAB_BOSS
            body = body + cyl_m((tx, s * ty, 0.5 * (zb + ztop)), 4.5, ztop - zb)
            body = body - cyl_m((tx, s * ty, zb + 0.95), FR.MAG_D / 2, 2.2)                      # matching pocket for the magnet
    body = body - louvers()
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
    body = body + roof_dam() - roof_dam_cavity()                                # one big air dam over the motor, opening forward
    import parts.w3_frame as _FR                                                           # hinge ears: the skin flips up on a pin through these and the frame's lugs
    for s in (1, -1):
        zt_ = top_z(_FR.HINGE_PIN[0], WALL) + 0.4
        y0, y1 = (_FR.HINGE_EAR[0], _FR.HINGE_EAR[1]) if s > 0 else (-_FR.HINGE_EAR[1], -_FR.HINGE_EAR[0])
        body = body + Manifold.cube((_FR.HINGE[0][1] - _FR.HINGE[0][0], y1 - y0, zt_ - 28.0), center=False).translate((_FR.HINGE[0][0], y0, 28.0))
        body = body - cyl_m((_FR.HINGE_PIN[0], s * 0.5 * (_FR.HINGE_EAR[0] + _FR.HINGE_EAR[1]), _FR.HINGE_PIN[1]), _FR.HINGE_D / 2, 8.0, 'y')
    _tl = __import__('parts.w3_tail', fromlist=['screw_holes'])
    body = body + _tl.screw_bosses() - _tl.screw_holes()                       # wing feet screw onto the hood from inside, so the wing flips up with the skin
    body = body - __import__('parts.w3_frame', fromlist=['relief']).relief()
    _sw = __import__('w3_swing')
    env = _sw.rear_travel_channels()
    hp = MultiPoint([(float(x), float(z)) for x, y, z in MB.to_trimesh(env).vertices if abs(y) > 40.0]).convex_hull.simplify(1.0)
    body = body - MB.prism_xz(list(hp.exterior.coords)[:-1], 30.0, 100.0) - MB.prism_xz(list(hp.exterior.coords)[:-1], -100.0, -30.0)   # one straight-edged trim over the full wheel/arm travel envelope
    body = body - env                    # wheel arch: the rear tyre and swing arm over their full travel (25 mm up, 20 mm down)
    body = body - __import__('w3_swing').swing_channels()                       # open-ended channels: the frame tubes slide out as the skin swings up on the nose hinge          # slots where frame tubes pass through the skin
    return body


CX_WAIST, CX_K = -211.0, STRETCH / 360.0 + 1.0          # canopy centred at 52 % of the stretched body length, 1.25 x its old length
CANOPY_HALF = [(CX_WAIST + (x - -165.0) * CX_K, y) for x, y in [(-198, 18), (-189, 27), (-178, 27), (-165, 17), (-152, 27), (-141, 27), (-132, 18)]]   # hourglass opening (y > 0 side), pinched at the waist
CX_FRONT, CX_REAR = CANOPY_HALF[-1][0], CANOPY_HALF[0][0]
RIM = 4.0                                                                  # 45-degree rim chamfer width


def canopy_cut():
    """Open canopy: a pinched (hourglass) opening cut through the roof with a 45-degree rim chamfer on the sides and rear (the front edge stays
    vertical, it is the screen header).  Two convex halves joined at the waist, each a prism plus a chamfer hull following the sloped roof."""
    pts = CANOPY_HALF + [(x, -y) for x, y in reversed(CANOPY_HALF)]
    cut = MB.prism_xy(pts, 45.0, 200.0)
    xw = CX_WAIST
    for x0, x1 in ((CX_REAR, xw), (xw, CX_FRONT)):
        half = [p for p in pts if x0 - 1e-6 <= p[0] <= x1 + 1e-6]
        a = MultiPoint(half).convex_hull
        grown = a.buffer(RIM + 0.5, join_style=2)
        grown = grown.intersection(Polygon([(-1e3, -1e3), (CX_FRONT, -1e3), (CX_FRONT, 1e3), (-1e3, 1e3)]))   # keep the front edge vertical
        P = [(x, y, top_z(x, 0.0) - RIM) for x, y in list(a.exterior.coords)[:-1]]
        Q = [(x, y, top_z(x, 0.0) + 0.5) for x, y in list(grown.exterior.coords)[:-1]]
        cut = cut + Manifold.hull_points(np.array(P + Q, float))
    return cut

COVER_H, COVER_IN = 18.0, 9.0          # canopy cover: height over the roof, and how far the top is drawn in (45-degree-ish leaning sides)


def _strut(a, b, w=4.0):
    """Square-section strut between two points (hull of two small boxes)."""
    h = w / 2.0
    pts = [(x + dx, y + dy, z + dz) for (x, y, z) in (a, b) for dx in (-h, h) for dy in (-h, h) for dz in (-h, h)]
    return Manifold.hull_points(np.array(pts, float))


CAGE = dict(h=16.0, t=3.0, yr=21.5, ro=34.5)


def canopy_cage():
    """Covered canopy as a cage: a flat roof slab (parallel to the roofline) held by diagonal pillars that run to the roof surface, with open side
    windows and an open windscreen between the pillars; low rails ring the foot of the screen.  Top view follows the owner's sketch."""
    c = CAGE
    zt = lambda x: top_z(x, 0.0)
    zr = lambda x: zt(x) + c["h"]
    xa, xb = CX_REAR - 8.0, CX_FRONT - 23.0                                 # roof slab rear and front edges
    xo_r, xo_f = CX_REAR - 20.0, CX_FRONT                                   # outer feet, rear and front
    xs_c, xs_b = CX_FRONT + 28.0, CX_FRONT + 21.4                           # windscreen corner and base
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


def front_window():
    """Hull of the front mechanism over the lean range, projected to (x, z), grown by 4 mm: a clean polygon cut through the flanks."""
    import w3_scene as S
    pts = []
    for ph in range(-25, 26, 5):
        for n, m, k in S.scene(float(ph)):
            if n.startswith(("arm_", "pod_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod")):
                pts += [(float(x), float(z)) for x, y, z in m.vertices[::7]]
    hull = MultiPoint(pts).convex_hull.buffer(5.5, join_style=2).simplify(2.0)
    return hull


LOUVER = dict(x_top=(-192.0, -136.0), x_bot=(-178.0, -150.0), z0=8.0, z1=40.0, n=5, slat=3.0, tilt=0.6)   # louvered flank intake: a trapezoid that narrows downward, angled slots


def louvers():
    """Louvered air intake on each flank: n angled slots cut through the skin inside a trapezoid that tapers downward."""
    c = LOUVER
    pitch = (c["z1"] - c["z0"]) / c["n"]
    xl = lambda z: np.interp(z, [c["z0"], c["z1"]], [c["x_bot"][0], c["x_top"][0]])
    xr = lambda z: np.interp(z, [c["z0"], c["z1"]], [c["x_bot"][1], c["x_top"][1]])
    out = None
    for k in range(c["n"]):
        za, zb = c["z0"] + k * pitch, c["z0"] + (k + 1) * pitch - c["slat"]
        slot = MB.prism_xz([(xl(za), za), (xr(za), za), (xr(zb), zb), (xl(zb), zb)], 0.0, 100.0)
        mat = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, -c["tilt"], 1.0, c["tilt"] * 60.0]])
        slot = slot.transform(mat)
        out = slot if out is None else out + slot
    band = prism_yz([(_tent_y(0.0) - 6.0, 0.0), (_tent_y(0.0) + 2.0, 0.0), (_tent_y(60.0) + 2.0, 60.0), (_tent_y(60.0) - 6.0, 60.0)], -300.0, 0.0)
    out = out ^ band
    return out + out.mirror((0.0, 1.0, 0.0))


def hood_scoop(xf=-36.0, xr=-76.0, hw=22.0, h=10.0, lean=6.0):
    """Ram-air scoop on the hood: a raised wedge (height h at the mouth, flush with the hood at the rear), half the hood width, whose front wall leans
    forward by `lean` (a parallelogram, not a 90 degree bend).  The cavity opens through the leaning front wall and has a hole through the hood floor."""
    zt = lambda x: top_z(x, 0.0)
    xt = xf + lean
    wedge = MB.prism_xz([(xf, zt(xf) - 1.0), (xt, zt(xt) + h), (xr, zt(xr)), (xr, zt(xr) - 1.0)], -hw, hw)
    sl = (zt(xt) + h - zt(xr)) / (xt - xr)
    tl = lambda x: zt(xr) + sl * (x - xr)                                               # the wedge's top line, extended
    xc = xr + 8.0
    cav = MB.prism_xz([(xf - 2.0, zt(xf - 2.0) - WALL - 2.0), (xt + 2.0, tl(xt + 2.0) - WALL), (xc, tl(xc) - WALL), (xc, zt(xc) - WALL - 2.0)], -(hw - WALL), hw - WALL)
    return wedge, cav


DAM = dict(x_rear=back(-237.0), x_out=-300.0, x_apex=-278.0, y_out=35.0, y_in=8.3, h=10.0)   # roof air dam: funnel in plan (mouth 16.6 wide at the front, widening to y +-35 toward the rear), tallest at the mouth


def _dam_plan():
    d = DAM
    return [(d["x_apex"], d["y_in"]), (d["x_out"], d["y_out"]), (d["x_rear"], d["y_out"]), (d["x_rear"], -d["y_out"]), (d["x_out"], -d["y_out"]), (d["x_apex"], -d["y_in"])]


def _dam_height(x):
    d = DAM
    return d["h"] * (x - d["x_rear"]) / (d["x_apex"] - d["x_rear"]) + 0.5


def roof_dam():
    """One big air dam on the roof: a faceted hull that grows out of the roof at the rear and stands tallest at a front mouth (the opening faces forward)."""
    pts = []
    for x, y in _dam_plan():
        zt = top_z(x, 0.0)
        pts += [(x, y, zt - 1.0), (x, y, zt + _dam_height(x))]
    return Manifold.hull_points(np.array(pts, float))


def roof_dam_cavity():
    """Cavity of the dam: open through the front mouth, with a window through the roof floor into the shell below (the motor's air path)."""
    d = DAM
    plan = Polygon(_dam_plan()).buffer(-WALL, join_style=2)
    pts = []
    for x, y in list(plan.exterior.coords)[:-1]:
        zt = top_z(x, 0.0)
        pts += [(x, y, zt - 5.0), (x, y, zt + _dam_height(x) - WALL)]
    xm = d["x_apex"] + 4.0                                                       # out through the front wall
    for y in (d["y_in"] - WALL, -(d["y_in"] - WALL)):
        zt = top_z(xm, 0.0)
        pts += [(xm, y, zt - 5.0), (xm, y, zt + _dam_height(d["x_apex"]) - WALL)]
    return Manifold.hull_points(np.array(pts, float))


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
