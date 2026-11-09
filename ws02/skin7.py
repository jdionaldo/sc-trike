"""Rev 7 faceted skin (WS03_SKIN=facet): a low-poly polyhedron lofted from per-station convex section polygons (flat panels, hard creases),
with faceted features (windscreen and side-window recesses with bezels, angular hood scoops, grille nose with bull bar, roll bar, lamp pods,
engine bay, octagonal rear arch). Stations are traced from sheet 61 (same body as sheet 60) and scaled to the 450 mm wheelbase."""
import os
import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import Polygon

import mono_build as MB

# Rev 9: strict trace of sheet 61 (trace61.py): side silhouette, plan and shoulder line come straight from the sheet; only the middle (roof/doors) is stretched to our wheelbase.
# Every section still has FIXED edge directions (vertical flank, bevel dy/dz -0.6, cabin flank dy/dz -0.12, horizontal floor/shelf/roof), so lateral quads stay planar.
import trace61 as T
S1, SC = 0.6, 0.12


def _pl(pts, x):
    q = sorted(reversed(list(pts)), key=lambda p: p[0])                  # stable: keeps the order of coincident-x vertices (a vertical step)
    return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))


_P = lambda pts, k="side": T.simplify(T.mm_polyline(pts, k))
YF = _P(T.PLAN, "plan")                                                      # plan half width (chisel nose, tapered hexagon, rear fender, tail)
ZR = _P(T.TOP)                                                               # roofline: hood, raked windscreen, roof, deck and tail
ZB = _P([(a, min(b, 10000)) for a, b in T.FLOOR])                            # floor: arch top, sill, rising rear fender rail
ZSH = _P(T.BELT)                                                             # shoulder shelf (belt line); hood top where there is no cabin
YR = _P(T.ROOFW, "plan")                                                     # roof / ridge half width
def _Xp(px):
    return T.to_xz(px, 706.0)[0]


_ZR0, _ZSH0 = ZR, ZSH
_xh, _xb = _Xp(380.0) + 1.0, _Xp(548.0) + 0.5
_xc = _Xp(267.0)                                                         # cowl base
_cz = _pl(T.mm_polyline(T.TOP), _xc) - (8.0 if T.ALONE else 2.0)                                               # cowl break forced to >= 15 deg (the sheet has 10 deg)
_MASK = T.ALONE and os.environ.get("WS03_MASK", "1") == "1"
if _MASK:                                                                # rev 12: plan, roofline and floor straight from the user's silhouette masks (mask61.py)
    import mask61
    _mt = mask61.tables()
    YF = mask61.merge(_mt["plan"], 15.0, 99.0); ZR = mask61.merge(_mt["top"], 15.0, 3.0); ZB = mask61.merge(_mt["bot"], 15.0, 2.0)
    ZB = [p for i, p in enumerate(ZB) if not (i > 0 and abs(p[0] - ZB[i - 1][0]) < 2.0 and abs(p[1] - ZB[i - 1][1]) < 2.0)]          # drop sub-2 mm steps (a 0.8 mm wall at the tail made a sliver)
    if not any(abs(p[0] - _xc) < 6.0 for p in ZR):                                                   # keep a cowl vertex on the roofline
        ZR = sorted(ZR + [(_xc, _pl(ZR, _xc))], reverse=True)
    _xcw = min((p for p in ZR if abs(p[0] - _xc) < 6.0), key=lambda p: abs(p[0] - _xc))[0]          # cowl vertex of the mask roofline
    _hood = [(a, b - 8.0 * min(1.0, (ZR[0][0] - a) / 25.0)) for a, b in ZR if a >= _xcw - 0.01]               # the hood centre is a ridge 8 mm above the side panels (the scoops sit beside it, so the silhouette stays the mask's)
    _rest = [p for p in _ZSH0 if p[0] <= _xb]
    ZSH = _hood + [(_rest[0][0], _hood[-1][1] - 6.0)] + _rest[1:]
    ZSH = [(a, min(b, _pl(ZR, a))) for a, b in ZSH]
elif T.ALONE:
    ZR = T.simplify([_ZR0[0], (_xc, _cz)] + [p for p in _ZR0 if p[0] <= _xh])
    _rest = [p for p in _ZSH0 if p[0] <= _xb]
    ZSH = T.simplify([_ZSH0[0], (_xc, _cz), (_rest[0][0], _cz - 6.0)] + _rest[1:])       # belt dips 6 mm behind the cowl (the sheet's window sill sits below the hood), so hood and belt break >= 15 deg
else:                                                                    # rev 9 (stretched, raked) numbers
    ZR = T.simplify([(28.0, 78.0), (-65.0, 97.0)] + [p for p in _ZR0 if p[0] <= -140.0])
    ZSH = T.simplify([(28.0, 78.0), (-81.0, 100.0)] + [p for p in _ZSH0 if p[0] <= -320.0])
BEV = 14.0                                                                   # shoulder bevel plan width


def _station(x):
    zb, yf, zr, zsh, yr = _pl(ZB, x), _pl(YF, x), _pl(ZR, x), _pl(ZSH, x), _pl(YR, x)
    zsh = min(zsh, zr)
    zb = min(zb, zsh - 6.0)
    zw = max(zsh - BEV / S1, zb + 2.0)
    ysh = max(yf - (zsh - zw) * S1, 1.0)
    yr = min(yr, ysh - 3.0)
    yc = yr + SC * (zr - zsh)
    return (x, zb, yf, zw, ysh, zsh, yc, yr, zr)


def _station_alone(x):
    zb, yf, zr, zsh = _pl(ZB, x), _pl(YF, x), _pl(ZR, x), _pl(ZSH, x)
    zsh = min(zsh, zr)
    zb = min(zb, zsh - 6.0)
    gb, gc = _pl(GB, x), _pl(GC, x)
    zw = (gb - yf) / S1
    ysh = gb - S1 * zsh
    if zw < zb + 2.0:                                                # no vertical flank left: clamp (not planar, listed if it happens)
        zw = zb + 2.0
        ysh = yf - (zsh - zw) * S1
    yr = gc - SC * zr
    yr = min(max(yr, 0.0), ysh - 3.0)
    yc = yr + SC * (zr - zsh)
    return (x, zb, yf, zw, ysh, zsh, yc, yr, zr)


if T.ALONE:                                                              # rev 11: oblique flank planes as offset polylines, so a break in zsh / zr / yr cannot bend a panel by a few degrees
    _kb, _kc = (1.0 + S1 * S1) ** 0.5, (1.0 + SC * SC) ** 0.5
    _xc1, _xc2, _xt1, _xt2 = _Xp(267.0), _Xp(267.0) - 22.0, _Xp(548.0) - 5.0, _Xp(548.0) - 45.0
    def _bev(x):                                                      # narrow bevel on the thin hood slab and on the tail rail, full width on the cabin
        w = 3.5 if x >= _xc1 else 0.0 if x <= _xt2 else (BEV if (_xc2 >= x >= _xt1) else None)
        if w is None:
            w = 3.5 + (BEV - 3.5) * (_xc1 - x) / (_xc1 - _xc2) if x > _xc2 else BEV * (x - _xt2) / (_xt1 - _xt2)
        return max(min(w, S1 * (min(_pl(ZSH, x), _pl(ZR, x)) - _pl(ZB, x) - 4.0)), 0.0 if x <= _xt2 else 3.0)
    GB = [(x, (_pl(YF, x) - _bev(x) + S1 * _pl(ZSH, x)) / _kb) for x in sorted({a for pts in (YF, ZSH, ZB) for a, _ in pts}, reverse=True)]   # bevel plane offset: ysh + S1 zsh = yf + S1 zw
    GC = [(x, (_pl(YR, x) + SC * _pl(ZR, x)) / _kc) for x in sorted({a for pts in (YR, ZR) for a, _ in pts}, reverse=True)]           # cabin flank offset: yr + SC zr = yc + SC zsh
    GB = [(a, b * _kb) for a, b in T.simplify(GB, 17.0)]
    GC = [(a, b * _kc) for a, b in T.simplify(GC, 17.0)]
else:
    GB = GC = None
if T.ALONE:                                                              # rev 11: snap breakpoints that lie within SNAP mm of each other onto one station so every lateral quad is exactly planar
    SNAP = 1.2 if _MASK else 3.5
    _all = sorted({a for pts in (YF, ZR, ZB, ZSH, YR, GB, GC) for a, _ in pts}, reverse=True)
    _cl, _cur = [], [_all[0]]
    for _x in _all[1:]:
        if _cur[-1] - _x < SNAP:
            _cur.append(_x)
        else:
            _cl.append(_cur); _cur = [_x]
    _cl.append(_cur)
    _map = {x: float(np.mean(c)) for c in _cl for x in c}
    YF, ZR, ZB, ZSH, YR, GB, GC = ([(_map[a], b) for a, b in pts] for pts in (YF, ZR, ZB, ZSH, YR, GB, GC))
_xs = sorted({a for pts in (YF, ZR, ZB, ZSH, YR) + ((GB, GC) if T.ALONE else ()) for a, _ in pts}, reverse=True)
XSTA = [_xs[0]]
for _x in _xs[1:]:
    if XSTA[-1] - _x >= (0.01 if T.ALONE else 2.5):
        XSTA.append(_x)
ST = [(_station_alone if T.ALONE else _station)(float(x)) for x in XSTA]
X0, X1 = ST[0][0], ST[-1][0]
XS = np.array([s[0] for s in ST])[::-1]


def _pitch(i):
    """Local roof pitch factor 1/cos(theta) at station i (steepest neighbour)."""
    k = 1.0
    for j in (i - 1, i + 1):
        if 0 <= j < len(ST):
            d = abs(ST[j][8] - ST[i][8]) / max(abs(ST[j][0] - ST[i][0]), 1e-6)
            k = max(k, (1.0 + d * d) ** 0.5)
    return k


def _polys(s, inset, belly=False, k=1.0, deep=False):
    x, zb, yf, zw, ysh, zsh, yc, yr, zr = s
    if inset > 0 and k > 1.0:
        zr = zr - inset * (k - 1.0)                                  # roof drop so the wall stays `inset` thick normal to a raked facet
    zbb = -200.0 if deep else (zb - 30.0 if belly else zb)              # open belly for the cavity; deep: no floor at all (detail layers must not form on the underside)
    lo = Polygon([(0, zbb), (yf, zbb), (yf, zw), (ysh, zsh), (0, zsh)])
    out = [lo]
    if zr > zsh + 1.0:
        k = (yc - yr) / (zr - zsh)
        out.append(Polygon([(0, zsh - 6.0), (yc + k * 6.0, zsh - 6.0), (yr, zr), (0, zr)]))
    res = []
    for p in out:
        q = p.buffer(-inset, join_style=2) if inset else p
        if q.is_empty or q.geom_type != "Polygon":
            continue
        res.append(q)
    return res


def _mirror(poly, x):
    c = list(poly.exterior.coords)[:-1]
    pts = [(x, y, z) for y, z in c] + [(x, -y, z) for y, z in c]
    return pts


def solid(inset=0.0, belly=False, deep=False):
    """Outer solid (inset 0), cavity (inset 2.4, belly=True) or a grown/shrunk layer: union of convex hulls between consecutive stations."""
    out = None
    pol = []
    for i, s in enumerate(ST):
        x = s[0] - inset if i == 0 else (s[0] + inset if i == len(ST) - 1 else s[0])
        pol.append((x, _polys(s, inset, belly, _pitch(i), deep)))
    for (xa, pa), (xb, pb) in zip(pol, pol[1:]):
        for k in range(2):
            if k >= len(pa) or k >= len(pb):
                continue
            pts = _mirror(pa[k], xa) + _mirror(pb[k], xb)
            h = Manifold.hull_points(np.array(pts, float))
            out = h if out is None else out + h
    if inset > 0 and belly:                                          # walls whose normal points along x (ramps between stations) get their thickness too
        d = 0.8 * inset
        out = out ^ out.translate((d, 0, 0)) ^ out.translate((-d, 0, 0))
    return out


def hw(x, inset=0.0):
    return _pl(YF, x) - inset


def tz(x, inset=0.0):
    return _pl(ZR, x) - inset


_M = {}


def surf(x, y):
    """Top surface height of the outer solid at (x, y), by ray cast."""
    if "m" not in _M:
        _M["m"] = MB.to_trimesh(solid(0.0))
    loc, _, _ = _M["m"].ray.intersects_location([[x, y, 400.0]], [[0, 0, -1]], multiple_hits=True)
    return float(loc[:, 2].max()) if len(loc) else float("nan")


def strut(a, b, w=4.0):
    h = w / 2.0
    pts = [(x + dx, y + dy, z + dz) for (x, y, z) in (a, b) for dx in (-h, h) for dy in (-h, h) for dz in (-h, h)]
    return Manifold.hull_points(np.array(pts, float))


def octagon(cx, cz, r):
    return [(cx + r * np.cos(np.radians(22.5 + 45 * k)), cz + r * np.sin(np.radians(22.5 + 45 * k))) for k in range(8)]


def Xp(px):
    """Sheet side-view px -> chassis x (mm)."""
    return T.to_xz(px, 706.0)[0]


def Xt(px):
    """Sheet top-view px -> chassis x (mm)."""
    return Xp(T.top_to_side_px(px))


def Zp(px, py):
    return T.to_xz(px, py)[1]


def features(body, S0, solid_fn, pink):
    if _MASK:                                                              # detail layers come from a skin without a floor, so nothing is added or cut on the open underside
        solid_fn = lambda i, belly=False: solid(i, belly, True)
        S0 = solid_fn(0.0)
    out15 = solid_fn(-2.5) - S0
    out30 = solid_fn(-2.2) - S0
    inl = S0 - solid_fn(1.0)
    pr = lambda poly: MB.prism_xy([(x + 0.213, y + 0.177) for x, y in poly], -60.0, 220.0)
    grow = lambda poly, d: list(Polygon(poly).buffer(d, join_style=2).exterior.coords)[:-1]
    body = body - pink()
    # 1. raked windscreen: hexagonal glass on the windscreen facets (sheet: front edge at the cowl, widest at the A-pillar feet, narrowing to the header)
    xc, xw, xh = Xt(262.0), Xt(297.0), Xt(380.0)
    W = [(xc - 2.0, 24.0), (xw, 50.0), (xh + 2.0, 27.0), (xh + 2.0, -27.0), (xw, -50.0), (xc - 2.0, -24.0)]
    body = body + (out15 ^ (pr(grow(W, 5.0)) - pr(W)))
    body = body - (inl ^ pr(grow(W, -0.4)))
    if _MASK:
        body = body + ((S0 - solid_fn(3.0)) ^ pr(grow(W, -3.0))) - ((S0 - solid_fn(1.8)) ^ pr(grow(W, -3.0)))      # inner glass pocket (wall thickened under it)
    # 2. large angular side windows on the cabin flank (sheet side view: bottom on the belt, raked A-pillar edge, flat top, raked rear edge)
    sw = [(367, 547), (364, 520), (412, 486), (514, 484), (484, 534)]
    SW = []
    for k, (px, py) in enumerate(sw):
        x = Xp(px)
        z = Zp(px, py)
        SW.append((x, min(max(z, _pl(ZSH, x) + 5.0), _pl(ZR, x) - 9.0)))
    swp = lambda poly: MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], 12.2, 90.0) + MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], -90.0, -12.2)
    body = body + (out15 ^ (swp(grow(SW, 4.5)) - swp(SW)))
    body = body - (inl ^ swp(grow(SW, -0.4)))
    if _MASK:
        body = body + ((S0 - solid_fn(3.0)) ^ swp(grow(SW, -3.0))) - ((S0 - solid_fn(1.8)) ^ swp(grow(SW, -3.0)))
    if _MASK:                                                              # 3. twin hood scoops beside the hood ridge, under the traced roofline: one inclined top plane (15.5 deg), vertical front face, open mouth
        Y = lambda x, d: _pl(YR, x) + d
        for s_ in (1, -1):
            foot = [(-18.0, Y(-18.0, 3.0)), (-18.0, Y(-18.0, 19.0)), (-45.0, Y(-45.0, 19.0)), (-45.0, Y(-45.0, 3.0))]
            pts = [(x, s_ * y, surf(x, y) - 2.0) for x, y in foot] + [(x, s_ * y, surf(x, y) + (7.5 if x > -20.0 else 0.0)) for x, y in foot]
            wedge = Manifold.hull_points(np.array(pts, float))
            ci = [(-20.0, Y(-20.0, 5.0)), (-20.0, Y(-20.0, 17.0)), (-41.0, Y(-41.0, 17.0)), (-41.0, Y(-41.0, 5.0))]
            cp = [(x, s_ * y, surf(x, y) - 3.0) for x, y in ci] + [(x, s_ * y, surf(x, y) + (4.5 if x > -22.0 else -0.6)) for x, y in ci]
            cav = Manifold.hull_points(np.array(cp, float))
            ym = Y(-22.0, 6.0)
            mouth = Manifold.cube((8.0, 10.0, 5.0), center=False).translate((-26.0, ym if s_ > 0 else -ym - 10.0, surf(-22.0, ym + 5.0) + 0.2))
            hole = MB.prism_xy([(-24.0, s_ * Y(-24.0, 6.0)), (-36.0, s_ * Y(-36.0, 6.0)), (-36.0, s_ * Y(-36.0, 16.0)), (-24.0, s_ * Y(-24.0, 16.0))], 40.0, 400.0) ^ (solid_fn(-1.0) - solid_fn(5.0))
            body = body + wedge - cav - mouth - hole
    elif T.ALONE:
        # 3. twin angular hood scoops: one inclined top plane (16.7 deg to the hood), vertical front face with an open mouth
        for s_ in (1, -1):
            foot = [(-8.0, 7.0), (-8.0, 25.0), (-38.0, 30.0), (-38.0, 10.0)]
            pts = [(x, s_ * y, surf(x, y) - 2.0) for x, y in foot] + [(x, s_ * y, surf(x, y) + (9.0 if x > -20.0 else 0.0)) for x, y in foot]
            wedge = Manifold.hull_points(np.array(pts, float))
            ci = [(-10.0, 9.0), (-10.0, 23.0), (-34.0, 27.0), (-34.0, 12.0)]
            cp = [(x, s_ * y, surf(x, y) - 3.0) for x, y in ci] + [(x, s_ * y, surf(x, y) + (6.0 if x > -20.0 else -0.6)) for x, y in ci]
            cav = Manifold.hull_points(np.array(cp, float))
            mouth = Manifold.cube((8.0, 10.0, 6.0), center=False).translate((-14.0, 10.0 if s_ > 0 else -20.0, surf(-10.0, 15.0) + 0.2))
            hole = MB.prism_xy([(-12.0, s_ * 11.0), (-30.0, s_ * 13.0), (-30.0, s_ * 23.0), (-12.0, s_ * 21.0)], 40.0, 400.0) ^ (solid_fn(-1.0) - solid_fn(5.0))
            body = body + wedge - cav - mouth - hole
    else:
        # 3. twin angular hood scoops (sheet: red-striped panels either side of the hood centre)
        for s_ in (1, -1):
            foot = [(-6.0, 6.0), (-50.0, 8.0), (-58.0, 28.0), (-34.0, 24.0), (-8.0, 15.0)]
            pts = [(x, s_ * y, surf(x, y) - 2.0) for x, y in foot] + [(x, s_ * y, surf(x, y) + (6.0 if x > -30.0 else 0.8)) for x, y in foot]
            wedge = Manifold.hull_points(np.array(pts, float))
            ci = [(-9.0, 9.0), (-46.0, 10.5), (-54.0, 25.0), (-34.0, 21.0), (-10.0, 14.0)]
            cp = [(x, s_ * y, surf(x, y) - 3.0) for x, y in ci] + [(x, s_ * y, surf(x, y) + (3.5 if x > -30.0 else -0.2)) for x, y in ci]
            cav = Manifold.hull_points(np.array(cp, float))
            mouth = Manifold.cube((10.0, 8.0, 5.0), center=False).translate((-20.0, 9.0 if s_ > 0 else -17.0, surf(-12.0, 12.0) + 0.2))
            hole = MB.prism_xy([(-12.0, s_ * 11.0), (-38.0, s_ * 12.0), (-38.0, s_ * 20.0), (-12.0, s_ * 16.0)], 40.0, 220.0) ^ (solid_fn(-1.0) - solid_fn(5.0))
            body = body + wedge - cav - mouth - hole
    # 4. door louvre slots and rear-fender vents
    for s_ in (1, -1):
        xl = Xp(318.0)
        for k in range(4):
            zl = Zp(318.0, 590.0) + 6.0 * k
            body = body - Manifold.cube((Xp(390.0) - Xp(318.0) if False else abs(Xp(390.0) - xl), 40.0, 2.4), center=False).translate((Xp(390.0), 40.0 if s_ > 0 else -80.0, zl))
        for k in range(3):
            xv = Xp(575.0) - 8.0 * k
            body = body - MB.prism_xy([(xv, s_ * 46.0), (xv - 3.0, s_ * 46.0), (xv - 3.0, s_ * 66.0), (xv, s_ * 66.0)], 60.0, 220.0)
    # 5. stepped sill panel with rivets
    xa, xb = Xp(305.0) - 0.43, Xp(553.0)
    za, zb_ = _pl(ZB, xa), _pl(ZB, xb)
    sill = [(xa, za), (xb, zb_), (xb, zb_ + 11.0), (xa, za + 11.0)]
    if _MASK:                                                              # recessed sill band (the plan mask is the outline: nothing may stand proud of it) with low rivet heads
        lay = S0 - solid_fn(1.4)
        body = body - (MB.prism_xz(sill, 30.0, 130.0) ^ lay) - (MB.prism_xz(sill, -130.0, -30.0) ^ lay)
        for s_ in (1, -1):
            for x in np.arange(xa - 10.0, xb + 10.0, -14.0):
                body = body + Manifold.sphere(1.6, 8).translate((float(x), s_ * (hw(float(x)) - 1.2), _pl(ZB, float(x)) + 5.5))
    else:
        body = body + (MB.prism_xz(sill, 30.0, 130.0) ^ out30) + (MB.prism_xz(sill, -130.0, -30.0) ^ out30)
        for s_ in (1, -1):
            for x in np.arange(xa - 10.0, xb + 10.0, -14.0):
                body = body + Manifold.sphere(1.6, 8).translate((float(x), s_ * (hw(float(x)) + 2.8), _pl(ZB, float(x)) + 7.0))
    # 6. roll bar behind the roof
    xr = Xp(552.0)
    zt = tz(xr) + 14.0
    for s_ in (1, -1):
        top = (xr, s_ * 22.0, zt)
        body = body + strut((xr + 10.0, top[1], tz(xr + 10.0) - 2.0), top, 4.0) + strut(top, (xr - 12.0, s_ * 22.0, tz(xr - 12.0) - 2.0), 4.0)
    body = body + strut((xr, -22.0, zt), (xr, 22.0, zt), 4.0)
    # 7. roof lamp pods (windscreen header corners)
    xl0 = Xp(385.0)
    for s_ in (1, -1):
        pts = [(x, y, tz(x) + dz) for x in (xl0 + 4.0, xl0 + 14.0) for y in ((28.0, 37.0) if s_ > 0 else (-37.0, -28.0)) for dz in (-2.0, 3.0 if _MASK else 6.0)]
        body = body + Manifold.hull_points(np.array(pts, float))
    # 8. open engine bay with mesh grille (sheet top view: rim behind the cabin, hole across the hump)
    e0, e1 = Xt(535.0), Xt(676.0)
    body = body - MB.prism_xy([(e0, -26.0), (e1, -26.0), (e1, 26.0), (e0, 26.0)], 60.0, 220.0)
    for i in range(3):
        for j in range(9):
            body = body - MB.prism_xy([(e1 - 5.0 * i, -22.0 + 5.0 * j), (e1 - 3.4 - 5.0 * i, -22.0 + 5.0 * j), (e1 - 3.4 - 5.0 * i, -18.6 + 5.0 * j), (e1 - 5.0 * i, -18.6 + 5.0 * j)], 60.0, 220.0)
    # 9. tail lamp bar on the tail face
    xt = ST[-1][0]
    zt0 = ST[-1][8]
    body = body + (MB.prism_xz([(xt - 6.0, zt0 - 24.0), (xt + 22.0, zt0 - 24.0), (xt + 22.0, zt0 - 17.0), (xt - 6.0, zt0 - 17.0)], -18.0, 18.0) ^ out30)
    # 10. diamond mesh grille through the nose face, and a hexagonal bull bar in front
    xn = ST[0][0]
    if _MASK:                                                              # the chin of the traced nose carries the grille and the bull bar, all inside the mask outline
        for zc, ys in ((108.0, (-9.0, -3.0, 3.0, 9.0)), (115.0, (-12.0, -6.0, 0.0, 6.0, 12.0)), (122.0, (-9.0, -3.0, 3.0, 9.0))):
            for yc_ in ys:
                pts = [(x, yc_ + dy, zc + dz) for x in (xn - 22.0, xn + 6.0) for dy, dz in ((2.8, 0.0), (-2.8, 0.0), (0.0, 2.8), (0.0, -2.8))]
                body = body - Manifold.hull_points(np.array(pts, float))
        zbb_ = 104.0
        bar = [(xn - 12.0, -20.0, zbb_), (xn - 6.0, -12.0, zbb_), (xn - 6.0, 12.0, zbb_), (xn - 12.0, 20.0, zbb_)]
        for a, b in zip(bar, bar[1:]):
            body = body + strut(a, b, 5.0)
        body = body + strut(bar[0], (xn - 17.0, -22.0, 118.0), 5.0) + strut(bar[-1], (xn - 17.0, 22.0, 118.0), 5.0)
        return details13(body, S0, solid_fn)
    zlo, zhi = ST[0][1], ST[0][8]
    for row, zc in enumerate((zlo + 7.0, zlo + 14.5)):
        ys = (-9.0, -3.0, 3.0, 9.0) if row == 0 else (-12.0, -6.0, 0.0, 6.0, 12.0)
        for yc_ in ys:
            pts = [(x, yc_ + dy, zc + dz) for x in (xn - 28.0, xn + 6.0) for dy, dz in ((3.0, 0.0), (-3.0, 0.0), (0.0, 3.0), (0.0, -3.0))]
            body = body - Manifold.hull_points(np.array(pts, float))
    zb_bar = zlo + 3.0
    bar = [(xn + 4.0, -22.0, zb_bar), (xn + 12.0, -14.0, zb_bar), (xn + 12.0, 14.0, zb_bar), (xn + 4.0, 22.0, zb_bar)]
    for a, b in zip(bar, bar[1:]):
        body = body + strut(a, b, 5.0)
    lx, lz = (xn - 4.0, zlo + 14.0) if T.ALONE else (xn - 8.0, zlo + 6.0)                  # leg ends inside the nose slab
    body = body + strut(bar[0], (lx, -22.0, lz), 5.0) + strut(bar[-1], (lx, 22.0, lz), 5.0)
    return body


def rear_arch(body):
    """Rev 9: the rear arch is the traced rising rail underside itself (the loft floor), nothing more to cut."""
    return body


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# Rev 13: detail layers read from sheet 61 (px of the 2000 x 848 sheet). Each detail is an outline polygon in the view where it is most visible, projected along that
# view direction onto the skin, with a raised bezel layer, one or two stepped recess layers and (where there is a lamp or glass) an inner pocket. Faceted: all steps are flat.
DETAILS = []                                                                # (name, view, vertices, layers) for the report


def prism_yz(pts, x0, x1):
    m = trimesh.creation.extrude_polygon(Polygon([(y + 0.173, z + 0.131) for y, z in pts]), x1 - x0)
    V = m.vertices
    return MB.man(trimesh.Trimesh(np.column_stack([V[:, 2] + x0 + 0.29, V[:, 0], V[:, 1]]), m.faces))


def _grow(poly, d):
    g = Polygon(poly).buffer(d, join_style=2)
    return list(g.exterior.coords)[:-1]


def details13(body, S0, solid_fn):
    if os.environ.get("NODET") == "1":
        return body
    cache = {}
    def lay_out(h):
        if ("o", h) not in cache:
            cache[("o", h)] = solid_fn(-h) - S0
        return cache[("o", h)]
    def lay_in(d):
        if ("i", d) not in cache:
            cache[("i", d)] = S0 - solid_fn(d)
        return cache[("i", d)]
    P_top = lambda p: MB.prism_xy([(x + 0.213, y + 0.177) for x, y in p], -60.0, 400.0)
    P_side = lambda p: MB.prism_xz([(x + 0.19, z + 0.23) for x, z in p], 12.2, 120.0) + MB.prism_xz([(x + 0.19, z + 0.23) for x, z in p], -120.0, -12.2)
    P_front = lambda p: prism_yz(p, -6.0, 42.0)
    P_rear = lambda p: prism_yz(p, -380.0, -342.3)

    def apply(name, view, prism, poly, bezel=None, cuts=()):
        nonlocal body
        if name in os.environ.get("SKIPDET", "").split(","):
            return
        if bezel:
            g, h = bezel
            body = body + (lay_out(h) ^ (prism(_grow(poly, g)) - prism(poly)))
        for shrink, d in cuts:
            pg = _grow(poly, -shrink) if shrink else poly
            if d > 1.0:                                                      # thicken the wall under a pocket so 1.2 mm of floor is left (walls are 2.4 mm)
                body = body + (lay_in(d + 1.2) ^ prism(_grow(pg, 0.6)))             # slightly wider than the pocket: no coincident side faces
            body = body - (lay_in(d) ^ prism(pg))
        DETAILS.append((name, view, len(poly), (f"bezel {bezel[1]} mm" if bezel else "no bezel") + "".join(f", recess {d} mm" + (f" (inner, -{s} mm)" if s else "") for s, d in cuts)))

    mir = lambda poly, c: [(2 * c - x, z) for x, z in poly]
    fyz = lambda px, py, dz=0.0: ((px - 1215.5) * 0.595, (383.0 - py) * 0.595 + dz)
    ryz = lambda px, py: ((px - 1720.0) * 0.595, (383.0 - py) * 0.595 + 12.0)
    ST0z = ST[0][1]
    # front view: headlight pockets (bezel, pocket, inner lamp), main and lower grille hexagons, side mesh pockets
    HL = [(1123, 168), (1163, 175), (1181, 184), (1174, 197), (1129, 188), (1123, 178)]
    for k_, pts in enumerate((HL, mir(HL, 1215.5))):
        apply("headlight pocket", "front", P_front, [fyz(px, py, 2.0) for px, py in pts], bezel=(2.0, 1.5), cuts=((0, 3.0), (3.0, 5.0)))
    GR = [(1170, 205), (1183, 191), (1245, 191), (1259, 204), (1247, 235), (1182, 235)]
    apply("main grille", "front", P_front, [(y, max(z, 106.0)) for y, z in [fyz(px, py, 2.0) for px, py in GR]], bezel=(2.0, 1.5), cuts=((0, 2.0),))
    SG = [(1133, 202), (1167, 207), (1172, 230), (1150, 240), (1135, 225)]
    for pts in (SG, mir(SG, 1215.5)):
        apply("side mesh pocket", "front", P_front, [(y, max(z, 106.0)) for y, z in [fyz(px, py, 2.0) for px, py in pts]], bezel=(1.5, 1.0), cuts=((0, 2.0),))
    # rear view: tail-light pockets
    TL = [(1621, 121), (1673, 119), (1684, 127), (1677, 142), (1623, 128)]
    for pts in (TL, mir(TL, 1720.0)):
        apply("tail-light pocket", "rear", P_rear, [ryz(px, py) for px, py in pts], bezel=(2.0, 1.5), cuts=((0, 1.6), (3.0, 2.8)))
    HP = [(178, 45), (208, 86), (263, 102), (242, 63)]
    for s_ in (1, -1):
        apply("hood panel", "top", P_top, [(Xt(tx), s_ * hw * T.HW) for tx, hw in HP], bezel=(2.0, 1.2), cuts=((0, 0.8),))
    apply("hood vent slot", "top", P_top, [(-12.0, -9.0), (-12.0, 9.0), (-38.0, 9.0), (-38.0, -9.0)], bezel=(1.5, 1.0), cuts=((0, 1.5), (2.5, 3.5)))
    # side view: door vent pocket, rear-fender vent pocket, door crease (two stepped groove layers)
    DV = [(310, 592), (325, 585), (392, 587), (375, 601)]
    apply("door vent pocket", "side", P_side, [(Xp(a), Zp(a, b)) for a, b in DV], bezel=(2.0, 1.2), cuts=((0, 2.0), (2.5, 3.5)))
    FV = [(566, 588), (576, 580), (598, 632), (584, 640)]
    apply("fender vent pocket", "side", P_side, [(Xp(a), Zp(a, b)) for a, b in FV], bezel=(2.0, 1.2), cuts=((0, 2.0), (2.0, 3.5)))
    for w_, d_ in ((4.0, 0.8), (1.6, 1.6)):
        a, b = (Xp(390.0), Zp(390.0, 655.0)), (Xp(545.0), Zp(545.0, 572.0))
        dd = np.array(b) - np.array(a); dd /= np.linalg.norm(dd); n_ = np.array([-dd[1], dd[0]]) * w_ / 2.0
        quad = [tuple(np.array(a) + n_), tuple(np.array(b) + n_), tuple(np.array(b) - n_), tuple(np.array(a) - n_)]
        body = body - (lay_in(d_) ^ P_side(quad))
    DETAILS.append(("door panel crease", "side", 4, "stepped V groove 4.0 x 0.8 mm + 1.6 x 1.6 mm"))
    # engine-bay opening rim
    e0, e1 = Xt(535.0), Xt(676.0)
    rim = [(e0, -26.0), (e1, -26.0), (e1, 26.0), (e0, 26.0)]
    body = body + (lay_out(2.0) ^ (P_top(_grow(rim, 5.0)) - P_top(_grow(rim, 0.5))))
    DETAILS.append(("engine-bay opening", "top", 4, "rim bezel 2.0 mm, through opening with 3 x 9 mesh"))
    return body
