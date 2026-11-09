"""Unsupported skin: area of the skin more than D mm from any cage member (frame tubes, pads, base plates).  python support_check.py [D]  -> per-piece fraction and the worst 3-D cells."""
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import w3_assembly as A


def run(D=60.0, n=120000, verbose=True):
    items = A.assembly(0.0, 0.0)
    cage = [m for nme, m, k in items if nme.startswith(("w3_frame", "w3_deck"))]
    cp = np.vstack([trimesh.sample.sample_surface(m, 60000)[0] for m in cage])
    tree = cKDTree(cp)
    out = {}
    cells = {}
    for nme, m, k in items:
        if not nme.startswith("body3_"):
            continue
        pts, fi = trimesh.sample.sample_surface(m, n)
        nrm = m.face_normals[fi]
        d = tree.query(pts)[0]
        far = d > D
        out[nme] = float(far.mean())
        for p in pts[far]:
            c = tuple((np.floor(p / 30.0) * 30).astype(int))
            cells[c] = cells.get(c, 0) + 1
        if verbose:
            print(f"{nme}: {100 * far.mean():.1f} % of the surface farther than {D:.0f} mm from the cage (max {d.max():.0f} mm)")
    top = sorted(cells.items(), key=lambda kv: -kv[1])[:8]
    if verbose:
        print("worst 30 mm cells (x,y,z lower corner, share of samples):", [(c, round(v / (3 * n), 3)) for c, v in top])
    return out


if __name__ == "__main__":
    run(float(sys.argv[1]) if len(sys.argv) > 1 else 60.0)
