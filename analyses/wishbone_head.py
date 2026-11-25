"""Lean head (parts/wishbone.py, seated on the deck in model.py), PETG, checked against 20 MPa across the layers.
Load case: landing on BOTH front wheels, each 65 N up plus 30 N sideways toward the vehicle at the tyre contact (x +-144, z -15.6).
Why both: the single heave shock sits between the two upper arms, so a wheel load is only held statically when the other arm pushes back with the same
shock force. With both wheels loaded every pivot rod carries its full load and the deck screws carry 130 N instead of 65 N: the worse case for the head.
(One wheel alone would give the same rod loads on that side and 224.6 N sideways on the screws, if something else held the other arm.)

Per side (+x written, -x mirrored), from the free bodies in wishbone_upper_arm.py and wishbone_lower_arm.py:
  upper arm on its rod: ball load (-26.5, 0, 65) N at the ball's y (-216.55) and shock load (+254.6, 0, 0) N at the post eye (y -190.3)
  lower arm on its rod: (-3.5, 0, 0) N at y -216.55
The rods (shoulder screws) rest in the front post (y -196.6) and the rear post (y -163.0), span 33.6 mm, as beams on two supports. The balls lie
19.95 mm AHEAD of the front post (overhang), so the front post gets more than the whole ball load and the rear post is pulled the other way:
  loads at y -216.55: front share 1.594, rear share -0.594        shock load at y -190.3: front 0.8125, rear 0.1875
  upper front bore (+164.6, 0, +103.6)   upper rear bore (+63.5, 0, -38.6)      sum (228.1, 0, 65) N
  lower front bore (-5.6, 0, 0)          lower rear bore (+2.1, 0, 0)           sum (-3.5, 0, 0) N
The x loads of the two sides cancel inside the head (the upper rods are pushed apart with 228 N each).

In the study: held at the flat top faces of the base tube ends around the four M3 insert bores (x +-28, y -196.6 and -163.0; the bore faces
themselves were not matched by the mesher, the deck under the base tubes is not counted),
loads on the eight rod bores."""
from soma.fem import Study
# held on the undersides of the base tubes, where the four M3 screws clamp them to the deck
study = Study("Lean head, two-wheel landing: pivot rod loads of both sides (65 N up + 30 N in per wheel)", material="PETG", safety=2, mesh=2.0)
for sx in (1, -1):
    study.fix("Lean head", near=(sx * 16.0, -195.28, 19.0))
    study.fix("Lean head", near=(sx * 28.0, -159.04, 21.5))
    study.force("Lean head", N=(sx * 164.6, 0, 103.6), near=(sx * 15.0, -195.28, 73.05))
    study.force("Lean head", N=(sx * 63.5, 0, -38.6), near=(sx * 15.0, -159.04, 73.05))
    study.force("Lean head", N=(sx * -5.6, 0, 0), near=(sx * 15.0, -195.28, 45.05))
    study.force("Lean head", N=(sx * 2.1, 0, 0), near=(sx * 15.0, -159.04, 45.05))
