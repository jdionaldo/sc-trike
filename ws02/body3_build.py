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

OUT = Path("out/mono3")
KX, KY, DZ, XOFF = 1.0, 1.0, 0.0, 0.0           # the profile below is already in the assembly frame
WALL = 2.4

# profile from the owner's sketch over the RT-1 sheet (assembly frame, mm): truncated nose, roof rising toward the rear, high rear hood
# with a scoop, open tail underside above the gearbox; wide mid body, narrow tail
NOSE_LOW = (-1.0, -26.0)                              # where the nose underside meets the chassis floor
NOSE_TH = math.atan2(53.0, 35.0)                      # underside slope (56.6 deg)
TAIL = [(-299.0, 50.0), (-341.5, 66.4), (-348.1, 83.3)]                # new tail from the owner's markup: underside rising to the tail-light face, then the roof
WHEEL_C, WHEEL_R = (-360.0, -11.0), 62.0                                           # rear tyre (radius 56) plus 6 mm: the skin's rear edge follows this radius over the wheel
ARC = [(WHEEL_C[0] + WHEEL_R * math.cos(math.radians(a_)), WHEEL_C[1] + WHEEL_R * math.sin(math.radians(a_))) for a_ in (-14, -7, 0, 10, 20, 30, 40, 50, 60, 70)]
SIDE = [(34, 40), (34, 27), NOSE_LOW] + ARC + TAIL[1:] + [(-259, 97)]   # straight roofline, flat vertical nose face, wheel-arch rear edge, short raked tail   # straight roofline, flat vertical nose face, short raked tail
HALF = [(30, 38), (20, 44), (-28, 44), (-73.5, 47), (-91.3, 60), (-120, 66), (-189, 74), (-229, 60), (-245, 61), (-254, 59), (-258, 57.5), (-266, 47.5), (-280, 43.5), (-300, 42.5), (-340, 40), (-348, 38.5)]
SECTION = [(-68, -40), (68, -40), (68, -9.3), (35, 110), (-35, 110), (-68, -9.3)]           # (y, z): flanks lean in toward the roof


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


ROCK = dict(zb=-26.0, zp=-10.0, zt=2.0, b=5.5)       # base, peak height, blend-out height above the peak, peak bulge (mm)


def _plan_hw(x):
    xs = [p[0] for p in sorted(HALF)]
    ys = [p[1] for p in sorted(HALF)]
    return float(np.interp(x, xs, ys))


def rocker(inset=0.0):
    """Rocker panels: an angular bulge along the lower flank (peak 5.5 mm out at z -10) that angles back in to the base plate below and blends
    into the flank above.  Built as hulls of cross-sections at the plan's own breakpoints, so the surface is exact and flat-faced."""
    r = ROCK
    xs = sorted({x for x, _ in HALF if -229.0 < x < -28.0} | {-229.0, -42.0, -28.0})
    def scale(x):                                                       # full bulge from x -189 forward, tapering to nothing at x -229 (one long smooth face)
        return float(np.clip((x + 229.0) / 40.0, 0.0, 1.0) * np.clip((-28.0 - x) / 14.0, 0.0, 1.0))
    def pts(x, sgn):
        w0 = min(_plan_hw(x), 68.0) - inset
        bb = r["b"] * scale(x)
        wt = min(w0, 68.0 - (r["zt"] + 9.3) / 3.615 - inset)             # the flank's own |y| at the blend height: the bulge's top edge lands exactly on it (no ledge)
        prof = [(wt - 10.0, r["zb"]), (w0, r["zb"]), (w0 + bb, r["zp"]), (wt, r["zt"]), (wt - 10.0, r["zt"])]
        return [(x, sgn * y, z) for y, z in prof]
    out = None
    for a, c in zip(xs, xs[1:]):
        for sgn in (1, -1):
            h = Manifold.hull_points(np.array(pts(a, sgn) + pts(c, sgn), float))
            out = h if out is None else out + h
    return out


def solid(inset=0.0, belly=False):
    side = Polygon(to_new(SIDE, "side")).buffer(-inset, join_style=2)
    hp = to_new(HALF, "plan")
    plan_pts = hp + [(x, -y) for x, y in reversed(hp)]
    plan = Polygon(plan_pts).buffer(-inset, join_style=2)
    sec = Polygon(to_new(SECTION, "sec")).buffer(-inset, join_style=2)
    s = MB.prism_xy(list(plan.exterior.coords)[:-1], -120.0, 140.0) ^ MB.prism_xz(list(side.exterior.coords)[:-1], -120.0, 120.0) ^ prism_yz(list(sec.exterior.coords)[:-1], -400.0, 100.0)
    s = s + rocker(inset)
    if belly:                                        # open belly: remove the floor with a straight prism of the cavity's plan (no stepped sweep: the lower edge stays clean)
        floor = MB.prism_xy(list(plan.exterior.coords)[:-1], -80.0, -26.0 + inset + 0.01) ^ Manifold.cube((296.2, 400.0, 100.0), center=False).translate((-296.6, -200.0, -80.0))
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
    tri = [(-226, 8), (-190, 8), (-208, 47)]                                   # one large exhaust vent per flank: recessed pocket, hole, covering scoop
    hole, wedge, chan = flank_vent(tri)
    body = body - hole + wedge - chan
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
    canopy = [(-198, -20), (-180, -28), (-150, -28), (-132, -20), (-132, 20), (-150, 28), (-180, 28), (-198, 20)]   # open canopy: a real cut through the roof, 45-degree corners
    body = body - MB.prism_xy(canopy, 45.0, 200.0)
    # roof gills over the motor: slanted slats, openings facing the rear; the slats run across y so both sides are mirror images
    for s_ in (1, -1):
        rect = [(-237.0, s_ * 5.0), (-205.0, s_ * 5.0), (-205.0, s_ * 37.0), (-237.0, s_ * 37.0)]
        body = body - (MB.prism_xy(rect, -100.0, 200.0) - solid(0.8))                    # shallow pocket so the blades blend into the roof
    cuts, wedges, chans = roof_gills(-233.0, -209.0, 8.0, 34.0)
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
    body = body - __import__('w3_swing').swing_channels()                       # open-ended channels: the frame tubes slide out as the skin swings up on the nose hinge          # slots where frame tubes pass through the skin
    return body



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


TENT_K = 68.0, -9.3, 3.615           # flank tent: y = 68 - (z + 9.3) / 3.615 above z -9.3


def _flank_y(x, z):
    """Skin outer surface |y| at (x, z): the smaller of the plan half width and the tent."""
    tent = TENT_K[0] - (z - TENT_K[1]) / TENT_K[2]
    return min(hw_in(min(max(x, -299.0), 29.0), 0.0), min(68.0, tent))


def _shear_y(m, s, zc):
    """Shear a flank solid so it follows the tent: |y| shrinks by 1/3.615 per mm of height above zc (left s=+1, right s=-1)."""
    k = 1.0 / TENT_K[2]
    mat = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, -s * k, s * k * zc], [0.0, 0.0, 1.0, 0.0]])
    return m.transform(mat)


def flank_vent(tri, blade=4.5):
    """One big exhaust vent per flank: the triangle is cut through the skin, covered by a scoop that grows out of the skin at its front edge and
    rises 4.5 mm at the rear; a channel inside the scoop opens to the rear only (the top, bottom and ends stay closed).  Returns (hole, scoop, channel)."""
    poly = Polygon(tri)
    xs = [p[0] for p in tri]
    xf, xr = max(xs) + 1.0, min(xs) - 2.0
    zc = poly.centroid.y
    ysf, ysr = _flank_y(xf, zc), _flank_y(xr, zc)
    yl = lambda x: ysf + (ysr - ysf) * (x - xf) / (xr - xf)                   # the flank's |y| along the vent (the plan is straight across this span)
    inner = list(poly.buffer(-1.2).exterior.coords)[:-1]
    grown = list(poly.buffer(1.0).exterior.coords)[:-1]
    hole = scoop = chan = None
    for s in (1, -1):
        h = _shear_y(MB.prism_xz(inner, 0.0 if s > 0 else -130.0, 130.0 if s > 0 else 0.0), s, zc)
        ramp = MB.prism_xy([(xf, s * (yl(xf) - 2.2)), (xr, s * (yl(xr) - 2.2)), (xr, s * (yl(xr) + blade)), (xf, s * (yl(xf) + 0.6))], zc - 40.0, zc + 40.0)
        sc = _shear_y(ramp, s, zc) ^ MB.prism_xz(grown, -200.0, 200.0)
        cq = MB.prism_xy([(xf - 1.0, s * (yl(xf - 1.0) - 4.0)), (xr + 3.0, s * (yl(xr + 3.0) - 4.0)), (xr + 3.0, s * (yl(xr + 3.0) + blade - 1.3)), (xf - 1.0, s * (yl(xf - 1.0) + 0.3))], zc - 40.0, zc + 40.0)
        ch = _shear_y(cq, s, zc) ^ MB.prism_xz(inner, -200.0, 200.0)
        # exit: a channel above the skin that runs out through the scoop's rear face, so the vent really opens to the rear
        ext = list(Polygon(inner).union(Polygon([(x - 10.0, z) for x, z in inner])).convex_hull.exterior.coords)[:-1]
        xe = xr + 0.7 * (xf - xr)
        tp = lambda x: 0.6 + (xf - x) / (xf - xr) * (blade - 0.6) - 1.3              # inner roof of the scoop above the flank at x
        ex = MB.prism_xy([(xr - 1.0, s * (yl(xr - 1.0) + 0.1)), (xe, s * (yl(xe) + 0.1)), (xe, s * (yl(xe) + tp(xe))), (xr - 1.0, s * (yl(xr - 1.0) + tp(xr - 1.0)))], zc - 40.0, zc + 40.0)
        ex = _shear_y(ex, s, zc) ^ MB.prism_xz(ext, -200.0, 200.0)
        ch = ch + ex
        hole = h if hole is None else hole + h
        scoop = sc if scoop is None else scoop + sc
        chan = ch if chan is None else chan + ch
    return hole, scoop, chan


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
