"""Radial section tables of a mesh cross-section at x: outer radius per angle bin about c=(0, zc) from the raw section points (open C-shaped shells have no closed envelope)."""
import numpy as np
NB = 72
def section_pts(mesh, x):
    s = mesh.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0]); v = s.vertices
    # densify along edges
    pts = [v[:, 1:3]]
    for e in s.entities:
        a, b = v[e.points[:-1]][:, 1:3], v[e.points[1:]][:, 1:3]
        for t in (0.25, 0.5, 0.75): pts.append(a * (1 - t) + b * t)
    return np.vstack(pts)
def table(P, c):
    th = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]); r = np.hypot(P[:, 0] - c[0], P[:, 1] - c[1])
    edges = np.linspace(-np.pi, np.pi, NB + 1); R = np.full(NB, np.nan)
    for i in range(NB):
        m = (th >= edges[i]) & (th < edges[i + 1])
        if m.any(): R[i] = r[m].max()
    ok = ~np.isnan(R); cen = 0.5 * (edges[:-1] + edges[1:])
    if ok.sum() < 8: return cen, np.full(NB, np.nanmean(R))
    R[~ok] = np.interp(cen[~ok], cen[ok], R[ok], period=2 * np.pi); return cen, R
