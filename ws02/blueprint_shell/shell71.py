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
    h0 = gt                                                                      # shares the grille's top edge
    h1 = [(10, -36, 47), (10, -14, 52), (10, 14, 52), (10, 36, 47)]              # through the headlight wing's ridge vertex
    h2 = [(26, -46, 52), (26, -18, 56), (26, 18, 56), (26, 46, 52)]              # fender tip (wing / P2 top corner)
    h3 = [(44, -45, 58), (44, -22, 59), (44, 22, 59), (44, 45, 58)]              # P2 top row
    h4 = [(62, -42, 60), (62, -26, 61), (62, 26, 61), (62, 42, 60)]              # P2 end = windshield frame base
    P["P3"] = dict(tris=strip([h0, h1, h2, h3, h4]), inside=(34, 0, 20))
    # ---- P8 side panels
    t = [(62, 40, 46), (96, 41, 44), (130, 43, 54), (160, 46, 62), (194, 50, 67)]
    m_ = [(62, 46, 24), (96, 48, 26), (130, 50, 30), (152, 53, 36), (194, 58, 58)]
    b = [(62, 42, 2), (96, 44, 2), (130, 46, 2), (150, 50, 4), (194, 54, 46)]
    P8L_t = strip([t, m_, b])
    P8R_t = strip(mirror_pts([t, m_, b]))
    # ---- P6 roof panel (rear part of the roof, ridge in the middle)
    q0 = [(176, -37, 95), (176, -15, 100), (176, 15, 100), (176, 37, 95)]
    q1 = [(198, -37, 94), (198, -15, 99), (198, 15, 99), (198, 37, 94)]
    q2 = [(222, -36, 91), (222, -14, 95), (222, 14, 95), (222, 36, 91)]
    P["P6"] = dict(tris=strip([q0, q1, q2]), inside=(198, 0, 60))
    # ---- P10 rear side covers: first column = P8's last column (one object with P8); P9 pitches down to P10's top row
    c_t = [(194, 50, 67), (215, 50, 80), (242, 50, 82), (268, 40, 80)]
    c_m = [(194, 58, 58), (215, 58, 62), (242, 56, 64), (268, 42, 70)]
    c_b = [(194, 54, 46), (218, 52, 44), (244, 50, 48), (264, 38, 56)]
    P10L_t = strip([c_t, c_m, c_b])
    P10R_t = strip(mirror_pts([c_t, c_m, c_b]))
    P["P8P10L"] = dict(tris=P8L_t + P10L_t, inside=(190, 20, 40))
    P["P8P10R"] = dict(tris=P8R_t + P10R_t, inside=(190, -20, 40))
    # ---- P9 rear upper cover: ridge down the middle, flanks drop to P10's top edge (rows at P10's columns)
    d0 = [(194, -50, 67), (194, -18, 90), (194, 18, 90), (194, 50, 67)]
    d1 = [(215, -50, 80), (215, -16, 92), (215, 16, 92), (215, 50, 80)]
    d2 = [(242, -50, 82), (242, -15, 91), (242, 15, 91), (242, 50, 82)]
    d3 = [(268, -40, 80), (268, -13, 85), (268, 13, 85), (268, 40, 80)]
    d4 = [(277, -30, 78), (277, -12, 82), (277, 12, 82), (277, 30, 78)]
    P["P9"] = dict(tris=strip([d0, d1, d2, d3, d4]), inside=(240, 0, 40))
    # ---- P11 rear lower diffuser = the rear tunnel (open belly), front to back: ceiling with a fold at mid length, outer cheeks that meet the P10 covers, inner walls
    # (flat pattern: centre rectangle + two kite wings folded down; tabs 3/3 on P9, 8 on the rear lip, 0/1/9 on P10).  Stations x: rake rises 46 -> 76.
    st = [(198, 46), (222, 56), (242, 66), (260, 70), (276, 73)]
    ceil = [[(x, -41, zc + 4), (x, -29, zc + 2), (x, -17, zc), (x, -6, zc + 2.5), (x, 6, zc + 2.5), (x, 17, zc), (x, 29, zc + 2), (x, 41, zc + 4)] for x, zc in st]
    wallL = [[(x, 29, zc + 2), (x, 28, 36)] for x, zc in st]
    wallR = [[(x, -29, zc + 2), (x, -28, 36)] for x, zc in st]
    P["P11"] = dict(tris=strip(ceil) + strip(wallL) + strip(wallR), inside=(240, 0, 100), toward=True)
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


def ray_hit(meshes, o, d):
    """first hit of the ray o + t d (t > 0) on any of the meshes (Moller-Trumbore); returns (t, unit normal facing the ray origin)."""
    best = (np.inf, None)
    d = np.asarray(d, float) / np.linalg.norm(d)
    for m in meshes:
        tri = m.vertices[m.faces]
        e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
        pv = np.cross(d, e2)
        det = np.einsum("ij,ij->i", e1, pv)
        ok = np.abs(det) > 1e-9
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        tv = o - tri[:, 0]
        u = np.einsum("ij,ij->i", tv, pv) * inv
        qv = np.cross(tv, e1)
        v = (qv @ d) * inv
        t = np.einsum("ij,ij->i", e2, qv) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.5)
        if hit.any():
            k = np.argmin(np.where(hit, t, np.inf))
            if t[k] < best[0]:
                n = np.cross(e1[k], e2[k]); n /= np.linalg.norm(n)
                best = (t[k], n if n @ d < 0 else -n)
    return best


def cube_hull(points_w):
    pts = []
    for p_, w_ in points_w:
        for dx in (-w_ / 2, w_ / 2):
            for dy in (-w_ / 2, w_ / 2):
                for dz in (-w_ / 2, w_ / 2): pts.append(np.add(p_, (dx, dy, dz)))
    return trimesh.convex.convex_hull(np.array(pts))


def plop(top, aim, w, skin, flare=1.9, rise=1.2, bury=1.6, depth_in=4.0, hit=None):
    """pillar from `top` towards `aim`, ended where it meets the skin: the leg runs on `depth_in` into the wall (no end face above the skin), and a collar
    (hull of the leg's section 10 mm above the skin and a pad lying in the skin plane, rim `rise` above it and `bury` into the wall) blends it onto the surface."""
    top, aim = np.asarray(top, float), np.asarray(aim, float)
    d = (aim - top) / np.linalg.norm(aim - top)
    if hit is not None:                                   # explicit contact point and surface normal (pillar lands on the flank's top edge strip)
        H, n = np.asarray(hit[0], float), np.asarray(hit[1], float)
        d = (H - top) / np.linalg.norm(H - top)
        if n @ d > 0: n = -n
    else:
        t, n = ray_hit(skin, top, d)
        if n is None: raise RuntimeError("pillar does not meet the skin")
        H = top + d * t
    leg = man(cube_hull([(top, w), (H + d * 2 * w, w * flare)])).trim_by_plane(tuple(n), float(n @ H) - 1.0)      # one flared taper, cut by the skin plane: it widens into the surface, no end face outside the skin
    u = d - n * (d @ n); u /= np.linalg.norm(u); v = np.cross(n, u)
    pad = []
    for su, sv, hz in ((-1, -1, rise), (1, -1, rise), (1, 1, rise), (-1, 1, rise), (-1.35, -1.25, -bury), (1.35, -1.25, -bury), (1.35, 1.25, -bury), (-1.35, 1.25, -bury)):
        pad.append(H + u * su * w * flare / 2 + v * sv * w * flare / 2 + n * hz)
    ring = [H - d * 10.0 + a_ * (w / 2) * sa + b_ * (w / 2) * sb for a_, b_ in [(np.cross(d, [0, 0, 1]) / np.linalg.norm(np.cross(d, [0, 0, 1])), None)] for sa in (-1, 1) for sb in (0,)] if False else None
    a1 = np.cross(d, [0.0, 0.0, 1.0]); a1 /= np.linalg.norm(a1); a2 = np.cross(d, a1)
    ringp = [H - d * 10.0 + a1 * sa * w / 2 + a2 * sb * w / 2 for sa in (-1, 1) for sb in (-1, 1)]
    collar = trimesh.convex.convex_hull(np.array(pad[:4] + ringp))
    padsolid = trimesh.convex.convex_hull(np.array(pad))
    return [leg]


def frames(X, res=None):
    """P4 windshield frame, P5 roof frame (+ B-pillars), P7 roof lights; returns {name: trimesh} in chassis mm."""
    out = {}
    def sq(pts): return [X(p) for p in pts]
    w = 7.0
    # P4 sloped ring: bottom edge x 64 z 60 (y +-40), top edge x 112 z 86 (y +-34)
    ob = [(62, -42, 60), (62, 42, 60), (112, 34, 86), (112, -34, 86)]
    ib = [(68, -42 + w, 62.5), (68, 42 - w, 62.5), (106, 34 - w, 83.5), (106, -34 + w, 83.5)]
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
    # crease joint: hull over the shared edge (x 165) of both plates, top and underside, so the two plates are one body without a wedge underneath
    def nrm(o):
        q = [X(p_) for p_ in o]; n_ = np.cross(q[1] - q[0], q[2] - q[1]); n_ /= np.linalg.norm(n_); return -n_ if n_[2] < 0 else n_
    nf, nr_ = nrm(ofr), nrm(orr)
    e = [X((165, -38, 97)), X((165, 38, 97))]
    jp = []
    for ee in e: jp += [ee, ee - nf * FRAME_DEPTH, ee - nr_ * FRAME_DEPTH]
    parts.append(man(trimesh.convex.convex_hull(np.array(jp))))
    wb = 6.0 * SCALE
    skin = [res["P8P10L"], res["P8P10R"], res["P9"]]
    for sy in (1, -1):
        # B pillar and rear pillar run into the skin and are blended onto it by a collar + pad (no flat end face standing on the surface)
        p1, p2 = X((160, sy * 46, 62)), X((160, sy * 54, 40))
        nb = np.cross([1.0, 0, 0], p2 - p1); nb /= np.linalg.norm(nb)
        if nb @ np.array([0, sy, 1.0]) < 0: nb = -nb
        Hb = X((160, sy * 48, 56.5))
        leg = man(cube_hull([(X((160, sy * 34, z_f(160) - 3.0)), wb), (X((160, sy * 49, 48)), wb * 1.5)]))
        parts.append(leg.trim_by_plane(tuple(-nb), float(-(nb @ Hb) - 0.2)))        # B pillar comes out from behind the flank's top edge, clipped to the skin's outer plane
        parts += plop(X((178, sy * 35, z_r(178) - 3.0)), X((199, sy * 54, 60)), wb, skin)
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
            if d.get("toward"):                                  # tunnel panel: the visible (outer) face looks into the tunnel, the wall grows outwards from it
                c = np.mean(p, 0)
                if n @ (X((0, 0, 0)) * 0 + np.array([c[0], 0.0, Z_BELLY + 15 * s]) - c) < 0: n = -n
            elif n @ (np.mean(p, 0) - ins) < 0: n = -n           # outward
            info.append((p, n))
            hull = np.array(p + [q - n * WALL for q in p])
            solids.append(man(trimesh.convex.convex_hull(hull)))
            for a, b_ in ((0, 1), (1, 2), (2, 0)):
                edges.setdefault(frozenset((key(p[a]), key(p[b_]))), []).append((p[a], p[b_], n))
        for e, lst in edges.items():
            for i1 in range(len(lst)):
                for i2 in range(i1 + 1, len(lst)):            # a crease shared by 3 facets (ceiling / cheek / wall) is joined pairwise
                    (a, b_, n1), (_, _, n2) = lst[i1], lst[i2]
                    pts = np.array([a, b_, a - n1 * WALL, b_ - n1 * WALL, a - n2 * WALL, b_ - n2 * WALL])
                    solids.append(man(trimesh.convex.convex_hull(pts)))
        M = m3.Manifold.batch_boolean(solids, m3.OpType.Add)
        res[name] = M
    res = {k: tm(v) for k, v in res.items()}
    res.update(frames(X, res))
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
    vv = []
    for cy in (-11, 11):
        c = X((252, cy, 72))
        vv.append(m3.Manifold.cube((12 * SCALE, 5 * SCALE, 30), center=True).translate((c[0], c[1], c[2])))
    # the tunnel ends on a flat plane z = 56 (just above the top of the rear swing envelope z <= 52): the front, still low, part of the ceiling and the wall feet fall away
    # in one clean planar cut instead of a tangent cut along the swing channel
    low = m3.Manifold.cube((600, 600, 200), center=True).translate((0, 0, 56 - 100))
    P11 = (man(res["P11"]) - m3.Manifold.batch_boolean(vv, m3.OpType.Add)) - low
    parts = tm(P11).split(only_watertight=False)
    parts = [q for q in parts if abs(q.volume) > 500]
    res["P11"] = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
    return res


if __name__ == "__main__":
    R = build_all()
    for k, t in R.items():
        print(k, len(t.faces), t.is_watertight, round(abs(t.volume), 0), t.bounds.round(0).tolist())
