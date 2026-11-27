"""Stealth-style body shell: a few convex blocks of large flat facets, built in printed coordinates (mm, y forward is negative).

Each block is the convex hull of a short landmark list. Its wall is exact: every inner plane is the outer plane moved WALL
inward (half-space intersection), so there are no offset plates, connector wedges or slivers, and the wall is the same on every
facet whatever its direction. Openings (windows, cabin, wheel arches) are prisms cut through afterwards.

Landmarks follow the earlier traced shell (hood ridge, cowl, belt, chine, rocker, roof), so the cage, chassis and tail housing
keep their clearances. Everything is mirrored about x = 0.
"""
import math
import numpy as np
import cadquery as cq
from scipy.spatial import ConvexHull, HalfspaceIntersection
from scipy.optimize import linprog

WALL = 3.0            # printed wall, mm
PILLAR = 9.0          # width of the frame left around a window, mm
CABIN_RIM = 7.0       # width of the deck left inside the belt line around the cabin opening, mm
COWL_TONGUE_X = 14.0  # half width of the hood tongue left over the front light contact (contact is 14 mm wide at y -215)
COWL_TONGUE_Y = -204.0  # rear edge of that tongue

# ---- landmarks, right half (x >= 0); the left half is the mirror image -------------------------------------------------
# Few points on purpose: every extra landmark off a plane adds a crease. Points marked "on plane" are computed, not typed.
RIDGE_NOSE = (0, -307, 112)          # hood centre line at the nose
RIDGE_COWL = (0, -214, 139)          # hood centre line at the cowl
SHOULDER_XY = (88, -228)             # outer hood corner, where the hood, cheek and flank meet (z on the rear hood plane)
RIDGE_MID_0 = (0, -265, 128)         # the hood kinks here, as on the original (nose droop); RIDGE_MID (below) is this point lifted for the hood merge
HOOD_MID = (63, -265, 121)           # outer hood edge at the kink
NOSE_BOT = (46, -272, 59)            # lower front corner of the nose box (37 deg rake, as the skid plate)
NOSE_BACK_Y = -253.0                 # the nose box ends here; behind it the belly is open over the front axle
NOSE_BACK_X = 60.0                   # half width of the nose box at its rear upper edge
BELT_FRONT = (90, -208, 134.0)         # belt line = canopy base, one straight edge per side
BELT_REAR = (50, 116, 171)       # tail apex, traced from the user's side-view lines (115, 171); the belt line rises straight to it from the cowl
CHINE = [(94, -195, 102), (90, -55, 92), (86, 50, 118)]     # widest line of the body
ROCKER = [(60, -55, 19), (66, 15, 29), (60, 85, 128), (50, 116, 171)]
ROOF_FRONT_YZ = (-92, 202)           # roof edge above the windscreen (x on the side-glass plane)
ROOF_PEAK = (51, 15, 225)            # roof edge at its highest point; the roof ends here, the rear is open (bare cage tubes)
B_FOOT = (61, 30, 161)               # foot of the B-pillar on the belt line
COWL_POST_YZ = (-210, 137)           # top of the short upright post at the cowl, where the windscreen starts
# Side glass outline (y, z). The lower edge follows the body belt line
# at the original opening's midpoint height.
SIDE_GLASS_FRONT_Y, SIDE_GLASS_REAR_Y = -191.7, 24.2
SIDE_GLASS_SILL_Z = 150.15
SIDE_GLASS_SILL_Y = (SIDE_GLASS_FRONT_Y + SIDE_GLASS_REAR_Y) / 2
BELT_SLOPE = (B_FOOT[2] - BELT_FRONT[2]) / (B_FOOT[1] - BELT_FRONT[1])
SIDE_GLASS = [
    (SIDE_GLASS_FRONT_Y, SIDE_GLASS_SILL_Z + BELT_SLOPE * (SIDE_GLASS_FRONT_Y - SIDE_GLASS_SILL_Y)),
    (-89.7, 193.2),
    (6.8, 212.9),
    (SIDE_GLASS_REAR_Y, SIDE_GLASS_SILL_Z + BELT_SLOPE * (SIDE_GLASS_REAR_Y - SIDE_GLASS_SILL_Y)),
]


def _x_on_plane(a, b, c, y, z):
    """x of the point (x, y, z) on the plane through a, b, c."""
    a, b, c = (np.array(p, float) for p in (a, b, c))
    n = np.cross(b - a, c - a)
    return float(a[0] - (n[1] * (y - a[1]) + n[2] * (z - a[2])) / n[0])


def _z_on_plane(a, b, c, x, y):
    a, b, c = (np.array(p, float) for p in (a, b, c))
    n = np.cross(b - a, c - a)
    return float(a[2] - (n[0] * (x - a[0]) + n[1] * (y - a[1])) / n[2])


# Hood: two planes per side, split at the kink. The nose corner sits on the front one, the shoulder on the rear one.
SHOULDER_LIFT = 8.0   # outer hood corner held this far above the rear hood plane: the hood crowns toward the windscreen foot (post z 137) and the drop
                      # to the shoulder shrinks from 11 to 3 mm. With the taller canopy tabs 9 mm is the limit (10 splits the canopy into 3 pieces).
SHOULDER = SHOULDER_XY + (_z_on_plane(RIDGE_MID_0, RIDGE_COWL, HOOD_MID, *SHOULDER_XY) + SHOULDER_LIFT,)
# Wedge at the front shoulder: the hood's outer edge ran 7 mm down to the belt line, leaving the canopy's pointed front foot below it (a V notch).
# This corner point holds the shoulder level out to the canopy front, so the body skin fills the notch.
WEDGE = (BELT_FRONT[0], BELT_FRONT[1], SHOULDER[2])
NOSE_TOP_0 = (42, -307, _z_on_plane(RIDGE_NOSE, RIDGE_MID_0, HOOD_MID, 42, -307))
# Hood merge (November 27): with the shoulder lifted the hull's front hood is two facets folded 1.6 deg along RIDGE_NOSE - SHOULDER, P1 (RIDGE_MID,
# RIDGE_NOSE, SHOULDER) and P11 (NOSE_TOP, RIDGE_NOSE, SHOULDER): two hood seams per side and a 0.7 mm ledge strip at (80.7, -240). The fold is convex,
# so one plane through the hinge lies above one of the two points; NOSE_TOP and RIDGE_MID are both lifted by the same smallest amount that puts them on
# one plane through RIDGE_NOSE and SHOULDER (about 0.47 mm). The shoulder itself is still set from the unlifted kink.
HOOD_MERGE = True
def _hood_merge_lift():
    rn, sh = np.array(RIDGE_NOSE, float), np.array(SHOULDER, float)
    def miss(d):     # RIDGE_MID_0 + d against the plane through RIDGE_NOSE, SHOULDER and NOSE_TOP_0 + d
        nt = (NOSE_TOP_0[0], NOSE_TOP_0[1], NOSE_TOP_0[2] + d)
        return _z_on_plane(tuple(rn), tuple(sh), nt, RIDGE_MID_0[0], RIDGE_MID_0[1]) - (RIDGE_MID_0[2] + d)
    lo, hi = 0.0, 2.0
    assert miss(lo) > 0 > miss(hi), 'hood merge: no lift between 0 and 2 mm'
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if miss(mid) > 0 else (lo, mid)
    return (lo + hi) / 2
HOOD_LIFT = _hood_merge_lift() if HOOD_MERGE else 0.0
RIDGE_MID = (RIDGE_MID_0[0], RIDGE_MID_0[1], RIDGE_MID_0[2] + HOOD_LIFT)
NOSE_TOP = (NOSE_TOP_0[0], NOSE_TOP_0[1], NOSE_TOP_0[2] + HOOD_LIFT)
# Canopy side glass: one plane per side through the belt front corner, the B-pillar foot and the roof peak. The roof front
# corner and the cowl post sit on it. Behind the B-pillar a second plane (roof peak, B-pillar foot, belt rear) is the closed rear quarter panel.
ROOF_FRONT = (_x_on_plane(BELT_FRONT, B_FOOT, ROOF_PEAK, *ROOF_FRONT_YZ),) + ROOF_FRONT_YZ
COWL_POST = (_x_on_plane(BELT_FRONT, B_FOOT, ROOF_PEAK, *COWL_POST_YZ),) + COWL_POST_YZ


def _both(points):
    out = []
    for x, y, z in points:
        out.append((float(x), float(y), float(z)))
        if abs(x) > 1e-9:
            out.append((-float(x), float(y), float(z)))
    return out


def _planes(points):
    """Unique outward planes (n, d with n.x + d <= 0 inside) of the convex hull of the points."""
    eq = ConvexHull(np.array(points)).equations
    keep = []
    for q in eq:
        if not any(np.allclose(q, k, atol=1e-6) for k in keep):
            keep.append(q)
    return np.array(keep)


def _solid(planes):
    """Convex solid bounded by the planes."""
    A, b = planes[:, :3], -planes[:, 3]
    fit = linprog([0, 0, 0, -1], A_ub=np.column_stack((A, np.ones(len(A)))), b_ub=b, bounds=[(None, None)] * 3 + [(0, None)], method='highs')
    assert fit.success and fit.x[3] > 1e-3, 'empty block'
    pts = HalfspaceIntersection(planes, fit.x[:3]).intersections
    from parts.util import hull
    return hull([tuple(p) for p in pts])


def _facets(planes):
    """Each plane's polygon (ordered corner points) on the solid bounded by the planes."""
    A, b = planes[:, :3], -planes[:, 3]
    fit = linprog([0, 0, 0, -1], A_ub=np.column_stack((A, np.ones(len(A)))), b_ub=b, bounds=[(None, None)] * 3 + [(0, None)], method='highs')
    pts = HalfspaceIntersection(planes, fit.x[:3]).intersections
    out = []
    for q in planes:
        on = np.array([p for p in pts if abs(q[:3] @ p + q[3]) < 1e-6])
        if len(on) < 3:
            out.append(None); continue
        c = on.mean(axis=0); n = q[:3]
        u = on[0] - c; u /= np.linalg.norm(u); v = np.cross(n, u)
        ang = np.arctan2((on - c) @ v, (on - c) @ u)
        poly = on[np.argsort(ang)]
        # drop repeated corners
        keep = [poly[0]]
        for p in poly[1:]:
            if np.linalg.norm(p - keep[-1]) > 1e-6: keep.append(p)
        if np.linalg.norm(keep[0] - keep[-1]) < 1e-6: keep.pop()
        out.append(np.array(keep))
    return out


CHAMFER = 0.5         # mm: uniform 45 degree break on every outside edge of the shell blocks and on the rim of every window cut through them
BEVEL_MIN_TURN = 50.0  # soft facet creases (turn below this) stay as they are
BEVEL_MIN_LEN = 3.0


def _bevel(planes, d=CHAMFER, only=None):
    """One extra half-space per outside edge of the convex block: the plane that cuts d mm off both faces at 45 degrees (exact chamfer,
    no kernel fillet). Edges shorter than BEVEL_MIN_LEN or turning less than BEVEL_MIN_TURN are skipped."""
    shared = {}
    for k, poly in enumerate(_facets(planes)):
        if poly is None: continue
        for a, b in zip(poly, np.roll(poly, -1, axis=0)):
            key = tuple(sorted((tuple(np.round(a, 3)), tuple(np.round(b, 3)))))
            shared.setdefault(key, []).append((k, a, b))
    rows = []
    for key, items in shared.items():
        if len(items) != 2: continue
        (k1, a, b), (k2, _, _) = items
        n1, n2 = planes[k1][:3], planes[k2][:3]
        phi = np.arccos(np.clip(n1 @ n2, -1, 1))
        if np.degrees(phi) < BEVEL_MIN_TURN or np.linalg.norm(a - b) < BEVEL_MIN_LEN: continue
        if only is not None and not any((np.linalg.norm(a - p) < 0.5 and np.linalg.norm(b - q) < 0.5) or (np.linalg.norm(a - q) < 0.5 and np.linalg.norm(b - p) < 0.5) for p, q in only): continue
        nc = (n1 + n2) / np.linalg.norm(n1 + n2)
        p = (a + b) / 2
        rows.append(np.append(nc, -(nc @ p) + d * np.sin(phi / 2)))
    return np.array(rows) if rows else np.zeros((0, 4))


def beveled_hull(points, d=CHAMFER):
    """Convex hull solid of the points with the CHAMFER bevel on its outside edges (for plates, webs and gussets of the printed arms)."""
    planes = _planes([tuple(map(float, q)) for q in points])
    return _solid(np.vstack([planes, _bevel(planes, d)]))


def block(points, wall=WALL, open_if=None, bevel=True, big_edges=None, big_d=0.0):
    """Hollow convex block. open_if(normal) -> True leaves that facet open (its inner plane is pushed outside).
    The outside edges carry a CHAMFER bevel; the returned planes are the unbevelled facets (windows are sized on them)."""
    outer = _planes(_both(points))
    inner = outer.copy()
    for q in inner:
        q[3] += -60.0 if (open_if is not None and open_if(q[:3])) else wall
    outer_b = np.vstack([outer, _bevel(outer)]) if bevel else outer
    if big_edges:
        outer_b = np.vstack([outer_b, _bevel(outer, big_d, only=big_edges)])
    body = _solid(outer_b).cut(_solid(inner))
    if open_if is not None:
        for tool in _rim_tools(outer, [bool(open_if(q[:3])) for q in outer], wall):
            body = body.cut(tool)
    return body, outer


RIM_LAND = 1.2        # mm: least width of the rim left where a wall ends in a point on an open facet
RIM_MIN_DOT = 0.05    # walls that meet an open facet within 3 degrees of square are left as they are


def _edge_map(outer):
    """Facet polygons of the block and, for every edge, the facets that share it."""
    polys = _facets(outer); shared = {}
    for k, poly in enumerate(polys):
        if poly is None: continue
        for a, b in zip(poly, np.roll(poly, -1, axis=0)):
            shared.setdefault(tuple(sorted((tuple(np.round(a, 3)), tuple(np.round(b, 3))))), []).append(k)
    return polys, shared


def _cell_rows(outer, polys, shared, is_open, k, wall):
    """Half-spaces of the wall cell of facet k (together with the block's outer planes): not deeper than the wall, and on this facet's side of the
    bisecting plane of every crease to a neighbouring wall. The cells of all facets tile the wall, with a mitre at each crease."""
    nk = outer[k][:3]; poly = polys[k]
    rows = [np.append(-nk, -outer[k][3] - wall - 0.01)]
    c = poly.mean(axis=0) - nk * wall / 2
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        js = [j for j in shared[tuple(sorted((tuple(np.round(a, 3)), tuple(np.round(b, 3)))))] if j != k]
        if not js or is_open[js[0]]: continue
        m = np.cross(b - a, nk + outer[js[0]][:3]); m /= np.linalg.norm(m)
        if m @ (c - a) > 0: m = -m
        rows.append(np.append(m, -(m @ a)))
    return rows


def _rim_tools(outer, is_open, wall):
    """Cutters that square off the wall where it ends on an open facet. The wall is the slab between a facet and its inner plane; the open facet slices
    it at the angle between the two planes, which leaves a knife edge on the inside (the usual case on a convex block: the inner face runs on past the
    outside edge by wall / tan(angle)). Each cutter is the part of that wall's cell beyond the plane that stands square on the facet through its outside
    edge, so the rim ends square, the outside edge stays where it is and no wall tapers to nothing. Where the point is on the outside instead (the wall
    leans the other way and is sharper than 60 degrees), the tip is cut back until the rim is RIM_LAND wide."""
    polys, shared = _edge_map(outer)
    tools = []
    for key, ks in shared.items():
        if len(ks) != 2 or is_open[ks[0]] == is_open[ks[1]]: continue
        o, k = ks if is_open[ks[0]] else ks[::-1]
        no, nk = outer[o][:3], outer[k][:3]
        p0 = np.array(key[0])
        dot = float(no @ nk)
        e = no - dot * nk; e /= np.linalg.norm(e)             # in the wall facet, square to the edge, pointing out through the open facet
        if dot > RIM_MIN_DOT: back = 0.0
        elif dot < -0.5: back = RIM_LAND * (-dot) / math.sqrt(1.0 - dot * dot)
        else: continue
        rows = _cell_rows(outer, polys, shared, is_open, k, wall) + [np.append(-e, e @ p0 - back)]
        try:
            tools.append(_solid(np.vstack([outer] + rows)))
        except Exception:
            continue                                          # nothing of the wall lies beyond the plane
    return tools


def _fuselage_points():
    return [RIDGE_NOSE, RIDGE_MID, HOOD_MID, RIDGE_COWL, SHOULDER, NOSE_TOP, BELT_FRONT, WEDGE, B_FOOT, BELT_REAR] + CHINE + ROCKER


def _fuselage_open(n):
    # open: the underside and the rear belly ramp (chassis below) and the tail face (cage tubes run out the back); the raked
    # nose face also points down, but it is a wall
    return (n[2] < -0.55 and n[1] > -0.5) or n[1] > 0.9


def _nose_open(n):
    return n[2] < -0.9 or n[1] > 0.9


def square_cuts(shell, tools, wall=WALL, chamfer=0.0, min_volume=0.02):
    """Square off what convex cutters (`tools`, already cut from the shell or not) leave in the skin. A cutter that crosses a wall at an angle, or only
    grazes it, leaves a feather edge or a thin skin: the wall tapers to nothing over wall / tan(angle). For every wall facet the part of each cutter
    inside that facet's wall cell is projected onto the facet, and the prism over that footprint is cut right through the wall: the opening is as large
    as the cutter needs on either face and its rim stands square on the skin. With `chamfer` the outside edge of each such opening gets a 45 degree
    break of that size (an exact facet, no steps). Returns the shell and a list of (tool index, block, facet, footprint mm2)."""
    from parts.util import hull
    done = []
    for bi, (pts, opn) in enumerate(((_fuselage_points(), _fuselage_open), (_nose_points(), _nose_open))):
        outer = _planes(_both(pts)); is_open = [bool(opn(q[:3])) for q in outer]
        polys, shared = _edge_map(outer)
        for k in range(len(outer)):
            if is_open[k] or polys[k] is None: continue
            rows = _cell_rows(outer, polys, shared, is_open, k, wall)
            try: cell = _solid(np.vstack([outer] + rows))
            except Exception: continue
            cb = cell.BoundingBox()
            nk = outer[k][:3]; o = polys[k][0]
            u = polys[k][1] - o; u /= np.linalg.norm(u); v = np.cross(nk, u)
            for ti, tool in enumerate(tools):
                tb = tool.BoundingBox()
                if (tb.xmin > cb.xmax or tb.xmax < cb.xmin or tb.ymin > cb.ymax or tb.ymax < cb.ymin or tb.zmin > cb.zmax or tb.zmax < cb.zmin): continue
                piece = tool.intersect(cell)
                if not piece.Solids() or piece.Volume() < min_volume: continue
                P = np.array([[(np.array(q.toTuple()) - o) @ u, (np.array(q.toTuple()) - o) @ v] for q in piece.Vertices()])
                try: ring = P[ConvexHull(P).vertices]
                except Exception: continue
                c2 = ring.mean(axis=0); side = []
                for a, b in zip(ring, np.roll(ring, -1, axis=0)):
                    e = b - a; m = np.array([e[1], -e[0]]) / np.linalg.norm(e)
                    if m @ (c2 - a) > 0: m = -m
                    m3 = m[0] * u + m[1] * v; a3 = o + a[0] * u + a[1] * v
                    side.append(np.append(m3, -(m3 @ a3)))
                try: prism = _solid(np.vstack([outer] + rows + side))
                except Exception: continue
                shell = shell.cut(prism)
                if chamfer:
                    big = _grow([tuple(q) for q in ring], chamfer)
                    on = lambda q, h: tuple(o + q[0] * u + q[1] * v + nk * h)
                    cone = hull([on(q, 0.2) for q in big] + [on(q, 0.0) for q in big] + [on(q, -chamfer) for q in ring])
                    shell = shell.cut(cone.intersect(cell))
                done.append((ti, bi, k, round(float(ConvexHull(P).volume), 1)))
    return shell.clean(), done


def window(planes, pick, inset=PILLAR, depth=WALL * 3, sill=None, span=None, top=None, flare=CHAMFER, loose=None, loose_inset=0.0):
    """Cutter for a window: the facet chosen by pick(normal, centre) shrunk by `inset`, pushed through the wall.
    A cutter that reaches past the outer face (span[1] > 0) opens out by `flare` at the face: a 45 degree chamfer round the opening."""
    cutters = []
    for q, poly in zip(planes, _facets(planes)):
        if poly is None or not pick(q[:3], poly.mean(axis=0)):
            continue
        n = q[:3]; c = poly.mean(axis=0)
        u = poly[1] - poly[0]; u /= np.linalg.norm(u); v = np.cross(n, u)
        P2 = np.array([[(p - c) @ u, (p - c) @ v] for p in poly])
        mids = [(poly[k][2] + poly[(k + 1) % len(poly)][2]) / 2 for k in range(len(poly))]
        low = int(np.argmin(mids))                   # the edge on the belt line gets the taller sill
        high = int(np.argmax(mids))                  # the top edge can get its own inset (nose light band)
        ins = [(sill if (sill is not None and k == low) else top if (top is not None and k == high) else inset) for k in range(len(poly))]
        if loose is not None:                        # edges where the opening runs on to the next facet (inset reduced to loose_inset)
            for k in range(len(poly)):
                if loose(poly[k], poly[(k + 1) % len(poly)]): ins[k] = loose_inset

        def ring_for(shrink):
            hs = []
            for k, (a, bb) in enumerate(zip(P2, np.roll(P2, -1, axis=0))):
                e = bb - a; m = np.array([e[1], -e[0]]); m /= np.linalg.norm(m)
                if m @ (-a) > 0: m = -m              # outward normal
                hs.append([m[0], m[1], -(m @ a) + ins[k] - shrink])
            hs = np.array(hs)
            fit = linprog([0, 0, -1], A_ub=np.column_stack((hs[:, :2], np.ones(len(hs)))), b_ub=-hs[:, 2], bounds=[(None, None)] * 2 + [(0, None)], method='highs')
            if not fit.success or fit.x[2] < 2.0: return None
            Q2 = HalfspaceIntersection(hs, fit.x[:2]).intersections
            Q2 = Q2[np.argsort(np.arctan2(Q2[:, 1] - Q2[:, 1].mean(), Q2[:, 0] - Q2[:, 0].mean()))]
            return [c + a * u + bq * v for a, bq in Q2]
        ring = ring_for(0.0)
        if ring is None:
            continue                                 # facet too small for a window
        from parts.util import hull
        lo, hi = span if span is not None else (-depth, depth)      # along the outward normal, 0 = the outer face
        big = ring_for(flare) if (flare and hi > 0) else None
        if big is None:
            cutters.append(hull([tuple(p + n * hi) for p in ring] + [tuple(p + n * lo) for p in ring]))
        else:
            cutters.append(hull([tuple(p + n * lo) for p in ring] + [tuple(p - n * flare) for p in ring] + [tuple(p) for p in big] + [tuple(p + n * hi) for p in big]))
    return cutters


def cabin_ring():
    """Cabin opening outline (+x half, front to rear): the belt line moved CABIN_RIM inboard. The front edge sits under the windscreen base,
    ahead of the cage hoop, one straight edge across the whole width; behind the B-pillar foot the edge stays parallel to the belt up to the
    tail apex (so the rim keeps CABIN_RIM there, it used to taper to 3.5 mm), then runs straight out through the open tail face."""
    return [(BELT_FRONT[0] - CABIN_RIM, COWL_TONGUE_Y), (B_FOOT[0] - CABIN_RIM, B_FOOT[1]),
            (BELT_REAR[0] - CABIN_RIM, BELT_REAR[1]), (BELT_REAR[0] - CABIN_RIM, BELT_REAR[1] + 40)]


def cabin_cut(grow=0.0, convex=False):
    """The cabin opening as a prism cut upwards through the body deck; grow > 0 for the rim chamfer (chamfer_rims). `convex`: the last edge (straight out
    through the tail face, behind the body) runs on in line with the one before, which makes the outline convex (for square_cuts); inside the body it is
    the same opening."""
    ring = cabin_ring()
    if convex:
        (x0, y0), (x1, y1), (_, y2) = ring[1], ring[2], ring[3]
        ring = ring[:3] + [(x1 + (x1 - x0) * (y2 - y1) / (y1 - y0), y2)]
    poly = ring + [(-x, y) for x, y in reversed(ring)]
    if grow: poly = _grow(poly, grow)
    return cq.Workplane('XY').workplane(offset=100).polyline(poly).close().extrude(80).val()


def fuselage():
    body, planes = block(_fuselage_points(), open_if=_fuselage_open)
    # cabin opening: the belt outline shrunk by CABIN_RIM, from the cowl back, cut upwards through the deck
    nb, nplanes = nose_box(with_planes=True)
    out = body.cut(cabin_cut()).fuse(nb)
    # the pocket between each nose cheek and the hood side wall (open underneath, seen from the front as a slot under the hood edge) is filled solid
    nose_hull = _solid(_planes(_both(_nose_points())))
    channel = outer_solid().intersect(cq.Solid.makeBox(60.0, 14.0, 34.0, cq.Vector(30.0, NOSE_BACK_Y - 13.0, 98.5)).fuse(
        cq.Solid.makeBox(60.0, 14.0, 34.0, cq.Vector(-90.0, NOSE_BACK_Y - 13.0, 98.5)))).cut(nose_hull)
    # the boxes run 1 mm past the open back of the nose box (so the filler bites into the hood wall): behind the hollow of the nose box that millimetre
    # was a free-standing 1 mm fin (26 x 17 mm each side); the nose outline moved back by that millimetre takes it off
    channel = channel.cut(nose_hull.translate(cq.Vector(0.0, 1.0, 0.0)))
    # the filler stays closed behind the end of the light strip: only the strip's own length (to y -258.5) is grooved
    keep = cq.Solid.makeBox(200.0, 60.0, 80.0, cq.Vector(-100.0, -318.5, 80.0))
    for cutter in _strip_slot(nplanes, 0.0, (-GROOVE_D, WALL * 3)):
        channel = channel.cut(cutter.intersect(keep))
    # the filler stops at the hood's underside plane (through the underside facet of the hull cheek), so its flat bottom does not hang below it as a step
    _p0 = np.array([-72.9, -237.3, 102.9]); _nu = np.array([-0.58, -0.31, -0.75]); _nu = _nu / np.linalg.norm(_nu)
    _above = None
    for _sx in (-1, 1):
        _n = _nu * np.array([-_sx, 1.0, 1.0]); _o = _p0 * np.array([-_sx, 1.0, 1.0])     # the +x side is the mirror image
        _half = cq.Workplane(cq.Plane(origin=tuple(_o), normal=tuple(-_n))).rect(800, 800).extrude(120).val()
        _half = _half.intersect(cq.Solid.makeBox(200.0, 400.0, 400.0, cq.Vector(0 if _sx > 0 else -200.0, -400.0, 0.0)))
        _above = _half if _above is None else _above.fuse(_half)
    channel = channel.intersect(_above)
    # straighten the lower edge of the hood underside across the step where the nose box starts (y -253): the filler's lower corner sticks out
    # past the straight line from the cheek-edge start to its front end; slice it off along a 45 deg plane through that line
    _A1 = np.array([-69.2, -238.7, 100.6]); _E = np.array([-49.7, -280.7, 102.6])
    _u = (_E - _A1) / np.linalg.norm(_E - _A1)
    _w = np.cross(_nu, _u); _w = _w / np.linalg.norm(_w)
    if _w[0] < 0: _w = -_w                                   # in the underside plane, pointing inboard (+x on the -x side)
    _dT = _w * math.cos(math.radians(45.0)) + (-_nu) * math.sin(math.radians(45.0))
    _nT = np.cross(_u, _dT); _nT = _nT / np.linalg.norm(_nT)
    if _nT @ _w < 0: _nT = -_nT
    _cut = cq.Workplane(cq.Plane(origin=tuple(_A1), normal=tuple(_nT))).rect(600, 600).extrude(60).val()
    _cut = _cut.intersect(cq.Solid.makeBox(200.0, 40.0, 60.0, cq.Vector(-100.0, -272.0, 80.0)))
    _both_cut = _cut.fuse(_cut.mirror('YZ'))
    channel = channel.cut(_both_cut)
    fill = channel
    for cutter in _strip_slot(nplanes, 0.0, (-GROOVE_D, WALL * 3)):
        out = out.cut(cutter)                      # the strip groove runs on under the hood body round the nose cheeks
    out = out.fuse(fill)
    # ...but past the end of the strip (y -258.5) that groove holds nothing: refill it up to the outer skin, no pocket left under the strip end
    beyond = cq.Solid.makeBox(200.0, 80.0, 80.0, cq.Vector(-100.0, -258.5, 80.0))
    env = outer_solid()
    for cutter in _strip_slot(nplanes, 0.0, (-GROOVE_D, WALL * 3)):
        try: plug = cutter.intersect(beyond).intersect(env)
        except Exception: continue          # this cutter does not reach past the strip end
        if plug.Solids() and plug.Volume() > 1e-3: out = out.fuse(plug)
    # the strip groove also goes through the hull's flank skin where it laps over the nose cheek; the strip of that skin left below the groove was a thin
    # tongue (0.2 to 1 mm thick, about 3 x 4 mm) standing off the cheek in front of the hood filler: whatever stands off the cheek below the groove goes
    ahead = cq.Solid.makeBox(200.0, 60.0, 80.0, cq.Vector(-100.0, NOSE_BACK_Y - 13.0 - 60.0, 80.0))
    for low in window(nplanes, _is_cheek, inset=-20.0, top=STRIP_EDGE + STRIP_H - 0.5, span=(0.01, WALL * 3), flare=0.0):
        out = out.cut(low.intersect(ahead))
    return out.clean(), planes


def _nose_points():
    # the hood face the hull really has over the nose cheek is the plane RIDGE_NOSE / RIDGE_MID / SHOULDER (the old plane through RIDGE_COWL stood 2.2 mm
    # proud of it and left a wedge-shaped step and a slit on the hood)
    top_back = (NOSE_BACK_X, NOSE_BACK_Y, _z_on_plane(RIDGE_NOSE, RIDGE_MID, SHOULDER, NOSE_BACK_X, NOSE_BACK_Y))
    ridge_back = (0, NOSE_BACK_Y, RIDGE_MID[2] + (RIDGE_COWL[2] - RIDGE_MID[2]) * (NOSE_BACK_Y - RIDGE_MID[1]) / (RIDGE_COWL[1] - RIDGE_MID[1]))
    return [NOSE_TOP, RIDGE_NOSE, RIDGE_MID, NOSE_BOT, (NOSE_BOT[0], NOSE_BACK_Y, NOSE_BOT[2]), top_back, ridge_back]


def nose_box(with_planes=False):
    """The bluff nose under the hood front: raked face with the grille opening, upright cheeks, open below and behind.
    Its top corners lie on the hood planes, so it joins the hood without a step."""
    pts = _nose_points()
    box, planes = block(pts, open_if=_nose_open)
    for cutter in window(planes, _is_nose_face, inset=PILLAR, top=GRILLE_TOP) + _strip_slot(planes, 0.0, (-GROOVE_D, WALL * 3)):
        box = box.cut(cutter)                                        # grille opening and the blind groove for the light strip above it
    for _peg, hole in _peg_parts(planes):
        box = box.cut(hole)                                          # round holes through the groove floor for the LED pegs
    if with_planes:
        return box, planes
    return box


def _is_nose_face(n, c):
    return n[1] < -0.5 and n[2] < 0


STRIP_EDGE = 4.0      # solid left around the nose light strip slot, mm
STRIP_H = 10.0        # height of the light strip slot, measured down the nose face, mm
GRILLE_TOP = STRIP_EDGE + STRIP_H + STRIP_EDGE      # top of the grille opening: a 4 mm bar stays between strip and grille
STRIP_FIT = 0.25      # clearance of the light strip in its slot, mm


def _is_cheek(n, c):
    return abs(n[0]) > 0.9 and n[1] < -0.2 and n[2] < 0           # the upright nose cheeks (normal about +-0.95, -0.28, -0.12)


def _shared_edge(a, b):
    """True for an edge that joins the nose face to a cheek: it runs from the top front corner (|x| 42, y -307) down to the lower corner (|x| 46, y -272)."""
    ends = sorted([(abs(a[0]), a[1]), (abs(b[0]), b[1])], key=lambda t: t[1])
    return abs(ends[0][1] + 307) < 2.0 and abs(ends[1][1] + 272) < 2.0 and abs(a[0] - b[0]) < 6.0


def _band(planes, pick, fit, span):
    kw = dict(inset=STRIP_EDGE + fit, loose=_shared_edge, loose_inset=fit)
    full = window(planes, pick, span=span, **kw)
    below = window(planes, pick, top=STRIP_EDGE + STRIP_H - fit, span=(span[0] - 1.0, span[1] + 1.0), **kw)
    # the flare of that cutter gave the lower wall of the groove and the lower edge of the strip a 10 degree lean (0.5 mm over the depth), so the strip's
    # lower edge was sharper than square. Its top edge is held to the square plane through the nominal line; the other edges keep the flare of `full`
    square = window(planes, pick, inset=-20.0, top=STRIP_EDGE + STRIP_H - fit, span=(span[0] - 1.5, span[1] + 1.5), flare=0.0)
    return full[0].cut(below[0].intersect(square[0])).clean()


def _strip_slot(planes, fit, span):
    """The band across the top of the nose face and round both cheeks: each facet shrunk by STRIP_EDGE, minus the same shape with its top
    edge moved down by STRIP_H; the edges between face and cheeks are left open so the band runs on round the corner. `fit` shrinks it all round (0 for
    the groove in the shell). Returns [face band, right cheek band, left cheek band]."""
    return [_band(planes, _is_nose_face, fit, span),
            _band(planes, lambda n, c: _is_cheek(n, c) and n[0] > 0, fit, span),
            _band(planes, lambda n, c: _is_cheek(n, c) and n[0] < 0, fit, span)]


GROOVE_D = 1.8        # depth of the blind groove for the light strip; the shell keeps WALL - GROOVE_D = 1.2 mm behind it as the backing
PEG_X = (-22.0, 22.0)  # LED peg stations along the strip (x), as on the BOM
PEG_D = 5.0           # peg outside diameter
PEG_HOLE_D = PEG_D + 0.3   # hole through the backing wall
PEG_BORE = 3.2        # 3 mm LED bore, blind: 0.8 mm of strip stays closed in front
PEG_OUT = 4.0         # how far the peg sticks out behind the shell wall


def _strip_plates(planes):
    return _strip_slot(planes, STRIP_FIT, (-GROOVE_D + 0.05, 0.0))


def _strip_plate(planes):
    return _strip_plates(planes)[0]


def _peg_parts(planes):
    """(peg, hole cutter) for each LED station: the peg is a tube standing on the back of the strip plate, through a round hole in
    the 1.2 mm backing wall of the groove, ending PEG_OUT behind the wall."""
    plate = _strip_plate(planes)
    n = next(np.array(q[:3]) for q, poly in zip(planes, _facets(planes)) if poly is not None and _is_nose_face(q[:3], poly.mean(axis=0)))
    n = n / np.linalg.norm(n)
    out = []
    mid = (GROOVE_D - 0.05) / 2
    for x in PEG_X:
        sl = plate.intersect(cq.Solid.makeBox(1.0, 60.0, 60.0, cq.Vector(x - 0.5, plate.Center().y - 30.0, plate.Center().z - 30.0)))
        c = sl.Center()
        base = np.array([c.x, c.y, c.z])
        d = cq.Vector(*(-n))
        length = mid + (WALL - GROOVE_D) + PEG_OUT
        peg = cq.Solid.makeCylinder(PEG_D / 2, length, cq.Vector(*base), d)
        hole = cq.Solid.makeCylinder(PEG_HOLE_D / 2, length + 2.0, cq.Vector(*(base - n * (GROOVE_D - mid - 0.1))), d)
        bore = cq.Solid.makeCylinder(PEG_BORE / 2, length + (mid - 0.8) + 0.01, cq.Vector(*(base - n * length)), cq.Vector(*n))   # blind: 0.8 mm closed at the face
        out.append((peg.cut(bore), hole))
    return out


def nose_strip():
    """Light strip for the blind groove across the top of the nose face: a translucent plate flush with the face (1.75 mm),
    resting on the 1.2 mm backing wall of the shell, with two round pegs for the 3 mm LEDs that go through holes in the wall."""
    from parts.util import hull as _hull
    box, planes = nose_box(with_planes=True)
    face, right, left = _strip_plates(planes)
    strip = face.fuse(right).fuse(left)
    # bridge the 0.5 mm seam at each corner so the bar is one piece: hull of both plates' vertices next to the shared edge, trimmed to the shell
    for cheek, sx in ((right, 1), (left, -1)):
        e0, e1 = np.array([sx * 42.0, -307.0, 107.0]), np.array([sx * 46.0, -272.0, 59.0])
        def near(sol):
            out = []
            for v in sol.Vertices():
                p = np.array([v.X, v.Y, v.Z]); t = np.clip((p - e0) @ (e1 - e0) / ((e1 - e0) @ (e1 - e0)), 0, 1)
                if np.linalg.norm(p - (e0 + t * (e1 - e0))) < 3.0: out.append((v.X, v.Y, v.Z))
            return out
        pts = near(face) + near(cheek)
        strip = strip.fuse(_hull(pts).cut(box))
    for peg, _hole in _peg_parts(planes):
        strip = strip.fuse(peg)
    return strip.clean()


GRILLE_FIT = 0.3      # clearance of the grille insert in its opening, mm
GRILLE_LAP = 4.0      # width of the flange that laps behind the nose wall, mm


def grille_insert():
    """Flat grille panel: a plate that fills the opening flush with the nose face, on a flange that laps behind the wall
    (bond it from inside the nose)."""
    _, planes = nose_box(with_planes=True)
    plate = window(planes, _is_nose_face, inset=PILLAR + GRILLE_FIT, top=GRILLE_TOP + GRILLE_FIT, span=(-WALL - 2.0, -1.0))
    # the flange laps behind the wall on the sides and below; at the top it stops at the bar under the light strip
    flange = window(planes, _is_nose_face, inset=PILLAR - GRILLE_LAP, top=GRILLE_TOP - 2.0, span=(-WALL - 2.0, -WALL - GRILLE_FIT))
    return plate[0].fuse(flange[0]).clean()


def outer_solid(inset=0.0, bevel=False):
    """Everything inside the outer skin of the body (fuselage and nose box), for seating the canopy on it. inset > 0 moves every outer plane
    that far inward (the wheel-well liners are clipped half a wall inside the skin, so they never share a face or a crease with the outer skin)."""
    pts = [RIDGE_NOSE, RIDGE_MID, HOOD_MID, RIDGE_COWL, SHOULDER, NOSE_TOP, BELT_FRONT, WEDGE, B_FOOT, BELT_REAR] + CHINE + ROCKER
    planes = _planes(_both(pts))
    if inset:
        planes = planes.copy(); planes[:, 3] += inset
    if bevel:   # the skin's own outer boundary: the same 0.5 mm bevels as block(bevel=True) puts on the fuselage (the wheel-well liners are clipped
        # with this, so their faces that reach the outside lie in a skin facet or bevel and end on its fold lines: NOTES, liner rebuild theory)
        planes = np.vstack([planes, _bevel(planes)])
    return _solid(planes)


def _grow(poly, d):
    """Convex polygon [(a, b), ...] moved outward by d on every edge (corners follow the bisectors)."""
    P = np.array(poly, float); c = P.mean(axis=0); out = []
    nrm = []
    for a, b in zip(P, np.roll(P, -1, axis=0)):
        e = b - a; m = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        nrm.append(m if m @ ((a + b) / 2 - c) > 0 else -m)
    for k, v in enumerate(P):
        n0, n1 = nrm[k - 1], nrm[k]
        out.append(v + d * (n0 + n1) / (1 + n0 @ n1))
    return out


def side_glass(planes, depth=WALL * 3, flare=CHAMFER):
    """Cutters for the traced side glass outline, pushed through the side facet along its normal, opened out by `flare` at the outer face."""
    from parts.util import hull
    out = []
    for q, poly in zip(planes, _facets(planes)):
        if poly is None: continue
        n = q[:3]
        if not (abs(n[0]) > 0.55 and poly.mean(axis=0)[1] < 0): continue
        on = lambda y, z: np.array([-(q[1] * y + q[2] * z + q[3]) / q[0], y, z])
        pts = [tuple(on(y, z) - n * depth) for y, z in SIDE_GLASS] + [tuple(on(y, z) - n * flare) for y, z in SIDE_GLASS]
        pts += [tuple(on(y, z)) for y, z in _grow(SIDE_GLASS, flare)] + [tuple(on(y, z) + n * depth) for y, z in _grow(SIDE_GLASS, flare)]
        out.append(hull(pts))
    return out


def canopy():
    pts = [BELT_FRONT, COWL_POST, ROOF_FRONT, ROOF_PEAK, B_FOOT, BELT_REAR]
    # open: the base, and the rear slope behind the roof peak (the original has a bare tube frame there)
    # the roof / pillar silhouette (drawn line: cowl post - roof front - roof peak - B-foot) carries a CANOPY_EDGE_CHAMFER bevel on both sides
    _edges = [(np.array(a, float) * np.array([sx, 1, 1]), np.array(b, float) * np.array([sx, 1, 1])) for a, b in ((COWL_POST, ROOF_FRONT), (ROOF_FRONT, ROOF_PEAK), (ROOF_PEAK, B_FOOT)) for sx in (1, -1)]
    shell, planes = block(pts, open_if=lambda n: n[2] < -0.6 or (n[1] > 0.3 and abs(n[0]) < 0.5), big_edges=_edges, big_d=CANOPY_EDGE_CHAMFER)
    cuts = side_glass(planes)            # side glass, ahead of the B-pillar
    cuts += window(planes, lambda n, c: n[1] < -0.35 and abs(n[0]) < 0.5 and c[2] > 150)   # windscreen
    for cutter in cuts:
        shell = shell.cut(cutter)
    # Clip the visor against the same outer planes as the pillar and roof.
    # Its swept wings blend into the pillars without crossing the chamfer.
    outer = _solid(np.vstack([planes, _bevel(planes), _bevel(planes, CANOPY_EDGE_CHAMFER, only=_edges)]))
    shell = shell.fuse(visor().intersect(outer)).clean()
    return shell, planes


VISOR_T = 3.0         # visor plate thickness, mm
VISOR_TIP_Y = -122.0  # front edge of the centre of the visor, mm (26 mm ahead of the roof front edge)
VISOR_WING_Y = -137.0  # front edge of the swept wing tips


def visor():
    """Sun visor over the windscreen: a flat plate in the plane of the windscreen glass, from the roof front edge forward, flat across the middle
    (x +-38) and swept forward to wing tips at the sides (plan traced from the user's markup). It is fused into the roof, 1 mm back."""
    slope = (ROOF_FRONT[2] - COWL_POST[2]) / (ROOF_FRONT[1] - COWL_POST[1])      # the windscreen glass slope (cowl post to roof front edge)
    zt = lambda y: ROOF_FRONT[2] + slope * (y - ROOF_FRONT[1])
    y0 = ROOF_FRONT[1] + 1.0
    # one plate, one outline (no seams between the middle and the wings, so no slits): the plan prism cut to a slab along the glass plane
    # the wing outer edges follow the A-pillar line (cowl post to roof front edge), 2 mm inside its outer edge, so each wing runs into the pillar frame:
    # no gap, no slit between the visor and the pillar
    xl = lambda y: ROOF_FRONT[0] + (y - ROOF_FRONT[1]) * (COWL_POST[0] - ROOF_FRONT[0]) / (COWL_POST[1] - ROOF_FRONT[1]) - 2.0
    plan = [(-xl(y0), y0), (-xl(VISOR_WING_Y), VISOR_WING_Y), (-38, VISOR_TIP_Y), (38, VISOR_TIP_Y), (xl(VISOR_WING_Y), VISOR_WING_Y), (xl(y0), y0)]
    ext = cq.Workplane('XY').workplane(offset=0).polyline(plan).close().extrude(400).val()
    ys = (VISOR_WING_Y - 5.0, y0 + 5.0)
    slab = beveled_hull([(x, y, zt(y) - dz) for x in (-90, 90) for y in ys for dz in (0.0, VISOR_T)], d=0.01)
    return ext.intersect(slab).clean()


# Front edge of the wheel arch (world y). The arch used to start at -263, 39 mm ahead of the front arm (-224) and its lock / bump travel cuts, which carve the rest.
ARCH_FRONT_Y = -240.0


# Arch outline in the side view (y, z): the old corner points joined by smooth curves instead of straight facets. The curves pass through the old corners
# and bulge outside the old polygon, so every clearance the polygon gave is kept. Rear shoulder: one rounded sweep from the rocker line up into the flat
# ceiling; front: the raked front edge runs up into the ceiling through a soft corner.
ARCH_CEIL_Z = 102.4


def _arch_solid(x0):
    f = ARCH_FRONT_Y
    w = (cq.Workplane('YZ', origin=(x0, 0, 0)).moveTo(f, -60).lineTo(f, 60)
         .spline([(f + 4.0, 88.0), (f + 22.0, ARCH_CEIL_Z)], tangents=[(0, 1), (1, 0)], includeCurrent=True)
         .lineTo(-122.0, ARCH_CEIL_Z)
         .spline([(-94.0, 96.0), (-80.0, 76.0), (-77, 60)], tangents=[(1, 0), (0, -1)], includeCurrent=True)
         .lineTo(-77, -60).close())
    return w.extrude(160).val()


def arch_cut(x0=56.5, grow=0.0):
    """Faceted front wheel arches plus the open belly between them. Each arch is a five-sided prism that contains the old
    round scoop and every suspension clearance cut, so the arch edge is three straight lines. Between the arches the same
    profile, starting behind the nose face, removes the underside so the nose is a hollow beak over the front axle."""
    prof = [(ARCH_FRONT_Y, -60), (ARCH_FRONT_Y, 60), (ARCH_FRONT_Y + 10.0, 102.4), (-103, 102.4), (-77, 60), (-77, -60)]
    if grow:
        one = cq.Workplane('YZ', origin=(x0, 0, 0)).polyline(_grow(prof, grow)).close().extrude(160).val()
    else:
        one = _arch_solid(x0)
    belly = [(NOSE_BACK_Y, -60), (NOSE_BACK_Y, 95), (ARCH_FRONT_Y + 26.0, 102.4), (-103, 102.4), (-77, 60), (-77, -60)]
    mid = cq.Workplane('YZ', origin=(-x0 - 1, 0, 0)).polyline(belly).close().extrude(2 * x0 + 2).val()
    return [one, one.mirror('YZ'), mid]


CANOPY_GAP = 0.3      # glue gap between the canopy foot and the body skin, mm
CANOPY_EDGE_CHAMFER = 4.0   # mm leg of the chamfer along the roof / pillar line
CANOPY_TABS = False       # the canopy locating tabs (two per side) were removed on request
TAB_Y = (-150.0, -40.0)   # stations of the canopy locating tabs along the belt, two per side
TAB_W = 12.0          # tab width along the belt, mm
TAB_DROP = 8.0        # how far a tab reaches down inside the cabin opening, mm


def _tabs(body):
    """Locating tabs under the canopy foot: each hooks over the deck rim and drops inside the cabin opening, so the canopy
    can only sit in one place. Cut against the body moved CANOPY_GAP every way, which leaves that clearance all round."""
    tabs = []
    (xa, ya, za), (xb, yb, zb) = BELT_FRONT, B_FOOT
    for y in TAB_Y:
        t = (y - ya) / (yb - ya); x = xa + t * (xb - xa); z = za + t * (zb - za)
        for side in (1, -1):
            x0, x1 = sorted((side * (x - CABIN_RIM - 4.0), side * (x - 0.5)))
            tab = cq.Solid.makeBox(x1 - x0, TAB_W, TAB_DROP + 22.0, cq.Vector(x0, y - TAB_W / 2, z - TAB_DROP))
            g = CANOPY_GAP
            for d in [(g, 0, 0), (-g, 0, 0), (0, g, 0), (0, -g, 0), (0, 0, g), (0, 0, -g)] + [(i * g, j * g, k * g) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]:
                tab = tab.cut(body.translate(cq.Vector(*d)))
            tabs.append(tab)
    return tabs


def make():
    """Body and canopy as two printable parts: the canopy stands on the body's outer skin with CANOPY_GAP all round."""
    f, fp = fuselage()
    c, cp = canopy()
    seat = outer_solid()
    # grow the seat by the glue gap: move every plane out
    grown = _planes(_both([RIDGE_NOSE, RIDGE_MID, HOOD_MID, RIDGE_COWL, SHOULDER, NOSE_TOP, BELT_FRONT, WEDGE, B_FOOT, BELT_REAR] + CHINE + ROCKER))
    grown[:, 3] -= CANOPY_GAP
    c = c.cut(_solid(grown))
    # 0.5 mm break on the canopy foot's outside edge (stepped skin-layer cuts, as chamfer_rims)
    base = _planes(_both([RIDGE_NOSE, RIDGE_MID, HOOD_MID, RIDGE_COWL, SHOULDER, NOSE_TOP, BELT_FRONT, WEDGE, B_FOOT, BELT_REAR] + CHINE + ROCKER))
    for i in range(CHAMFER_STEPS):
        a, b = CHAMFER * i / CHAMFER_STEPS, CHAMFER * (i + 1) / CHAMFER_STEPS
        pa, pb = cp.copy(), cp.copy(); pa[:, 3] += a; pb[:, 3] += b
        g = base.copy(); g[:, 3] -= CANOPY_GAP + CHAMFER * (1 - i / CHAMFER_STEPS)
        piece = _solid(g).intersect(_solid(pa).cut(_solid(pb)))
        if piece.Volume() > 1e-6:
            c = c.cut(piece)
    # tabs: keep only what lies inside the canopy's own outer skin, so nothing shows from outside
    inside = _solid(cp)
    for tab in (_tabs(f) if CANOPY_TABS else []):
        piece = tab.intersect(inside)
        big = max(piece.Solids(), key=lambda q: q.Volume()) if piece.Solids() else None
        if big is not None and big.Volume() > 50.0:
            c = c.fuse(big)
    return f, c.clean(), fp, cp


CHAMFER_STEPS = 3


def _skin_inset(d):
    """Solid of the body and the nose box with every outer plane moved inward by d (the skin's outer layer is inset(a) minus inset(b))."""
    pts = [RIDGE_NOSE, RIDGE_MID, HOOD_MID, RIDGE_COWL, SHOULDER, NOSE_TOP, BELT_FRONT, WEDGE, B_FOOT, BELT_REAR] + CHINE + ROCKER
    out = None
    for plist in (pts, _nose_points()):
        pl = _planes(_both(plist)); pl[:, 3] += d
        sol = _solid(pl)
        out = sol if out is None else out.fuse(sol)
    return out


def chamfer_rims(shell, growers, size=CHAMFER):
    """Break the outside edge of cuts through the skin by `size` (45 degrees, approximated by CHAMFER_STEPS steps). OCC's chamfer crashes on these
    shells, so each step removes (cutter grown by size*(1 - i/N)) from the skin layer between depths size*i/N and size*(i+1)/N. `growers` are
    functions g -> [cutter grown by g mm]."""
    n = CHAMFER_STEPS
    for i in range(n):
        slab = _skin_inset(size * i / n).cut(_skin_inset(size * (i + 1) / n))
        for grow in growers:
            for gc in grow(size * (1 - i / n)):
                piece = gc.intersect(slab)
                if piece.Volume() > 1e-6:
                    shell = shell.cut(piece)
    return shell.clean()


def _arch_outline(x0=56.5, step=0.5):
    """The arch opening's real outline (lines and splines of _arch_solid) as a dense (y, z) polygon, counter-clockwise."""
    sol = _arch_solid(x0)
    f = [f for f in sol.Faces() if f.geomType() == 'PLANE' and abs(f.Center().x - x0) < 1e-6][0]
    pts = []
    for e in f.outerWire().Edges():
        n = max(2, int(math.ceil(e.Length() / step)))
        for v in e.positions([i / n for i in range(n)]):
            pts.append((v.y, v.z))
    P = []
    for p in pts:
        if not P or math.hypot(p[0] - P[-1][0], p[1] - P[-1][1]) > 1e-6: P.append(p)
    P = np.array(P)
    if 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]) < 0: P = P[::-1]
    return P


def exact_arch_chamfer(shell, x0=56.5, size=CHAMFER):
    """Exact 45 degree break on the outside edge of both wheel arches (replaces the stepped chamfer_rims there). For every outer plane k of the
    fuselage that faces the arch's side, a ruled cutter runs from the real arch outline grown by `size` on plane k down to the outline itself `size`
    deeper; it is clipped to the region of the body closer to plane k than to any other outer plane, so the cutters of two facets meet exactly on
    their fold. The outline is the real one (splines included), not the straight-sided stand-in the stepped version grew."""
    planes = _planes(_both(_fuselage_points()))
    P0 = _arch_outline(x0); P1 = np.array(_grow([tuple(p) for p in P0], size))
    big = 600.0
    box = [np.array([1, 0, 0, -big]), np.array([-1, 0, 0, -big]), np.array([0, 1, 0, -big]), np.array([0, -1, 0, -big]),
           np.array([0, 0, 1, -big]), np.array([0, 0, -1, -big])]
    n_cut = 0
    for side in (1, -1):
        for k, q in enumerate(planes):
            n, d = q[:3], q[3]
            if side * n[0] < 0.2: continue
            on = lambda yz, depth: np.array(((-(d + depth) - n[1] * yz[0] - n[2] * yz[1]) / n[0], yz[0], yz[1]))
            outer = [on(p, 0.0) for p in P1]; inner = [on(p, size) for p in P0]
            mk = lambda ps: cq.Wire.makePolygon([cq.Vector(*p) for p in ps], close=True)
            faces = [cq.Face.makeFromWires(mk(outer)), cq.Face.makeFromWires(mk(inner))]
            m = len(outer)
            for i in range(m):
                j = (i + 1) % m
                faces.append(cq.Face.makeFromWires(mk([outer[i], outer[j], inner[j]])))
                faces.append(cq.Face.makeFromWires(mk([outer[i], inner[j], inner[i]])))
            try:
                fr = cq.Solid.makeSolid(cq.Shell.makeShell(faces)).fix()
                if fr.Volume() < 0: fr = cq.Solid(fr.wrapped.Reversed())
            except Exception:
                continue
            # Voronoi cell of plane k: depth to k <= depth to every other outer plane, inside a big box
            cell = [np.append(planes[j][:3] - n, planes[j][3] - d) for j in range(len(planes)) if j != k]
            try:
                c = _solid(np.array(cell + box))
            except Exception:
                continue
            cut = fr.intersect(c)
            if cut.Volume() > 1e-6:
                shell = shell.cut(cut); n_cut += 1
    print('exact arch chamfer: %d facet cutters' % n_cut)
    return shell.clean()
