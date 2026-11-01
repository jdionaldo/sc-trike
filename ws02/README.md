# WS-02 lean-steer reverse trike (370 mm), shell from base.stl

Single source of truth: `params.py`. Parts are SolidCraft command scripts (`parts/`), built by `build.py`, validated by
`validate.py` and `tests/`. The body skin is extracted from `base/base.stl` (not in the repo).

## Status
- **Mechanism (done, 41 tests pass, no interference in the 9 lean/travel poses):** lean-steer front end on a 233 mm
  track with 83 x 24 mm tires, narrow tub (84 mm), single-sided swingarm with a fixed 2830 motor, 15T/60T spur and a
  15T/30T belt to a cantilevered 8 mm axle, 85 x 50 mm rear tire, ESC above the battery, receiver tray.
- **Body (not finished):** `shell_from_base.py` pulls the exterior skin from the base model (scaled to 370 mm, chassis
  frame) and `blender/solidify_shell.py` gives it a 2.4 mm wall; `blender/split_shell.py` splits it into left and right
  halves (`out/rt1_body/body_left.stl`, `body_right.stl`, each about 184 x 58 x 88 mm, bed-legal). The skin is not
  watertight (the base model is a surface with internal frames), so the halves need a manual repair pass in a mesh tool
  before slicing. Not built: nose fairing, tail wing, body-to-chassis fixings, interference checks against the repaired shell.
- **Not done:** mass/CG and tip-over report (needs the repaired shell), print plan and BOM refresh, shock tower, ESC tray.

## Layout
params.py, kinematics.py, cad.py, parts/*.py, build.py, validate.py, assembly.py, renders.py, report.py, sc_scene.py,
shell_from_base.py, blender/*.py, tests/.
