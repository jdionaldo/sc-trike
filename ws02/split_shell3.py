"""Split the welded WS-03 body across x into three pieces that each fit the bed. Output: out/mono3/body3_{front,mid,rear}.stl"""
import numpy as np, trimesh
from manifold3d import Manifold
import mono_build as MB, validate

PIECES = ("front", "mid", "rear")
import skin_user as _SU
CUTS = _SU.JOINT_X    # x of the two cut planes (front|mid, mid|rear): the joints of the user's skin pieces


def main():
    """Cut across x only (the left and right halves are welded: the 147 mm width fits the bed); a 0.025 mm gap at each cut."""
    body = MB.man(trimesh.load("out/mono3/body3.stl"))
    his = (1000.0,) + CUTS
    los = CUTS + (-1000.0,)
    for part, hi, lo in zip(PIECES, his, los):
        x0, x1 = lo + (0.0137 if lo > -1000.0 else 0.0), hi - (0.0137 if hi < 1000.0 else 0.0)
        box = Manifold.cube((x1 - x0, 400.0, 400.0), center=False).translate((x0, -200.0, -200.0))
        m = _SU.unpinch(MB.to_trimesh(body ^ box)); m.vertices = np.asarray(m.vertices, np.float32).astype(np.float64); m.merge_vertices()
        if not m.is_watertight:
            m = _SU.heal_pinches(m); m.merge_vertices()
        m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
        m.export(f"out/mono3/body3_{part}.stl")
        pm = m.copy(); pm.apply_translation((0, 0, -pm.bounds[0][2]))
        print(part, len(m.faces), m.is_watertight, np.round(m.extents, 1).tolist(), validate.check_bed(pm, 3.0))


if __name__ == "__main__":
    main()
