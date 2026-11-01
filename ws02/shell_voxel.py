"""Thicken the extracted skin into a watertight hollow shell: voxelize the surface, dilate to the wall thickness, mesh it."""
import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

from shell_from_base import load_shell

PITCH, WALL = 0.8, 2.4


def thick_shell(mesh, pitch=PITCH, wall=WALL):
    vox = trimesh.voxel.creation.voxelize(mesh, pitch=pitch, method="subdivide")
    occ = np.pad(vox.matrix, 4)
    r = max(1, int(round((wall / pitch - 1) / 2)))
    occ = ndimage.binary_dilation(occ, structure=ndimage.generate_binary_structure(3, 1), iterations=r)
    verts, faces, _, _ = measure.marching_cubes(occ.astype(np.float32), 0.5, spacing=(pitch,) * 3)
    origin = vox.transform[:3, 3] - 4 * pitch
    m = trimesh.Trimesh(verts + origin, faces)
    m.merge_vertices()
    return m


if __name__ == "__main__":
    s = thick_shell(load_shell())
    print(len(s.faces), s.is_watertight, round(s.volume), np.round(s.extents, 1).tolist())
    s.export("out/base_split/shell_thick.stl")
