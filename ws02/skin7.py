"""Rev 7 faceted skin (WS03_SKIN=facet): a low-poly polyhedron lofted from per-station convex section polygons (flat panels, hard creases),
with faceted features (windscreen and side-window recesses with bezels, angular hood scoops, grille nose with bull bar, roll bar, lamp pods,
engine bay, octagonal rear arch). Stations are traced from sheet 61 (same body as sheet 60) and scaled to the 450 mm wheelbase."""
import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import Polygon

import mono_build as MB

# Rev 8: every section is built from FIXED edge directions (vertical flank, shoulder bevel dy/dz -0.6, cabin flank dy/dz -0.12, horizontal floor/shelf/roof), only the
# offsets vary per station, so the lateral quads between stations are exactly planar trapezoids. Each parameter is a polyline whose breaks are >= 15 deg.
S1, SC = 0.6, 0.12
YF = [(49, 12), (6, 46), (-124, 83), (-300, 83), (-330, 92), (-384, 92), (-441, 64)]          # plan half width (tapered hexagon: chisel nose, flat cabin, flared rear fender, tail taper)
ZR = [(49, 52), (-100, 88), (-166, 133), (-300, 133), (-312, 116), (-441, 104)]                # roof: hood, raked windscreen, flat roof, step down to the deck
ZB = [(49, 38), (34, 27), (-3, -26), (-441, -26)]                                              # floor / nose underside
ZSH = [(49, 46), (-300, 62), (-312, 88), (-441, 90)]                                           # shoulder shelf


def _pl(pts, x):
    q = sorted(pts)
    return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))


YSH = [(49, 9), (-60, 62), (-300, 66), (-312, 40), (-384, 40), (-441, 13)]                    # shoulder edge (top of the bevel), independent of the plan so the bevel stays one plane
YR = [(49, 2), (-60, 41), (-300, 41), (-312, 27), (-384, 27), (-441, 5)]                        # roof half width


def _station(x):
    zb, yf, zr, zsh, ysh, yr = _pl(ZB, x), _pl(YF, x), _pl(ZR, x), _pl(ZSH, x), _pl(YSH, x), _pl(YR, x)
    zw = zsh - (yf - ysh) / S1                                       # bevel runs at the fixed slope from (yf, zw) to (ysh, zsh)
    yc = yr + SC * (zr - zsh)
    return (x, zb, yf, zw, ysh, zsh, yc, yr, zr)


XSTA = sorted({a for pts in (YF, ZR, ZB, ZSH, YSH, YR) for a, _ in pts}, reverse=True)
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
    zbb = zb - 30.0 if (belly and zb <= -26.0) else zb              # open belly for the cavity
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


def features(body, S0, solid_fn, pink):
    out15 = solid_fn(-2.5) - S0
    out30 = solid_fn(-3.0) - S0
    inl = S0 - solid_fn(1.0)
    pr = lambda poly: MB.prism_xy([(x + 0.213, y + 0.177) for x, y in poly], -60.0, 220.0)
    grow = lambda poly, d: list(Polygon(poly).buffer(d, join_style=2).exterior.coords)[:-1]
    body = body - pink()
    # 1. raked windscreen: trapezoid on the roof/hood facets, glazing 1.0 mm down, raised bezel
    W = [(-104.0, 38.0), (-163.0, 36.0), (-163.0, -36.0), (-104.0, -38.0)]
    body = body + (out15 ^ (pr(grow(W, 5.0)) - pr(W)))
    body = body - (inl ^ pr(grow(W, -0.4)))
    # 2. large angular side windows on the cabin flank
    SW = [(-186.0, 98.0), (-204.0, 124.0), (-292.0, 124.0), (-292.0, 104.0), (-262.0, 92.0), (-210.0, 90.0)]
    swp = lambda poly: MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], 12.2, 90.0) + MB.prism_xz([(x + 0.19, z + 0.23) for x, z in poly], -90.0, -12.2)
    body = body + (out15 ^ (swp(grow(SW, 4.5)) - swp(SW)))
    body = body - (inl ^ swp(grow(SW, -0.4)))
    # 3. twin angular hood scoops: raised wedges, open mouths forward, mirrored
    for s_ in (1, -1):
        foot = [(-30.0, 7.0), (-84.0, 9.0), (-90.0, 28.0), (-62.0, 24.0), (-30.0, 17.0)]
        pts = [(x, s_ * y, surf(x, y) - 2.0) for x, y in foot] + [(x, s_ * y, surf(x, y) + (7.0 if x > -50.0 else 0.8)) for x, y in foot]
        wedge = Manifold.hull_points(np.array(pts, float))
        ci = [(-33.0, 10.0), (-80.0, 11.0), (-85.0, 25.0), (-62.0, 21.0), (-33.0, 15.0)]
        cp = [(x, s_ * y, surf(x, y) - 3.0) for x, y in ci] + [(x, s_ * y, surf(x, y) + (4.0 if x > -50.0 else -0.2)) for x, y in ci]
        cav = Manifold.hull_points(np.array(cp, float))
        mouth = Manifold.cube((12.0, 8.0, 5.5), center=False).translate((-42.0, 9.0 if s_ > 0 else -17.0, surf(-34.0, 12.0) + 0.2))
        hole = MB.prism_xy([(-36.0, s_ * 11.0), (-70.0, s_ * 12.0), (-70.0, s_ * 20.0), (-36.0, s_ * 16.0)], 40.0, 220.0) ^ (solid_fn(-1.0) - solid_fn(5.0))
        body = body + wedge - cav - mouth - hole
    # 4. slim vents behind the windows, shoulder louvres
    for s_ in (1, -1):
        for k in range(3):
            xv = -300.0 - 6.0 * k
            body = body - MB.prism_xy([(xv, s_ * 20.0), (xv - 2.4, s_ * 20.0), (xv - 2.4, s_ * 40.0), (xv, s_ * 40.0)], 60.0, 220.0)
        for k in range(4):
            body = body - Manifold.cube((30.0, 40.0, 2.4), center=False).translate((-200.0, 40.0 if s_ > 0 else -80.0, 40.0 + 6.0 * k))
    # 5. stepped sill panel with rivets, door ridge
    body = body + (MB.prism_xz([(-128.0, -21.0), (-300.0, -21.0), (-300.0, -6.0), (-128.0, -6.0)], 30.0, 130.0) ^ out30) + (MB.prism_xz([(-128.0, -21.0), (-300.0, -21.0), (-300.0, -6.0), (-128.0, -6.0)], -130.0, -30.0) ^ out30)
    for s_ in (1, -1):
        for x in range(-160, -290, -14):
            body = body + Manifold.sphere(1.6, 8).translate((float(x), s_ * (hw(float(x)) + 2.8), -13.5))
    # 6. roll bar and roof ridge
    for s_ in (1, -1):
        top = (-240.0, s_ * 22.0, 133.0 + 15.0)
        body = body + strut((top[0], top[1], 132.0), top, 4.0) + strut(top, (-296.0, s_ * 22.0, 132.0), 4.0)
    body = body + strut((-240.0, -22.0, 148.0), (-240.0, 22.0, 148.0), 4.0)
    # 7. roof lamp pods (windscreen corners)
    for s_ in (1, -1):
        pts = [(x, y, 133.0 + dz) for x in (-182.0, -172.0) for y in ((24.0, 34.0) if s_ > 0 else (-34.0, -24.0)) for dz in (-2.0, 6.0)]
        body = body + Manifold.hull_points(np.array(pts, float))
    # 8. open engine bay with mesh grille
    body = body - MB.prism_xy([(-308.0, -26.0), (-356.0, -26.0), (-356.0, 26.0), (-308.0, 26.0)], 60.0, 220.0)
    for i in range(3):
        for j in range(9):
            body = body - MB.prism_xy([(-356.0 - 5.0 * i, -22.0 + 5.0 * j), (-359.4 - 5.0 * i, -22.0 + 5.0 * j), (-359.4 - 5.0 * i, -18.6 + 5.0 * j), (-356.0 - 5.0 * i, -18.6 + 5.0 * j)], 60.0, 220.0)
    # 9. tail lamp bar
    body = body + (MB.prism_xz([(-452.0, 88.0), (-420.0, 88.0), (-420.0, 95.0), (-452.0, 95.0)], -36.0, 36.0) ^ out30)
    # 10. mesh grille nose: a grid of square holes through the nose facets, and a hexagonal bull bar in front
    for j in range(-3, 4):
        for k in range(3):
            body = body - Manifold.cube((14.0, 3.4, 3.4), center=False).translate((36.0, 6.0 * j - 1.7, 33.0 + 6.0 * k))
    bar = [(47.0, -24.0, 24.0), (60.0, -16.0, 24.0), (60.0, 16.0, 24.0), (47.0, 24.0, 24.0)]
    for a, b in zip(bar, bar[1:]):
        body = body + strut(a, b, 4.0)
    body = body + strut((47.0, -24.0, 24.0), (36.0, -24.0, 30.0), 4.0) + strut((47.0, 24.0, 24.0), (36.0, 24.0, 30.0), 4.0)
    body = body + strut((60.3, -16.2, 24.0), (60.3, -16.2, 36.0), 3.6) + strut((60.3, 16.2, 24.0), (60.3, 16.2, 36.0), 3.6) + strut((60.1, -17.0, 36.3), (60.1, 17.0, 36.3), 4.4)
    return body


def rear_arch(body):
    """Polygonal rear arch: an octagon round the rear wheel and a straight underside wedge under the tail, cut through the full width."""
    from w3_stretch import back, RAXLE_Z
    oct_ = octagon(back(-360.0), RAXLE_Z, 66.0)
    body = body - MB.prism_xz(oct_, -120.0, 120.0)
    wedge = [(-296.0, -60.0), (-299.0, 50.0), (-341.5, 66.4), (-440.0, 88.0), (-460.0, 88.0), (-460.0, -60.0)]
    return body - MB.prism_xz(wedge, -120.0, 120.0)
