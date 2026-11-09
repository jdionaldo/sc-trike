"""Facet metrics of a skin STL: planar panels by region growing (normal within 1.5 deg, plane offset within 0.25 mm), then
panel count, mean triangles per panel, flat-panel coverage (area in panels >= 50 mm2), and the dihedral change across panel edges.
usage: python tools_skin/facet_metrics.py STL [OUTER_ONLY=1]"""
import sys
import numpy as np, trimesh
from collections import defaultdict, deque
m = trimesh.load(sys.argv[1]); m.merge_vertices()
# outer surface only: faces whose outward ray leaves the body (the cavity walls are excluded)
hit = m.ray.intersects_any(m.triangles_center + m.face_normals * 0.05, m.face_normals)
m = trimesh.Trimesh(m.vertices, m.faces[~hit], process=False)
import os
if os.environ.get("WS03_ALONE") == "1":                                  # open belly: cavity ceilings also pass the ray test, so drop faces more than 1 mm inside the outer envelope
    import skin7 as _K, mono_build as _MB
    _env = _MB.to_trimesh(_K.solid(0.0))
    _d = trimesh.proximity.signed_distance(_env, m.triangles_center)         # positive inside
    m = trimesh.Trimesh(m.vertices, m.faces[_d < 1.0], process=False)
F = len(m.faces); N = m.face_normals; A = m.area_faces; C = m.triangles_center
adj = defaultdict(list)
for a, b in m.face_adjacency: adj[a].append(b); adj[b].append(a)
lab = -np.ones(F, int); n = 0
cos = np.cos(np.radians(1.5))
for s in np.argsort(-A):
    if lab[s] >= 0: continue
    lab[s] = n; q = deque([s]); n0 = N[s]; d0 = n0 @ C[s]
    while q:
        f = q.popleft()
        for g in adj[f]:
            if lab[g] < 0 and N[g] @ n0 > cos and abs(N[g] @ C[g] - 0 - (n0 @ C[g])) < 1e9 and abs(n0 @ C[g] - d0) < 0.25:
                lab[g] = n; q.append(g)
    n += 1
pa = np.bincount(lab, weights=A); pt = np.bincount(lab)
big = pa >= 50.0
cover = pa[big].sum() / pa.sum() * 100
ang = np.degrees(m.face_adjacency_angles)
cross = lab[m.face_adjacency[:, 0]] != lab[m.face_adjacency[:, 1]]
ea = ang[cross]
el = m.face_adjacency_edges; ln = np.linalg.norm(m.vertices[el[:, 0]] - m.vertices[el[:, 1]], axis=1)[cross]
sig = ln > 3.0                                                           # ignore tiny edges (rivet domes, grille cells)
print(f"triangles {F}, panels {n}, panels >= 50 mm2: {int(big.sum())}")
print(f"mean triangles per panel {pt.mean():.1f} (area-weighted {np.average(pt, weights=pa):.1f})")
print(f"flat-panel coverage {cover:.1f} % of surface area (panels >= 50 mm2)")
print(f"edges between panels: {len(ea)}; longer than 3 mm: {int(sig.sum())}")
print(f"normal change at panel edges (>3 mm long): median {np.median(ea[sig]):.0f} deg, p95 {np.percentile(ea[sig],95):.0f} deg, max {ea[sig].max():.0f} deg")
print(f"smooth blends (panel edge change < 15 deg, >3 mm long): {int((ea[sig] < 15).sum())} edges = {100*(ea[sig] < 15).mean():.1f} % of panel edges")
try:                                                                     # edges cut by the frame-relief / swing channels (interface cuts, swept arcs) are reported separately
    import mono_build as MB, w3_swing
    ch = MB.to_trimesh(w3_swing.swing_channels())
    mids = m.vertices[el[cross][sig]].mean(1)
    iface = trimesh.proximity.closest_point(ch, mids)[1] < 0.4
    sm = ea[sig] < 15
    if len(sys.argv) > 2:
        for q, a_ in zip(mids[sm & ~iface], ea[sig][sm & ~iface]): print('   own', np.round(q, 0).tolist(), round(float(a_), 0))
    print(f"  of those, {int((sm & iface).sum())} lie on the frame-relief / swing-channel cuts (interface, swept arcs) and {int((sm & ~iface).sum())} on the skin itself = {100*(sm & ~iface).sum()/max(1, (~iface).sum()):.1f} % of the skin's own panel edges")
except Exception as e:
    print("  (channel split skipped:", e, ")")
if len(sys.argv) > 2:
    mid = m.vertices[el[cross][sig][ea[sig] < 15]].mean(1)
    a = ea[sig][ea[sig] < 15]
    print("smooth-edge angles: <3:", int((a < 3).sum()), "3-8:", int(((a >= 3) & (a < 8)).sum()), "8-15:", int((a >= 8).sum()))
    h, e = np.histogram(mid[:, 0], bins=12, range=(-445, 65)); print("by x:", dict(zip(e[:-1].astype(int), h)))
    print("z>110:", int((mid[:, 2] > 110).sum()), " |y|>60:", int((abs(mid[:, 1]) > 60).sum()))
if len(sys.argv) > 3:
    sel = np.where(cross)[0][sig]; sel = sel[ea[sig] < 15]
    xs0, xs1 = float(sys.argv[2]), float(sys.argv[3])
    for k in sel:
        mp = m.vertices[el[k]].mean(0)
        if xs0 <= mp[0] <= xs1: print(np.round(mp, 1).tolist(), round(float(ang[k]), 1), round(float(np.linalg.norm(m.vertices[el[k][0]] - m.vertices[el[k][1]])), 1))
