"""Printable tube frame (roll cage, space frame, truss arm) for CadQuery, with clean faceted joints.

Extracted from Project_Fugu parts/cage.py (November 2026). Units mm. Depends on cadquery, numpy, scipy.

    f = Frame()
    f.tube((0, 0, 0), (0, 0, 60), 10)        # members are centre lines between named nodes; nothing is built yet
    f.tube((0, 0, 60), (80, 0, 60), 10)
    cage = f.build()                          # one valid solid; raises if a member cannot be fused

Rules the code enforces:
- every member is a chamfered square tube (an octagon), one flat face horizontal, so it prints without support in any orientation it is likely to get;
- tubes never overlap: a tube that ends on another splits it, two tubes that cross mid-span become four tubes at one node;
- every joint is one convex hull of the incident tube sections; each tube stops at a set-back section that is exactly a face of that hull,
  so no mitre spike, cope gap or cube corner sticks out of a joint;
- nodes joined by a tube with no free length are merged into one hull (two hulls with a stub between them leave a slot);
- members are fused one at a time and every step is checked (valid, volume grows); a failed fuse is retried with a tiny nudge.
"""
import math
import cadquery as cq
import numpy as np
from scipy.spatial import ConvexHull

TUBE_K = 0.88            # square side = TUBE_K x the nominal (round) diameter: similar section area, corners inside the round tube
TUBE_CHAMFER_K = 0.18    # 45 degree chamfer on each long edge, as a share of the side
NODE_E_CAP = 0.45        # share of a tube's length its end may be set back into a node
NODE_MERGE_FREE = 1.0    # two nodes whose joining tube has less free length than this become one node
V = cq.Vector


def tube_profile(d):
    h = d * TUBE_K / 2.0; c = d * TUBE_K * TUBE_CHAMFER_K
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]


def section_radius(d):
    h = d * TUBE_K / 2.0; c = d * TUBE_K * TUBE_CHAMFER_K
    return math.hypot(h, h - c)


def section_points(A, u, d):
    """The 8 corners of the tube section at A, normal u. One flat stays horizontal (vertical members: flats face +-x)."""
    ref = V(0, 0, 1) if abs(u.z) < 0.99 else V(1, 0, 0)
    w = ref.cross(u).normalized(); v = u.cross(w)
    return [(A + w * x + v * y).toTuple() for x, y in tube_profile(d)]


def hull_solid(pts, tol=2e-3):
    """Convex hull as a solid in which every facet is one planar face (triangles on the same plane within tol are merged)."""
    P = np.array(pts, float)
    h = ConvexHull(P)
    groups = []
    for eq, simp in zip(h.equations, h.simplices):
        for g in groups:
            if np.dot(g[0][:3], eq[:3]) > 1 - 1e-7 and all(abs(np.dot(g[0][:3], P[k]) + g[0][3]) < tol for k in simp):
                g[1].update(int(k) for k in simp); break
        else:
            groups.append([eq, set(int(k) for k in simp)])
    def solid(faces):
        sol = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
        if sol.Volume() < 0: sol = cq.Solid(sol.wrapped.Reversed())
        sol = sol.fix()
        assert sol.isValid() and abs(sol.Volume() - h.volume) < 1e-3 * h.volume + 1e-3, 'hull solid failed'
        return sol
    try:
        faces = []
        for eq, idx in groups:
            n = np.array(eq[:3]); Q = P[sorted(idx)]; c = Q.mean(0)
            u = np.cross(n, [0, 0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(n, u)
            Q = Q[np.argsort(np.arctan2((Q - c) @ v, (Q - c) @ u))]
            keep = [q for k, q in enumerate(Q) if np.linalg.norm(q - Q[k - 1]) > 1e-6]
            faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon([V(*q) for q in keep], close=True)))
        return solid(faces).clean()
    except Exception:      # a merged facet was not planar enough for OCC: fall back to one face per hull triangle
        HULL_FALLBACKS.append(len(pts))
        return solid([cq.Face.makeFromWires(cq.Wire.makePolygon([V(*P[k]) for k in simp], close=True)) for simp in h.simplices]).clean()


HULL_FALLBACKS = []      # point counts of the hulls that needed the triangle fallback (should stay empty or short)


def _key(p):
    return tuple(round(float(c), 1) for c in p)      # nodes snap to 0.1 mm: members that should meet must use the same point


class Frame:
    def __init__(self):
        self.segs = []       # (a, b, d)
        self.extras = []     # solids fused after the tubes (feet, bosses, plates, clevis ears)
        self.holes = []      # solids cut at the end (screw holes, slots, bores)

    def tube(self, a, b, d):
        self.segs.append((_key(a), _key(b), float(d)))

    def add(self, solid): self.extras.append(solid)
    def cut(self, solid): self.holes.append(solid)

    def _split_endpoints(self):
        """A tube that ends on the side of another splits it there, so every junction is a real node."""
        for _ in range(200):
            split = None
            for i, (a, b, d) in enumerate(self.segs):
                A, B = V(*a), V(*b); L = (B - A).Length
                if L < 1e-6: continue
                for j, (a2, b2, d2) in enumerate(self.segs):
                    if i == j: continue
                    for p in (a2, b2):
                        N = V(*p); t = (N - A).dot(B - A) / (L * L)
                        if 0.02 < t < 0.98 and (A + (B - A) * t - N).Length < 0.5: split = (i, p); break
                    if split: break
                if split: break
            if not split: return
            i, p = split; a, b, d = self.segs[i]
            self.segs[i] = (a, p, d); self.segs.append((p, b, d))

    def _split_crossings(self):
        """Two tubes passing through each other mid-span become four tubes meeting at one node."""
        for _ in range(200):
            hit = None
            for i in range(len(self.segs)):
                a0, a1 = np.array(self.segs[i][0]), np.array(self.segs[i][1])
                for j in range(i + 1, len(self.segs)):
                    b0, b1 = np.array(self.segs[j][0]), np.array(self.segs[j][1])
                    u, v, w = a1 - a0, b1 - b0, a0 - b0
                    A, B, C, D, E = u @ u, u @ v, v @ v, u @ w, v @ w
                    den = A * C - B * B
                    if den < 1e-9: continue
                    s = (B * E - C * D) / den; t = (A * E - B * D) / den
                    if not (0.03 < s < 0.97 and 0.03 < t < 0.97): continue
                    if np.linalg.norm(a0 + s * u - (b0 + t * v)) < (self.segs[i][2] + self.segs[j][2]) / 2 - 0.3:
                        hit = (i, j, _key((a0 + s * u + b0 + t * v) / 2)); break
                if hit: break
            if not hit: return
            i, j, p = hit
            for k in (i, j):
                a, b, d = self.segs[k]
                self.segs[k] = (a, p, d); self.segs.append((p, b, d))

    def crossings(self):
        """Pairs of members still crossing mid-span (should be empty after build)."""
        n0 = len(self.segs); self._split_crossings(); return len(self.segs) - n0

    def _solids(self):
        self._split_endpoints(); self._split_crossings(); self._split_endpoints()
        ends = {}
        for i, (a, b, d) in enumerate(self.segs):
            if (V(*b) - V(*a)).Length < 0.05: continue
            for k, p in ((0, a), (1, b)): ends.setdefault(p, []).append((i, k))
        set_back = {}; nodes = []
        for nk, group in ends.items():
            N = V(*nk); dirs = []
            for i, k in group:
                a, b, d = self.segs[i]; A, B = V(*a), V(*b)
                dirs.append(((B - A).normalized() if k == 0 else (A - B).normalized(), (B - A).Length, d))
            if len(group) == 1 or (len(group) == 2 and dirs[0][0].dot(dirs[1][0]) < -0.9995):
                for e in group: set_back[e] = 0.0             # free end or straight run
                continue
            R = [section_radius(d) for _, _, d in dirs]
            cap = [NODE_E_CAP * L for _, L, _ in dirs]
            e = [min(r, c) for r, c in zip(R, cap)]
            for _ in range(600):      # fixed point of e_i = max(R_i, max_j (e_j cos + R_j sin)): each tube's end section becomes a face of the node hull
                ch = 0.0
                for ii in range(len(dirs)):
                    need = R[ii]
                    for jj in range(len(dirs)):
                        if ii == jj: continue
                        c = max(-1.0, min(1.0, dirs[ii][0].dot(dirs[jj][0])))
                        need = max(need, e[jj] * c + R[jj] * math.sqrt(max(0.0, 1 - c * c)))
                    ne = min(need + 0.05, cap[ii]); ch = max(ch, abs(ne - e[ii])); e[ii] = ne
                if ch < 1e-3: break
            for g, ee in zip(group, e): set_back[g] = ee
            pts = [q for (u, L, d), ee in zip(dirs, e) for q in section_points(N + u * ee, u, d)]
            for u, L, d in dirs:      # each section at the node itself keeps the outer corner full
                for q in section_points(N, u, d):
                    if all(sum((qa - pa) ** 2 for qa, pa in zip(q, p_)) > 0.25 for p_ in pts): pts.append(q)
            nodes.append((nk, pts))
        idx = {nk: k for k, (nk, _) in enumerate(nodes)}
        parent = list(range(len(nodes)))
        def find(k):
            while parent[k] != k: k = parent[k]
            return k
        merged = set()
        for i, (a, b, d) in enumerate(self.segs):
            if a in idx and b in idx and a != b:
                if (V(*b) - V(*a)).Length - set_back.get((i, 0), 0.0) - set_back.get((i, 1), 0.0) < NODE_MERGE_FREE:
                    merged.add(i); parent[find(idx[a])] = find(idx[b])
        groups = {}
        for k, (nk, pts) in enumerate(nodes): groups.setdefault(find(k), []).extend(pts)
        out = []
        for i, (a, b, d) in enumerate(self.segs):
            A, B = V(*a), V(*b); L = (B - A).Length
            if L < 0.05 or i in merged: continue
            u = (B - A) / L; e0, e1 = set_back.get((i, 0), 0.0), set_back.get((i, 1), 0.0)
            if L - e0 - e1 < 0.3: continue        # covered by its two nodes
            out.append(('tube %s -> %s' % (a, b), hull_solid(section_points(A + u * e0, u, d) + section_points(B - u * e1, u, d))))
        out += [('node', hull_solid(pts)) for pts in groups.values()]
        return out

    def build(self):
        parts = self._solids() + [('extra %d' % i, s) for i, s in enumerate(self.extras)]
        s = parts[0][1]
        for tag, x in parts[1:]:
            ok = False
            for dx, dy, dz in [(0, 0, 0), (0.013, 0.007, 0.011), (-0.017, 0.011, -0.013), (0.031, -0.023, 0.019), (-0.043, -0.037, 0.029)]:
                try: t = s.fuse(x if (dx, dy, dz) == (0, 0, 0) else x.translate(V(dx, dy, dz)))
                except Exception: continue
                if t.isValid() and t.Volume() >= s.Volume() - max(1e-6, s.Volume() * 1e-8) and len(t.Solids()) <= len(s.Solids()) + 1:
                    s = t; ok = True; break
            if not ok: raise RuntimeError('frame member failed to fuse: ' + tag)
        try:
            t = s.clean()
            if t.isValid(): s = t
        except Exception: pass
        for h in self.holes:
            t = s.cut(h)
            if t.isValid() and t.Volume() < s.Volume(): s = t
        assert s.isValid() and len(s.Solids()) == 1, 'frame is not one valid solid (%d solids): a member is not connected' % len(s.Solids())
        return s


if __name__ == '__main__':      # self test: a small hoop frame with a diagonal crossing and a T joint
    f = Frame()
    P = dict(a=(40, 0, 0), b=(40, 0, 60), c=(-40, 0, 60), d=(-40, 0, 0), e=(40, 80, 50), g=(-40, 80, 50), h=(40, 80, 0), i=(-40, 80, 0))
    for m, n in ('ab', 'bc', 'cd', 'be', 'cg', 'eg', 'eh', 'gi', 'bg', 'ce', 'ah'):
        f.tube(P[m], P[n], 8)
    f.tube((0, 0, 60), (0, 0, 0), 8)      # ends on the middle of b-c: splits it
    s = f.build()
    small = sum(1 for q in s.Faces() if q.Area() < 0.05)
    print('ok: 1 solid, volume %.0f mm3, faces %d, faces under 0.05 mm2: %d' % (s.Volume(), len(s.Faces()), small))
