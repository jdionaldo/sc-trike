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
if T.ALONE and os.environ.get("WS03_MASK", "1") == "1":                           # rev 16: tumblehome - the greenhouse base meets the door's outer edge (sheet plan: ~17 mm gap), roof stays as traced
    SC = float(os.environ.get("WS03_TUMBLE", "0.5"))


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
    def gring(prism, poly, shrinks=(0.0,), w=1.2, d=0.7):                  # rev 17: drawn detail = slight groove (outline w wide, d deep), the skin keeps its 2.4 mm wall
        lay = S0 - solid_fn(d)
        out = None
        for sh in shrinks:
            try:
                p0 = grow(poly, -sh) if sh else poly
                ring = prism(grow(p0, w / 2.0)) - prism(grow(p0, -w / 2.0))
            except Exception:
                continue
            out = ring if out is None else out + ring
        return lay ^ out
    pr = lambda poly: MB.prism_xy([(x + 0.213, y + 0.177) for x, y in poly], -60.0, 220.0)
    grow = lambda poly, d: list(Polygon(poly).buffer(d, join_style=2).exterior.coords)[:-1]
    body = body - pink()
    # 1. raked windscreen: hexagonal glass on the windscreen facets (sheet: front edge at the cowl, widest at the A-pillar feet, narrowing to the header)
    xc, xw, xh = Xt(262.0), Xt(297.0), Xt(380.0)
    W = [(xc - 2.0, 24.0), (xw, 50.0), (xh + 2.0, 27.0), (xh + 2.0, -27.0), (xw, -50.0), (xc - 2.0, -24.0)]
    if _MASK:                                                              # rev 15: glass base reaches the hood panels' outer rear corners (ref: base 66 mm, front 37 mm, header 35 mm half width)
        W = [(xc - 2.0, 33.0), (xw, 60.0), (xh + 2.0, 29.0), (xh + 2.0, -29.0), (xw, -60.0), (xc - 2.0, -33.0)]
    if _MASK:
        body = body - gring(pr, W, (0.0, 3.5))
    else:
        body = body + (out15 ^ (pr(grow(W, 5.0)) - pr(W)))
        body = body - (inl ^ pr(grow(W, -0.4)))
    # 2. large angular side windows on the cabin flank (sheet side view: bottom on the belt, raked A-pillar edge, flat top, raked rear edge)
    sw = [(367, 547), (364, 520), (412, 486), (514, 484), (484, 534)]
    SW = []
    for k, (px, py) in enumerate(sw):
        x = Xp(px)
        z = Zp(px, py)
        SW.append((x, min(max(z, _pl(ZSH, x) + 5.0), _pl(ZR, x) - 9.0)))
    swp = lambda poly: MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], 12.2, 90.0) + MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], -90.0, -12.2)
    if _MASK:
        body = body - gring(swp, SW, (0.0, 3.5))
    else:
        body = body + (out15 ^ (swp(grow(SW, 4.5)) - swp(SW)))
        body = body - (inl ^ swp(grow(SW, -0.4)))
    if _MASK:                                                              # 3. twin hood scoops beside the hood ridge, under the traced roofline: one inclined top plane (15.5 deg), vertical front face, open mouth
        _hin = sorted([(Xt(178.0), 45.0 * T.HW), (Xt(242.0), 63.0 * T.HW)])                      # rev 15: the scoops sit on the traced hood panels (inner edge of the panel + offset)
        Y = lambda x, d: float(np.interp(x, [p[0] for p in _hin], [p[1] for p in _hin])) - 1.0 + 0.85 * d
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
        for k in range(0 if _MASK else 3):                                   # rev 15: replaced by the two rear-quarter intakes
            xv = Xp(575.0) - 8.0 * k
            body = body - MB.prism_xy([(xv, s_ * 46.0), (xv - 3.0, s_ * 46.0), (xv - 3.0, s_ * 66.0), (xv, s_ * 66.0)], 60.0, 220.0)
    # 5. stepped sill panel with rivets
    xa, xb = Xp(305.0) - (0.43 if T.ALONE else 0.0), Xp(553.0)
    za, zb_ = _pl(ZB, xa), _pl(ZB, xb)
    sill = [(xa, za), (xb, zb_), (xb, zb_ + 11.0), (xa, za + 11.0)]
    if _MASK:                                                              # recessed sill band (the plan mask is the outline: nothing may stand proud of it) with low rivet heads
        for y0, y1 in ((30.0, 130.0), (-130.0, -30.0)):                  # rev 17: the sill is a drawn line (groove) now, no recessed band, no rivet heads
            body = body - ((S0 - solid_fn(0.7)) ^ (MB.prism_xz(grow(sill, 0.6), y0, y1) - MB.prism_xz(grow(sill, -0.6), y0, y1)))
    else:
        body = body + (MB.prism_xz(sill, 30.0, 130.0) ^ out30) + (MB.prism_xz(sill, -130.0, -30.0) ^ out30)
        for s_ in (1, -1):
            for x in np.arange(xa - 10.0, xb + 10.0, -14.0):
                body = body + Manifold.sphere(1.6, 8).translate((float(x), s_ * (hw(float(x)) + 2.8), _pl(ZB, float(x)) + 7.0))
    # 6. roll bar behind the roof (rev 14: removed from the standalone skin; replaced by the mini spoiler, slots and grab rails in details13)
    if not _MASK:
        xr = Xp(552.0)
        zt = tz(xr) + 14.0
        for s_ in (1, -1):
            top = (xr, s_ * 22.0, zt)
            body = body + strut((xr + 10.0, top[1], tz(xr + 10.0) - 2.0), top, 4.0) + strut(top, (xr - 12.0, s_ * 22.0, tz(xr - 12.0) - 2.0), 4.0)
        body = body + strut((xr, -22.0, zt), (xr, 22.0, zt), 4.0)
    # 7. roof lamp pods (windscreen header corners)
    xl0 = Xp(385.0)
    for s_ in ((1, -1) if not _MASK else ()):                                  # rev 17: the roof lamp pods are merged into the roof (no separate blocks)
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
    if not _MASK:
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
        """Rev 17: every drawn detail is a slight groove (1.2 mm wide, 0.7 mm deep) along its outline, plus one inner line where there was an inner step; no raised bezels, no thickened pockets."""
        nonlocal body
        if name in os.environ.get("SKIPDET", "").split(","):
            return
        lay = lay_in(0.7)
        for sh in [0.0] + sorted({sh for sh, d in cuts if sh}):
            try:
                p0 = _grow(poly, -sh) if sh else poly
                ring = prism(_grow(p0, 0.6)) - prism(_grow(p0, -0.6))
            except Exception:
                continue
            body = body - (lay ^ ring)
        DETAILS.append((name, view, len(poly), "groove 1.2 x 0.7 mm" + (" + inner groove" if any(sh for sh, d in cuts) else "")))

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
    # rev 15: two rear-quarter intakes per side (sheet 62 markup). Light areas = shallow faceted panels, dark strips = the real openings (through the wall, louvred)
    xq = [float(x) for x in np.arange(-240.0, -358.01, -3.0)]
    _band = lambda sg: MB.prism_xy([(x, sg * (hw(x) + 3.0)) for x in xq] + [(x, sg * (hw(x) - 12.0)) for x in reversed(xq)], -60.0, 400.0)
    _above = MB.prism_xz([(x, _pl(ZB, x) + 7.0) for x in xq] + [(xq[-1], 320.0), (xq[0], 320.0)], -200.0, 200.0)       # keep above the floor line: the deep (floorless) skin extends below it
    QB = (_band(1) + _band(-1)) ^ _above                                   # flank strip only: the projection must not touch the deck, tail face or other surfaces
    P_quarter = lambda p: P_side(p) ^ QB
    SX = lambda pts: [(Xp(a + 0.7), Zp(a, b + 0.45)) for a, b in pts]
    # rev 15b: the two vents are low faceted triangular "tents" hugging the rear quarter, opening to the front, one above the other
    for s_ in (1, -1):
        # upper tent: on the shoulder beside the engine bay, apex swept back toward the tail corner
        xf, xa = -256.0, -331.0
        F = [(xf, 48.0), (xf, 62.0), (xa, 64.0), (xa, 61.0)]
        pts = [(x, s_ * y, surf(x, y) - 2.0) for x, y in F] + [(xf, s_ * 55.0, surf(xf, 55.0) + 5.0), (xa, s_ * 62.5, surf(xa, 62.5) + 0.5)]
        tent = Manifold.hull_points(np.array(pts, float))
        mouth = Manifold.hull_points(np.array([(x, s_ * y, surf(xf - 1.0, 55.0) + z) for x in (xf + 0.5, xf - 9.0) for y in (53.5, 56.5) for z in (0.4, 2.0)], float))
        body = body + tent - mouth
        # lower tent: a shallow recess in the flank with a low faceted tent standing in it (nothing leaves the outline)
        p1, p2, pa = SX([(577, 566)])[0], SX([(556, 610)])[0], SX([(700, 528)])[0]
        tri = [p1, p2, pa]
        body = body - (lay_in(1.4) ^ P_quarter(_grow(tri, 3.0))) if s_ == 1 else body - (lay_in(1.4) ^ P_quarter(_grow(tri, 3.0)))
        fm = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        yb = lambda x: s_ * (hw(x) - 1.7)
        yr = lambda x: s_ * (hw(x) - 0.25)
        lp = [(p1[0], yb(p1[0]), p1[1]), (p2[0], yb(p2[0]), p2[1]), (pa[0], yb(pa[0]), pa[1]), (fm[0], yr(fm[0]), fm[1]), (pa[0] + 0.0, yr(pa[0]), pa[1])]
        body = body + Manifold.hull_points(np.array(lp, float))
    DETAILS.append(("upper vent tent", "top", 4, "raised faceted triangular tent 5 mm high on the shoulder, 75 mm swept back, 3 x 1.6 mm mouth at the front"))
    DETAILS.append(("lower vent tent", "side", 3, "triangle recess 1.4 mm in the flank with a 1.15 mm tent inside it, opening forward"))
    thru = lambda poly: (lay_in(0.0) if False else (solid_fn(-1.0) - solid_fn(5.0))) ^ P_quarter(poly)        # through the 2.4 mm wall
    US = [(549, 499), (556, 498), (575, 518), (572, 526)]                   # dark orange: slot at the front notch
    body = body - thru(SX(US))
    DETAILS.append(("upper intake slot", "side", 4, "through the wall, 4.5 x 19 mm, at the notch of the wedge panel"))
    ls = lambda t: ((577 - 33 * t), (566 + 62 * t))                         # leading edge of the lower panel, t 0..1 (top to bottom)
    nsl = 5
    for k in range(nsl):
        t0, t1 = k / nsl + 0.012, (k + 1) / nsl - 0.012
        (xa0, ya0), (xa1, ya1) = ls(t0), ls(t1)
        sl = [(xa0, ya0), (xa0 + 9.0, ya0 - 3.0), (xa1 + 9.0, ya1 - 3.0), (xa1, ya1)]               # dark green strip, angled slats
        body = body - thru(SX(sl))
    DETAILS.append(("lower intake strip", "side", 4, "5 through slots with 1.6 mm bars along the leading edge, 6 mm wide"))
    for w_, d_ in ((4.0, 0.8), (1.6, 1.6)):
        a, b = (Xp(390.0), Zp(390.0, 655.0)), (Xp(545.0), Zp(545.0, 572.0))
        dd = np.array(b) - np.array(a); dd /= np.linalg.norm(dd); n_ = np.array([-dd[1], dd[0]]) * w_ / 2.0
        quad = [tuple(np.array(a) + n_), tuple(np.array(b) + n_), tuple(np.array(b) - n_), tuple(np.array(a) - n_)]
        body = body - (lay_in(d_) ^ P_side(quad))
    DETAILS.append(("door panel crease", "side", 4, "stepped V groove 4.0 x 0.8 mm + 1.6 x 1.6 mm"))
    # engine-bay opening rim
    e0, e1 = Xt(535.0), Xt(676.0)
    rim = [(e0, -26.0), (e1, -26.0), (e1, 26.0), (e0, 26.0)]
    body = body - (lay_in(0.7) ^ (P_top(_grow(rim, 4.0)) - P_top(_grow(rim, 2.8))))                    # rev 17: the rim is a groove line
    DETAILS.append(("engine-bay opening", "top", 4, "rim bezel 2.0 mm, through opening with 3 x 9 mesh"))
    return spoiler14(body, solid_fn, e0, e1)


def spoiler14(body, solid_fn, e0, e1):
    """Rev 14 (sheet 62): inset slots (deck cut away), mini spoiler floating over the engine-bay front, grab rails on the bay rim."""
    if os.environ.get("NOSPOIL") == "1":
        return body
    zr = tz(e0)
    DEPTH, T, HALF = 23.5, 4.0, 35.0                                                # plan depth (6 % of the car length), slab thickness, half span (~40 % of the width)
    xt = lambda y: e0 + (10.0 if abs(y) <= 10.0 else 10.0 - 0.5 * (abs(y) - 10.0) if abs(y) <= 22.0 else 4.0 - 1.2 * (abs(y) - 22.0))     # trailing edge: 5-facet chevron
    TAN = 0.39                                                                        # top plane falls rearward (21 deg), leading edge 16 mm above the roofline
    xref = e0 + 10.0 + DEPTH
    ztop = lambda x: zr + 16.0 - TAN * (xref - x)
    ys = [-HALF, -22.0, -10.0, 10.0, 22.0, HALF]
    trail = [(xt(y), y) for y in ys]
    plan = [(x, y) for x, y in trail] + [(x + DEPTH, y) for x, y in reversed(trail)]
    plan = [(x + 0.0, y) for x, y in plan]
    allow = solid_fn(-22.0) - solid_fn(1.2)                                          # outside the cavity: nothing may fill the hollow
    # inset slots first (the slab is added afterwards, so it is not cut)
    xlc = e0 + 10.0 + DEPTH
    slots = [[(xlc + 2.5, -22.0), (xlc + 8.5, -22.0), (xlc + 8.5, 22.0), (xlc + 2.5, 22.0)]]
    for s_ in (1, -1):
        slots.append([(e0 + 1.0, s_ * 23.0), (e0 + 6.0, s_ * 23.0), (e0 + 6.0, s_ * 31.0), (e0 + 1.0, s_ * 31.0)])
    for q in slots:
        body = body - MB.prism_xy(q, zr - 10.0, zr + 40.0)
    # slab: plan prism between two parallel planes sloping down to the rear
    lo, hi = (min(x for x, _ in plan) - 1.0, max(x for x, _ in plan) + 1.0)
    band = [(lo, ztop(lo)), (hi, ztop(hi)), (hi, ztop(hi) - T), (lo, ztop(lo) - T)]
    slab = MB.prism_xy(plan, 0.0, 400.0) ^ MB.prism_xz(band, -60.0, 60.0)
    # legs: the two ends of the slab (|y| > 30) stand on the deck, 5 mm long behind the leading edge
    legs = None
    for s_ in (1, -1):
        y0, y1 = (30.0, HALF) if s_ > 0 else (-HALF, -30.0)
        xl_ = xt(s_ * 32.0) + DEPTH
        q = [(xl_ - 5.0, y0), (xl_, y0), (xl_, y1), (xl_ - 5.0, y1)]
        blk = MB.prism_xy(q, 0.0, 400.0) ^ MB.prism_xz([(xl_ - 6.0, ztop(xl_ - 6.0) - T), (xl_ + 1.0, ztop(xl_ + 1.0) - T), (xl_ + 1.0, zr - 8.0), (xl_ - 6.0, zr - 8.0)], -60.0, 60.0)
        legs = blk if legs is None else legs + blk
    body = body + ((slab + legs) ^ allow)
    DETAILS.append(("mini spoiler", "top/side/rear", len(plan), f"5-facet chevron slab {T} mm thick, {DEPTH} mm deep, +16 mm over the roofline, supported at the ends"))
    DETAILS.append(("inset slots", "top/rear", 4, "deck cut away: 1 centre strip ahead + 2 flank strips at the bay corners"))
    # grab rails: slanted bars on the rim, from the spoiler trailing edge, sloping down/back, kinking down at the tail
    xs_ = [e0 - 3.0, e1 + 14.0, e1 - 4.0, e1 - 14.0]
    zt_ = [tz(e0 - 3.0) + 5.0, tz(e1 + 14.0) + 3.0, tz(e1 - 4.0) + 2.0, tz(e1 - 14.0) - 3.0]
    TH, SL = 6.4, 1.3
    rails = None
    for s_ in (1, -1):
        yb = (27.0 * s_, 31.6 * s_)
        yt = ((27.0 - SL) * s_, (31.6 - SL) * s_)
        for i in range(len(xs_) - 1):
            pts = [(xs_[j], yy, zt_[j] - TH) for j in (i, i + 1) for yy in yb] + [(xs_[j], yy, zt_[j]) for j in (i, i + 1) for yy in yt]
            h = Manifold.hull_points(np.array(pts, float))
            rails = h if rails is None else rails + h
    body = body + (rails ^ allow)
    DETAILS.append(("grab rails", "side/top/rear", 8, f"2 slanted beams {TH} mm tall x 4.6 mm, 4 stations, kink down at the tail, stand 2-5 mm proud"))
    return body
