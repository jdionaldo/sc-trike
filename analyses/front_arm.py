"""Front swing arm (+x side), PETG, treated as solid PETG across the layers (20 MPa).
Held at the two pivot bores (D5.4, y -116.8, z 47.5). At the tip shaft holes (D4.3, y -216.6, z 40.6) the wheel load of a landing: 65 N up (about 8 g on one front
wheel of a 2.6 kg vehicle, 60 % on the front axle) plus 30 N sideways toward the vehicle (cornering), split over the two plates.
The front shock reacts the bump. Since the passive lean beam (parts/lean_beam.py) the shock lies almost level, from the clevis on a 7 mm post on the U1 node to the beam end:
its line passes 24.2 mm from the pivot axis, so F = 65 N x 100 / 24.2 = 268 N along the shock axis, split over the two pin holes."""
from soma.fem import Study
study = Study("Front arm, 65 N bump + 30 N side at the tip, 268 N shock force at the clevis", material="PETG", safety=2)
study.fix("arm 1", near=(66.2, -116.8, 47.5))
study.fix("arm 1", near=(89.5, -116.8, 47.5))
study.force("arm 1", N=(-15.0, 0, 32.5), near=(66.2, -216.6, 40.6))
study.force("arm 1", N=(-15.0, 0, 32.5), near=(89.5, -216.6, 40.6))
study.force("arm 1", N=(30.9, -130.1, 8.4), near=(69.6, -152.9, 74.9))
study.force("arm 1", N=(30.9, -130.1, 8.4), near=(60.4, -155.1, 74.9))
