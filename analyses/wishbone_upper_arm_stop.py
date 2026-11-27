"""Upper wishbone (+x, parts/wishbone.py) at its up stop (lean stop), PETG, checked against 20 MPa across the layers.
At lean 10 deg with this side up plus 12 mm bump the arm's front leg top meets the TPU pad under the cage's front brace (parts/stops.py
up_stop_pad). The contact, turned back to the arm at rest, is at (55.9, -205.4, 82.9) (model geometry of 2026-11-26); the pad pushes against the
arm's motion there, (0.30, 0, -0.95) at rest. Load: the stop load of analyses/cage_upstop.py, 257 N (equilibrium would need 143 N against the
one-wheel landing's 6110 N mm on this 42.7 mm lever: on the safe side), plus the one-wheel landing at the ball as in analyses/wishbone_upper_arm.py;
the heave shock is left out (at the stop its force is shared, here all of it goes to the stop). Supports as in analyses/wishbone_upper_arm.py."""
import os
from soma.fem import Study
_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else 1.5
_F = float(os.environ.get("FEM_STOP_N", "257"))       # FEM_STOP_N: 143 = the arm's own balance (NOTES), 257 = the margin case
_STOP_N = (0.30 * _F, 0, -0.95 * _F)
# Load basis (NOTES, November 26): car 3.09 kg from the model (sliced kit 1866 g + bought parts), CG at y -41.4: 61.3 % front, 38.7 % rear;
# landing 8.5 g (0.30 m drop stopped over the 35 mm wheel travel). The loads below were written for 2.6 kg / 60 %: K scales them.
K = 1.216   # front wheel 79.0 N for 65 N (landing at the ball); the stop load is not scaled
study = Study("Upper wishbone at the up stop: %.0f N stop load" % _F + " on the front leg + one-wheel landing at the ball", material="PETG", safety=2, mesh=_MESH)
_force = study.force
study.force = lambda part, N, **kw: _force(part, N=tuple(K * n for n in N), **kw)
study.fix("Upper arm 1", faces="%CYLINDER", near=(15.0, -177.2, 73.1), axes="xz")
study.fix("Upper arm 1", near=(15.0, -189.16, 74.5), axes="y")
study.fix("Upper arm 1", near=(15.0, -165.16, 74.5), axes="y")
study.force("Upper arm 1", N=(-26.5, 0, -78.0), near=(89.5, -216.55, 72.05))
study.force("Upper arm 1", N=(0, 0, 143.0), near=(97.0, -216.55, 74.0))
_force("Upper arm 1", N=_STOP_N, near=(55.9, -205.4, 82.9))   # stop load as given (FEM_STOP_N): 257 margin case; the balance is now 143 x 1.216 = 174 N
