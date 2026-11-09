"""Rev 7 faceted skin (WS03_SKIN=facet): a low-poly polyhedron lofted from per-station convex section polygons (flat panels, hard creases),
with faceted features (windscreen and side-window recesses with bezels, angular hood scoops, grille nose with bull bar, roll bar, lamp pods,
engine bay, octagonal rear arch). Stations are traced from sheet 61 (same body as sheet 60) and scaled to the 450 mm wheelbase."""
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
    q = sorted(pts)
    return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))


_P = lambda pts, k="side": T.simplify(T.mm_polyline(pts, k))
YF = _P(T.PLAN, "plan")                                                      # plan half width (chisel nose, tapered hexagon, rear fender, tail)
ZR = _P(T.TOP)                                                               # roofline: hood, raked windscreen, roof, deck and tail
ZB = _P([(a, min(b, 10000)) for a, b in T.FLOOR])                            # floor: arch top, sill, rising rear fender rail
ZSH = _P(T.BELT)                                                             # shoulder shelf (belt line); hood top where there is no cabin
YR = _P(T.ROOFW, "plan")                                                     # roof / ridge half width
ZR = T.simplify([(28.0, 78.0), (-65.0, 97.0)] + [p for p in ZR if p[0] <= -140.0])             # cowl break forced to >= 15 deg (sheet has 10 deg)
ZSH = T.simplify([(28.0, 78.0), (-81.0, 100.0)] + [p for p in ZSH if p[0] <= -320.0])
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


_xs = sorted({a for pts in (YF, ZR, ZB, ZSH, YR) for a, _ in pts}, reverse=True)
XSTA = [_xs[0]]
for _x in _xs[1:]:
    if XSTA[-1] - _x >= 2.5:
        XSTA.append(_x)
ST = [_station(float(x)) for x in XSTA]
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


def _polys(s, inset, belly=False, k=1.0):
    x, zb, yf, zw, ysh, zsh, yc, yr, zr = s
    if inset > 0 and k > 1.0:
        zr = zr - inset * (k - 1.0)                                  # roof drop so the wall stays `inset` thick normal to a raked facet
    zbb = zb - 30.0 if belly else zb              # open belly for the cavity
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


def solid(inset=0.0, belly=False):
    """Outer solid (inset 0), cavity (inset 2.4, belly=True) or a grown/shrunk layer: union of convex hulls between consecutive stations."""
    out = None
    pol = []
    for i, s in enumerate(ST):
        x = s[0] - inset if i == 0 else (s[0] + inset if i == len(ST) - 1 else s[0])
        pol.append((x, _polys(s, inset, belly, _pitch(i))))
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
    xa, xb = Xp(305.0), Xp(553.0)
    za, zb_ = _pl(ZB, xa), _pl(ZB, xb)
    sill = [(xa, za), (xb, zb_), (xb, zb_ + 11.0), (xa, za + 11.0)]
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
        pts = [(x, y, tz(x) + dz) for x in (xl0 + 4.0, xl0 + 14.0) for y in ((28.0, 37.0) if s_ > 0 else (-37.0, -28.0)) for dz in (-2.0, 6.0)]
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
    body = body + strut(bar[0], (xn - 8.0, -22.0, zlo + 6.0), 5.0) + strut(bar[-1], (xn - 8.0, 22.0, zlo + 6.0), 5.0)
    return body


def rear_arch(body):
    """Rev 9: the rear arch is the traced rising rail underside itself (the loft floor), nothing more to cut."""
    return body
