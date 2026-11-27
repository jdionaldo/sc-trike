"""Upper wishbone with the heave shock post (+x side, parts/wishbone.py), PETG, checked against 20 MPa across the layers.
Load case: landing on one front wheel, 65 N up plus 30 N sideways toward the vehicle at the tyre contact (x 144, z -15.6), as in analyses/front_arm.py.

Free body of the knuckle (xz plane, ball joints at x 106, upper z 70, lower z 42, spacing 28, scrub 38): the lower arm is level and turns freely
about its pivot rod, so it only pushes or pulls along x (L). Moments about the upper ball: contact lever (38, -85.6) mm,
-85.6 x (-30) - 38 x 65 = 2568 - 2470 = +98 N mm, balanced by -28 x L: L = +3.5 N on the knuckle. Upper ball on the knuckle: x = 30 - 3.5 = 26.5 N, z = -65 N.
So the knuckle loads the upper arm at its ball (106, -216.55, 70) with (-26.5, 0, +65) N.

Free body of the upper arm: 65 N at 94 mm from the pivot axis (x 12, z 70) = 6110 N mm about the pivot rod. The heave shock lies level along x and
holds the post eye (34, -190.3, 94), SHOCK_H = 24 mm above the axis: S = 6110 / 24 = 254.6 N toward +x (the compressed shock pushes the eye outboard),
half on each fork cheek (the x position of the eye does not matter for a level force). Pivot reaction: (-228.1, 0, -65) N.

In the study: held at the outer end faces of the two pivot bosses (y -191.8 and -167.8, flat faces: the pivot bore is one curved face that the
mesher did not match), the shock force on the flat outer faces of the two eye cheeks (y -194.7 and -185.9). The ball sits 9 mm outboard of the arm's end face (x 97) on the ball cup, whose
shank is screwed into the apex bore (x 82 to 97). 65 N at x 106 is put on the arm as a couple: -78 N on the bore (centre x 89.5) and +143 N on the end
face (x 97), together 65 N acting at x 106. The 26.5 N side force goes on the bore."""
import os
from soma.fem import Study
_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else 1.5   # FEM_MESH: mesh size override for convergence runs
# the shock force is applied on the outer side face of each fork cheek (the pin bore faces cannot be selected in the mesh)
# Load basis (NOTES, November 26): car 3.09 kg from the model (sliced kit 1866 g + bought parts), CG at y -41.4: 61.3 % front, 38.7 % rear;
# landing 8.5 g (0.30 m drop stopped over the 35 mm wheel travel). The loads below were written for 2.6 kg / 60 %: K scales them.
K = 1.216   # front wheel 79.0 N for 65 N: 3.09 kg x 0.613 / 2 x 9.81 x 8.5 / 65
study = Study("Upper wishbone, one-wheel landing: 65 N up + 26.5 N in at the ball, 254.6 N shock at the post eye", material="PETG", safety=2, mesh=_MESH)   # 2.0 gave 10 distorted elements at the edge breaks (Nov 24)
_force = study.force
study.force = lambda part, N, **kw: _force(part, N=tuple(K * n for n in N), **kw)
# supports as the pivot rod gives them: the bore carries the radial loads (x, z), the two thrust collars only hold the arm along the rod (y)
study.fix("Upper arm 1", faces="%CYLINDER", near=(15.0, -177.2, 73.1), axes="xz")
study.fix("Upper arm 1", near=(15.0, -189.16, 74.5), axes="y")
study.fix("Upper arm 1", near=(15.0, -165.16, 74.5), axes="y")
study.force("Upper arm 1", N=(-26.5, 0, -78.0), near=(89.5, -216.55, 72.05))
study.force("Upper arm 1", N=(0, 0, 143.0), near=(97.0, -216.55, 74.0))
study.force("Upper arm 1", N=(126.0, 0, 0), near=(34.0, -191.1, 95.0))
study.force("Upper arm 1", N=(126.0, 0, 0), near=(34.0, -175.3, 95.0))
