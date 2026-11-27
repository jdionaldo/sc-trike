"""Cage (parts/cage.py) under the up stop (lean stop) load, PETG, checked against the strength across the layers.
The upper arm's post diagonal meets the TPU pad under the cage's front brace (parts/stops.py up_stop_pad) at lean 10 deg with that side up plus
12 mm bump. Load: the arm's whole moment from a one-wheel landing goes into the stop instead of the heave shock (on the safe side; at that pose
the heave bump stop also engages): analyses/wishbone_upper_arm.py has the shock at 254.6 N on a 24.5 mm lever about the pivot, the stop's lever
is 32.5 mm (pad contact x 47.5, pivot x 15): 254.6 x 24.5 / 32.5 = 192 N; the case uses 257 N (wheel contact lever 129 mm x 65 N / 32.5, the orchestrator's value), straight up on the brace underside at the pad, one
side (+x) at a time. Held at the end faces of the six feet as in analyses/cage.py."""
import os
from soma.fem import Study

_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else 2.5   # FEM_MESH: mesh size override for convergence runs
study = Study("Cage, up stop: 257 N up on the front brace at the +x pad", material="PETG", safety=2, mesh=_MESH)
for sx in (1, -1):
    for y, z in ((-127.0, 22.1), (-48.0, 26.7), (38.0, 32.8)):
        study.fix("Cage", near=(sx * 45.0, y + 3.0, z))
    study.fix("Cage", near=(sx * 38.0, -203.5, 15.6))         # front hoop leg foot (parts/cage.py HOOP_FEET)
study.force("Cage", N=(0, 0, 257.0), near=(47.5, -203.9, 102.5))       # brace underside at the pad's contact (model.py prints it)
