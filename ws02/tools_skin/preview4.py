"""Clean 4-view preview (iso, side, top, front) of the standalone skin with crease lines, flat shaded. usage: python tools_skin/preview4.py OUT.png"""
import sys
import numpy as np, trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
D = "out/skin_alone/"
import os
skin = trimesh.load(D + "skin.stl"); wing = trimesh.load(D + "wing.stl") if os.path.exists(D + "wing.stl") else trimesh.Trimesh()
VIEWS = os.environ.get("VIEWS", "iso,side,top,front").split(",")
def basis(view):
    if view == "side": d, r, u = np.array([0, 1, 0.]), np.array([-1, 0, 0.]), np.array([0, 0, 1.])        # from the left, nose to the left
    elif view == "top": d, r, u = np.array([0, 0, 1.]), np.array([0, -1, 0.]), np.array([1, 0, 0.])      # nose up
    elif view == "front": d, r, u = np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([0, 0, 1.])
    elif view == "rear": d, r, u = np.array([-1, 0, 0.]), np.array([0, -1, 0.]), np.array([0, 0, 1.])
    else:
        az, el = np.radians(38.0 if view == "iso" else 218.0), np.radians(24.0 if view == "iso" else 30.0)
        d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])                       # towards the camera: front, left, above
        r = np.cross([0, 0, 1.0], d); r /= np.linalg.norm(r); u = np.cross(d, r)
    return r, u, d


def render(ax, view):
    r, u, d = basis(view)
    light = d + 0.6 * u - 0.4 * r; light /= np.linalg.norm(light)
    both = trimesh.util.concatenate([skin, wing]) if len(wing.faces) else skin
    P, C, L = [], [], []
    for m, base in [(mm, bb) for mm, bb in ((skin, np.array([0.80, 0.30, 0.55])), (wing, np.array([0.92, 0.78, 0.18]))) if len(mm.faces)]:
        V = m.vertices; N = m.face_normals; F = m.faces
        vis = N @ d > 0.02
        uv = np.stack([V @ r, V @ u], 1)
        dep = V[F].mean(1) @ d
        for f in np.where(vis)[0]:
            sh = 0.45 + 0.55 * max(0.0, float(N[f] @ light))
            P.append((dep[f], uv[F[f]], np.clip(base * sh + 0.08, 0, 1)))
        ang = np.degrees(m.face_adjacency_angles); fa = m.face_adjacency; ed = m.face_adjacency_edges
        for e in ed[(ang > 12.0) & (vis[fa[:, 0]] | vis[fa[:, 1]])]: L.append((float((V[e].mean(0)) @ d), uv[e]))
    P.sort(key=lambda t: t[0])
    ax.add_collection(PolyCollection([p[1] for p in P], facecolors=[p[2] for p in P], edgecolors=[p[2] for p in P], linewidths=0.3))
    keep = []
    if L:
        mids = np.array([[*(seg.mean(0))] for _, seg in L])                                              # 2D mids; rebuild 3D from edges below
    E3 = []
    for m in ([skin, wing] if len(wing.faces) else [skin]):
        ang = np.degrees(m.face_adjacency_angles); fa = m.face_adjacency; ed = m.face_adjacency_edges
        N = m.face_normals; vis = N @ d > 0.02
        for e in ed[(ang > 12.0) & (vis[fa[:, 0]] | vis[fa[:, 1]])]: E3.append(m.vertices[e])
    E3 = np.array(E3)
    mid3 = E3.mean(1) + d * 0.4
    hit = both.ray.intersects_any(mid3, np.tile(d, (len(mid3), 1)))                                     # an edge is visible if nothing lies between it and the camera
    for seg, h in zip(E3, hit):
        if not h: keep.append(np.stack([seg @ r, seg @ u], 1))
    ax.add_collection(LineCollection(keep, colors=(0.10, 0.03, 0.08), linewidths=0.35))
    allp = np.vstack([p[1] for p in P])
    if os.environ.get("CLIP"):                                                   # zoom on the part of the car between x = a and b (other faces still hide what they should)
        _a, _b = map(float, os.environ["CLIP"].split(","))
        _V = skin.vertices[(skin.vertices[:, 0] > _a) & (skin.vertices[:, 0] < _b) & (skin.vertices[:, 2] > 150)]
        allp = np.stack([_V @ r, _V @ u], 1)
    ax.set_xlim(allp[:, 0].min() - 8, allp[:, 0].max() + 8); ax.set_ylim(allp[:, 1].min() - 8, allp[:, 1].max() + 8)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(view, fontsize=11)


fig, axs = plt.subplots(2, 2, figsize=(16, 10), dpi=110)
for ax, v in zip(axs.ravel(), VIEWS): render(ax, v)
fig.suptitle("WS03 standalone skin (rev 14) - flat shaded, creases drawn where panels meet at more than 12 deg", fontsize=12)
fig.tight_layout(); fig.savefig(sys.argv[1]); print("ok")
