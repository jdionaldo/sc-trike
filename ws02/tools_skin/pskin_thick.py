"""Wall thickness sample: from points on the outer surface a ray goes inward along -n; the first exit distance is the wall. usage: python tools_skin/pskin_thick.py MESH.stl"""
import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1], force="mesh")
pts, fi = trimesh.sample.sample_surface_even(m, 6000)
n = m.face_normals[fi]
o = pts - n * 0.02
loc, ri, _ = m.ray.intersects_location(o, -n, multiple_hits=False)
d = np.full(len(pts), np.nan); d[ri] = np.linalg.norm(loc - o[ri], axis=1)
ok = ~np.isnan(d)
inner = d[ok] < 8
print(f"samples {ok.sum()}, wall median {np.median(d[ok][inner]):.2f}, p5 {np.percentile(d[ok][inner],5):.2f}, min {d[ok][inner].min():.2f}; under 1.2 mm: {100*np.mean(d[ok][inner]<1.2):.1f} %, under 2.0: {100*np.mean(d[ok][inner]<2.0):.1f} %")
