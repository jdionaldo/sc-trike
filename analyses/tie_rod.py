"""Steering tie rod (+x side), PETG, 8 x 8 mm chamfered square tube with an eye at each end. Held on the two flat faces of the horn-side eye (y -105), 101 N along the rod
(servo stall load through the horn) on the three flat faces of the knuckle-side end, split by area. Tension; compression is checked for buckling by hand."""
from soma.fem import Study
import numpy as np
A = np.array((103.3, -214.8, 14.5)); B = np.array((68.6, -104.0, 21.6))
d = (A - B) / np.linalg.norm(A - B)
study = Study("Tie rod, 101 N along the rod", material="PETG", safety=2)
study.fix("tie rod 1", near=(68.6, -105.1, 24.0))
study.fix("tie rod 1", near=(68.6, -104.8, 19.0))
for share, p in ((0.58, (104.0, -214.4, 14.5)), (0.21, (103.1, -214.9, 18.0)), (0.21, (103.1, -214.6, 11.0))):
    study.force("tie rod 1", N=tuple(101.0 * share * d), near=p)
