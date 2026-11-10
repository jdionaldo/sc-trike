"""WS-03 body shell rebuilt panel by panel from the Pepakura blueprint, sheet 71.

Panels are authored in SHEET millimetres (1:10 shell: x from the nose tail-ward 0..278, y left, z up from the belly 0..102) as facet strips whose
rail topology follows the traced flat patterns (flat_patterns.json: outlines + fold lines) and whose 3D positions come from the five views.
`build()` scales to WS-03 (SCALE), poses on the chassis, thickens every planar facet inward by WALL and unions per panel (manifold3d).
"""
import json, os, sys
import numpy as np, trimesh
import manifold3d as m3
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = float(os.environ.get("BP_SCALE", 1.46))     # sheet mm -> real mm (width 139 -> 203 mm = width of the previous skin)
NOSE_X = float(os.environ.get("BP_NOSE_X", 60.0))   # chassis x of the nose tip
Z_BELLY = -29.0                                       # chassis z of the belly line (as the previous skin)
WALL = 2.4
S = 1.0


def man(t):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def tm(M):
    mm = M.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3].astype(float), np.asarray(mm.tri_verts), process=False)


def mirror_pts(rows):
    """rows of (x,y,z) for y>=0 -> mirrored rows (y -> -y), same order."""
    return [[(x, -y, z) for x, y, z in r] for r in rows]


def strip(rows, flip=False):
    """facet triangles between consecutive rows (each row a list of points). Quad split along the shorter diagonal."""
    tris = []
    for a, b in zip(rows[:-1], rows[1:]):
        for j in range(len(a) - 1):
            q = [a[j], a[j + 1], b[j + 1], b[j]]
            d1 = np.linalg.norm(np.subtract(q[0], q[2])); d2 = np.linalg.norm(np.subtract(q[1], q[3]))
            if d1 <= d2: tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
            else: tris += [(q[0], q[1], q[3]), (q[1], q[2], q[3])]
    return tris


# ------------------------------------------------------------------ panels (sheet mm) ----
def panels():
    P = {}
    # ---- P1 front nose / grille: grille fascia, bumper, two headlight wings
    gt = [(4, -24, 36), (4, -12, 37), (4, 12, 37), (4, 24, 36)]
    gb = [(8, -22, 8), (8, -11, 7), (8, 11, 7), (8, 22, 8)]
    bm = [(15, -25, 1), (15, -12, 0), (15, 12, 0), (15, 25, 1)]
    wing_top = [(4, 24, 36), (10, 36, 47), (26, 46, 52)]
    wing_bot = [(8, 22, 8), (12, 32, 16), (26, 46, 24)]
    wingL = strip([wing_top, wing_bot])
    wingR = strip(mirror_pts([wing_top, wing_bot]))
    P["P1"] = dict(tris=strip([gt, gb, bm]) + wingL + wingR, inside=(40, 0, 25))
    # ---- P2 front side panels (flank in front of the wheel arch)
    r0 = [(26, 46, 52), (44, 45, 58), (62, 42, 60)]
    r1 = [(26, 47, 38), (44, 49, 44), (62, 46, 46)]
    r2 = [(26, 46, 24), (44, 48, 26), (62, 47, 26)]
    P["P2L"] = dict(tris=strip([r0, r1, r2]), inside=(44, 20, 38))
    P["P2R"] = dict(tris=strip(mirror_pts([r0, r1, r2])), inside=(44, -20, 38))
    # ---- P3 hood
    h0 = [(6, -27, 37), (6, -14, 39), (6, 14, 39), (6, 27, 37)]
    h1 = [(34, -40, 50), (34, -16, 56), (34, 16, 56), (34, 40, 50)]
    h2 = [(62, -40, 56), (62, -26, 60), (62, 26, 60), (62, 40, 56)]
    P["P3"] = dict(tris=strip([h0, h1, h2]), inside=(34, 0, 20))
    # ---- P8 side panels
    t = [(62, 40, 46), (96, 41, 44), (130, 43, 54), (160, 46, 62), (194, 50, 67)]
    m_ = [(62, 46, 24), (96, 48, 26), (130, 50, 30), (152, 53, 36), (194, 58, 58)]
    b = [(62, 42, 2), (96, 44, 2), (130, 46, 2), (150, 50, 4), (194, 54, 46)]
    P["P8L"] = dict(tris=strip([t, m_, b]), inside=(130, 20, 40))
    P["P8R"] = dict(tris=strip(mirror_pts([t, m_, b])), inside=(130, -20, 40))
    # ---- P6 roof panel (rear part of the roof, ridge in the middle)
    q0 = [(176, -37, 95), (176, -15, 100), (176, 15, 100), (176, 37, 95)]
    q1 = [(198, -37, 94), (198, -15, 99), (198, 15, 99), (198, 37, 94)]
    q2 = [(222, -36, 91), (222, -14, 95), (222, 14, 95), (222, 36, 91)]
    P["P6"] = dict(tris=strip([q0, q1, q2]), inside=(198, 0, 60))
    # ---- P9 rear upper cover
    d0 = [(205, -36, 90), (205, -14, 92), (205, 14, 92), (205, 36, 90)]
    d1 = [(232, -40, 91), (232, -15, 92), (232, 15, 92), (232, 40, 91)]
    d2 = [(262, -42, 85), (262, -14, 86), (262, 14, 86), (262, 42, 85)]
    d3 = [(277, -36, 82), (277, -12, 82), (277, 12, 82), (277, 36, 82)]
    P["P9"] = dict(tris=strip([d0, d1, d2, d3]), inside=(240, 0, 40))
    # ---- P10 rear side covers (claws that leave the rear opening between them)
    c_t = [(190, 44, 66), (215, 50, 80), (242, 50, 82), (268, 40, 80)]
    c_m = [(190, 52, 56), (215, 58, 62), (242, 56, 64), (268, 42, 70)]
    c_b = [(194, 48, 46), (218, 52, 44), (244, 50, 48), (264, 38, 56)]
    P["P10L"] = dict(tris=strip([c_t, c_m, c_b]), inside=(220, 30, 50))
    P["P10R"] = dict(tris=strip(mirror_pts([c_t, c_m, c_b])), inside=(220, -30, 50))
    # ---- P11 rear lower diffuser
    e0 = [(198, -30, 46), (198, -12, 44), (198, 12, 44), (198, 30, 46)]
    e1 = [(240, -28, 56), (240, -12, 52), (240, 12, 52), (240, 28, 56)]
    e2 = [(276, -30, 68), (276, -14, 70), (276, 14, 70), (276, 30, 68)]
    P["P11"] = dict(tris=strip([e0, e1, e2]), inside=(240, 0, 100))
    return P


def ring_panel(outer3, inner3, depth):
    """flat frame (ring between two coplanar 3D polygons) extruded `depth` along its plane normal (down), real mm."""
    o = np.asarray(outer3, float); i_ = np.asarray(inner3, float)
    c = o.mean(0)
    u = o[1] - o[0]; u /= np.linalg.norm(u)
    n = np.cross(o[1] - o[0], o[2] - o[1]); n /= np.linalg.norm(n)
    if n[2] < 0: n = -n
    v = np.cross(n, u)
    f = lambda a: [((p - c) @ u, (p - c) @ v) for p in a]
    poly = Polygon(f(o), [f(i_)]).buffer(0)
    mesh = trimesh.creation.extrude_polygon(poly, depth)           # z in [0, depth], extruded along +z local
    T = np.eye(4); T[:3, 0] = u; T[:3, 1] = v; T[:3, 2] = n; T[:3, 3] = c - n * depth
    mesh.apply_transform(T)                                         # top face at the frame plane, body below
    return mesh


FRAME_DEPTH = 4.8     # real mm: frames are solid plates (a folded box section on the paper model)


def bar(p0, p1, w):
    """square bar (real mm) as the hull of two cubes."""
    pts = []
    for p in (p0, p1):
        for dx in (-w / 2, w / 2):
            for dy in (-w / 2, w / 2):
                for dz in (-w / 2, w / 2):
                    pts.append(np.add(p, (dx, dy, dz)))
    return trimesh.convex.convex_hull(np.array(pts))


def frames(X):
    """P4 windshield frame, P5 roof frame (+ B-pillars), P7 roof lights; returns {name: trimesh} in chassis mm."""
    out = {}
    def sq(pts): return [X(p) for p in pts]
    w = 7.0
    # P4 sloped ring: bottom edge x 64 z 60 (y +-40), top edge x 112 z 86 (y +-34)
    ob = [(64, -40, 60), (64, 40, 60), (112, 34, 86), (112, -34, 86)]
    ib = [(70, -40 + w, 62.5), (70, 40 - w, 62.5), (106, 34 - w, 83.5), (106, -34 + w, 83.5)]
    out["P4"] = ring_panel(sq(ob), sq(ib), FRAME_DEPTH)
    # P5: front plate (112..165), rear plate (165..226), window in the front plate, another under the roof panel
    def z_f(x): return 86 + (x - 112) * 11 / 53.0
    def z_r(x): return 97 - (x - 165) * 7 / 61.0
    ofr = [(112, -34, 86), (112, 34, 86), (165, 38, 97), (165, -38, 97)]
    ifr = [(122, -27, z_f(122)), (122, 27, z_f(122)), (160, 27, z_f(160)), (160, -27, z_f(160))]
    orr = [(165, -38, 97), (165, 38, 97), (226, 36, 90), (226, -36, 90)]
    irr = [(172, -26, z_r(172)), (172, 26, z_r(172)), (205, 26, z_r(205)), (205, -26, z_r(205))]
    pf = ring_panel(sq(ofr), sq(ifr), FRAME_DEPTH)
    pr = ring_panel(sq(orr), sq(irr), FRAME_DEPTH)
    parts = [man(pf), man(pr)]
    wb = 6.0 * SCALE
    for sy in (1, -1):
        parts.append(man(bar(X((160, sy * 36, 95)), X((160, sy * 46, 62)), wb)))        # B pillar
        parts.append(man(bar(X((178, sy * 37, 94)), X((197, sy * 52, 66)), wb)))        # rear slanted pillar
    out["P5"] = tm(m3.Manifold.batch_boolean(parts, m3.OpType.Add))
    # P7 roof lights: shelled boxes (open towards the windshield), on the front roof corners
    for sy, nm in ((1, "P7L"), (-1, "P7R")):
        c = X((107, sy * 24, 93))
        sx, sy_, sz = 10 * SCALE, 12 * SCALE, 7 * SCALE
        o = m3.Manifold.cube((sx, sy_, sz), center=True)
        inn = m3.Manifold.cube((sx - WALL, sy_ - 2 * WALL, sz - 2 * WALL), center=True).translate((WALL / 2, 0, 0))
        out[nm] = tm((o - inn).translate(tuple(c)))
    return out


def build_all():
    """returns {name: trimesh} in CHASSIS mm."""
    s = SCALE
    def X(p):  # sheet (x,y,z) -> chassis
        return np.array([NOSE_X - p[0] * s, p[1] * s, Z_BELLY + p[2] * s])
    res = {}
    P = panels()
    for name, d in P.items():
        tris = d["tris"]
        ins = X(d["inside"])
        solids = []
        edges = {}
        key = lambda p: tuple(np.round(p, 3))
        info = []
        for tri in tris:
            p = [X(q) for q in tri]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            if np.linalg.norm(n) < 1e-6: continue
            n /= np.linalg.norm(n)
            if n @ (np.mean(p, 0) - ins) < 0: n = -n           # outward
            info.append((p, n))
            hull = np.array(p + [q - n * WALL for q in p])
            solids.append(man(trimesh.convex.convex_hull(hull)))
            for a, b_ in ((0, 1), (1, 2), (2, 0)):
                edges.setdefault(frozenset((key(p[a]), key(p[b_]))), []).append((p[a], p[b_], n))
        for e, lst in edges.items():
            if len(lst) == 2:
                (a, b_, n1), (_, _, n2) = lst
                pts = np.array([a, b_, a - n1 * WALL, b_ - n1 * WALL, a - n2 * WALL, b_ - n2 * WALL])
                solids.append(man(trimesh.convex.convex_hull(pts)))
        M = m3.Manifold.batch_boolean(solids, m3.OpType.Add)
        res[name] = M
    res = {k: tm(v) for k, v in res.items()}
    res.update(frames(X))
    return openings(res, X)


def openings(res, X):
    """grille slots (P1) and the four vent slots (P9); roof / cockpit / lights openings are built into the frames."""
    # grille: 5 horizontal slots through the fascia, between z 11 and 33 (sheet), y +-17
    cuts = []
    for k in range(5):
        z = 12 + k * 4.6
        a, b = X((0, -17, z)), X((14, 17, z + 2.6))
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        cuts.append(m3.Manifold.cube(tuple(hi - lo), center=False).translate(tuple(lo)))
    g = man(res["P1"]) - m3.Manifold.batch_boolean(cuts, m3.OpType.Add)
    res["P1"] = tm(g)
    # P9 vents: two centre slots and two diagonal side slots
    v = []
    for cx, cy, lx, ly, ang in ((214, 0, 6, 22, 0), (230, 0, 6, 22, 0), (222, 25, 5, 18, 35), (222, -25, 5, 18, -35)):
        c = X((cx, cy, 90))
        box_ = m3.Manifold.cube((lx * SCALE, ly * SCALE, 30), center=True).rotate((0, 0, ang)).translate((c[0], c[1], c[2]))
        v.append(box_)
    res["P9"] = tm(man(res["P9"]) - m3.Manifold.batch_boolean(v, m3.OpType.Add))
    return res


if __name__ == "__main__":
    R = build_all()
    for k, t in R.items():
        print(k, len(t.faces), t.is_watertight, round(abs(t.volume), 0), t.bounds.round(0).tolist())
