"""Mesh checks for print preparation: topology, thinnest section, thin gaps, hole / peg detection with clearance advice.

Pure trimesh/numpy.  Nothing here writes into shared part files.  Used by print_prep.py; usable alone:
    python print_checks.py out/stl/w3_deck_front.stl
"""
import sys
import numpy as np
import trimesh

WALL_MIN = 1.2          # mm, thinner than three 0.4 mm perimeters is unreliable
GAP_MIN = 0.8           # mm, narrower gaps fuse together
RAY_EPS = 1e-3


# --------------------------------------------------------------------------------------------- topology
def topology(m):
    """Single watertight manifold with outward normals?  Returns dict of facts and a list of problems."""
    probs = []
    bodies = len(m.split(only_watertight=False))
    edges = m.edges_sorted
    _, counts = np.unique(edges, axis=0, return_counts=True)
    nonmanifold = int((counts != 2).sum())
    degenerate = int((m.area_faces < 1e-9).sum())
    vol = float(m.volume)
    if not m.is_watertight:
        probs.append("not watertight")
    if not m.is_winding_consistent:
        probs.append("inconsistent winding")
    if vol < 0:
        probs.append("inverted normals (negative volume)")
    if bodies != 1:
        probs.append(f"{bodies} separate bodies")
    if nonmanifold:
        probs.append(f"{nonmanifold} non-manifold edges")
    warns = [f"{degenerate} zero-area faces (harmless, slicers drop them)"] if degenerate else []
    return dict(watertight=bool(m.is_watertight), winding=bool(m.is_winding_consistent), volume=vol, bodies=bodies,
                nonmanifold_edges=nonmanifold, degenerate=degenerate, euler=int(m.euler_number), problems=probs, warnings=warns)


def repair(m):
    """Cheap, safe repairs: merge vertices, drop degenerate faces, fix winding/normals.  Returns (mesh, notes)."""
    m = m.copy()
    notes = []
    n0 = len(m.faces)
    m.merge_vertices()
    keep = m.area_faces > 1e-9
    if not keep.all():
        m.update_faces(keep)
        m.remove_unreferenced_vertices()
        notes.append(f"dropped {int((~keep).sum())} degenerate faces")
    if not m.is_winding_consistent:
        trimesh.repair.fix_winding(m)
        notes.append("fixed winding")
    if m.is_watertight and m.volume < 0:
        trimesh.repair.fix_inversion(m)
        notes.append("flipped inverted normals")
    if not m.is_watertight:
        trimesh.repair.fill_holes(m)
        if m.is_watertight:
            notes.append("filled holes")
    return m, notes


# --------------------------------------------------------------------------------------------- thickness / gaps
def _samples(m, n, seed=0):
    pts, fi = trimesh.sample.sample_surface(m, n, seed=seed)
    return pts, m.face_normals[fi], fi


def thickness_profile(m, n=2500, seed=0):
    """Wall thickness by shooting rays into the solid from sample points; gaps by shooting them outward.

    Returns dict(min, p1, p5, frac_thin, thin_at, gap_min, gap_count, gap_at)."""
    pts, nrm, _ = _samples(m, n, seed)
    ray = m.ray
    o = pts - nrm * RAY_EPS
    loc, idx, _ = ray.intersects_location(o, -nrm, multiple_hits=False)
    th = np.full(len(pts), np.inf)
    th[idx] = np.linalg.norm(loc - pts[idx], axis=1)
    fin = th[np.isfinite(th)]
    out = dict(min=float(fin.min()) if len(fin) else float("nan"),
               p1=float(np.percentile(fin, 1)) if len(fin) else float("nan"),
               p5=float(np.percentile(fin, 5)) if len(fin) else float("nan"))
    thin = np.isfinite(th) & (th < WALL_MIN)
    out["frac_thin"] = float(thin.mean())
    out["thin_at"] = pts[np.argmin(th)].round(1).tolist() if len(fin) else None
    o2 = pts + nrm * RAY_EPS
    loc2, idx2, _ = ray.intersects_location(o2, nrm, multiple_hits=False)
    gp = np.full(len(pts), np.inf)
    gp[idx2] = np.linalg.norm(loc2 - pts[idx2], axis=1)
    bad = gp < GAP_MIN
    out["gap_min"] = float(gp.min()) if np.isfinite(gp).any() else float("inf")
    out["gap_count"] = int(bad.sum())
    out["gap_at"] = pts[np.argmin(gp)].round(1).tolist() if np.isfinite(gp).any() else None
    return out


# --------------------------------------------------------------------------------------------- holes and pegs
# (name, printed-hole target range, nominal drawn size that has no clearance)
FIT_CLASSES = [
    ("M2.5 pilot (self-tap)", 1.95, 2.25, None),
    ("M2 clear", 2.3, 2.6, 2.0),
    ("M2.5 clear", 2.65, 2.95, 2.5),
    ("M2 insert / M3 clear", 3.0, 3.65, 3.0),
    ("4 mm shaft / M3 insert", 4.1, 4.45, 4.0),
    ("5 mm shaft / bearing bore", 5.15, 5.45, 5.0),
    ("magnet 6x2", 6.15, 6.45, 6.0),
    ("8 mm axle", 8.15, 8.45, 8.0),
    ("bearing 5x11x4 seat", 11.1, 11.4, 11.0),
    ("bearing 8x16x5 seat", 16.1, 16.4, 16.0),
]
NOMINAL_TOL = 0.08


def classify_hole(d):
    """Returns (class name or None, verdict string)."""
    for name, lo, hi, nom in FIT_CLASSES:
        if lo <= d <= hi:
            return name, "ok"
    for name, lo, hi, nom in FIT_CLASSES:
        if nom is not None and abs(d - nom) <= NOMINAL_TOL:
            return name, f"drawn at nominal {nom:g} mm: open to {lo:g}-{hi:g} mm (0.2-0.3 mm clearance)"
    for name, lo, hi, nom in FIT_CLASSES:
        if hi < d <= hi + 0.35 and name != "M2.5 pilot (self-tap)":
            return name, "loose by %.2f mm" % (d - hi)
    return None, "unclassified"


def _fit_circle(xy):
    A = np.c_[2 * xy, np.ones(len(xy))]
    b = (xy ** 2).sum(1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = sol[:2]
    r = float(np.sqrt(max(sol[2] + c @ c, 0.0)))
    res = np.abs(np.linalg.norm(xy - c, axis=1) - r)
    return c, r, float(np.sqrt((res ** 2).mean()))


def find_cylinders(m, max_faces=500, max_dia=40.0):
    """Detect cylindrical holes and pegs: smooth face groups whose normals are coplanar and whose vertices sit on a circle."""
    adj = m.face_adjacency
    ang = m.face_adjacency_angles
    sel = ang < 0.52
    import networkx as nx
    g = nx.Graph()
    g.add_nodes_from(range(len(m.faces)))
    g.add_edges_from(adj[sel])
    res = []
    area_f = m.area_faces
    for comp in nx.connected_components(g):
        k = len(comp)
        if k < 8 or k > max_faces:
            continue
        f = np.fromiter(comp, int)
        N = m.face_normals[f]
        _, s, vt = np.linalg.svd(N, full_matrices=False)
        if s[-1] / np.sqrt(k) > 0.06:
            continue
        axis = vt[-1]
        V = m.vertices[np.unique(m.faces[f])]
        ax_len = float(np.ptp(V @ axis))
        if ax_len < 0.8:
            continue
        # basis perpendicular to the axis
        u = np.cross(axis, [1, 0, 0] if abs(axis[0]) < 0.9 else [0, 1, 0])
        u /= np.linalg.norm(u)
        w = np.cross(axis, u)
        xy = np.c_[V @ u, V @ w]
        c, r, rms = _fit_circle(xy)
        if r * 2 > max_dia or r < 0.6 or rms > 0.04 * r + 0.02:
            continue
        a = np.sort(np.arctan2(xy[:, 1] - c[1], xy[:, 0] - c[0]))
        gaps = np.diff(np.r_[a, a[0] + 2 * np.pi])
        cover = float(np.degrees(2 * np.pi - gaps.max()))
        if cover < 150:
            continue
        cen3 = u * c[0] + w * c[1] + axis * float((V @ axis).mean())
        cp = m.triangles_center[f]
        toward = ((cen3 - cp) - axis * ((cen3 - cp) @ axis)[:, None])
        concave = float(np.mean(np.einsum("ij,ij->i", N, toward))) > 0
        # drop tube-like long convex cylinders: only keep pegs shorter than 25 mm
        if not concave and ax_len > 25:
            continue
        res.append(dict(dia=round(2 * r, 3), length=round(ax_len, 2), axis=axis.round(3).tolist(), centre=cen3.round(1).tolist(),
                        kind="hole" if concave else "peg", cover=round(cover), faces=k))
    return res


def hole_report(m, up=(0, 0, 1)):
    """Holes with fit verdicts and orientation notes (horizontal holes > 4 mm want teardrop tops)."""
    out = []
    for c in find_cylinders(m):
        cls, verdict = classify_hole(c["dia"]) if c["kind"] == "hole" else (None, "peg")
        c["class"] = cls
        c["verdict"] = verdict
        c["vertical"] = abs(np.dot(c["axis"], up)) > 0.9
        c["horizontal"] = abs(np.dot(c["axis"], up)) < 0.3
        out.append(c)
    return out


def peg_report(holes, up=(0, 0, 1)):
    """Pegs that stick out sideways and are long compared with their diameter print as unsupported overhangs."""
    return [h for h in holes if h["kind"] == "peg" and h["horizontal"] and h["length"] > 2.5 * h["dia"]]


def all_checks(m):
    topo = topology(m)
    th = thickness_profile(m)
    return topo, th


if __name__ == "__main__":
    for p in sys.argv[1:]:
        mm = trimesh.load(p, force="mesh")
        t, th = all_checks(mm)
        print(p, t["problems"] or "OK", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in th.items()})
        for h in hole_report(mm):
            print("  ", h["kind"], h["dia"], h["class"], h["verdict"])
