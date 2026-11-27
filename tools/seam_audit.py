"""Seam and facet audit of the faceted shell parts against the shoulder-to-door-skin reference (NOTES, November 26).

The reference: the hood's rear plane and the flank (door skin) are two facets of one convex body that share one straight edge: no ledge, no sliver,
no patch line, one wall all round. For every outside face pair that shares an edge this prints the angle step between their normals, and it flags
- SEAM: two faces within SEAM_DEG of each other (a patch line across what should be one facet, or a facet broken by a joint),
- SLIVER: a face under SLIVER_MM2 or narrower than SLIVER_W (area / longest edge),
- LEDGE: a face narrower than LEDGE_W between two faces that are within LEDGE_DEG of parallel (a step).
  python -I tools/seam_audit.py output/model.step [part ...]
"""
import sys, math
from collections import defaultdict
sys.path.insert(0, 'tools'); sys.path.insert(0, '.')
import cadquery as cq
import front_check as fc
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE

SEAM_DEG, LEDGE_DEG = 3.0, 10.0
LEDGE_SIDE = 3.0                      # mm: a ledge's near-parallel neighbours must each share at least this much edge with it (its long sides)
SLIVER_MM2, SLIVER_W, LEDGE_W = 0.2, 0.2, 1.5   # the shell rims carry deliberate 0.5 mm edge breaks: a sliver is narrower than those
SKIN_ONLY = '--all' not in sys.argv     # --all: every outward face, also trim pockets and inner walls seen through openings
INNER_PROBE = 3.3                     # mm: one 3.0 mm wall plus 0.3 (inner-wall test below)
SKIN_D = 4.0                          # mm from the convex hull that still counts as skin
PARTS = ['Front_shell', 'Rear_shell', 'Tail_light_housing', 'Grille_insert', 'Canopy']


def normal(f):
    try:
        return f.normalAt()
    except Exception:
        return None


def audit(shape, name):
    faces = shape.Faces()
    idx = {f.hashCode(): i for i, f in enumerate(faces)}
    m = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape.wrapped, TopAbs_EDGE, TopAbs_FACE, m)
    nb = defaultdict(set); edge_len = {}
    for k in range(1, m.Extent() + 1):
        e = cq.Edge(m.FindKey(k)); fl = m.FindFromIndex(k)
        fs = [cq.Face(f) for f in fl]
        ids = sorted({idx.get(f.hashCode()) for f in fs} - {None})
        if len(ids) == 2:
            a, b = ids; nb[a].add(b); nb[b].add(a); edge_len[(a, b)] = edge_len.get((a, b), 0) + e.Length()
    N = [normal(f) for f in faces]
    planar = [f.geomType() == 'PLANE' for f in faces]
    outer = []                       # the visible skin: a ray from the face along its normal never re-enters the part
    for i, f in enumerate(faces):
        c, n = f.Center(), N[i]
        outer.append(n is not None and not any(shape.isInside(c + n * d, 0.05) for d in (1.0, 3.0, 6.0, 10.0, 16.0, 25.0, 40.0, 60.0)))
    if SKIN_ONLY:                    # the body skin of a faceted convex shell lies on its convex hull: drop trim pockets and the cockpit's inner wall
        import numpy as np
        from scipy.spatial import ConvexHull
        V = np.array([v.toTuple() for v in shape.Vertices()]); H = ConvexHull(V)
        eq = H.equations                 # a.x + d <= 0 inside
        for i, f in enumerate(faces):
            if outer[i]:
                c = np.array(f.Center().toTuple()); outer[i] = bool(-np.max(eq[:, :3] @ c + eq[:, 3]) < SKIN_D)
                if outer[i] and N[i] is not None:
                    # inner wall of a skin panel seen through an opening (the hood's underside through the open belly, November 27): it lies within SKIN_D
                    # of the hull too, but one wall plus 0.3 mm behind it (against its normal) is outside the hull, past the outer skin; a true outer face
                    # has the panel and then the body's inside behind it, which is inside the hull
                    q = c - np.array(N[i].toTuple()) * INNER_PROBE
                    if np.max(eq[:, :3] @ q + eq[:, 3]) > 0.0: outer[i] = False
    N = [n if outer[i] else None for i, n in enumerate(N)]
    seams, slivers, ledges, steps = [], [], [], []
    for (a, b), L in edge_len.items():
        if N[a] is None or N[b] is None or not (planar[a] and planar[b]):
            continue
        ang = math.degrees(math.acos(max(-1, min(1, N[a].dot(N[b])))))
        steps.append(ang)
        if ang < SEAM_DEG and L > 2.0:
            seams.append((ang, L, faces[a].Center(), a, b))
    for i, f in enumerate(faces):
        if not outer[i]:
            continue
        ar = f.Area(); le = max((e.Length() for e in f.Edges()), default=1.0); w = ar / le
        if ar < SLIVER_MM2 or w < SLIVER_W:
            slivers.append((ar, w, f.Center()))
        elif w < LEDGE_W and planar[i]:
            # a step strip separates its two near-parallel neighbours along its LONG edges; a neighbour that only touches one of its short ends does not
            # make a ledge (November 27: the reference edge's 0.5 mm bevel at the WEDGE fold was paired with a door-skin face touching its 1.7 mm end; the
            # two flank faces there share their fold edge, step 0.00 mm, probed at five stations)
            ns = [j for j in nb[i] if N[j] is not None and planar[j] and edge_len.get((min(i, j), max(i, j)), 0.0) >= LEDGE_SIDE]
            for p in range(len(ns)):
                for q in range(p + 1, len(ns)):
                    if math.degrees(math.acos(max(-1, min(1, N[ns[p]].dot(N[ns[q]]))))) < LEDGE_DEG:
                        ledges.append((w, f.Center())); break
    print('%s: %d faces (%d on the outer skin), %d shared edges; angle steps min %.1f median %.1f deg; SEAM %d, SLIVER %d, LEDGE %d'
          % (name, len(faces), sum(outer), len(edge_len), min(steps) if steps else 0, sorted(steps)[len(steps) // 2] if steps else 0, len(seams), len(slivers), len(ledges)))
    for ang, L, c, a, b in sorted(seams, key=lambda q: q[0])[:12]:
        print('  SEAM   %.2f deg over %.1f mm at (%.1f, %.1f, %.1f)' % (ang, L, c.x, c.y, c.z))
    for ar, w, c in sorted(slivers, key=lambda q: q[0])[:12]:
        print('  SLIVER %.2f mm2, %.2f mm wide at (%.1f, %.1f, %.1f)' % (ar, w, c.x, c.y, c.z))
    for w, c in sorted(ledges, key=lambda q: q[0])[:12]:
        print('  LEDGE  %.2f mm wide at (%.1f, %.1f, %.1f)' % (w, c.x, c.y, c.z))
    return len(seams), len(slivers), len(ledges)


if __name__ == '__main__':
    P = fc.load(sys.argv[1]); by = {fc.leaf(k): k for k in P}
    want = [a for a in sys.argv[2:] if not a.startswith('--')] or PARTS
    for n in want:
        if n in by:
            audit(P[by[n]], n)
