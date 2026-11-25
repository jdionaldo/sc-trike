"""Mesh polish for the printed shell: remove sliver and dust triangles and merge coplanar facets, keeping the shape.

Runs inside kit/build_kit.py (before splitting, shell parts only; `--no-polish` skips it) via polish_part(); also usable standalone:
    python kit/polish_stls.py <stl_dir> <polished_dir> [--tol 0.05]
Uses manifold3d's simplify(): edge collapses that move the surface by less than --tol mm (default 0.05, a quarter of a 0.2 mm
layer; the 0.3 mm PANEL_GAP seam is untouched), preserving manifoldness and every real crease. A part is accepted only if it stays one
closed manifold, its volume moves by < 0.1 % and its bounding box by < tol; otherwise the original is copied and the reason logged.
Shell parts are polished (see SHELL_STEMS); every other STL is copied unchanged. Writes polish_report.json next to the output.
"""
import os, sys, json, argparse, shutil
import numpy as np, trimesh
import manifold3d as M

SHELL_STEMS = ("Front_shell", "Canopy", "Tail_light_housing", "Grille_insert", "Nose_light_strip", "Tail_light_strip")


def thin_stats(m):
    tri = m.triangles; a = m.area_faces
    e = np.linalg.norm(tri[:, [1, 2, 0]] - tri, axis=2)
    alt = 2 * a / np.maximum(e.max(1), 1e-12)
    return {"faces": int(len(m.faces)), "area_lt_0.05mm2": int((a < 0.05).sum()), "altitude_lt_0.05mm": int((alt < 0.05).sum()),
            "min_altitude_mm": round(float(alt.min()), 5)}


def polish(m, tol):
    m = m.copy(); m.merge_vertices(digits_vertex=5); m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
    mf = M.Manifold(M.Mesh(vert_properties=np.array(m.vertices, np.float32), tri_verts=np.array(m.faces, np.uint32)))
    if mf.status() != M.Error.NoError:
        raise ValueError("input is not a manifold: %s" % mf.status())
    for _ in range(2):          # a second pass catches slivers exposed by the first
        mf = mf.simplify(tol)
    o = mf.to_mesh()
    return trimesh.Trimesh(np.array(o.vert_properties[:, :3], float), np.array(o.tri_verts), process=False), m


def polish_part(m0, tol=0.05):
    """Return (mesh, report): the polished mesh if it stays one closed manifold with the same body count, <0.1 % volume change and
    <tol bbox shift; otherwise the original m0 and the reason."""
    try:
        p, m = polish(m0, tol)
        dv = (p.volume - m.volume) / m.volume
        dbb = float(np.abs(p.bounds - m.bounds).max())
        ok = (p.is_watertight and p.is_winding_consistent and abs(dv) < 1e-3 and dbb < tol + 1e-6
              and len(p.split(only_watertight=False)) == len(m.split(only_watertight=False)))
        return (p if ok else m0), {"accepted": bool(ok), "before": thin_stats(m), "after": thin_stats(p),
                                   "dvol_pct": round(100 * dv, 4), "dbbox_mm": round(dbb, 4)}
    except Exception as e:
        return m0, {"accepted": False, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("--tol", type=float, default=0.05)
    a = ap.parse_args(); os.makedirs(a.dst, exist_ok=True); report = {}
    for f in sorted(os.listdir(a.src)):
        if not f.lower().endswith(".stl"): continue
        stem = f[:-4]; src = os.path.join(a.src, f); dst = os.path.join(a.dst, f)
        if stem not in SHELL_STEMS:
            shutil.copy2(src, dst); continue
        p, r = polish_part(trimesh.load(src, process=False), a.tol); report[stem] = r; p.export(dst)
        r = report[stem]; print(stem, "OK" if r.get("accepted") else "KEPT ORIGINAL", {k: v for k, v in r.items() if k != "accepted"})
    json.dump(report, open(os.path.join(a.dst, "polish_report.json"), "w"), indent=1)
    sys.exit(0 if all(r.get("accepted") for r in report.values()) else 1)


if __name__ == "__main__":
    main()
