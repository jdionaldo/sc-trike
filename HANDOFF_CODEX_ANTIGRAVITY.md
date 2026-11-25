# Project Fugu: handoff for Codex and Antigravity (SOMA)

Project folder: `/Users/johndionaldo/GitHub/sc-trike/Project_Fugu`. Branch: `shell/defect-sweep`. Never merge to main, never rewrite history, never create branches.
App: `/Applications/SOMA.app` (CadQuery code-CAD). The model is `model.py` plus `parts/`. Read `AGENTS.md` and `.soma/skills/*.md` before changing anything.

## How to work here (applies to both tools)

1. Use the SOMA Python: `export PATH=/Applications/SOMA.app/Contents/Resources/python/bin:$PATH`. No virtual environments.
2. `soma build` after every change (about 4-5 min). It must end with "Build ok". Then `python tools/collide.py`: it must report `0 overlapping pairs`.
3. After a successful build and a clean collision check: `git add -A` and `git commit -m "<what changed>"`. One commit per working iteration.
4. `soma render` only works from a terminal inside the SOMA app. Outside the app, render with the VTK scripts (see "Rendering" below).
5. Do not delete any files from the computer without the owner's explicit approval. Work only inside this project.
6. Units are mm, Z is up, front faces -Y. Dimensions are named constants in `parts/params.py` or at the top of each part module.
7. Standing quality bar: market-ready, no defects, everything assembles without modification and prints on Bambu printers. No shortcuts.
8. The owner reads on an iPad: show every visual change as a picture.

## Frames (a common source of mistakes)

- `chassis_ref.step` nodes are in the "ref" frame. World = ref + (0, CHASSIS_Y = 9, CHASSIS_Z = -15.3). So ref y = world y - 9, ref z = world z + 15.3.
- Stand-in node names use spaces (`steer horn 1`); built assembly part names use underscores (`Chassis/Steering/tie_rod_1`).
- Cage and shells are built in world coordinates.

## Done in this branch (latest first)

| What | Where | Status |
|---|---|---|
| Front bull bar (chamfered square tubes, same section as the cage): bumper hoop at y -326 with top, mid and bottom crossbars, two uprights, two diagonals; upper rail (kink at y -250, level at z 88 so it stays under the nose light strip at z 96.2+) to the front hoop outrigger; lower rail to the front foot post; brace between rails. The nose and grille insert get 0.6 mm slots for the tubes. | `parts/cage.py` (`add_guard`, `guard_members`, `guard_cutter`, `GUARD_*` constants, `ENABLE_GUARD`), slot cut in the stealth block of `model.py` | Built, 0 overlaps. Not FEA'd. Not in the kit yet. |
| Canopy roof/pillar line (cowl post, roof front, roof peak, B-foot) chamfered 4 mm; the four canopy locating tabs removed | `parts/stealth_shell.py` (`CANOPY_EDGE_CHAMFER`, `CANOPY_TABS = False`) | Built, committed d05d51f |
| Rear-deck wall bends in (plan view) to the tail wall, closing the slit; front deck corner gussets close the triangles beside the skid | `parts/deck_walls.py` (`TAIL_X`, `TAIL_JOIN_Y`), `model.py` (deck gusset block) | Built, committed d05d51f |
| Wheel arch front edge moved from y -263 to -240 | `parts/stealth_shell.py` (`ARCH_FRONT_Y`) | Built, committed 67e24cb |
| Steering servos low-profile (40.8 x 20.2 x 26.5), moved 6 mm outboard (`STEER_OUT`), tie rod slotted around the horn, horn screw clearance, front deck lifted 0.9 mm flush to the diff base with recesses | `parts/params.py`, `parts/steer_hw.py`, `model.py` | Committed |
| Walls trace the user's drawn line, tail deck debris walls | `parts/deck_walls.py` | Committed |
| Amazon sourcing scan | `kit/sourcing_amazon.md` | Committed; nothing verified for fit |

## Still to do (priority order)

1. **Yeti-style rear cage and shorter back.** Redesign the rear cage like the green Axial Yeti (owner supplied two reference images in the conversation), and shorten the body and cage so they end about mid rear tyre: rear tyre centre y is about 236, the body now ends at y 257. The rear tail tube network in `make_cage()` (`tail`, `tail_low`, `tail_screws`, shock clevis `tie`, `supports`) is coupled to the tail light housing screws and the rear shock top pin carried by the cage clevis. Change them together. Keep the shock pin corridor open.
2. **Shell sides cover the tub.** Update the shell proportions (`parts/stealth_shell.py`: `ROCKER`, `CHINE`, belly) so the side of the shell covers the tub. Check the front arm sweep and the lock/bump travel after the change.
3. **Wheel arch check.** The arch now starts at y -240. Verify with a full-lock and full-compression sweep (`tools/` has the relief tools; the scratch scripts `sweep_all.py` and `battery.py` are not in the repo) that the opening is not narrower than the tyre at full lock under compression.
4. **ESC and RX shelves.** Owner wants "receiver and electronic speed controller shelves ... at either side of the motor" removed. They could not be found in the model. Ask the owner for a marked screenshot (or search `parts/` and the chassis_ref.step node names for 'shelf', 'esc', 'rx', 'receiver').
5. **Front roll cage additions.** The bull bar adds the front structure; the owner also asked for "any additional roll cage around the front". Consider A-pillar to bull bar triangulation and a front cross tube, then run the strength check.
6. **Strength.** Cage and bull bar have not been through FEM (`.soma/skills/fem.md`, `soma analyze fem analyses/x.py`). The front arm is at 95 % of allowable.
7. **Kit regeneration.** After the geometry is final: `soma export`, `kit/build_kit.py`, `kit/mesh_audit.py`, `kit/make_manifest.py`, `kit/bambu_kit.py --check`, `kit/make_docs.py` (about 10+ min; run in the background). The kit still uses the P2S profile (`kit/p2s_profile.config`, bed 256). H2C-class plates (330 x 320 x 325, `kit/print_h3c`) are unvalidated: Bambu Studio needs an H2C project profile, which the owner must export. The `sc/` folder (the "sc file") was not refreshed. The bill of materials and assembly manual need the new bull bar, canopy changes and servo.
8. **Open checks.** Two unexplained hole sets (front arm r 2.7 at (89.5, -116.8, 47.5); rear arm three r 1.4 at x 72.8, y 238-247), a few tight fits, the rear light block touching the canopy, stale untracked files in `sc/`.

## Rendering without the app

`soma render` needs the running app. Otherwise load `output/model.step` with `soma.import_assembly`, tessellate each part (`shape.tessellate(0.3, 0.3)`) and draw it with VTK offscreen (`vtkRenderWindow.SetOffScreenRendering(1)`), one colour per part group. Do not read raw mesh or STEP data into the model's context.

## For Codex

- Run from the project folder in a terminal with the SOMA Python on PATH. Codex reads `AGENTS.md` automatically: it already holds the project rules. This file adds the current state.
- Work one open item at a time. Edit with small diffs; do not rewrite `model.py` (it is long). Keep part code in `parts/`.
- Per item: change, `soma build`, `python tools/collide.py`, render, commit. Stop after three failed attempts at the same fix and report the evidence.
- Boolean pitfalls on this model: fusing translated copies to grow a solid can give invalid solids on NURBS shapes (use plain cuts and keep the largest solid); shear transforms make NURBS that later booleans reject; OCC's chamfer crashes on the stealth shell (the code uses stepped planar cuts instead).

## For Antigravity

- Open the folder as the workspace and point the agent at `AGENTS.md`, this file and `.soma/skills/`. Run the terminal commands above from the workspace terminal.
- Use it for the visual and review side: render the views listed under "Rendering without the app", compare against the owner's markup images in `.soma/feedback/`, and write findings back as concrete geometry changes (part, constants, mm values).
- Let the agent that edits `model.py` be the same one that runs `soma build`; do not run two builds at the same time (they write `output/model.step`).
- Do not let two agents edit the same file at once.
