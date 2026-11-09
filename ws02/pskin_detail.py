"""Layer C detail cuts on the closed panel shell (standalone skin).  Every detail is an outline read from the sheet view where it is clearest,
projected along that view onto the panels: grooves 1.2 mm wide x 0.7 mm deep along outlines (rev 17 rule), through slots / holes, scoops, bay opening,
mini spoiler and rails.  Nothing here touches the rev 9 chassis build."""
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh, OpType
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
import pskin_core as C

GW, GD = 1.2, 0.7
LOG = []


def man(t):
    return Manifold(Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))


def prism(poly, axis, lo, hi):
    """Polygon extruded along axis 'z' (poly in x,y), 'y' (poly in x,z) or 'x' (poly in y,z) over [lo, hi]."""
    pg = poly if isinstance(poly, (Polygon, MultiPolygon)) else Polygon(poly)
    if not pg.is_valid:
        pg = pg.buffer(0)
    geoms = list(pg.geoms) if isinstance(pg, MultiPolygon) else [pg]
    out = []
    for g in geoms:
        if g.area < 1e-6:
            continue
        m = trimesh.creation.extrude_polygon(g, hi - lo)
        V = m.vertices.copy()
        if axis == "z":
            V[:, 2] += lo
        elif axis == "y":
            V = np.stack([V[:, 0], hi - V[:, 2], V[:, 1]], 1)
        else:                                                   # 'x': (a, b, c) -> (c + lo, a, b)
            V = np.stack([V[:, 2] + lo, V[:, 0], V[:, 1]], 1)
        m = trimesh.Trimesh(V, m.faces, process=False)
        if m.volume < 0:
            m.invert()
        out.append(man(m))
    return Manifold.batch_boolean(out, OpType.Add) if out else Manifold()


def ring(poly, w=GW):
    pg = Polygon(poly).buffer(0)
    return pg.buffer(w / 2.0).difference(pg.buffer(-w / 2.0))


def line_band(pts, w=GW):
    return LineString(pts).buffer(w / 2.0, cap_style=2)


class Detail:
    def __init__(self, P, panels, t=2.4):
        self.P, self.panels = P, panels
        self.body = C.manifold_of(C.shell_mesh(P, panels, t))
        self.skin = C.manifold_of(C.shell_mesh(P, panels, GD))              # outer 0.7 mm layer (groove depth)
        self.names = {p["name"]: p for p in panels}

    # -- polygons from the panel graph (plan / side projections) --
    def pts(self, names):
        out = []
        for n in names:
            out += self.names[n]["ids"]
        return sorted(set(out))

    def plan_poly(self, panel_names, inset=0.0):
        pgs = [Polygon([(self.P[i][0], self.P[i][1]) for i in self.names[n]["ids"]]).buffer(0) for n in panel_names]
        u = unary_union(pgs)
        return u.buffer(-inset) if inset else u

    # -- operations: cutters are collected and subtracted in one boolean (many small sequential booleans were slow) --

    def groove(self, geom, axis, lo, hi, name):
        """Cut a groove: the part of the outer 0.7 mm layer inside prism(geom)."""
        from shapely.affinity import translate
        geom = translate(geom, 0.0313, 0.0171)                     # jitter: avoids exact coincidence with panel creases (pinch points after the boolean)
        cut = prism(geom, axis, lo, hi) ^ self.skin
        self.cutters = getattr(self, "cutters", []) + [cut]
        LOG.append((name, "groove", round(cut.volume(), 1)))

    def through(self, geom, axis, lo, hi, name):
        cut = prism(geom, axis, lo, hi)
        self.cutters = getattr(self, "cutters", []) + [cut]
        LOG.append((name, "through", round((cut ^ self.body).volume(), 1)))

    def add(self, man_, name):
        self.adders = getattr(self, "adders", []) + [man_]
        LOG.append((name, "add", round(man_.volume(), 1)))

    def finish(self):
        if getattr(self, "adders", None):
            self.body = Manifold.batch_boolean([self.body] + self.adders, OpType.Add)
        self.dbg = list(getattr(self, "cutters", []) or []) + getattr(self, "dbg", [])
        if getattr(self, "cutters", None):
            ok = self.body
            dropped = 0
            for c in self.cutters:                       # greedy: a cutter that leaves pinch points after welding is dropped (and logged)
                nb = ok - c
                if C.to_trimesh(nb).is_watertight:
                    ok = nb
                else:
                    dropped += 1
            self.body = ok
            if dropped:
                LOG.append(("dropped cutters (non-watertight after weld)", "info", dropped))
        self.adders, self.cutters = [], []


# ----------------------------------------------------------------------------------------------------------------------------------
def front_yz(px, py):                      # sheet front view -> (y, z): centre px 1212, 0.60 mm/px across, 0.643 mm/px up from the ground line (py 382)
    return (px - 1212.0) * 0.60, (382.0 - py) * 0.643


def rear_yz(px, py):                       # sheet rear view -> (y, z): centre px 1721
    return (px - 1721.0) * 0.73, (382.0 - py) * 0.63


def mir(pts):
    return [(a, -b) for a, b in pts]


def both(d, geom_fn, *a, **k):
    pass


def panel_plane(d, names):
    Q = np.array([d.P[i] for n in names for i in d.names[n]["ids"]])
    c = Q.mean(0)
    n = np.linalg.svd(Q - c)[2][2]
    if n[2] < 0:
        n = -n
    return c, n


def scoop(d, pname, tag):
    """Wedge scoop on a hood-side panel: 7.5 mm high at the front edge (vertical front face), 0 at the rear edge, open mouth, cavity, hole through the panel."""
    ids = d.names[pname]["ids"]
    Q = np.array([d.P[i] for i in ids])
    c, n = panel_plane(d, [pname])
    # order front -> rear by x
    cen = Q.mean(0)
    poly = Polygon(Q[:, :2]).buffer(-3.5)
    pts2 = np.array(poly.exterior.coords)[:-1]
    xs = pts2[:, 0]
    zq = lambda x, y: c[2] - (n[0] * (x - c[0]) + n[1] * (y - c[1])) / n[2]
    base = np.array([[x, y, zq(x, y) - 0.5] for x, y in pts2])
    u = (xs.max() - xs) / max(xs.max() - xs.min(), 1e-6)
    top = np.array([[x, y, zq(x, y) + 7.5 * (1 - uu)] for (x, y), uu in zip(pts2, u)])
    solid = man(trimesh.convex.convex_hull(np.vstack([base, top])))
    # cavity: inset 1.6, open at the front (extend the cavity forward past the vertical face)
    p2 = poly.buffer(-1.6)
    q2 = np.array(p2.exterior.coords)[:-1]
    qs = q2[:, 0]
    uu = (xs.max() - qs) / max(xs.max() - xs.min(), 1e-6)
    cb = np.array([[x, y, zq(x, y) + 0.4] for x, y in q2])
    ct = np.array([[x, y, zq(x, y) + 7.5 * (1 - u_) - 1.4] for (x, y), u_ in zip(q2, uu)])
    cav = man(trimesh.convex.convex_hull(np.vstack([cb, ct])))
    front = np.array([[xs.max() + 1.5, y, zq(xs.max(), y) + 6.2] for y in (q2[:, 1].min(), q2[:, 1].max())] + [[xs.max() + 1.5, y, zq(xs.max(), y) + 0.4] for y in (q2[:, 1].min(), q2[:, 1].max())])
    mouth = man(trimesh.convex.convex_hull(np.vstack([cb, ct, front])))
    d.add(solid, f"scoop {tag} wedge")
    d.finish()                                                         # wedge fused first, then the mouth cavity and the hole through the panel
    d.body = d.body - mouth
    d.body = d.body - prism(p2.buffer(-0.6), "z", c[2] - 8, c[2] + 2)
    LOG.append((f"scoop {tag}", "mouth+hole", round(mouth.volume(), 1)))


def apply_details(d):
    import os
    if os.environ.get('WS03_WARP') == '1':
        import pskin_warp as _W
        _px, _sx = C.plan_xy, C.side_xz
        C.plan_xy = lambda px, py: (lambda a: (_W.wx(a[0]), a[1]))(_px(px, py))
        C.side_xz = lambda px, py: (lambda a: (_W.wx(a[0]), a[1]))(_sx(px, py))
    P = d.P
    Z0, Z1 = 60, 260
    # ---- top layer (plan outlines, projected along z) ----
    d.groove(ring(d.plan_poly(["WS", "WS'"], 4.0)), "z", 100, 260, "windscreen glass")
    for s, nm in ((1, "HS"), (-1, "HS'")):
        d.groove(ring(d.plan_poly([nm], 2.0)), "z", 100, 260, f"hood panel {nm}")
    # hood vent: ring + three through slots (plan px)
    def pp(l):
        return [C.plan_xy(a, b) for a, b in l]
    vent = pp([(207, 186), (252, 182), (252, 238), (207, 234)])
    d.groove(ring(vent), "z", 100, 260, "hood vent frame")
    for px in (214, 227, 240):
        x0, _ = C.plan_xy(px, 210); x1, _ = C.plan_xy(px + 5, 210)
        d.through(Polygon([(x0, -17), (x1, -17), (x1, 17), (x0, 17)]), "z", 100, 260, "hood vent slot")
    # roof stripes (sheet red lines, plan px py 148.5/152, x px 395..525)
    for pyv in (148.5, 152.0):
        a, b = C.plan_xy(395, pyv), C.plan_xy(525, pyv)
        for sg in (1, -1):
            d.groove(line_band([(a[0], sg * a[1]), (b[0], sg * b[1])]), "z", 100, 260, "roof stripe")
    # engine-bay opening (through) + rim groove
    bay = pp([(556, 175), (575, 154), (666, 154), (686, 172), (697, 210)])
    bay = Polygon(bay + [(x, -y) for x, y in reversed(bay[:-1])] if bay[-1][1] == 0 else bay + mir(list(reversed(bay[:-1]))))
    d.through(bay, "z", 120, 260, "engine bay opening")
    d.groove(ring(bay.buffer(3.0)), "z", 120, 260, "engine bay rim")
    # ---- side layer (side px, projected along y; left y>0 and right y<0) ----
    def sd(l):
        return [C.side_xz(a, b) for a, b in l]
    glass = sd([(333, 548), (386, 488), (522, 474), (537, 525)])
    for lo, hi in ((20, 140), (-140, -20)):
        d.groove(ring(Polygon(glass).buffer(-3.0)), "y", lo, hi, "side glass")
    vent = sd([(325, 587), (390, 579), (388, 591), (331, 600)])
    for lo, hi in ((20, 140), (-140, -20)):
        d.groove(ring(Polygon(vent).buffer(0.5)), "y", lo, hi, "door vent pocket")
        for k in range(4):                                   # louvre slots across the pocket
            t0, t1 = 0.12 + 0.22 * k, 0.12 + 0.22 * k + 0.12
            quad = [tuple(np.array(vent[0]) * (1 - t) + np.array(vent[1]) * t) for t in (t0, t1)] + [tuple(np.array(vent[3]) * (1 - t) + np.array(vent[2]) * t) for t in (t1, t0)]
            d.through(Polygon(quad).buffer(0), "y", lo, hi, "door louvre")
        for k in range(5):                                   # rear-quarter intake: five slanted through slots along the dark strip
            a = np.array(C.side_xz(580, 550)); b = np.array(C.side_xz(556, 605))
            c0 = a * (1 - (0.1 + 0.19 * k)) + b * (0.1 + 0.19 * k)
            dirv = (b - a) / np.linalg.norm(b - a); nrm = np.array([-dirv[1], dirv[0]])
            quad = [tuple(c0 + nrm * 2.2 + dirv * 2.4), tuple(c0 + nrm * 2.2 - dirv * 2.4), tuple(c0 - nrm * 2.2 - dirv * 2.4), tuple(c0 - nrm * 2.2 + dirv * 2.4)]
            d.through(Polygon(quad), "y", lo, hi, "quarter slot")
        for (a, b) in (((357, 668), (500, 640)), ((592, 608), (640, 535)), ((640, 535), (700, 508))):
            d.groove(line_band([C.side_xz(*a), C.side_xz(*b)]), "y", lo, hi, "red line")
    # ---- front layer (grille, headlights) projected along x ----
    hl = [front_yz(*p) for p in ((1250, 185), (1262, 178), (1305, 167), (1303, 178), (1270, 196), (1255, 196))]
    for pts in (hl, mir_y(hl)):
        d.groove(ring(Polygon(pts)), "x", -0.37, 45, "headlight")
    grille = [front_yz(*p) for p in ((1172, 205), (1182, 192), (1245, 192), (1253, 205), (1253, 227), (1245, 235), (1182, 235), (1172, 227))]
    gm = [(1.0 * (y - 0.5 * (min(a for a, _ in grille) + max(a for a, _ in grille))) + 0.5 * (min(a for a, _ in grille) + max(a for a, _ in grille)), z) for y, z in grille]
    d.groove(ring(Polygon(grille)), "x", 10, 45, "grille frame")
    yc = 0.5 * (min(a for a, _ in grille) + max(a for a, _ in grille))
    for r, (zc, n) in enumerate(((116.0, 5), (108.5, 4), (101.5, 3))):
        for k in range(n):
            y = yc + (k - (n - 1) / 2.0) * 7.0
            d.through(Polygon([(y - 3.0, zc), (y, zc + 3.0), (y + 3.0, zc), (y, zc - 3.0)]), "x", 10, 45, "grille hole")
    # ---- rear layer (tail lights) projected along x ----
    tl = [rear_yz(*p) for p in ((1622, 122), (1667, 118), (1683, 130), (1667, 143), (1625, 137))]
    for pts in (tl, mir_y(tl)):
        d.groove(ring(Polygon(pts)), "x", -362, -325, "tail light")
    d.finish()
    scoop(d, "HS", "L"); scoop(d, "HS'", "R")
    return d


def mir_y(pts):
    return [(-a, b) for a, b in pts]


# ----------------------------------------------------------------------------------------------------------------------------------
def surf_z(mesh, x, y, k=0):
    """z of the k-th hit (0 = outer top surface, 1 = inner face) of a vertical ray through (x, y)."""
    loc, _, _ = mesh.ray.intersects_location([[x, y, 400.0]], [[0, 0, -1.0]], multiple_hits=True)
    zs = sorted((float(v) for v in loc[:, 2]), reverse=True)
    return zs[k] if len(zs) > k else None


def hullm(pts):
    return man(trimesh.convex.convex_hull(np.array(pts, float)))


def spoiler_and_rails(d):
    """Mini spoiler (rev 14 numbers: 4 mm slab, 23.5 mm deep, span 70 mm, leading edge 16 mm over the roof, top plane falling 21 deg, 5-panel chevron
    trailing edge, open underneath, two 5 x 5 mm legs) on the rear end of the roof, and two slanted grab rails along the deck (6.4 x 4.6 mm, 4 stations)."""
    mesh = C.to_trimesh(d.body)
    x0, x1 = -206.0, -229.7
    zl = surf_z(mesh, x0, 0.0) + 16.0
    tn = np.tan(np.radians(21.0))
    plan = [(x0, 35.0), (-221.0, 35.0), (-227.0, 18.0), (x1, 0.0), (-227.0, -18.0), (-221.0, -35.0), (x0, -35.0)]
    top = [(x, y, zl - tn * (x0 - x)) for x, y in plan]
    sp = hullm(top + [(x, y, z - 4.0) for x, y, z in top])
    d.add(sp, "mini spoiler plate")
    for sg in (1, -1):
        yy = sg * 32.5
        zr = surf_z(mesh, -209.5, yy)
        zt = zl - tn * (x0 + 209.5) - 0.0
        d.add(hullm([(x, y, z) for x in (-207.0, -212.0) for y in (yy - 2.5, yy + 2.5) for z in (zr - 3.0, zt - 3.0)]), "spoiler leg")
    # rails
    st = [(-236.0, 46.0), (-268.0, 46.0), (-304.0, 43.0), (-338.0, 34.0)]
    for sg in (1, -1):
        prev = None
        for (x, y) in st:
            yy = sg * y
            z = surf_z(mesh, x, yy)
            if z is None:
                continue
            lean = -sg * 1.3
            sec = [(x - 2.3 * 0, yy + dy, z + dz) for dy in (-2.3, 2.3) for dz in (-1.0, 5.4)]
            sec = [(a, b + (lean if dz > 0 else 0.0) * 1.0, c) for (a, b, c), dz in zip(sec, (-1.0, 5.4, -1.0, 5.4))]
            sec = [(a + e, b, c) for (a, b, c) in sec for e in (-1.2, 1.2)]
            if prev is not None:
                d.add(hullm(prev + sec), "grab rail")
            prev = sec
    d.finish()
    return d
