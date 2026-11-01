"""All WS-03 printed parts as Part objects (front end, drivetrain, inner structure, rods)."""
import math
import numpy as np
from params import P
from parts import w3_front, w3_drive, w3_chassis, lean_linkage
import w3_scene as S


def all_parts():
    lt = float(np.linalg.norm(np.array([S.W.ARM_A[0], S.W.KP_Y + S.W.ARM_A[1], S.W.ARM_A[2]])
                              - np.array([S.I0[0], 56.0 + S.W.YS, S.I0[1]])))
    rods = [lean_linkage.rod(P, "w3_tie_rod", lt, P.rod_boss), lean_linkage.rod(P, "w3_lean_rod", S.LR, P.rod_boss)]
    return w3_front.build(P) + rods + w3_drive.build(P) + w3_chassis.build(P)
