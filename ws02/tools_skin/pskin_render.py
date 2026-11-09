"""Flat-shaded multi-view render of a panel-skin mesh (STL/GLB-free): python tools_skin/pskin_render.py MESH.stl OUT.png [views]
views default top,front,rear,side,q34 (the sheet's views).  Creases drawn where facets meet at > 12 deg; visible edges only (ray test)."""
import sys, os
import numpy as np, trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection


def basis(view):
    if view == "side": d, r, u = np.array([0, 1, 0.]), np.array([-1, 0, 0.]), np.array([0, 0, 1.])
    elif view == "top": d, r, u = np.array([0, 0, 1.]), np.array([0, -1, 0.]), np.array([1, 0, 0.])
    elif view == "front": d, r, u = np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.])
    elif view == "rear": d, r, u = np.array([-1, 0, 0.]), np.array([0, -1, 0.]), np.array([0, 0, 1.])
    else:
        az, el = np.radians(38.0), np.radians(24.0)
        if view == "q34r": az = np.radians(218.0)
        d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        r = np.cross([0, 0, 1.0], d); r /= np.linalg.norm(r); u = np.cross(d, r)
    return r, u, d


def render(ax, mesh, view, crease=12.0):
    r, u, d = basis(view)
    light = d + 0.6 * u - 0.4 * r; light /= np.linalg.norm(light)
    base = np.array([0.80, 0.30, 0.55])
    V, N, F = mesh.vertices, mesh.face_normals, mesh.faces
    vis = N @ d > 0.02
    uv = np.stack([V @ r, V @ u], 1)
    dep = V[F].mean(1) @ d
    P = []
    for f in np.where(vis)[0]:
        sh = 0.45 + 0.55 * max(0.0, float(N[f] @ light))
        c = np.clip(base * sh + 0.08, 0, 1)
        P.append((dep[f], uv[F[f]], c))
    P.sort(key=lambda t: t[0])
    ax.add_collection(PolyCollection([p[1] for p in P], facecolors=[p[2] for p in P], edgecolors=[p[2] for p in P], linewidths=0.3))
    ang = np.degrees(mesh.face_adjacency_angles); fa = mesh.face_adjacency; ed = mesh.face_adjacency_edges
    sel = (ang > crease) & (vis[fa[:, 0]] | vis[fa[:, 1]])
    E3 = V[ed[sel]]
    keep = []
    if len(E3):
        mid3 = E3.mean(1) + d * 0.4
        hit = mesh.ray.intersects_any(mid3, np.tile(d, (len(mid3), 1)))
        for seg, h in zip(E3, hit):
            if not h:
                keep.append(np.stack([seg @ r, seg @ u], 1))
    ax.add_collection(LineCollection(keep, colors=(0.10, 0.03, 0.08), linewidths=0.45))
    allp = np.stack([V @ r, V @ u], 1)
    ax.set_xlim(allp[:, 0].min() - 6, allp[:, 0].max() + 6); ax.set_ylim(allp[:, 1].min() - 6, allp[:, 1].max() + 6)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(view, fontsize=11)


def sheet(mesh, out, views=("top", "front", "rear", "side", "q34"), title=""):
    fig, axs = plt.subplots(2, 3, figsize=(18, 9), dpi=100)
    axs = axs.ravel()
    for ax, v in zip(axs, views):
        render(ax, mesh, v)
    for ax in axs[len(views):]:
        ax.axis("off")
    if title:
        fig.suptitle(title, fontsize=12)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


if __name__ == "__main__":
    m = trimesh.load(sys.argv[1], force="mesh")
    sheet(m, sys.argv[2], tuple(sys.argv[3].split(",")) if len(sys.argv) > 3 else ("top", "front", "rear", "side", "q34"))
    print("ok")
