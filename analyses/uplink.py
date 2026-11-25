"""Front upper link (+x side), PETG, 8 x 8 mm chamfered square tube with solid ends, 6 mm tongues and M3 hinge holes (parts/uplink.py).
Held at the inner hinge hole (68.5, -119.4, 97.9), 80 N along the link at the outer hinge hole (105.0, -219.3, 91.0) (share of the landing load carried by the link, ASSUMED
as in analyses/strength_check.md). Tension; compression is checked for buckling by hand."""
from soma.fem import Study
import numpy as np
A = np.array((105.0, -219.3, 91.0)); B = np.array((68.5, -119.4, 97.9))
d = (A - B) / np.linalg.norm(A - B)
study = Study("Upper link, 80 N along the link", material="PETG", safety=2)
study.fix("uplink 1", near=tuple(B))
study.force("uplink 1", N=tuple(80.0 * d), near=tuple(A))
