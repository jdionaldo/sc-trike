"""Read-out (November 25): the global maximum sits on the rigid held / loaded faces and grows with the mesh (singular); the result is read away
from them with `python tools/fem_away.py .soma/results/<this>.glb D` (D = 2 element sizes, at least 2 mm) at two meshes (FEM_MESH), see NOTES.
Front knuckle (+x side, parts/wishbone.py), PETG, checked against 20 MPa across the layers.
Load case: landing on one front wheel, 65 N up plus 30 N sideways toward the vehicle at the tyre contact (x 144, z -15.6), as in analyses/front_arm.py.

The wheel passes the load into the 6 mm axle pin, the pin into the axle bore (x 112.5 to 142, z 40.6, centre x 127.25). Moved to the bore centre the
contact force (-30, 0, 65) N has the lever (16.75, -56.2) mm: moment about y = -56.2 x (-30) - 16.75 x 65 = 1686 - 1089 = +597 N mm. The pin's couple
is put on as two vertical forces 14.75 mm apart: +105.5 N on the bore (x 127.25) and -40.5 N on the boss end face (x 142): together 65 N up and
597 N mm. The 30 N side force goes on the bore.

Reactions expected (free body, ball studs at x 106, z 70 and 42): upper stud (+26.5, 0, -65) N on the knuckle (the upper arm carries the wheel load),
lower stud +3.5 N in x only (the lower arm is a two-force member). The support forces of the run should come out close to these.

Tie rod: none in this load case. The contact point lies at the kingpin's y (no trail) and both forces lie in the xz plane, so they have no moment
about the kingpin. A fore-aft force F at the contact would turn the knuckle with 38 mm x F and load the tie rod (lever 71.55 mm from the kingpin to
the steering ball at y -145) with 0.53 x F. The servo cannot load it harder than its stall torque allows: 15.5 kg cm on the 51 mm horn is 30 N.

In the study: held at the two M3 heat-set insert pockets of the ball studs in the upright plate (both set from the back, y -203.05 to -195.55, where the studs' threads pull): the upper one in x, y, z, the lower one
in x only. The studs' balls sit 8.5 mm ahead of the plate face; that offset is not modelled (the bores are held where they are)."""
import os
from soma.fem import Study
_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else None   # FEM_MESH: mesh size override for convergence runs
# Load basis (NOTES, November 26): car 3.09 kg from the model (sliced kit 1866 g + bought parts), CG at y -41.4: 61.3 % front, 38.7 % rear;
# landing 8.5 g (0.30 m drop stopped over the 35 mm wheel travel). The loads below were written for 2.6 kg / 60 %: K scales them.
K = 1.216   # front wheel 79.0 N for 65 N: 3.09 kg x 0.613 / 2 x 9.81 x 8.5 / 65
study = Study("Knuckle, one-wheel landing: 65 N up + 30 N in at the tyre contact, through the axle bore", material="PETG", safety=2, mesh=_MESH)
_force = study.force
study.force = lambda part, N, **kw: _force(part, N=tuple(K * n for n in N), **kw)
if os.environ.get("FEM_KN_SUPPORT") == "cyl":       # Nov 24 variant: on the insert pocket walls only
    study.fix("Knuckle 1", faces="%CYLINDER", near=(106.0, -199.3, 72.1))
    study.fix("Knuckle 1", faces="%CYLINDER", near=(106.0, -199.3, 44.1), axes="x")
else:                                                # the original supports (eb9aa32): nearest face to the pocket points
    study.fix("Knuckle 1", near=(106.0, -201.0, 71.9))           # upper insert pocket, set from the back (D 3.8, y -203.05 to -195.55)
    study.fix("Knuckle 1", near=(106.0, -201.0, 43.9), axes="x")    # lower insert pocket, also set from the back
study.force("Knuckle 1", N=(-30.0, 0, 105.5), near=(127.0, -216.55, 43.65))
study.force("Knuckle 1", N=(0, 0, -40.5), near=(142.0, -216.55, 46.1))
