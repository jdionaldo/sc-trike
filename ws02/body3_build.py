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
    body = body + windscreen() + canopy_cover()[0]
    body = body - canopy_cover()[1] - canopy_cut()
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
SCREEN = dict(xf=CX_FRONT + 45.0, xr=CX_FRONT, wf=20.0, wr=32.0, h=16.0, top_in=7.0)   # windscreen: raked wedge rising rearward to a header over the canopy front edge


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


def canopy_cover():
    """Covered canopy: a convex, angular hull over the hourglass opening (base ring outside the 45-degree rim, top drawn in), returned as
    (outer solid, cavity).  The cavity opens down into the cockpit cut, so the cover is a 2.4 mm roof-and-wall shell."""
    base = MultiPoint(CANOPY_HALF + [(x, -y) for x, y in CANOPY_HALF]).convex_hull
    def hull(grow, dz):
        b = base.buffer(RIM + 3.4 + grow, join_style=2)
        t = base.buffer(RIM + 3.4 + grow - COVER_IN, join_style=2)
        P = [(x, y, top_z(x, 0.0) - 3.0 - 6.0 * (dz > 0)) for x, y in list(b.exterior.coords)[:-1]]
        Q = [(x, y, top_z(x, 0.0) + COVER_H - dz) for x, y in list(t.exterior.coords)[:-1]]
        return Manifold.hull_points(np.array(P + Q, float))
    return hull(0.0, 0.0), hull(-WALL, WALL)


def windscreen():
    """Raked windscreen: a hollow wedge that starts flush with the hood and rises rearward to a header at the canopy's front edge, narrower at the top
    (leaning sides).  Its cavity opens down into the shell."""
    c = SCREEN
    def hull(m, dz):
        zf, zr = top_z(c["xf"], 0.0), top_z(c["xr"], 0.0)
        pts = []
        for sg in (1, -1):
            pts += [(c["xf"] - m, sg * (c["wf"] - m), zf - 3.0), (c["xr"] + m, sg * (c["wr"] - m), zr - 3.0),
                    (c["xr"] + m, sg * (c["wr"] - c["top_in"] - m), zr + c["h"] - dz), (c["xf"] - m, sg * (c["wf"] - 2.0 - m), zf - dz)]
        return Manifold.hull_points(np.array(pts, float))
    return hull(0.0, 0.0) - hull(WALL * 1.1, WALL * 1.2)


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


def roof_gills(x0, x1, y0, y1, n=4, slat=3.0, shift=8.0, blade=3.6):
    """Roof exhaust over the motor: n slanted slots across y; each is covered by a wedge that grows out of the roof at its front edge and rises
    3.6 mm at the rear, with closed ends (1.2 mm cheeks): the only opening is a slot in the wedge's rear face.  Returns (cuts, wedges, channels)."""
    pitch = (x1 - x0 - slat) / (n - 1)
    cuts = wedges = chans = None
    for k in range(n):
        xa = x0 + k * pitch
        zs = top_z(xa + slat / 2, 0.0)
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
