"""All WS-03 printed parts as Part objects (front end, drivetrain, inner structure, rods)."""
import math
import numpy as np
from params import P
from parts import w3_front, w3_drive, w3_chassis, lean_linkage
import w3_scene as S


def tube_rod(name, length, boss):
    """Round tube link with an eyelet boss at each end (bores vertical, u along x, bed at z = 0)."""
    import mono_build as MB
    from manifold3d import Manifold
    from parts.w3_style import MeshPart, _clean
    def fn():
        td, bh = 4.6, 5.0
        body = Manifold.cylinder(length, td / 2, td / 2, 32).rotate((0.0, 90.0, 0.0)).translate((0.0, 0.0, bh / 2))
        for u in (0.0, length):
            body = body + Manifold.cylinder(bh, boss / 2, boss / 2, 32).translate((u, 0.0, 0.0))
        for u in (0.0, length):
            body = body - Manifold.cylinder(bh + 2.0, P.m2_clear / 2, P.m2_clear / 2, 24).translate((u, 0.0, -1.0))
        return _clean(MB.to_trimesh(body))
    return MeshPart(name, fn, walls=False, supports=True)


def all_parts():
    lt = float(np.linalg.norm(np.array([S.W.ARM_A[0], S.W.KP_Y + S.W.ARM_A[1], S.W.ARM_A[2]])
                              - np.array([S.I0[0], 56.0 + S.W.YS, S.I0[1]])))
    rods = [tube_rod("w3_tie_rod", lt, P.rod_boss), tube_rod("w3_lean_rod", S.LR, P.rod_boss)]
    return w3_front.build(P) + rods + w3_drive.build(P) + w3_chassis.build(P)
