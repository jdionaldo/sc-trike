"""Section-based strength check of the printed articulating parts that the solid FEM cannot constrain reliably (faceted meshes without bores).

For every part: slice it perpendicular to a chosen axis at 60 stations, take the area and the section moduli of each slice, and compare the load case
with the allowable stress. Allowable = printed PETG strength / SAFETY: 20 MPa across the layers (worst direction), 40 MPa along the layers.
Axial members (tie rod, uplink) are also checked for Euler buckling with pinned ends.
Run:  python tools/strength_check.py   (from the project folder, with the SOMA python on PATH). Prints a table and writes analyses/strength_check.md.

ASSUMED loads (no measured data; the vehicle mass is 2.6 kg, 60 % on the front axle):
  landing, one front wheel: 65 N up (about 8 g of the static 8 N), cornering 30 N sideways, tyre contact patch 56 mm under the axle
  steering servo: 15.5 kg.cm stall = 1520 N.mm at the servo spline; the horn radius is taken from the model
  lean servo: same torque class
"""
import sys, math, os
sys.path.insert(0, '.')
import numpy as np
import cadquery as cq
from soma import import_assembly

SAFETY = 2.0
ACROSS, ALONG = 20.0, 40.0
E_PETG = 2000.0


def sections(shape, axis, n=60, trim=0.12):
    """Slices perpendicular to axis (0, 1, 2) with OpenCascade. Returns [(position, area, Z_min, I_min)] over the middle 1-2*trim of the length."""
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    bb = shape.BoundingBox()
    lo, hi = (bb.xmin, bb.ymin, bb.zmin)[axis], (bb.xmax, bb.ymax, bb.zmax)[axis]
    ext = [bb.xlen + 20, bb.ylen + 20, bb.zlen + 20]
    out = []
    for s in np.linspace(lo + trim * (hi - lo), hi - trim * (hi - lo), n):
        org = [bb.xmin - 10, bb.ymin - 10, bb.zmin - 10]; org[axis] = s - 0.02
        size = list(ext); size[axis] = 0.04
        sl = shape.intersect(cq.Solid.makeBox(size[0], size[1], size[2], cq.Vector(*org)))
        fs = [f for f in sl.Faces() if abs(f.normalAt(f.Center()).toTuple()[axis]) > 0.99 and f.Center().toTuple()[axis] > s]
        if not fs: continue
        g = GProp_GProps()
        for f in fs: BRepGProp.SurfaceProperties_s(f.wrapped, g, True) if False else None
        comp = cq.Compound.makeCompound(fs)
        BRepGProp.SurfaceProperties_s(comp.wrapped, g)
        A = g.Mass(); c = g.CentreOfMass(); M = g.MatrixOfInertia()
        i1, i2 = [i for i in range(3) if i != axis]
        Ia = M.Value(i1 + 1, i1 + 1); Ib = M.Value(i2 + 1, i2 + 1)   # inertia matrix terms are about the other axes
        # matrix of inertia: Ixx = integral (y2 + z2). The bending inertia about axis i1 is (sum of the other two terms - own) / 2 ... use the planar form directly:
        Jtot = M.Value(axis + 1, axis + 1)                              # polar moment about the slice normal = Ia' + Ib'
        Ibend_i1 = (M.Value(i2 + 1, i2 + 1) + M.Value(axis + 1, axis + 1) - M.Value(i1 + 1, i1 + 1)) / 2
        Ibend_i2 = (M.Value(i1 + 1, i1 + 1) + M.Value(axis + 1, axis + 1) - M.Value(i2 + 1, i2 + 1)) / 2
        cb = comp.BoundingBox(); cen = (c.X(), c.Y(), c.Z()); mn = (cb.xmin, cb.ymin, cb.zmin); mx = (cb.xmax, cb.ymax, cb.zmax)
        r1 = max(cen[i1] - mn[i1], mx[i1] - cen[i1]); r2 = max(cen[i2] - mn[i2], mx[i2] - cen[i2])
        # a planar slice has Ibend about axis i1 = integral of (coordinate along i2)^2 dA
        I_a = abs(Ibend_i1); I_b = abs(Ibend_i2)                          # about i1 uses extent along i2, and vice versa
        za, zb = I_a / max(r2, 1e-6), I_b / max(r1, 1e-6)
        out.append((float(s), A, (min(za, zb), max(za, zb)), min(I_a, I_b)))
    return out


def main():
    a = import_assembly('output/model.step')
    P = {n: (nd.obj.val() if isinstance(nd.obj, cq.Workplane) else nd.obj).moved(nd.loc) for n, nd in a.objects.items() if nd.obj is not None}
    allow = lambda dirn: (ACROSS if dirn == 'across' else ALONG) / SAFETY
    rows = []
    def part(name): return P[name]
    horn_R = 15.0     # mm, spline to ball stud, from the model (65,-116,37) -> (69,-116,22)
    F_rod = 1520.0 / horn_R   # N, stall force at the rod
    # name, axis, load kind, value, extra
    cases = [
        ('Tie rod', 'Chassis/Steering/tie_rod_1', 1, 'axial', F_rod, 110.0, 'servo stall through the horn'),
        ('Uplink', 'Chassis/Suspension/uplink_1', 1, 'axial', 80.0, 108.0, 'share of the landing load carried by the link (ASSUMED)'),
        ('Steering horn', 'Chassis/Steering/steer_horn_1', 0, 'bend', F_rod * horn_R * 0.6, None, 'stall torque at the horn root: F x 9 mm to the stud (60 % of the radius)'),
        ('Knuckle', 'Chassis/Steering/knuckle_1', 0, 'bend', 65.0 * 40 + 30.0 * 56, None, 'bump 65 N x 40 mm + side 30 N x 56 mm'),
        ('Carrier', 'Chassis/Steering/carrier_1', 0, 'bend', 65.0 * 30 + 30.0 * 56, None, 'bump 65 N x 30 mm + side 30 N x 56 mm'),
        ('Lean horn', 'Chassis/Suspension/lean_horn_c', 0, 'bend', 1520.0 * 0.8, None, 'lean servo stall, 80 % of the torque at the root'),
        ('Lean rocker', 'Chassis/Suspension/lean_rocker_c', 0, 'bend', 1520.0, None, 'lean servo stall through the rocker'),
    ]
    for label, name, axis, kind, val, L, note in cases:
        m = part(name); bb0 = m.BoundingBox(); axis = int(np.argmax([bb0.xlen, bb0.ylen, bb0.zlen]))   # slice along the longest direction of the part
        sec = sections(m, axis)
        amin = min(s[1] for s in sec); zmin = min(s[2][0] for s in sec); zstrong = min(s[2][1] for s in sec); imin = min(s[3] for s in sec)
        if kind == 'axial':
            sig = val / amin; pcr = math.pi ** 2 * E_PETG * imin / L ** 2
            rows.append((label, note, f'{val:.0f} N axial', amin, sig, allow('across'), val / pcr if pcr else 99, f'Euler load {pcr:.0f} N (pinned ends)'))
        else:
            sig = val / zstrong
            rows.append((label, note, f'{val:.0f} N.mm bending', amin, sig, allow('across'), 0, f'best case, load along the strong axis (Z {zstrong:.0f} mm3); load along the weak axis (Z {zmin:.0f} mm3) is {val / zmin:.0f} MPa'))
    lines = ['# Section check of the printed articulating parts', '',
             f'Allowable = {ACROSS:.0f} MPa (printed PETG across the layers) / safety {SAFETY:.0f} = {ACROSS / SAFETY:.0f} MPa. Loads are ASSUMED, see `tools/strength_check.py`.', '',
             '| Part | Load | Weakest section mm2 | Stress MPa | Allowable MPa | Utilisation | Note |', '|---|---|---|---|---|---|---|']
    for label, note, load, amin, sig, al, buck, extra in rows:
        lines.append(f'| {label} | {load} ({note}) | {amin:.1f} | {sig:.1f} | {al:.1f} | {sig / al * 100:.0f} % | {extra}{"; buckling load ratio %.2f" % buck if buck else ""} |')
    txt = '\n'.join(lines); print(txt)
    open('analyses/strength_check.md', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
