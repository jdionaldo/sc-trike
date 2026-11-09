"""Panel-skin core (WS-03, branch ws03-panel-skin): explicit planar panels, planarity solve, mitred 2.4 mm slabs.
Frame: x forward, y left, z up (ground z 0). Sheet 68 registration: plan px -> (x, y), side px -> (x, z), both fitted to the user's masks (see WS03_PANEL_SKIN.md).
A Model holds the UPPER (y >= 0) half; mirror() builds the other half (vertices on the centre line are shared)."""
import math
import numpy as np
from scipy.optimize import least_squares

# ---- registration of sheet 68 to the mask frame (nose x 34.3, tail x -356.8, sill z 52.2, roof z 209.3) ----
PX0, X0, KX = 118.5, 34.3, 0.6517          # plan: x = X0 - (px - PX0) * KX      (nose px 118.5, tail px 718.6)
PYC, KY = 210.0, 0.65                      # plan: y = (PYC - py) * KY           (centre line py 210)
SX0, SKX = 112.0, 0.6258                   # side: x = X0 - (px - SX0) * SKX
SZ0, SZR, SKZ = 458.0, 209.3, 0.6546       # side: z = SZR + (SZ0 - py) * SKZ


def plan_xy(px, py):
    return X0 - (px - PX0) * KX, (PYC - py) * KY


def xy_plan(x, y):
    return PX0 + (X0 - x) / KX, PYC - y / KY


def side_xz(px, py):
    return X0 - (px - SX0) * SKX, SZR + (SZ0 - py) * SKZ


def xz_side(x, z):
    return SX0 + (X0 - x) / SKX, SZ0 - (z - SZR) / SKZ


# ---- the model ----
class Model:
    def __init__(self):
        self.tg = {}          # name -> [x, y, z] targets (None = free), upper half
        self.w = {}           # name -> [wx, wy, wz]
        self.panels = []      # dict(name, ids (outward CCW), hint (3,), layer)
        self.pos = {}         # solved positions (upper half)
        self.full = None

    def v(self, name, x=None, y=None, z=None, w=(1.0, 1.0, 1.0)):
        self.tg[name] = [x, y, z]
        self.w[name] = list(w)
        return name

    def vp(self, name, px, py, z=None, w=(1.0, 1.0, 1.0)):
        x, y = plan_xy(px, py)
        return self.v(name, x, y, z, w)

    def panel(self, name, ids, hint, layer="top", kind="plane"):
        ids = [i for k, i in enumerate(ids) if not (k > 0 and ids[k - 1] == i)]
        if len(ids) > 1 and ids[0] == ids[-1]:
            ids = ids[:-1]
        self.panels.append(dict(name=name, ids=list(ids), hint=np.array(hint, float), layer=layer, kind=kind))

    # ---- T junctions: a vertex that lies on another panel's edge is inserted into that panel ----
    def init_pos(self):
        P = {}
        for n, t in self.tg.items():
            P[n] = np.array([0.0 if a is None else a for a in t], float)
        return P

    def tjunctions(self, tol=1.2):
        P = self.init_pos()
        added = []
        for p in self.panels:
            ids = p["ids"]
            k = 0
            while k < len(ids):
                a, b = ids[k], ids[(k + 1) % len(ids)]
                A, B = P[a], P[b]
                d = B - A
                L2 = float(d @ d)
                ins = None
                if L2 > 1e-9:
                    for n, X in P.items():
                        if n in ids:
                            continue
                        t = float((X - A) @ d) / L2
                        if 0.04 < t < 0.96 and np.linalg.norm(A + t * d - X) < tol:
                            if ins is None or t < ins[0]:
                                ins = (t, n)
                if ins:
                    ids.insert(k + 1, ins[1])
                    added.append((p["name"], ins[1], a, b))
                    continue
                k += 1
        self.tj = added
        return added

    # ---- planarity solve ----
    def solve(self, wplan=20.0, wcol=60.0, verbose=False):
        names = sorted(self.tg)
        idx = {n: i for i, n in enumerate(names)}
        X0_ = np.array([self.init_pos()[n] for n in names]).ravel()
        tgt = np.array([[np.nan if a is None else a for a in self.tg[n]] for n in names])
        wt = np.array([self.w[n] for n in names])
        polys = [[idx[i] for i in p["ids"]] for p in self.panels if len(p["ids"]) > 3 and p.get("kind", "plane") == "plane"]
        # collinear triples created by T-junctions
        tri = []
        for p in self.panels:
            ids = p["ids"]
            n = len(ids)
            for k in range(n):
                pass
        # free coordinates start at the mean of the targets of neighbours
        for i, n in enumerate(names):
            for c in range(3):
                if np.isnan(tgt[i, c]):
                    X0_[3 * i + c] = 0.0
        # fill unknown z by averaging neighbours through panels
        known = ~np.isnan(tgt)
        for _ in range(60):
            for p in self.panels:
                ii = [idx[i] for i in p["ids"]]
                for c in range(3):
                    vals = [X0_[3 * i + c] for i in ii if known[i, c]]
                    if vals:
                        for i in ii:
                            if not known[i, c]:
                                X0_[3 * i + c] = float(np.mean(vals))
        tj = [(idx[a], idx[v], idx[b]) for (_, v, a, b) in getattr(self, "tj", [])]

        def res(x):
            P = x.reshape(-1, 3)
            r = []
            d = (P - np.where(np.isnan(tgt), P, tgt)) * wt
            r.append(d.ravel())
            for pl in polys:
                Q = P[pl]
                c = Q.mean(0)
                u, s, vt = np.linalg.svd(Q - c, full_matrices=False)
                r.append(wplan * ((Q - c) @ vt[2]))
            for a, v, b in tj:
                A, B, V = P[a], P[b], P[v]
                d_ = B - A
                r.append(wcol * np.cross(V - A, d_) / max(np.linalg.norm(d_), 1e-6))
            return np.concatenate(r)

        sol = least_squares(res, X0_, method="trf", x_scale=1.0, max_nfev=200, xtol=1e-10, ftol=1e-10)
        for wp in (200.0, 1000.0):                                              # polish: planarity weight up, starting from the previous solution
            wplan = wp
            sol = least_squares(res, sol.x, method="trf", x_scale=1.0, max_nfev=100, xtol=1e-12, ftol=1e-12)
        P = sol.x.reshape(-1, 3)
        self.pos = {n: P[idx[n]].copy() for n in names}
        for n in names:
            if self.tg[n][1] == 0.0:
                self.pos[n][1] = 0.0                                   # centre-line vertices are exactly on y = 0
        if verbose:
            print("solve cost", sol.cost, "nfev", sol.nfev)
        return sol

    def warp_positions(self, fn):
        """Apply a point warp fn(p)->p to every solved vertex, then re-solve planarity with the warped positions as (soft) targets."""
        for n, p in list(self.pos.items()):
            q = fn(p)
            self.tg[n] = [float(q[0]), 0.0 if self.tg[n][1] == 0.0 else float(q[1]), float(q[2])]
            self.w[n] = [3.0, 100.0 if self.tg[n][1] == 0.0 else 3.0, 3.0]
        return self.solve()

    def planarity(self):
        out = []
        for p in self.panels:
            Q = np.array([self.pos[i] for i in p["ids"]])
            if len(Q) > 3:
                c = Q.mean(0)
                n = np.linalg.svd(Q - c)[2][2]
                out.append((float(np.abs((Q - c) @ n).max()), p["name"]))
        return sorted(out, reverse=True)

    # ---- mirror ----
    def mirror(self):
        P = {}
        panels = []
        shared = {n for n, p in self.pos.items() if abs(p[1]) < 1e-6}
        mn = lambda n: n if n in shared else n + "'"
        for n, p in self.pos.items():
            P[n] = p.copy()
            if n not in shared:
                P[n + "'"] = p * np.array([1, -1, 1])
        for p in self.panels:
            panels.append(dict(p))
            q = dict(p)
            q["name"] = p["name"] + "'"
            q["ids"] = [mn(i) for i in reversed(p["ids"])]
            q["hint"] = p["hint"] * np.array([1, -1, 1])
            panels.append(q)
        self.full = (P, panels)
        return P, panels


# ---- geometry helpers ----
def newell(Q):
    n = np.zeros(3)
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]
        n += np.cross(a, b)
    return n


ORIENTED = False


def panel_normal(Q, hint):
    n = newell(Q)
    nn = np.linalg.norm(n)
    n = n / nn if nn > 1e-12 else np.array([0, 0, 1.0])
    if ORIENTED:
        return n
    return n if n @ hint >= 0 else -n


def convex_pieces(Q, n):
    """Split a (near) planar polygon (outward normal n) into convex pieces (index lists) by ear clipping + greedy merge."""
    m = len(Q)
    a = np.cross(n, [1, 0, 0]) if abs(n[0]) < 0.9 else np.cross(n, [0, 1, 0])
    a /= np.linalg.norm(a)
    b = np.cross(n, a)
    UV = np.stack([Q @ a, Q @ b], 1)
    area = 0.5 * sum(UV[i, 0] * UV[(i + 1) % m, 1] - UV[(i + 1) % m, 0] * UV[i, 1] for i in range(m))
    idx = list(range(m)) if area > 0 else list(range(m))[::-1]
    # orientation: panel_normal is outward and the ids are CCW about it by construction, but be safe

    def cross(o, p, q):
        return (UV[p, 0] - UV[o, 0]) * (UV[q, 1] - UV[o, 1]) - (UV[p, 1] - UV[o, 1]) * (UV[q, 0] - UV[o, 0])

    def is_convex(ids):
        if len(ids) < 3:
            return False
        s = [cross(ids[i - 1], ids[i], ids[(i + 1) % len(ids)]) for i in range(len(ids))]
        return all(v > -1e-7 for v in s)

    if is_convex(idx):
        return [idx] if area > 0 else [idx[::-1]]
    tris = []
    ids = idx[:]
    guard = 0
    while len(ids) > 3 and guard < 500:
        guard += 1
        for k in range(len(ids)):
            o, p, q = ids[k - 1], ids[k], ids[(k + 1) % len(ids)]
            if cross(o, p, q) <= 1e-9:
                continue
            ok = True
            for r in ids:
                if r in (o, p, q):
                    continue
                c1, c2, c3 = cross(o, p, r), cross(p, q, r), cross(q, o, r)
                if c1 >= -1e-9 and c2 >= -1e-9 and c3 >= -1e-9:
                    ok = False
                    break
            if ok:
                tris.append([o, p, q])
                ids.pop(k)
                break
        else:
            break
    tris.append(ids)
    pieces = [t[:] for t in tris]

    def try_merge(A, B):
        for ka in range(len(A)):
            u, v = A[ka], A[(ka + 1) % len(A)]
            for kb in range(len(B)):
                if B[kb] == v and B[(kb + 1) % len(B)] == u:
                    Ar = A[(ka + 1) % len(A):] + A[:(ka + 1) % len(A)]          # v ... u
                    Br = B[(kb + 1) % len(B):] + B[:(kb + 1) % len(B)]          # u ... v
                    cand = Ar + Br[1:-1]
                    if is_convex(cand):
                        return cand
        return None

    merged = True
    while merged:
        merged = False
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                c = try_merge(pieces[i], pieces[j])
                if c:
                    pieces[i] = c
                    pieces.pop(j)
                    merged = True
                    break
            if merged:
                break
    return pieces


def ear_triangles(Q, n):
    """Ear clipping of a (near) planar polygon with outward normal n; returns index triples wound CCW about n."""
    m = len(Q)
    a = np.cross(n, [1, 0, 0]) if abs(n[0]) < 0.9 else np.cross(n, [0, 1, 0])
    a /= np.linalg.norm(a)
    b = np.cross(n, a)
    UV = np.stack([Q @ a, Q @ b], 1)
    area = 0.5 * sum(UV[i, 0] * UV[(i + 1) % m, 1] - UV[(i + 1) % m, 0] * UV[i, 1] for i in range(m))
    ids = list(range(m)) if area > 0 else list(range(m))[::-1]

    def cross(o, p, q):
        return (UV[p, 0] - UV[o, 0]) * (UV[q, 1] - UV[o, 1]) - (UV[p, 1] - UV[o, 1]) * (UV[q, 0] - UV[o, 0])
    tris = []
    guard = 0
    while len(ids) > 3 and guard < 1000:
        guard += 1
        best = None
        for k in range(len(ids)):
            o, p, q = ids[k - 1], ids[k], ids[(k + 1) % len(ids)]
            cr = cross(o, p, q)
            if cr <= 1e-9:
                continue
            ok = all(not (cross(o, p, r) >= -1e-9 and cross(p, q, r) >= -1e-9 and cross(q, o, r) >= -1e-9) for r in ids if r not in (o, p, q))
            if ok and (best is None or cr > best[0]):
                best = (cr, k)
        if best is None:
            best = (0, 0)
        k = best[1]
        tris.append((ids[k - 1], ids[k], ids[(k + 1) % len(ids)]))
        ids.pop(k)
    tris.append(tuple(ids))
    return tris if area > 0 else [(t[0], t[2], t[1]) for t in tris] if False else tris


class Slabs:
    """Thicken every panel inward by t with mitred joints (bisector planes through shared creases)."""

    def __init__(self, P, panels, t=2.4):
        self.P, self.t = P, t
        self.items = []                     # (panel name, outer pts (n,3), inner pts (n,3), outward n)
        self.edgeinfo = {}
        pcs = []
        for p in panels:
            Q = np.array([P[i] for i in p["ids"]])
            n = panel_normal(Q, p["hint"])
            for pc in convex_pieces(Q, n):
                ids = [p["ids"][k] for k in pc]
                pcs.append(dict(name=p["name"], ids=ids, n=n, Q=np.array([P[i] for i in ids]), kind=p.get("kind", "plane")))
        self.pcs = pcs
        emap = {}
        for k, pc in enumerate(pcs):
            ids = pc["ids"]
            for e in range(len(ids)):
                emap.setdefault(frozenset((ids[e], ids[(e + 1) % len(ids)])), []).append(k)
        self.emap = emap

    def mitre(self, k, a, b):
        pcs = self.pcs
        pc = pcs[k]
        A, B = self.P[a], self.P[b]
        L = B - A
        L = L / max(np.linalg.norm(L), 1e-12)
        others = [j for j in self.emap[frozenset((a, b))] if j != k]
        n = pc["n"]
        if others:
            nq = pcs[others[0]]["n"]
            bvec = -(n + nq)
            if np.linalg.norm(bvec) < 1e-6:
                bvec = -n
        else:
            bvec = -n
        bvec = bvec / np.linalg.norm(bvec)
        m = np.cross(L, bvec)
        m /= np.linalg.norm(m)
        cen = pc["Q"].mean(0)
        if m @ (cen - A) < 0:
            m = -m
        return m, A

    def build(self):
        out = []
        for k, pc in enumerate(self.pcs):
            ids, n, Q = pc["ids"], pc["n"], pc["Q"]
            inner = []
            ms = [self.mitre(k, ids[e], ids[(e + 1) % len(ids)]) for e in range(len(ids))]
            for i in range(len(ids)):
                m1, a1 = ms[i - 1]
                m2, a2 = ms[i]
                M = np.array([n, m1, m2])
                rhs = np.array([n @ Q[i] - self.t, m1 @ a1, m2 @ a2])
                try:
                    x = np.linalg.solve(M, rhs)
                except np.linalg.LinAlgError:
                    x = Q[i] - n * self.t
                if np.linalg.norm(x - (Q[i] - n * self.t)) > 6.0 * self.t + 8.0:          # near parallel mitre planes: fall back to a plain offset
                    x = Q[i] - n * self.t
                inner.append(x)
            out.append((pc["name"], Q, np.array(inner), n))
        self.items = out
        return out


def surface_mesh(P, panels):
    """Open outer surface: every panel fan-triangulated about its centroid (panels are planar to < 0.05 mm), outward winding."""
    import trimesh
    V, F = [], []
    for p in panels:
        Q = np.array([P[i] for i in p["ids"]])
        n = panel_normal(Q, p["hint"])
        c = Q.mean(0)
        base = len(V)
        V.extend([c] + list(Q))
        for k in range(len(Q)):
            a, b = base + 1 + k, base + 1 + (k + 1) % len(Q)
            t = np.cross(Q[(k) % len(Q)] - c, Q[(k + 1) % len(Q)] - c)
            F.append([base, a, b] if t @ n >= 0 else [base, b, a])
    return trimesh.Trimesh(np.array(V), np.array(F), process=False)


def slab_solid(P, panels, t=2.4):
    """Union of the mitred panel slabs as a Manifold."""
    import trimesh
    from manifold3d import Manifold, Mesh, OpType
    S = Slabs(P, panels, t)
    items = S.build()
    ms = []
    for name, Q, I, n in items:
        pts = np.vstack([Q, I])
        h = trimesh.convex.convex_hull(pts)
        mm = Manifold(Mesh(np.array(h.vertices, np.float32), np.array(h.faces, np.uint32)))
        if mm.volume() > 1e-6:
            ms.append(mm)
    return Manifold.batch_boolean(ms, OpType.Add), S


def to_trimesh(man):
    """Manifold -> watertight trimesh of the largest component (float32 weld, degenerate faces dropped)."""
    import trimesh
    from scipy.spatial import cKDTree
    best = max(man.decompose(), key=lambda d: d.volume())
    mm = best.to_mesh()
    V = np.array(mm.vert_properties, float)[:, :3]
    Tr = np.array(mm.tri_verts)
    t = trimesh.Trimesh(V.copy(), Tr, process=False)
    edges = set(map(tuple, np.sort(t.edges, axis=1)))
    vn = t.vertex_normals
    for i, j in sorted(cKDTree(V).query_pairs(3e-4)):
        if (i, j) in edges:
            continue
        d = V[j] - V[i]
        d = d / np.linalg.norm(d) if np.linalg.norm(d) > 1e-9 else vn[j]
        V[j] = V[j] + d * 0.012
    V = V.astype(np.float32).astype(float)
    t = trimesh.Trimesh(V, Tr, process=False)
    t.merge_vertices()
    t.update_faces(t.nondegenerate_faces())
    t.update_faces(t.area_faces > 1e-6)
    t.remove_unreferenced_vertices()
    return t


def shell_mesh(P, panels, t=2.4, lam=1e-3):
    """Closed wall: outer panel surface + inner surface (every vertex moved to the intersection of its incident panel planes shifted inward by t,
    least squares for vertices of valence > 3) + rim strips along the open bottom edge.  Same topology, so it is watertight by construction."""
    import trimesh
    used = {i for p in panels for i in p["ids"]}
    names = sorted(n for n in P if n in used)
    idx = {n: i for i, n in enumerate(names)}
    pn = []
    inc = {n: [] for n in names}
    for k, p in enumerate(panels):
        Q = np.array([P[i] for i in p["ids"]])
        n = panel_normal(Q, p["hint"])
        pn.append((n, float(n @ Q.mean(0))))
        for i in p["ids"]:
            inc[i].append(k)
    inner = {}
    for nme in names:
        ks = inc[nme]
        v = P[nme]
        A = np.array([pn[k][0] for k in ks])
        b = np.array([pn[k][1] - t for k in ks])
        nbar = A.sum(0); nbar /= np.linalg.norm(nbar)
        x0 = v - t * nbar
        M = np.vstack([A, np.sqrt(lam) * np.eye(3)])
        r = np.concatenate([b, np.sqrt(lam) * x0])
        inner[nme] = np.linalg.lstsq(M, r, rcond=None)[0]
    V = [P[n] for n in names] + [inner[n] for n in names]
    nV = len(names)
    F = []

    def tri(a, b, c, ccw_n):
        pa, pb, pc = np.array(a), np.array(b), np.array(c)
        return (a, b, c)
    for k, p in enumerate(panels):
        ids = [idx[i] for i in p["ids"]]
        Q = np.array([P[i] for i in p["ids"]])
        n = pn[k][0]
        for (i0, i1, i2) in ear_triangles(Q, n):
            F.append([ids[i0], ids[i1], ids[i2]])                              # outer, CCW about n
            F.append([ids[i0] + nV, ids[i2] + nV, ids[i1] + nV])               # inner, reversed
    # rim: edges used by one panel
    use = {}
    for p in panels:
        ids = p["ids"]
        for j in range(len(ids)):
            a, b = idx[ids[j]], idx[ids[(j + 1) % len(ids)]]
            use.setdefault(frozenset((a, b)), []).append((a, b))
    for e, lst in use.items():
        if len(lst) == 1:
            a, b = lst[0]
            F.append([b, a, a + nV]); F.append([b, a + nV, b + nV])
    return trimesh.Trimesh(np.array(V), np.array(F), process=False)


def orient_panels(P, panels, verbose=False):
    """Make every panel's vertex order consistent with its neighbours (shared edge traversed in opposite directions), then flip all if the
    body is inside-out (sum of outward-hint agreement).  Returns the list of panels whose hint disagreed after propagation."""
    from collections import deque
    emap = {}
    for k, p in enumerate(panels):
        ids = p["ids"]
        for j in range(len(ids)):
            emap.setdefault(frozenset((ids[j], ids[(j + 1) % len(ids)])), []).append(k)
    seen = {0}
    dq = deque([0])
    while dq:
        k = dq.popleft()
        ids = panels[k]["ids"]
        for j in range(len(ids)):
            a, b = ids[j], ids[(j + 1) % len(ids)]
            for k2 in emap[frozenset((a, b))]:
                if k2 in seen:
                    continue
                i2 = panels[k2]["ids"]
                fwd = any(i2[m] == a and i2[(m + 1) % len(i2)] == b for m in range(len(i2)))
                if fwd:
                    panels[k2]["ids"] = i2[::-1]
                seen.add(k2)
                dq.append(k2)
    agree = 0
    for p in panels:
        Q = np.array([P[i] for i in p["ids"]])
        n = newell(Q)
        agree += 1 if n @ p["hint"] > 0 else -1
    if agree < 0:
        for p in panels:
            p["ids"] = p["ids"][::-1]
    bad = []
    for p in panels:
        Q = np.array([P[i] for i in p["ids"]])
        if newell(Q) @ p["hint"] <= 0:
            bad.append(p["name"])
    return bad


def manifold_of(t):
    from manifold3d import Manifold, Mesh
    return Manifold(Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))
