# WS-03 cleanup: leftover objects and frame joints

Method: every ladder pad / screw hole was probed against the assembly (`w3_assembly.assembly(0, 0)`): a 1.4 mm radius probe along each screw axis on the
inboard side, and a 0.8 mm skin of each pad's inner face, intersected with every other part (printed or bought placeholder).  Dead names were found by
counting word occurrences over the W3 sources and tests (`parts/w3_*.py`, `body3_build.py`, `w3_*.py`, `tests/test_w3.py`).

## Deleted

| Object | What it was | Why dead | Checked |
|---|---|---|---|
| `PS2` stadium pad + 2 screw holes + head pockets (x -135.9, z -19/-9, both sides) | 3 mm pad with two side screws at the tube node PS2 | No servo, diff ear or deck screw reaches it (probe: only the deck's top skim of 1.6 mm3). The steering servo placeholder touches only the -92..-79 plate | probe of pads and holes; no test, FE or fit script reads it (FE uses the tube graph) |
| `PS1` stadium pad + 2 screw holes (x -35.5, z -23.8/-13.8, both sides) | same, at the front end of the lean servo run | The lean servo placeholder ends at x -40; nothing mounts at -35.5 (only a 14 mm3 skim of the deck) | same |
| `PE1` pad and its diff-ear pilot on the -y side | 15 mm pad with a pilot for the front diff case's rear ear | The front diff case has its ears on +y only (`w3_drive.front_diff_case`); on -y nothing touches (probe 0 mm3). Kept on +y (103.9 mm3 contact, live screw) | probe; the -y node is now a plain ball |
| `_stadium()` | helper for the two pads above | no users left | grep |
| dead code after the cuts loop in `frame()` (`ax`, import of `NOSE_TH`) | leftover from the skid-pad refactor | unused | grep |
| `M25` in `parts/w3_drive.py` | tap-size constant | no users | grep |
| `_cut_edge()` in `parts/w3_style.py` | skin chamfer helper from an earlier body | no users | grep |

## Checked and kept

| Object | Result |
|---|---|
| hood-tab magnet pad (`_tab_pos()[3:]`) | **live**: `body3_build.details` puts the skin boss and matching magnet pocket over it (the hood is held by hinge + magnets) |
| `FEET` (FS, FP1, FPB, FPR, FPF) | all live: each has a matching deck hole generated from `feet_xy()`, so removing one would leave a cage node floating over the plate; they carry the FE boundary conditions |
| `HOUSING_BOLTS` | every entry has a matching `hole_z` in `w3_drive` (front 4, centre 4, rear 4), so none is unused |
| `w3_uplink_standoff` | live: spacer between the pivot pad (|y| 57.6) and the upper link on the pivot pin (`w3_scene` uplink, `w3_assembly`) |
| `w3_motor_plate` | motor mount at x -236, touching `b_motor`.  **Dead once the Fusion SE motor moves forward**; left for that change, which also moves the screws through the bulkhead |
| servo-ear plate x -92..-79 | live: touches both servo placeholders (10.0 and 5.7 mm3) and the diff ear (66 mm3).  Will be revisited when the four servos become two |
| pivot-pad stack at PL (two 16 mm discs) | live: standoff and uplink sit on it (probe: standoff within 3 mm) |
| unused functions in `parts/w3_tail.py` (`foot_z`, `_panel_matrix`, `_decimate`, `_lower_z`, `_chamfered_prism_uw`) | dead by grep, **not deleted here** to avoid merge conflicts with the wheelbase change, which edits that file; delete after the merge |

## Joint changes (`parts/w3_frame.py`)

* Servo-ear plate: sharp corners rounded (2 mm radius).
* Hinge lug plate: 3.0 to 4.5 mm thick (`HINGE_LUG` y 9.5..14, inboard side is free of the skin); the gusset web follows it.  The ligament round the 3.2 mm pin hole is unchanged in height but the section is 50 % thicker.
* Hood tab pad: 9 to 10.4 mm diameter (wall round the 6.3 mm magnet pocket 1.35 to 2.05 mm), flared to the node ball with a hull (same idea as the feet) instead of a bare cylinder poking out of the ball.
* Feet: already filleted (previous commit), unchanged.  Tube ends: every end is a sphere, a ball, or a pad that the tube is trimmed back to; unchanged.

## Joint check (`w3_joint_check.py`)

* The cage is one connected body (components 1), both printed pieces are single watertight bodies.
* Thinnest sections: tubes 6.0 mm (r 3), ladder pads and feet discs 3.0 mm, hinge lug 4.5 mm, magnet-pad wall 2.05 mm.  The wall screen (`thin_spots`) also marks pad/tube creases and screw-head pockets as "< 3 mm": those are concave corners with a pad or pocket wall of at least 2 mm, not stand-alone thin webs.
* Strength (`w3_strength.py`): tube frame factor of safety 2.7 (9.4 MPa, 1.14 mm), rear arm 5.2: identical to before, because the changes do not touch the beam graph.

## Test status

See the commit message / final report for the results of `pytest tests/test_w3.py`, the 35 degree swing run and `w3_clearance.py`.
