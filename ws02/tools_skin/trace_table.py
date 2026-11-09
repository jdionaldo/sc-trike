"""Traced (sheet 61, stretched) versus built numbers per station. usage: python tools_skin/trace_table.py [STL]"""
import sys
import numpy as np, trimesh
import trace61 as T
m = trimesh.load(sys.argv[1] if len(sys.argv) > 1 else "out/mono3_facet/body3.stl")
V = m.vertices
side_top = T.mm_polyline(T.TOP); side_floor = T.mm_polyline(T.FLOOR); plan = T.mm_polyline(T.PLAN, "plan")
pl = lambda pts, x: float(np.interp(x, [a for a, _ in sorted(pts)], [b for _, b in sorted(pts)]))
rows = []
print("| x (mm) | roof z traced | roof z built | half width traced | half width built | floor z traced | floor z built |")
print("|---:|---:|---:|---:|---:|---:|---:|")
errs = []
for x in (30, 10, -20, -50, -80, -110, -140, -170, -200, -250, -300, -330, -360, -390, -420, -440):
    sec = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sec is None:
        continue
    sl = sec.vertices
    zt, zf, hw = pl(side_top, x), pl(side_floor, x), pl(plan, x)
    # built: roof/floor from the centre line (|y|<30 ring) and half width from the whole slab; floor = lowest vertex of the flank skin
    rz = sl[:, 2].max(); bz = sl[:, 2].min(); bh = np.abs(sl[:, 1]).max()
    print(f"| {x} | {zt:.0f} | {rz:.0f} | {hw:.0f} | {bh:.0f} | {zf:.0f} | {bz:.0f} |")
    errs.append((rz - zt, bh - hw))
e = np.array(errs); print(f"\nroof z built - traced: mean {e[:,0].mean():+.1f} mm, max |{np.abs(e[:,0]).max():.1f}| mm; half width built - traced: mean {e[:,1].mean():+.1f} mm, max |{np.abs(e[:,1]).max():.1f}| mm")
