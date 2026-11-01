"""Watertight shell from the extracted base skin: voxelize, close gaps, fill each column between its lowest and highest
skin voxel, hollow to a 2.4 mm wall and open the belly so the chassis drops in. Output: out/mono/shell_watertight.stl"""
import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

PITCH, WALL = 0.8, 2.4


def build(skin_path="out/base_split/ext_final.stl", out="out/mono/shell_watertight.stl"):
    skin = trimesh.load(skin_path)
    vox = trimesh.voxel.creation.voxelize(skin, pitch=PITCH, method="subdivide")
    occ = np.pad(vox.matrix.astype(bool), 12)
    origin = vox.transform[:3, 3] - 12 * PITCH
    shell = ndimage.binary_dilation(occ, structure=ndimage.generate_binary_structure(3, 2), iterations=max(1, round((WALL / PITCH - 1) / 2)))   # skin thickened to about WALL
    shell = ndimage.binary_closing(shell, iterations=1)
    lab, n = ndimage.label(shell)
    if n > 1:
        sizes = ndimage.sum(shell, lab, range(1, n + 1))
        shell = np.isin(lab, 1 + np.where(sizes > 0.02 * sizes.max())[0])
    field = ndimage.gaussian_filter(np.pad(shell, 1).astype(np.float32), sigma=0.72 / PITCH)          # smooths the voxel terraces
    verts, faces, _, _ = measure.marching_cubes(field, 0.42, spacing=(PITCH,) * 3)
    verts = verts + origin - PITCH
    m = trimesh.Trimesh(verts, faces[:, ::-1])
    m.merge_vertices()
    trimesh.smoothing.filter_taubin(m, iterations=6)
    m.fix_normals()
    m.export(out)
    return m


if __name__ == "__main__":
    import os
    os.makedirs("out/mono", exist_ok=True)
    m = build()
    print(len(m.faces), m.is_watertight, round(m.volume), np.round(m.extents, 1).tolist(), np.round(m.bounds, 0).tolist())
