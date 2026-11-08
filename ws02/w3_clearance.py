"""WS-03 clearance check: minimum distance between every pair of parts that can meet (printed vs printed or bought) over three poses,
plus a watertight check of every exported STL.  Writes WS03_CLEARANCE.md.  Surface distances come from dense point sampling (about 0.1 mm)."""
import itertools
import numpy as np
import trimesh
from scipy.spatial import cKDTree

import w3_assembly as A
import w3_scene as S

POSES = [(0.0, 0.0), (20.0, 17.0), (-20.0, -17.0)]
GAP = 0.3                       # flag pairs closer than this (and not declared as mated)


def samples(m, n=6000):
    p, _ = trimesh.sample.sample_surface_even(m, n)
    return np.asarray(p)


def main():
    rows = {}
    for lean, steer in POSES:
        items = A.assembly(lean, steer=steer)
        tr = {}
        for (an, am, ak), (bn, bm, bk) in itertools.combinations(items, 2):
            if ak == bk == "bought" or S.declared(an, bn):
                continue
            if np.any(am.bounds[1] + 2.0 < bm.bounds[0]) or np.any(bm.bounds[1] + 2.0 < am.bounds[0]):
                continue
            if an not in tr:
                tr[an] = (cKDTree(samples(am)), am)
            if bn not in tr:
                tr[bn] = (cKDTree(samples(bm)), bm)
            pa, pb = samples(am, 3000), samples(bm, 3000)
            d = min(tr[bn][0].query(pa)[0].min(), tr[an][0].query(pb)[0].min())
            key = (an, bn)
            rows[key] = min(rows.get(key, 99.0), float(d))
    flagged = sorted([(d, k) for k, d in rows.items() if d < GAP])
    import glob
    bad = []
    for f in sorted(glob.glob("out/stl/w3_*.stl") + glob.glob(__import__("skin_cfg").MONO + "/body3_*.stl")):
        t = trimesh.load(f)
        if not (t.is_watertight and len(t.split(only_watertight=False)) == 1):
            bad.append(f)
    lines = ["# WS-03 clearance check", "", f"Poses: lean/steer {POSES}. Pairs closer than {GAP} mm that are not declared as mated:", ""]
    lines += [f"- {a} / {b}: {d:.2f} mm" for d, (a, b) in flagged] or ["- none"]
    lines += ["", "Pairs checked: %d. Smallest 12 clearances:" % len(rows), ""]
    lines += [f"- {a} / {b}: {d:.2f} mm" for d, (a, b) in sorted((d, k) for k, d in rows.items())[:12]]
    lines += ["", "STL files that are not a single watertight body: " + (", ".join(bad) if bad else "none")]
    open("WS03_CLEARANCE.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
