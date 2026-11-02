"""Split the welded WS-03 body across x so both pieces fit the 220 x 220 bed. Output: out/mono3/body3_{front,rear}.stl"""
import numpy as np, trimesh
from manifold3d import Manifold
import mono_build as MB, validate

def main():
    """Cut across x only (the left and right halves are welded: the 141 mm width fits the bed); a 0.025 mm gap at the cut."""
    body = MB.man(trimesh.load("out/mono3/body3.stl"))
    XS = -165.0
    for part, sgn in (("front", 1), ("rear", -1)):
        box = Manifold.cube((400.0, 400.0, 400.0), center=True).translate((XS + sgn * 200.0 + sgn * 0.0125, 0, 0))
        m = MB.to_trimesh(body ^ box); m.merge_vertices()
        m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
        m.export(f"out/mono3/body3_{part}.stl")
        pm = m.copy(); pm.apply_translation((0, 0, -pm.bounds[0][2]))
        print(part, len(m.faces), m.is_watertight, np.round(m.extents, 1).tolist(), validate.check_bed(pm, 3.0))


if __name__ == "__main__":
    main()
