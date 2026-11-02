"""WS-03 shell: the base.stl skin stretched and widened to fit the 3WD layout, hollowed to a watertight shell, with windows cut
where the front arms swing and where the rear arm leaves the body. Output: out/mono3/shell3.stl and left/right halves."""
import sys
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
import mono_shell

OUT = Path("out/mono3")
X0, XN = -196.0, -300.0          # old tail end of the skin -> new tail end
KX, KY, DZ = 1.9, 1.17, 20.7     # stretch along x, widen along y, frame shift (old origin was the lower bar pivot, 20.7 above the axle)
GAP = 3.0                        # clearance around the swept mechanism


def stretched_skin():
    skin = trimesh.load("out/base_split/ext_final.stl")
    skin = trimesh.intersections.slice_mesh_plane(skin, np.array([-1.0, 0, 0]), np.array([-40.0, 0, 0]), cap=False)
    c = skin.triangles_center
    inside = (np.abs(c[:, 1]) < 36.0) & (c[:, 2] < 31.0) & (c[:, 0] < -45.0)         # the base's seat and frame seen through the canopy
    skin = trimesh.Trimesh(skin.vertices, skin.faces[~inside], process=False)
    v = skin.vertices.copy()
    v[:, 0] = XN + KX * (v[:, 0] - X0)
    v[:, 1] *= KY
    v[:, 2] += DZ
    skin.vertices = v
    skin.export(OUT / "skin.stl")
    return skin


def swept_windows():
    """Union of every front-mechanism part over the lean range, grown by GAP in x and z."""
    import w3_scene as S
    keep = ("arm_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod", "lean_horn", "steer_horn")
    acc = None
    for ph in range(-30, 31, 6):
        for n, m, k in S.scene(float(ph)):
            if not n.startswith(keep):
                continue
            mm = MB.man(m)
            for dx in (-GAP, GAP):
                for dz in (-GAP, GAP):
                    g = mm.translate((dx, 0, dz))
                    acc = g if acc is None else acc + g
    return acc


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stretched_skin()
    mono_shell.PITCH = 0.5
    shell = mono_shell.build(str(OUT / "skin.stl"), str(OUT / "shell_watertight.stl"))
    import fast_simplification
    v, f = fast_simplification.simplify(np.asarray(shell.vertices), np.asarray(shell.faces), target_reduction=0.75)
    shell = trimesh.Trimesh(v, f, process=False)
    shell.merge_vertices()
    print("decimated", len(shell.faces))
    comps = sorted(shell.split(only_watertight=False), key=lambda c: -c.volume)
    shell = trimesh.util.concatenate([c for c in comps if c.volume > 0.05 * comps[0].volume])
    S = MB.man(shell)
    print("shell", np.round(shell.bounds, 1).tolist())
    S = S - swept_windows()
    S = S - Manifold.cube((38.0, 40.0, 90.0), center=True).translate((-281.0, 59.0, 0.0))     # rear arm leaves the body on the left
    S = S - Manifold.cube((38.0, 40.0, 90.0), center=True).translate((-281.0, -59.0, 0.0))    # mirrored so the halves stay identical
    m = MB.cleanup(MB.to_trimesh(S))
    m.export(OUT / "shell3.stl")
    print("shell3", len(m.faces), m.is_watertight, round(m.volume), np.round(m.bounds, 1).tolist())
    big = 1000.0
    for side, name in ((1, "shell3_left"), (-1, "shell3_right")):
        box = Manifold.cube((2 * big, big, 2 * big), center=True).translate((0, side * big / 2 - side * 0.013, 0))
        h = MB.cleanup(MB.to_trimesh(S ^ box))
        h.export(OUT / f"{name}.stl")
        print(name, len(h.faces), h.is_watertight, round(h.volume), np.round(h.extents, 1).tolist())


if __name__ == "__main__":
    main()
