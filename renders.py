"""Renders of the assembled model from the exported STL files (matplotlib, flat shading, painter's depth sort)."""
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import assembly
from parts import body as body_parts
from params import P

OUT = Path("out/renders")
YELLOW, BLACK = "#f2c400", "#17171a"
LIGHT = np.array([0.35, -0.5, 0.8])
LIGHT /= np.linalg.norm(LIGHT)


def colour(item, body_colors):
    n = item.name
    if n in body_colors:
        return YELLOW if body_colors[n] == "yellow" else BLACK
    if "TIRE" in n:
        return "#202020"
    if n.startswith(("POWER", "GEAR", "AXLE", "SHAFT", "DOWEL")):
        return "#a9adb5"
    if n.startswith(("LIPO", "RECEIVER", "SERVO", "LEAD")):
        return "#2f5f9e" if n.startswith("LIPO") else "#4b4b52"
    if n.startswith(("hub", "upright", "lean", "link", "rod")):
        return "#d9d9de"
    if n.startswith("swingarm") or n.startswith("rear_hub"):
        return "#8c8f99"
    return "#c8c8cf"


def triangles(mesh, target=6000):
    m = mesh
    if len(m.faces) > target:
        import fast_simplification as fs
        v, f = fs.simplify(m.vertices.astype(np.float32), m.faces.astype(np.int32), target_count=target, agg=4)
        return v, f
    return m.vertices, m.faces


def render(items, views, path, size=(11, 6), hide=()):
    body_colors = body_parts.colors(P)
    polys, cols = [], []
    for it in items:
        if it.name in hide:
            continue
        v, f = triangles(it.mesh)
        tri = v[f]
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
        shade = 0.45 + 0.55 * np.clip(np.abs(nrm @ LIGHT), 0, 1)
        base = np.array(matplotlib.colors.to_rgb(colour(it, body_colors)))
        polys.append(tri)
        cols.append(np.clip(base[None, :] * shade[:, None], 0, 1))
    polys, cols = np.concatenate(polys), np.concatenate(cols)
    fig = plt.figure(figsize=(size[0], size[1] * len(views) / max(1, len(views))))
    for k, (title, elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, len(views), k + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, linewidths=0))
        lo, hi = polys.reshape(-1, 3).min(0), polys.reshape(-1, 3).max(0)
        ctr, span = (lo + hi) / 2, (hi - lo).max() / 2
        ax.set_xlim(ctr[0] - span, ctr[0] + span)
        ax.set_ylim(ctr[1] - span, ctr[1] + span)
        ax.set_zlim(ctr[2] - span * 0.6, ctr[2] + span * 0.6)
        ax.set_box_aspect((1, 1, 0.6))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def exploded(items, k=1.0):
    """Radial explosion about the assembly centroid; bigger throw for the body, smaller for the bought parts."""
    centre = np.mean([i.mesh.centroid for i in items if i.kind == "printed"], axis=0)
    out = []
    for it in items:
        d = it.mesh.centroid - centre
        d[0] *= 0.6
        n = np.linalg.norm(d)
        throw = {"body": 60.0, "chassis": 32.0, "front": 28.0, "swingarm": 22.0}.get(it.group, 20.0)
        if it.kind == "bought":
            throw *= 0.6
        shift = d / (n + 1e-9) * throw * k
        mesh = it.mesh.copy()
        mesh.apply_translation(shift)
        out.append(assembly.Item(it.name, mesh, it.kind, it.group))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = assembly.scene(0.0, 0.0, body=True)
    render(items, [("side", 0, -90)], OUT / "assembly_side.png", size=(12, 5))
    render(items, [("top", 90, -90)], OUT / "assembly_top.png", size=(12, 5))
    render(items, [("front three-quarter", 22, -35)], OUT / "assembly_iso_front.png", size=(12, 7))
    render(items, [("rear three-quarter", 22, 145)], OUT / "assembly_iso_rear.png", size=(12, 7))
    lean = assembly.scene(P.lean_target_deg, 0.0, body=True)
    render(lean, [("front, 30 deg lean", 0, 0)], OUT / "assembly_front_lean.png", size=(8, 6))
    render(exploded(assembly.scene(0.0, 0.0, lead=False, body=True)), [("exploded", 24, -40)],
           OUT / "assembly_exploded.png", size=(14, 8))
    render(items, [("chassis only, body hidden", 22, -35)], OUT / "assembly_no_body.png", size=(12, 7),
           hide=tuple(i.name for i in items if i.group == "body"))


if __name__ == "__main__":
    main()
