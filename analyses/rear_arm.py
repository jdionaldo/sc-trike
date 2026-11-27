"""Read-out (November 25): the global maximum sits on the rigid held / loaded faces and grows with the mesh (singular); the result is read away
from them with `python tools/fem_away.py .soma/results/<this>.glb D` (D = 2 element sizes, at least 2 mm) at two meshes (FEM_MESH), see NOTES.
Rear swingarm, PETG. Held at the pivot bearing seats (D11.1, x -1 / 44 / 69). Wheel load of a landing at the axle bores (D30 plates, y 244, z 57):
99.8 N up plus 35.7 N sideways, split over the two plates (by hand, NOTES 'Load basis', November 26: 3.09 kg from the model, 38.7 % on the
rear wheel by the CG = 1.197 kg, at 8.5 g = 99.8 N; earlier 86.6 N on an assumed 2.6 kg / 40 %, before that 55 N). The shock pushes down on the shock
mount (y 134, z 102) with 273 N along the shock axis (99.8 N x 121.8 mm about the pivot / 44.5 mm shock lever; motion ratio 0.365)."""
import os
from soma.fem import Study
_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else 2.0   # FEM_MESH: mesh size override for convergence runs
study = Study("Rear arm, 99.8 N bump + 35.7 N side at the axle, shock 273 N", material="PETG", safety=2, mesh=_MESH)      # 3.5 and 3.0 give a distorted element on the arm since the pin corridor got flat sides
# November 24: the arm rides on 5x11x4 bearings (seats D11.1 x 4 at x -3..1, 42..46, 67..71) and the axle turns in 8x16x5 bearings (seats D16.1 x 5 at
# x 47..52, 67..72): held on the pivot seat cylinders, the wheel load on the axle seat cylinders (points on the seat faces, pivot y 114.65 z 63.68,
# axle y 236.43 z 54.70 at ride height). The old points picked the plain bores, which now end in the thin shoulders beside the seats.
for x in (-1.0, 44.0, 69.0):
    study.fix("w3 rear arm", faces="%CYLINDER", near=(x, 114.65, 63.68 + 5.55))
study.force("w3 rear arm", N=(17.8, 0, 49.9), faces="%CYLINDER", near=(49.5, 236.43, 54.70 - 8.05))
study.force("w3 rear arm", N=(17.8, 0, 49.9), faces="%CYLINDER", near=(69.5, 236.43, 54.70 - 8.05))
study.force("w3 rear arm", N=(0, 33.1, -271.2), near=(0, 134, 102))   # 273 N along the shock axis (y -0.121, z 0.993), pushing the arm down
