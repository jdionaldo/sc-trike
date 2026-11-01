"""Build the WS-03 front parts (plus tie and lean rods) and print-check them."""
import math
import numpy as np
import build, validate
from params import P
from parts import w3_front, lean_linkage
import w3_scene as S

lug0 = S.F.P + np.array(S.W.LUG)
tip0 = S.tip_at(S.SH_LEAN, S.R_H, 0.0, math.radians(-40.0))
lr = S.LR
lt = float(np.linalg.norm(np.array([S.W.ARM_A[0], S.W.KP_Y + S.W.ARM_A[1], S.W.ARM_A[2]]) - np.array([S.I0[0], 56.0, S.I0[1]])))
parts = w3_front.build(P) + [lean_linkage.rod(P, "w3_tie_rod", lt, P.rod_boss), lean_linkage.rod(P, "w3_lean_rod", lr, P.rod_boss)]
for part in parts:
    build.run_part(part)
    r = validate.validate_part(part.name, part.walls, part.supports)
    bad = {k: v[1] for k, v in r.items() if not v[0]}
    print(part.name, "OK" if not bad else bad)
print("rods", round(lr, 2), round(lt, 2))
