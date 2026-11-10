"""WS-03 skin from the user's hand-edited SolidCraft file (WS03_graft_v3_after.sc), hollowed and fitted to the cage.

Source (skin_src/*.stl, millimetres, skin frame: x forward, y left, z up; exported from the .sc bodies FrontShell, RearShell, RearCabin and the
mesh bodies pods / spoiler / roof rack; the .sc stores them 1000x too large, one unit there = 0.001 mm):
  user_Front.stl  solid  (nose, hood, windscreen)        x   0 .. 181.4
  user_Cab.stl    hollow tunnel with a 1.6 mm rear bulkhead, open belly and open front   x -57.5 .. 0.5
  user_Rear.stl   solid  (rear deck, hatch pocket, tail) x -181 .. -57.5  (its front cap is missing in the export: capped here)
  acc_g4/g5 pods, acc_g7 roof rack, acc_g6 spoiler: small solid parts, kept solid (thinner than 2 x 2.4 mm walls)

Build: Front and Rear are hollowed with a uniform 2.4 mm inward wall (skin_hollow.py: vertex plane intersections, so the outer surface and its creases
are untouched), the belly and the joint ends are opened by sweeping the cavity out, places thinner than 2 x 2.4 mm stay solid.  The cab keeps its own wall.
Pieces are then moved into the chassis frame (POSE) and exported as out/mono3/body3_{front,mid,rear}.stl and the welded out/mono3/body3.stl.
"""
import os
import numpy as np
import trimesh
import manifold3d as m3

import skin_hollow as SH

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skin_src")
CACHE = os.path.join(SRC, "cache")
WALL = 2.4
XOFF, ZOFF = -148.4, 19.0                       # skin frame -> chassis frame (nose tip at x +33, 3.6 mm ahead of the cage's bumper bar, belly line on the deck's underside)
JOINTS = (0.0, -57.5)                           # skin-frame x of the two joints (front|cab, cab|rear)


def man(t):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def tm(M):
    me = M.to_mesh()
    return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3].astype(float), np.asarray(me.tri_verts), process=False)


def load(name):
    t = trimesh.load(os.path.join(SRC, name))
    t.merge_vertices()
    return t


def hollow_pieces(force=False):
    """Hollow Front and Rear (skin frame).  Cached in skin_src/cache (a minute of boolean work)."""
    os.makedirs(CACHE, exist_ok=True)
    out = {}
    for name, src, dirs in (("front", "user_Front.stl", [(0, 0, -1), (-1, 0, 0)]), ("rear", "user_Rear_capped.stl", [(0, 0, -1), (1, 0, 0), (-1, 0, 0)])):
        f = os.path.join(CACHE, f"hollow_{name}.stl")
        if os.path.exists(f) and not force:
            out[name] = trimesh.load(f)
            continue
        H, cav = SH.open_shell(load(src), dirs, WALL)
        H = unpinch(H)
        H.vertices = np.asarray(H.vertices, np.float32).astype(np.float64)
        H.merge_vertices()
        H.export(f)
        cav.export(os.path.join(CACHE, f"cavity_{name}.stl"))
        out[name] = H
    return out


def cab_open():
    """The user's cab tunnel with its rear bulkhead opened: a window as big as the rear cavity's front opening (and the lower band below it), a 5 mm frame stays."""
    from shapely.geometry import Polygon, box
    cab = man(load("user_Cab.stl"))
    rear_cap = Polygon([(57, 73.242), (-57, 73.242), (-75, 38), (-81.742, -6.787), (-78.335, -17), (78.335, -17), (81.742, -6.787), (75, 38)])
    win = rear_cap.buffer(-(WALL + 2.6), join_style=2).union(box(-72, -60, 72, -9.0))
    from shapely.geometry.polygon import orient
    pts = list(orient(win, 1.0).exterior.coords)[:-1]
    cs = m3.CrossSection([[(float(y), float(z)) for y, z in pts]])
    prism = m3.Manifold.extrude(cs, 3.6).rotate((90.0, 0.0, 90.0)).translate((-57.5 - 0.8, 0, 0))      # extrude along z, then to x: (y,z) plane
    return tm(cab - prism)


TAIL_X1 = -321.0          # skin-frame x of the tail cover's rear end (chassis -469): over the rear tyre (x -394 .. -506)
TAIL_P0 = [(62.0, 36.0), (61.5, 30.0), (60.0, 24.0), (-60.0, 24.0), (-61.5, 30.0), (-62.0, 36.0), (-38.0, 44.0), (38.0, 44.0)]      # (y, z) of the user's tail face at x -181
TAIL_P1 = [(-28.0, 31.0), (28.0, 31.0), (44.0, 15.0), (44.0, -14.0), (32.0, -20.0), (-32.0, -20.0), (-44.0, -14.0), (-44.0, 15.0)]    # (y, z) over the wheel, skin frame


def tail_cover():
    """Added at the user's request: the shell is carried back over the top of the rear wheel and down the sides as skirts that end at the rear swing arm.
    Convex hull of the user's tail face and a smaller face over the tyre (planar facets), hollowed like the other pieces; the tyre / arm travel arch and the swing
    channels are cut later in fit().  Joint to the rear piece: plain rim + dowels."""
    pts = [(-181.0, y, z) for y, z in TAIL_P0] + [(TAIL_X1, y, z) for y, z in TAIL_P1]
    solid = trimesh.convex_hull.convex_hull(np.array(pts)) if hasattr(trimesh, "convex_hull") else trimesh.Trimesh(np.array(pts)).convex_hull
    solid.merge_vertices()
    f = os.path.join(CACHE, "hollow_tail.stl")
    if os.path.exists(f):
        return trimesh.load(f)
    H, cav = SH.open_shell(solid, [(0, 0, -1), (1, 0, 0)], WALL)
    H = unpinch(H)
    H.vertices = np.asarray(H.vertices, np.float32).astype(np.float64)
    H.merge_vertices()
    H.export(f)
    return H


def accessories():
    return {k: load(f"acc_{k}.stl") for k in ("g4", "g5", "g6", "g7")}


def skin_frame_pieces(force=False):
    """front / mid / rear in the skin frame, accessories merged in, the two small pods cut out of the front where they overlap it."""
    hp = hollow_pieces(force)
    acc = accessories()
    front, mid, rear = man(hp["front"]), man(cab_open()), man(hp["rear"])
    pods = man(acc["g4"]) + man(acc["g5"])
    front = front - pods
    mid = mid + pods                                                  # roof rack (g7) removed at the user's request
    posts = None
    for sy in (-44.0, 44.0):                                       # the spoiler's two legs end 1.3 mm above the deck: posts into the deck wall make it one piece
        c = m3.Manifold.cylinder(6.2, 2.3, 2.3, 24).translate((-165.7, sy, 43.1))
        posts = c if posts is None else posts + c
    # spoiler (g6) and its posts removed at the user's request (the old rear wing is off as well)
    return {"front": tm(front), "mid": tm(mid), "rear": tm(rear)}


def unpinch(t, eps=0.006):
    """Boolean results can hold two sheets that touch along an edge or at a point: the Manifold keeps them as distinct vertices at the same position, an STL (and a
    slicer) welds them into a non-manifold edge.  Every vertex that shares its position with another is nudged by eps (6 microns) along its own vertex normal, which opens
    the touching sheets."""
    V = np.asarray(t.vertices, float).copy()
    from scipy.spatial import cKDTree
    pr = np.array(sorted(cKDTree(V).query_pairs(5e-4)))
    dup = np.zeros(len(V), bool)
    if len(pr):
        dup[pr[:, 0]] = True
        dup[pr[:, 1]] = True
    if dup.any():
        vn = t.vertex_normals
        V[dup] += eps * vn[dup]
    return trimesh.Trimesh(V, t.faces, process=False)


def split_pinches(t, eps=0.004):
    """Repair what is left of non-manifold (touching-sheet) vertices on a welded mesh: the faces round a vertex are grouped into fans (through manifold edges; the 4 faces of a
    non-manifold edge are paired by smallest turning angle), every fan beyond the first gets its own copy of the vertex, nudged by eps along the fan's normal."""
    F = np.asarray(t.faces).copy()
    V = np.asarray(t.vertices, float).copy()
    e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
    uniq, inv, cnt = np.unique(e, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    bad_e = np.where(cnt > 2)[0]
    if len(bad_e) == 0:
        return t
    fidx = np.tile(np.arange(len(F)), 3)
    fn = t.face_normals
    # faces per edge
    fe = {}
    for k in range(len(inv)):
        fe.setdefault(inv[k], []).append(fidx[k])
    badv = set(uniq[bad_e].ravel().tolist())
    new_V = []
    for v in badv:
        fs = np.where((F == v).any(axis=1))[0]
        parent = {int(f): int(f) for f in fs}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for f in fs:                                              # edges at v
            for j in range(3):
                a, b = F[f][j], F[f][(j + 1) % 3]
                if v not in (a, b):
                    continue
                ei = inv[np.where((fidx == f))[0][j]] if False else None
        edges_v = {}
        for f in fs:
            tri = F[f]
            for j in range(3):
                a, b = int(tri[j]), int(tri[(j + 1) % 3])
                if v in (a, b):
                    key = (min(a, b), max(a, b))
                    edges_v.setdefault(key, []).append((int(f), (a, b)))
        for key, lst in edges_v.items():
            if len(lst) == 2:
                parent[find(lst[0][0])] = find(lst[1][0])
            elif len(lst) > 2:
                fw = [x for x in lst if x[1] == key]
                bw = [x for x in lst if x[1] != key]
                used = set()
                for x in fw:                                       # pair each forward face with the backward face of the smallest turning angle
                    best, bd = None, 9.0
                    for y in bw:
                        if y[0] in used:
                            continue
                        d = 1.0 - float(fn[x[0]] @ fn[y[0]])
                        if d < bd:
                            best, bd = y, d
                    if best is not None:
                        used.add(best[0])
                        parent[find(x[0])] = find(best[0])
        groups = {}
        for f in fs:
            groups.setdefault(find(int(f)), []).append(int(f))
        if len(groups) < 2:
            continue
        for gi, (root, gf) in enumerate(groups.items()):
            nrm = fn[gf].sum(0)
            nrm = nrm / (np.linalg.norm(nrm) + 1e-12)
            if gi == 0:
                V[v] = V[v] + eps * nrm
                continue
            idx = len(V) + len(new_V)
            new_V.append(V[v] + eps * nrm)
            for f in gf:
                F[f][F[f] == v] = idx
    if new_V:
        V = np.vstack([V, np.array(new_V)])
    return trimesh.Trimesh(V, F, process=False)


def collapse_slivers(t, area=0.002, rounds=4):
    """Collapse needle triangles (area < `area` mm2) onto their shortest edge: they are what a pinched (4-face) edge usually carries."""
    V = np.asarray(t.vertices, float).copy()
    F = np.asarray(t.faces).copy()
    for _ in range(rounds):
        tri = V[F]
        ar = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        bad = np.where(ar < area)[0]
        if len(bad) == 0:
            break
        for f in bad:
            a, b, c = F[f]
            if len({a, b, c}) < 3:
                continue
            es = [(np.linalg.norm(V[a] - V[b]), a, b), (np.linalg.norm(V[b] - V[c]), b, c), (np.linalg.norm(V[c] - V[a]), c, a)]
            _, p_, q_ = min(es)
            F[F == q_] = p_
        keep = np.array([len(set(f)) == 3 for f in F])
        F = F[keep]
    m = trimesh.Trimesh(V, F, process=False)
    m.remove_unreferenced_vertices()
    return m


def heal_pinches(t, rounds=6):
    """For every edge used by more than two faces, collapse the smallest face on it onto its shortest edge (the needle triangle a pinch drags along)."""
    V = np.asarray(t.vertices, float).copy()
    F = np.asarray(t.faces).copy()
    for _ in range(rounds):
        e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
        u, inv, c = np.unique(e, axis=0, return_inverse=True, return_counts=True)
        inv = inv.reshape(-1)
        bad = np.where(c > 2)[0]
        if len(bad) == 0:
            break
        fid = np.tile(np.arange(len(F)), 3)
        tri = V[F]
        ar = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        for bi in bad:
            fs = fid[inv == bi]
            f = fs[np.argmin(ar[fs])]
            a, b, c3 = F[f]
            if len({a, b, c3}) < 3:
                continue
            es = [(np.linalg.norm(V[a] - V[b]), a, b), (np.linalg.norm(V[b] - V[c3]), b, c3), (np.linalg.norm(V[c3] - V[a]), c3, a)]
            _, p_, q_ = min(es)
            F[F == q_] = p_
        F = F[np.array([len(set(f)) == 3 for f in F])]
    m = trimesh.Trimesh(V, F, process=False)
    m.remove_unreferenced_vertices()
    return m


def to_chassis(t):
    t = t.copy()
    t.apply_translation((XOFF, 0.0, ZOFF))
    return t


FRONT_MOVERS = ("arm_", "pod_", "uplink_", "tip_shaft_", "tie_rod_", "mock_fbelt_", "mock_fpulley_tip_", "diff_out_", "carrier_", "knuckle_", "steer_horn_")


def arm_slot(pcs, margin=2.0, step=3.0):
    """Slot polygon (x, z) and y band for the front mechanism: for every lean / steer pose the parts of the front mechanism are intersected with the skin, the
    pierce points of consecutive poses are joined by convex hulls (so the sweep between poses is covered), grown by `margin` and simplified to an angular
    polygon.  Cached as out/mono3/arm_slot.json: {"poly": [[x,z]..], "y": [y0, y1]}."""
    import json
    import w3_assembly as A
    from shapely.geometry import MultiPoint, box
    from shapely.ops import unary_union
    f = "out/mono3/arm_slot.json"
    if os.path.exists(f) and os.environ.get("WS03_REWINDOW") != "1":
        return json.load(open(f))
    skin = man(pcs["front"]) + man(pcs["mid"])
    per_pose = []
    ys = []
    for lean in np.arange(-20.0, 20.01, step):
        for steer in (-17.0, 0.0, 17.0):
            movers = [man(m) for n, m, k in A.assembly(float(lean), steer=steer) if n.startswith(FRONT_MOVERS) and m.bounds[0][0] < 40.0]
            I = m3.Manifold.batch_boolean(movers, m3.OpType.Add) ^ skin
            if I.volume() > 0.01:
                v = np.asarray(I.to_mesh().vert_properties)[:, :3]
                v = v[v[:, 1] > 0.0]                                   # one side: the car is mirror-symmetric
                per_pose.append(v)
                ys.append((v[:, 1].min(), v[:, 1].max()))
    hulls = []
    for k in range(len(per_pose)):
        pts = per_pose[k][:, [0, 2]]
        hulls.append(MultiPoint(pts).convex_hull)
        for dk in (1, 3):                                              # next lean step (same steer) and the other steers
            if k + dk < len(per_pose):
                hulls.append(MultiPoint(np.vstack([pts, per_pose[k + dk][:, [0, 2]]])).convex_hull)
    u = unary_union(hulls).buffer(margin, join_style=2)
    u = u.convex_hull if u.geom_type != "Polygon" else u
    u = u.simplify(2.5)
    x0, z0, x1, z1 = u.bounds
    belly = ZOFF - 48.0
    if z0 < belly + 12.0:                                              # the slot reaches (nearly) the rim: open it down to a wheel arch
        u = unary_union([u, box(x0, belly - 5.0, x1, z0 + 1.0)]).convex_hull.simplify(1.0)
    out = {"poly": [[float(a), float(b)] for a, b in list(u.exterior.coords)[:-1]], "y": [float(min(a for a, b in ys)) - 2.0, float(max(b for a, b in ys)) + 2.0]}
    json.dump(out, open(f, "w"))
    return out


JOINT_X = (XOFF - 57.5, XOFF - 115.0)     # front|mid, mid|rear, rear|tail (chassis x): front runs to the old end of the cab, mid moved back 57.5 mm
PIN_D, SOCKET_D, SOCKET_L, BOSS_R = 3.0, 3.2, 7.0, 3.6          # steel dowel pins 3 x 12 mm at the joints, 3.2 mm sockets 7 mm deep, 7.2 mm bosses


def joints(mans, pcs):
    """Dowel pins at the two joints (front|cab and cab|rear): four 7.2 mm bosses per joint on the inside of the wall (two under the roof, two on the flanks),
    each drilled 3.2 mm x 7 mm from the joint plane on both sides, so a 3 x 12 mm pin aligns the pieces (CA glue or M2 later)."""
    W = _noacc()
    out = {k: v for k, v in mans.items()}
    plan = [(x, "all", "all") for x in JOINT_X]
    for xj, a, b in plan:                                               # a is the piece at x > xj, b at x < xj
        spots = []
        yr = 26.0 if abs(xj - JOINT_X[1]) < 1 else 38.0            # at the mid|rear joint the roof rails run at y 38..54 and 8: bosses between them
        for y in (-yr, yr):
            h = W.ray.intersects_location([[xj, y, 300.0]], [[0, 0, -1.0]])[0]
            z = np.sort(h[:, 2])[::-1]
            zin = z[1] if len(z) > 1 else z[0]
            spots.append((y, zin - 2.6))
        for sg in (-1, 1):
            zf = ZOFF - 48.0 + 40.0
            h = W.ray.intersects_location([[xj, 0.0, zf]], [[0, float(sg), 0]])[0]
            if len(h):
                spots.append((float(sg * np.min(np.abs(h[:, 1]))) - sg * 3.0 + sg * 0.0, zf))
        for (y, z) in spots:
            cyl = m3.Manifold.cylinder(14.0, BOSS_R, BOSS_R, 24).rotate((0.0, 90.0, 0.0)).translate((xj - 7.0, y, z))
            half_a = m3.Manifold.cube((40.0, 40.0, 40.0), center=True).translate((xj + 20.0, y, z))
            half_b = m3.Manifold.cube((40.0, 40.0, 40.0), center=True).translate((xj - 20.0, y, z))
            sock = m3.Manifold.cylinder(2 * SOCKET_L, SOCKET_D / 2, SOCKET_D / 2, 24).rotate((0.0, 90.0, 0.0)).translate((xj - SOCKET_L, y, z))
            out[a] = (out[a] + (cyl ^ half_a)) - sock
            out[b] = (out[b] + (cyl ^ half_b)) - sock
    return out


def fit(pcs):
    """Cuts and additions that tie the skin to the cage (all in the chassis frame): arm windows, tube relief + swing channels + rear wheel arch (the skin opens
    on its nose pin), hinge ears, magnet bosses.  Returns the three pieces."""
    import parts.w3_frame as FR
    import mono_build as MB
    import w3_swing as SW
    from shapely.geometry.polygon import orient
    from shapely.geometry import Polygon
    mans = {k: man(v) for k, v in pcs.items()}
    slot = arm_slot(pcs)
    sp = list(orient(Polygon(slot["poly"]), 1.0).exterior.coords)[:-1]
    for s_ in (1, -1):
        y0, y1 = (slot["y"][0], 120.0) if s_ > 0 else (-120.0, -slot["y"][0])
        mans["front"] = mans["front"] - MB.prism_xz(sp, y0, y1)
    # hinge ears on the roof's underside at the nose pin
    zt = top_z(FR.HINGE_PIN[0], WALL, ys=(0.0, 8.0, 16.0)) + 0.4
    for s_ in (1, -1):
        y0, y1 = (FR.HINGE_EAR[0], FR.HINGE_EAR[1]) if s_ > 0 else (-FR.HINGE_EAR[1], -FR.HINGE_EAR[0])
        ear = m3.Manifold.cube((FR.HINGE[0][1] - FR.HINGE[0][0], y1 - y0, zt - FR.HINGE_PIN[1] + 10.0), center=False).translate((FR.HINGE[0][0], y0, FR.HINGE_PIN[1] - 10.0))
        mans["front"] = mans["front"] + ear - m3.Manifold.cylinder(8.0, FR.HINGE_D / 2, FR.HINGE_D / 2, 24).rotate((-90.0, 0.0, 0.0)).translate((FR.HINGE_PIN[0], s_ * 0.5 * (FR.HINGE_EAR[0] + FR.HINGE_EAR[1]) - 4.0, FR.HINGE_PIN[1]))
    # magnet bosses over the frame's tab pads
    for (tx, ty, tz, _br) in FR.tab_stations():
        for s_ in (1, -1):
            piece = "front" if tx > XOFF else ("mid" if tx > XOFF - 57.5 else "rear")
            zb = tz + FR.TAB_BOSS
            ztop = top_z(tx, WALL) + 0.6
            mans[piece] = mans[piece] + m3.Manifold.cylinder(ztop - zb, 4.5, 4.5, 32).translate((tx, s_ * ty, zb))
            mans[piece] = mans[piece] - m3.Manifold.cylinder(2.2, FR.MAG_D / 2, FR.MAG_D / 2, 32).translate((tx, s_ * ty, zb + 0.0))
    rel = FR.relief()
    env = SW.rear_travel_channels()
    ch = SW.swing_channels().translate((0.0071, 0.0043, -0.0059))
    for k in mans:
        # (the swing channels below already contain the grown tubes and pads at rest: no separate relief cut, whose surfaces would coincide with theirs)
        mans[k] = mans[k] - env.translate((0.0037, 0.0029, -0.0011))
        mans[k] = mans[k] - ch
    return {k: tm(v) for k, v in mans.items()}


def main(force=False):
    os.makedirs("out/mono3", exist_ok=True)
    pcs = {k: to_chassis(t) for k, t in skin_frame_pieces(force).items()}
    for k, t in pcs.items():                                   # first pass: the unfitted pieces, so the assembly-based scans below see a skin
        t.export(f"out/mono3/body3_{k}.stl")
    pcs = fit(pcs)
    w = None
    for k, t in pcs.items():
        w = man(t) if w is None else w + man(t)
    w = joints({"all": w}, pcs)["all"]
    w = w - pocket_opening()
    w = unpinch(tm(w))
    w.vertices = np.asarray(w.vertices, np.float32).astype(np.float64)
    w.merge_vertices()
    w.export("out/mono3/body3.stl")
    print("body3", len(w.faces), w.is_watertight, round(abs(w.volume) / 1e3, 1), "cm3")


def pocket_opening(inset=1.5, zmin=40.0):
    """Opens the user's hatch pocket in the rear deck: its floor footprint (found on the unmodified hollow skin: columns whose top is >8 mm below the deck beside
    them) is cut through, the pocket walls stay."""
    from shapely.geometry import MultiPoint
    from shapely.geometry.polygon import orient
    t = _noacc()
    pts = []
    for x in np.arange(-312.0, -228.0, 2.0):
        for y in np.arange(-48.0, 48.1, 2.0):
            h = t.ray.intersects_location([[x, y, 300.0]], [[0, 0, -1.0]])[0]
            hs = t.ray.intersects_location([[x, 62.0, 300.0]], [[0, 0, -1.0]])[0]
            if len(h) and len(hs) and h[:, 2].max() < hs[:, 2].max() - 8.0:
                pts.append((x, y))
    poly = orient(MultiPoint(pts).convex_hull.buffer(-inset, join_style=2), 1.0)
    cs = m3.CrossSection([[(float(a), float(b)) for a, b in list(poly.exterior.coords)[:-1]]])
    return m3.Manifold.extrude(cs, 120.0).translate((0, 0, zmin))


# ---------------------------------------------------------------- what the cage asks of the skin (body3_build.top_z / hw_in delegate here)
_SK = {}


def _noacc():
    """Welded hollow skin without the roof rack, pods and spoiler, chassis frame (cached)."""
    if "m" not in _SK:
        hp = hollow_pieces()
        parts = [man(hp["front"]), man(cab_open()), man(hp["rear"])]
        w = parts[0] + parts[1] + parts[2]
        t = tm(w)
        t.apply_translation((XOFF, 0.0, ZOFF))
        _SK["m"] = t
    return _SK["m"]


def top_z(x, inset=0.0, fallback=None, ys=(0.0, 12.0, 24.0, 36.0, 48.0)):
    """Roof height at chassis x: lowest over a few y of the outer surface (inset 0) or of the roof's underside (inset > 0).  Falls back to `fallback(x, inset)` off the skin."""
    t = _noacc()
    if not (t.bounds[0][0] + 1.0 < x < t.bounds[1][0] - 1.0):
        return fallback(x, inset) if fallback else 0.0
    zs = []
    for y in ys:
        h = t.ray.intersects_location([[x, y, 400.0]], [[0, 0, -1.0]])[0]
        if len(h) == 0:
            continue
        z = np.sort(h[:, 2])[::-1]
        zs.append(z[0] if inset <= 0.0 or len(z) < 2 else z[1])
    return float(min(zs)) if zs else (fallback(x, inset) if fallback else 0.0)


def hw_in(x, inset=WALL, fallback=None, z=-20.0):
    """Inner half width of the skin at chassis x and height z (the deck level): first wall met going out from the centre line."""
    t = _noacc()
    if not (t.bounds[0][0] + 1.0 < x < t.bounds[1][0] - 1.0):
        return fallback(x, inset) if fallback else 0.0
    h = t.ray.intersects_location([[x, 0.0, z]], [[0, 1.0, 0]])[0]
    return float(np.min(h[:, 1])) if len(h) else (fallback(x, inset) if fallback else 0.0)


if __name__ == "__main__":
    main("--force" in os.sys.argv)
