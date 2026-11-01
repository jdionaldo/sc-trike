# WS-03: 3WD lean-steer reverse trike (current design)

The 233 mm single-servo design below is the earlier WS-02 build and is kept for reference. The current build is WS-03: three-wheel drive
(centre diff, bevel front diff, bevel rear), swing-arm lean and steer with four servos, a 269 mm front track (stable in sharp turns),
a 4 degree nose-down rake, a procedural faceted body from the base.stl silhouettes, slotted decks and a servo wall.

- `SPEC3WD.md` design decisions and status, `WS03_REPORT.md` printed parts and numbers, `WS03_BOM.md` bought parts.
- Build and check: `PYTHONPATH=. python body3_build.py && python split_shell3.py && pytest tests/test_w3.py`.
- Modules: `front3wd.py` (arm kinematics), `parts/w3_front.py`, `parts/w3_drive.py`, `parts/w3_chassis.py`, `w3_scene.py` and `w3_assembly.py`
  (placement and interference), `layout3wd.py` (block layout), `body3_build.py`.

---

# WS-02 lean-steer reverse trike (370 mm) with a base.stl shell

Single source of truth: `params.py`. Mechanism parts are SolidCraft command scripts (`parts/`), built by `build.py` and checked by
`validate.py` and `tests/` (65 pass). The body is the exterior skin of `base/base.stl` (not in the repo) turned into a watertight
shell by `shell_from_base.py` and `mono_shell.py`, fused with the tub and cradle by `mono_build.py`.

## What it is
- Lean-steer front end on a 233 mm track (83 x 24 mm tires), one servo drives lean; a steer servo per front wheel sits on the lower lean bar and drives the knuckle through a short tie rod (radio mixes lean into steer, so three servo channels).
- Fixed 2830 motor in a narrow cradle, 15T/60T spur and a 15T/30T GT2 belt in a single-sided swingarm, cantilevered 8 mm axle,
  85 x 50 mm rear tire, small bolt-on `swingarm_cover`. ESC above the battery, receiver tray, placeholder envelopes for all bought parts.
- Body: `mono_left` and `mono_right` (shell + tub + cradle fused, watertight, 226 x 62 x 115 mm, supports, print turned on the bed),
  `canopy_lid` over the battery/ESC/receiver bay, tail hood over the cradle so nothing protrudes at the rear.
- No interference in the 9 lean and travel poses; mass about 865 g, CG about 60 mm above ground, tip-over margin about 0.75 g.

## Not done
- A more compact lean-steer mechanism (cantilever style). A 175 mm track version of the current linkage collides; it needs a
  new linkage, not a rescale. The front end, yoke and ear still stand ahead of the shell (no nose fairing yet).
- Nose fairing, body fixings (pins/screws between the lid and shell), shock tower, ESC tray, motor-side cooling vents, wiring layout.
- The shell is a voxel-smoothed copy of the base skin: facets are slightly rounded.

## Build
`uv venv --python 3.12 .venv`; install numpy scipy trimesh manifold3d shapely networkx scikit-image matplotlib pytest rtree;
`PYTHONPATH=. python build.py` then `python mono_build.py` (needs `out/base_split/ext_final.stl` from `shell_from_base.py`, Blender for
`blender/solidify_shell.py`), `python -m pytest tests`, `python report.py`.
