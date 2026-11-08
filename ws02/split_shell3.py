"""Split the welded WS-03 body across x into three pieces that each fit the bed. Output: out/mono3/body3_{front,mid,rear}.stl"""
import numpy as np, trimesh
from manifold3d import Manifold
import mono_build as MB, validate
from skin_cfg import MONO, CONCEPT

LAP = 6.0
LAP_JOINT = False                                                         # rev 6 registers with dowel pins instead (body3_build.details)
PIECES = ("front", "mid", "rear")
CUTS = (-152.0, -300.0) if CONCEPT else (-165.0, -300.0)               # x of the two cut planes (front|mid, mid|rear)


def main():
    """Cut across x only (the left and right halves are welded: the 147 mm width fits the bed); a 0.025 mm gap at each cut."""
    body = MB.man(trimesh.load(f"{MONO}/body3.stl"))
    his = (1000.0,) + CUTS
    los = CUTS + (-1000.0,)
    if CONCEPT and LAP_JOINT:                                                  # lap joint on each cut: the piece ahead of the cut grows a 6 mm tongue (inner 0.95 mm of the wall) into a rebate in the piece behind
        import body3_build as B
        deep13, deep12 = B.solid(1.45), B.solid(1.2)
        slab = lambda xa, xb: Manifold.cube((xb - xa, 400.0, 400.0), center=False).translate((xa, -200.0, -200.0))
        flanks = Manifold.cube((400.0, 150.0, 400.0), center=False).translate((-200.0, 50.0, -200.0)) + Manifold.cube((400.0, 150.0, 400.0), center=False).translate((-200.0, -200.0, -200.0))
        only = [flanks, None]                                                  # the front cut runs through the windscreen bezel: lap on the flanks only (|y| > 50)
        rebate = [body ^ deep12 ^ slab(c - LAP, c) for c in CUTS]
        tongue = [(body ^ deep13 ^ slab(c - LAP, c + 0.05)) - ((body ^ slab(c - LAP, c)) - r) for c, r in zip(CUTS, rebate)]   # never touches what stays in the piece behind
        tongue = [t if o is None else t ^ o for t, o in zip(tongue, only)]
        rebate = [r if o is None else r ^ o for r, o in zip(rebate, only)]
    for k, (part, hi, lo) in enumerate(zip(PIECES, his, los)):
        x0, x1 = lo + (0.0125 if lo > -1000.0 else 0.0), hi - (0.0125 if hi < 1000.0 else 0.0)
        box = Manifold.cube((x1 - x0, 400.0, 400.0), center=False).translate((x0, -200.0, -200.0))
        piece = body ^ box
        if CONCEPT and LAP_JOINT:
            if k > 0:
                piece = piece - rebate[k - 1]                                  # rebate for the tongue of the piece ahead
            if k < 2:
                piece = piece + tongue[k]                                      # tongue into the piece behind
        if CONCEPT:
            mm = piece.to_mesh()
            m = trimesh.Trimesh(np.array(mm.vert_properties, np.float32)[:, :3].astype(float), np.array(mm.tri_verts), process=False)
            m.merge_vertices(); m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
        else:
            m = MB.to_trimesh(piece); m.merge_vertices()
        m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
        m.export(f"{MONO}/body3_{part}.stl")
        pm = m.copy(); pm.apply_translation((0, 0, -pm.bounds[0][2]))
        print(part, len(m.faces), m.is_watertight, np.round(m.extents, 1).tolist(), validate.check_bed(pm, 3.0))


if __name__ == "__main__":
    main()
