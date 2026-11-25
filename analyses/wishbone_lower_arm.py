"""Lower wishbone (+x side, parts/wishbone.py), PETG, checked against 20 MPa across the layers.
Load case: front wheel with 65 N up and 30 N sideways toward the vehicle at the tyre contact (x 144, z -15.6), as in analyses/front_arm.py.

The lower arm is level and turns freely about its pivot rod (the heave shock sits on the upper arms), so it is a two-force member along x.
Free body of the knuckle (ball joints at x 106, upper z 70, lower z 42, spacing 28, scrub 38), moments about the upper ball, contact lever (38, -85.6) mm:
  side force alone:  -85.6 x (-30) = +2568 N mm  ->  91.7 N compression in the lower arm
  bump alone:        -38 x 65      = -2470 N mm  ->  88.2 N tension
  both together:                      +98 N mm   ->   3.5 N compression (the two almost cancel)
The landing with both forces would leave the arm nearly unloaded, so the study uses the larger single part: 91.7 N compression (30 N side force
without the bump: cornering). The knuckle pushes the arm toward the vehicle: (-91.7, 0, 0) N. The result is linear: the bump alone is the same
picture with the sign turned and 4 % less, the combined landing 4 % of it. Buckling is not part of this calculation.

In the study: held at the outer end faces of the two pivot bosses (y -191.8 and -167.8, flat faces: the mesher did not match the rear bore face), the force on the apex bore that holds the ball cup's shank (x 82 to 97; the
force line is the bore axis, so no couple is needed)."""
from soma.fem import Study
study = Study("Lower wishbone, 30 N side force at the tyre contact: 91.7 N push along x at the ball", material="PETG", safety=2, mesh=2.0)
# supports as the pivot rod gives them: the bore carries the radial loads (x, z), the two thrust collars only hold the arm along the rod (y)
study.fix("Lower arm 1", faces="%CYLINDER", near=(15.0, -177.2, 45.1), axes="xz")
study.fix("Lower arm 1", near=(15.0, -189.16, 46.5), axes="y")
study.fix("Lower arm 1", near=(15.0, -165.16, 46.5), axes="y")
study.force("Lower arm 1", N=(-91.7, 0, 0), near=(89.5, -216.55, 44.05))
