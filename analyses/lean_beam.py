"""Lean balance beam (parts/lean_beam.py), PETG, printed flat (loads run along the layers, but checked against 20 MPa across the layers to stay on the safe side).
Held at the pivot bore (M4, x 0, y -109.6, z 72.5). Both shocks push their beam end at once (two-wheel bump, 65 N per wheel): 268 N along each shock axis,
split over the two pin holes of each clevis. In lean the beam turns freely and carries no load."""
from soma.fem import Study
study = Study("Lean beam, both shocks 268 N (two-wheel bump)", material="PETG", safety=2)
study.fix("Lean beam", near=(0.0, -109.6, 72.45))
for sx in (1, -1):
    for x, y in ((62.0, -120.8), (52.8, -123.0)):
        study.force("Lean beam", N=(sx * -30.9, 130.1, -8.4), near=(sx * x, y, 72.8))
