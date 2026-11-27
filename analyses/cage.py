"""Cage (parts/cage.py), PETG, checked against the strength across the layers.
Held at the end faces of the six square feet (they sit on the pocket floors, M3 from below): front rail feet (+-45, -127, z 22.1),
rail feet (+-45, -48, z 26.7) and (+-45, 38, z 32.8). The front hoop has no feet of its own any more (wishbone front end, November 22):
it hangs from the upper belt start and the cowl corners.
One envelope load case, all at once (more than any single event, so on the safe side):
- Roll-over landing on the roof: 3.09 kg (NOTES 'Load basis') at 3 g = 95.2 N down, spread over the five roof nodes (four corners and the roof X
  centre, 19.03 N each), plus 35.7 N sideways (+x) on the two left roof corners (a roll onto the left side).
- Rear shock reaction at the clevis bore: 273 N up along the shock axis (by hand, see NOTES and analyses/rear_arm.py; was 237 / 150 / 135 N) (lower eye y 154.6 z 103.7 -> upper eye y 145.3 z 180.2), split over
  both ears (the value analyses/rear_arm.py puts on the arm).
- Front bumper tube: 47.6 N rearward (+y; 40 N at 2.6 kg, scaled by mass) on the crash bumper tube of the front hoop (a nose hit), to load the hoop that now hangs free."""
import os
from soma.fem import Study
_LOADS = os.environ.get("FEM_CAGE_LOADS", "roof,side,shock,bumper").split(",")   # FEM_CAGE_LOADS: a subset, to see which load drives a spot
_MESH = float(os.environ["FEM_MESH"]) if os.environ.get("FEM_MESH") else 2.5

study = Study("Cage, roof landing 95.2 N + 35.7 N side, rear shock 273 N, bumper 47.6 N", material="PETG", safety=2, mesh=_MESH)
for sx in (1, -1):
    for y, z in ((-127.0, 22.1), (-48.0, 26.7), (38.0, 32.8)):
        study.fix("Cage", near=(sx * 45.0, y + 3.0, z))          # foot end face (the insert pocket is in its centre)
    study.fix("Cage", near=(sx * 38.0, -203.5, 15.6))         # front hoop leg foot (parts/cage.py HOOP_FEET)
# roof landing: roof corners (cabin tube 7 mm, top face 3.1 mm above the node) and the roof X centre
for p in ((60.9, -86.9, 196.9), (-60.9, -86.9, 196.9), (45.9, 15.0, 219.9), (-45.9, 15.0, 219.9), (0.0, -36.0, 208.4)) if "roof" in _LOADS else ():
    study.force("Cage", N=(0, 0, -19.03), near=(p[0], p[1], p[2] + 3.1))
for p in ((-60.9, -86.9, 196.9), (-45.9, 15.0, 219.9)) if "side" in _LOADS else ():
    study.force("Cage", N=(17.84, 0, 0), near=(p[0] - 3.1, p[1], p[2]))
# rear shock: M6 bore in both clevis ears (x 4.4..12)
for sx in (1, -1) if "shock" in _LOADS else ():
    study.force("Cage", N=(0, -16.53, 135.65), near=(sx * 7.0, 145.3, 183.4))
# nose hit on the bumper tube (front hoop top, y -229, z about 102): front face of the tube
if "bumper" in _LOADS:
    study.force("Cage", N=(0, 47.6, 0), near=(0.0, -233.4, 102.0))
