"""Print audit for a folder of oriented STLs (as printed: z up, bed at the lowest point).

    python mesh_audit.py <stl_dir> [out.json] [--bed 256] [--allow-multi T0_,T1_]

Per part: watertight, separate bodies, enclosed cavities (negative-volume shells), fits the bed, overhang mm2 (faces steeper than 47 deg
from vertical, ceilings in the first 0.9 mm ignored), floating layer regions mm2 (a region with nothing under it in the layer below: what
Bambu Studio reports as "floating regions"). Exit 1 if any part is flagged. Needs: trimesh, numpy, shapely.
"""
import sys, os, glob, json
import numpy as np
import trimesh

OVERHANG_NZ = -0.735      # 47.3 deg: 45 deg chamfers pass despite tessellation error
FIRST_MM = 0.9            # bed-face recesses bridge; no support can stand under them


def overhang(m):
    z0 = m.bounds[0][2]
    sel = (m.face_normals[:, 2] < OVERHANG_NZ) & (m.triangles_center[:, 2] > z0 + FIRST_MM)
    return float(m.area_faces[sel].sum())


def floating(m, lh=0.2, tol=0.05):
    """mm2 of layer regions with nothing under them in the layer below."""
    from shapely.ops import unary_union
    z0, z1 = m.bounds[0][2], m.bounds[1][2]
    zs = np.arange(z0 + lh / 2, z1, lh)
    prev, out = None, 0.0
    for s in m.section_multiplane((0, 0, 0), (0, 0, 1), zs):
        cur = unary_union([q.buffer(0) for q in s.polygons_full]) if s is not None and len(s.polygons_full) else None
        if cur is not None and prev is not None:
            out += sum(g.area for g in getattr(cur, "geoms", [cur]) if g.area > 0.05 and not g.intersects(prev.buffer(tol)))
        prev = cur if cur is not None else prev
    return out


def audit(m, bed=256.0):
    parts = m.split(only_watertight=False)
    vols = [p.volume for p in parts]
    return dict(watertight=bool(m.is_watertight), winding=bool(m.is_winding_consistent), bodies=int(sum(v >= 2.0 for v in vols)),
                cavities=int(sum(v < -0.01 for v in vols)), slivers=int(sum(0 < v < 2.0 for v in vols)), volume=round(float(m.volume), 1),
                overhang=round(overhang(m), 1), floating=round(floating(m), 2), extents=[round(float(e), 1) for e in m.extents],
                fits_bed=bool(max(m.extents[:2]) <= bed - 2 and m.extents[2] <= bed))


def main():
    args, opt, it = [], {}, iter(sys.argv[1:])
    for a in it:
        if a.startswith("--"):
            opt[a] = next(it)
        else:
            args.append(a)
    bed = float(opt.get("--bed", 256))
    multi = tuple(opt.get("--allow-multi", "T0_").split(","))
    rows, bad = [], []
    for f in sorted(glob.glob(os.path.join(args[0], "*.stl"))):
        n = os.path.basename(f)[:-4]
        r = dict(name=n, **audit(trimesh.load(f), bed))
        rows.append(r)
        why = [k for k, ok in (("open", r["watertight"]), ("winding", r["winding"]), ("bed", r["fits_bed"])) if not ok]
        if not n.startswith(multi):
            why += [k for k, v in (("bodies", r["bodies"] > 1), ("cavity", r["cavities"]), ("sliver", r["slivers"])) if v]
        if why:
            bad.append((n, why))
    if len(args) > 1:
        json.dump(rows, open(args[1], "w"), indent=1)
    for n, why in bad:
        print("FLAG", n, why)
    print(f"{len(rows)} parts; {len(bad)} flagged; overhang total {sum(r['overhang'] for r in rows):.0f} mm2; "
          f"floating on {[r['name'] for r in rows if r['floating'] > 0.3]} (needs supports or a new orientation)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
