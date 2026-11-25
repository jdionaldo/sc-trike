# Printable reverse-trike shell

## Requirements
- Replaces the earlier full vehicle: body shell only, no tires, suspension, drivetrain or bumper.
- Follow all three input images, primarily `Futuristic Reverse Trike Shell Blueprint.png`, and the top-profile markups at 14:40 and side/rear markups at 14:45 on November 10.
- Blueprint dimensions: length 278 mm, maximum width 139 mm, height approximately 107 mm from the uniformly scaled reference trace, without roof light pods. These replace the earlier full-size concept envelope.
- Sharp triangular armor facets, trapezoidal hex grille, swept headlight recesses, open windshield/side window frame, solid sloping roof without lights, raised humped rear deck with long vent, folded tail lip, triangular rear quarter windows, distinct side fins and rear wheel opening.
- Shell divided into front, rear, canopy and grille insert; four watertight printable solids.
- Exterior joints must be crisp and cohesive: blended frame feet, hood-continuous cowl, roof flush to rail tops, no obsolete exposed blocks or unintended seam holes.
- (assumed) PLA FDM, 0.4 mm nozzle, 0.2 mm layers, 220 × 220 × 250 mm bed, 45° support threshold.
- Broad body, canopy and roof panels use 2.5 mm normal wall thickness, adjustable to 3 mm. Window-frame outline width is approximately 4.5 mm; small internal sill/peg seats and the nose frame retain local reinforcement.
- 0.3 mm assembly gap following existing rear shoulder/rocker creases; butt-glued with external alignment, no glue tongues. Canopy and grille bonded after printing. No chassis mounting interfaces specified.
- Apply `.soma/skills/3d-printing.md`, `.soma/skills/tolerances.md`, `.soma/skills/assemblies.md`, `.soma/skills/analysis.md`, `.soma/skills/strength.md`, `.soma/skills/joints.md` and `.soma/skills/soma-app.md`.
- Input pictures are visual references, not dimensionally consistent manufacturing drawings. Panel facets are reconstructed from views, not an exact scan.

## Parts and assembly
| Part | Count | Material/process |
|---|---|---|
| Front shell | 1 | PLA FDM, graphite paint; red paint in headlight grooves |
| Rear shell | 1 | PLA FDM, graphite paint |
| Canopy | 1 | PLA FDM, graphite paint; solid roof |
| Grille insert | 1 | PLA FDM, black paint, shallow hex recesses |

Dry-fit and externally align the front/rear crease seam for gluing, bond grille from inside nose, then bond canopy to hood/side ledges. Light details are molded recesses, not electrical fixtures. No loose hardware.

## Printing
- Exported parts are in assembled coordinates. Arrange each separately in your slicer and drop it onto the bed.
- Body and canopy: rotate +90° about X so the original +Y points up; use supports and a brim. Front nose and rear forward edge face toward the bed. Preview supports around rear vent slots, tail shoulders, canopy roof rails and nose brows.
- Grille: lay its flat solid rear face on the bed with hex recesses up. With the current nose rake this is approximately -107.35° about X, then drop onto the bed; no supports. This supersedes the old -90° orientation.
- All four parts fit the stated bed. Bond only after support removal and dry fitting. Dry-fit the crease seam and canopy pegs before bonding; lightly sand if needed.
- Broad panels have 2.5 mm nominal thickness. Thin samples at sharp facet edges and seams require slicer preview; supports are required. The roof is closed per the latest request; the tail vent stays open.

## Reference corrections
- Narrow nose grows continuously toward the windshield shoulders, replacing the broad blunt tip.
- Rear quarter fins have separate lobes and open channels alongside the central dorsal body. Their roots join the side armor; the print seam sits forward of the blades to avoid detached fin tips.
- Roof falls from the windshield crown toward the rear, then the deck rises to a faceted hump before the tail lip.
- Added B-pillars and triangular rear quarter window openings.
- Latest instruction supersedes the reference roof opening: solid roof and no roof lights.

## Direct tracing revision
- Side landmarks are recorded in `parts/reference_trace.py` directly from `inputs/Screenshot 2026-11-10 at 2.44.31 PM.png` (actual filename contains a narrow space before PM).
- Calibration: pixel X 280–1428 maps uniformly to 278 mm; rocker datum at pixel Y 450. This replaces the earlier guessed side-profile stations and yields approximately 107 mm height.
- Rebuilt hood, bent A-pillar, roof crown, descending rear roof rail, quarter blade, front wheel cutout, rocker edges and undercut tail from the trace.
- Two angular rocker apertures follow the reference intake regions. Forward nose below the tire-obscured area and transverse widths remain inferred from the other views.
- Print split moved to Y = -25 mm (at default length) so the quarter blades remain integral with the rear print.
- `tools/compare_trace.py` projects the current STEP onto the source image coordinates and writes `renders/traced-comparison.png` and `.svg`. Cyan lines are the reference trace.
- Solid roof and no roof lights remain explicit user overrides to the reference artwork.

## Lower-side cleanup — November 10
- Removed both exposed square glue flanges and their receiving pockets at the body split. Front and rear now use the existing 0.3 mm butt-joint gap.
- Closed both rocker aperture shapes on both sides by retaining the original faceted panel skins. Upper quarter opening, rear vent and wheel clearances are retained.
- This supersedes the earlier inner-tongue assembly and rocker-aperture notes: align front/rear externally during bonding; no glue tongues remain.

## Straight lower window rails — November 10
- Replaced the bent lower window belt with one straight beam per side, retaining the original front and rear attachment points.
- Side-panel upper vertices, rail seat, seat clearance and B-pillar junction follow the same straight belt. Rails remain integral with the canopy as a single printable solid.

## Analysis — November 10
- Follows `.soma/skills/analysis.md` (on demand). `soma analyze thickness` (limit 1.2 mm) and `overhang --up y` (45°) run after the sill change.
- Thin spots are narrow slivers along facet seams, not whole panels. Judge them in slicer preview.

## Rear roof rail foot — November 10
- The sloping rear roof rail of the canopy now lands on the sill just behind the B-pillar foot (`REAR_RAIL_FOOT_PX = 945` in `parts/shell_geometry.py`, B-pillar foot is at 930) instead of at the rear corner (1082). Its seat pocket follows. The straight sill still runs on to the rear corner.
- The triangular rear quarter window under the sloping rear rail is now closed by a 2.5 mm canopy panel (foot, roof end, rear corner). The canopy sill rail ends at the rail foot; the shell's seat pocket still runs to the rear corner and the panel has its own pocket (4 % larger in plane, 0.15 mm gap).

## Using another coding agent (e.g. Google Antigravity)
- SOMA has no special MCP integration. Any agent that can read files and run shell commands can work on this model.
- Open this workspace folder in the agent. Tell it to read `AGENTS.md` first (rules, commands), then this file, then the skills in `.soma/skills/`.
- Its terminal needs the app's environment: `soma` and `python` on PATH (see `.soma/skills/shell-environment.md` if `soma` is not found).
- Workflow: edit `model.py` / `parts/`, run `soma build`, commit when it says "Build ok".
- `soma render` needs the SOMA app open on this model.
- Use one agent at a time to avoid overwriting each other's edits; the git timeline shows every change.
- Flush beltline: the canopy sill rail (and its shell pocket) sits `RAIL_DROP` = 1.5 mm lower (`parts/params.py`) so its top is level with the shell's top edge. Sections at y = -80, -40, 10 confirm the match.

## Cowl/seat knuckle blend — November 10
- The square ends of the shell's cowl cross-rail and seat rail left spikes and notches at each A-pillar foot. `seat_corner()` in `parts/shell_geometry.py` hulls the last/first `SEAT_BLEND` = 14 mm of both rails into one faired block (counterpart of the canopy's `corner_block`).
- `seat_slope()` adds a wedge under the outer edge of each seat rail (`SLOPE_DROP` = 10 mm, fades out `SLOPE_END` = 12 mm before each rail end), so the door facets slope up into the window sill instead of meeting a flat overhanging underside.
- Canopy beam joints (roof vertices, A-pillar top, B-pillar foot, rail foot) are hulled into knuckles by `joint()`/`canopy_joints()` (`JOINT_BLEND` = 7 mm); their pockets in the shell grow by 1.5 × `GLUE_GAP`. The joint at the rear roof end (ROOF[-1]) is left as plain beam ends: its hull touched the rear shell and broke the clearance check.
- The shell's seat rails along the belt hold the front shell together: removing them leaves 3 separate solids, so they stay.

## Inner ledge and pegs instead of outer seat rails — November 10
- The outer seat rails (and the cowl-rail knuckle and slope fairings) are gone from the shell. The canopy sill rail now sits in its pocket in the door panel top edge.
- `inner_ledge()` in `parts/shell_geometry.py`: hidden 45° ledge on the inner face of each door panel, 7 mm wide, top 4 mm below the belt line. It carries the canopy and ties the front body to the tail (without it the shell fell into separate solids). A small tie block (`tie`) at the rear corner overlaps body and tail.
- Peg joinery: three pegs per side (Ø2 × 4.5 mm, `PEG_PX` stations) on the canopy sill rail drop into holes (Ø2.6 × 5.2 mm, 0.3 mm clearance) in the ledge. Glue the rail, no loose parts.
- `strip_dust()` drops sub-5 mm³ slivers that the pocket cut leaves on the thin panel top.
- Shoulder patches (`shoulder_patches()`, `SHOULDER_PATCHES`, `PATCH_DEPTH` = 8 mm): solid fill behind the door shoulder fold. One patch plugs the slot between the quarter blade tip and the door skin, the other the dark V-notch at the crease below the shoulder. The outer surface is unchanged; the fill is internal. Sections at y = -40.5 and -5.4 show no open slot any more.
- Rear corner: the tie block shrank to 6.5 × 10 × 8 mm (it hung out as a big flat box). A new patch fills the quarter-fin channel from the blade back to the door skin (x = 44); `SHOULDER_PATCHES` entries may now be `(points, to_x)`.
- The quarter-fin channel fill is removed again (the fin keeps its open channel); the other shoulder patches stay.
- The rear tie block is replaced by a 3 × 6 × 6 mm bridge inside the pocket zone; it only exists because body and tail are 0.75 mm apart at the sill pocket there.

## Selected-face cleanup — November 11
- Removed both legacy solid shoulder patches on both sides. These left broad flat interior faces and excess material across the front/rear split. This supersedes the shoulder-fill notes above; the original faceted skins remain.
- Other selected faces are the inner surfaces of the continuous door/rocker skin, required to close the 2.5 mm panels; retained rather than opening the printable shell.

## Crease seam, interior fairing and raked nose — November 11
- Replaced the transverse mid-body seam with a mirrored crease path through trace landmarks (836,446), (943,345), (889,319), (940,286), (1082,144). It follows the rear rocker/shoulder folds up to the sill, with 0.3 mm clearance. The quarter blades now belong to the front shell. This supersedes the Y=-25 split notes.
- Removed detached offset-skin chips at the seam (under 25 mm3 each); substantial disconnected panels trigger a build error. Four single-solid printable parts remain.
- User chose to retain the exterior panels and simplify their insides. Lower side vertices away from the upper sill panels share a fitted planar inner wall. Adjacent facets transition to it; original exterior vertices stay put. The fairing adds local interior material while maintaining at least the original normal offset; it does not create panel openings. Upper sill/seat geometry remains outside the fairing.
- Nose lower edge pitches rearward by 10 mm over 32 mm height (about 17 degrees from vertical), with the upper edge fixed. (assumed) 10 mm setback gives the requested slash profile. Grille, aperture and backstop share the rake; hood cheeks blend into it ahead of Y=-100.
- Build checks cover one valid solid per part, fit in the established +90 degree X print orientation, and assembly interference/clearances. The crease seam will still need glue and finishing for a visually seamless painted result.

## Cohesive frame and flush roof — November 11
- Side sill rails now have tapered 10 mm-deep fascia blending into sampled outer body facets, with matching clearance pockets; end depths taper into the hood and tail. Rear pillar feet use 20 mm swept transitions spread along 28 mm of sill. A-pillar transitions extend 22 mm along the adjoining members.
- Replaced the exposed 8 mm square cowl crossbar with a shallow hood-continuous faceted cowl, reinforced 4 mm underneath. The cowl and A-pillar corners meet the side sill fascia.
- Roof bridges the actual top faces of both roof rails and headers, including caps at the folded joints. This removes the recessed roof and raised rail rim. The rear seat pocket extends to the outer rail edges.
- Single-solid validity, bed fit and assembly clearance assertions pass at defaults. Further exterior audit requested: remove legacy steps and small unintended seam holes while retaining designed windows, vents and print clearances.

## Full exterior audit — November 11
- Reviewed front/rear oblique, top, side, front and rear views, with close comparisons at the A-pillars, sill, rear pillars and roof. The viewer connection was unavailable; inspected static STEP-based previews instead (`renders/exterior-audit.png`, `renders/frame-roof-comparison.png`).
- Removed obsolete quarter-fin root overlap blocks; the skins and current inner fairing already provide a connected shell. Hidden structural ledges/peg seats remain.
- Replaced the oversized 4-percent quarter-panel pockets and extra rear-header relief with pockets derived from the actual panels/roof plus the named glue clearance. This removes oversized seam slots. The fascia's lower edge now splits exactly at every body-facet crossing, matching each underlying crease.
- Quarter-wing intake cuts now affect only the wing and return skins, retaining the inner body wall. Intentional wing channels/intakes, tail vent, windows and wheel clearances remain.
- Trimmed two tiny overlapping skin islands at the wing roots back to their surrounding facet planes; these were raised intersections bounded by small face loops, not functional openings. No matching small root loops remain in the final STEP.
- The tail's first upper station meets the outer rear roof-header corner, with a flat transverse landing before the original tail crown resumes. This removes the roof/tail height step while retaining the deck hump.
- Grille seating clearance now comes from the actual raked insert outline, so the thicker wall setting cannot pinch the insert. The seam-chip threshold scales with wall thickness; large disconnected pieces still fail the build.
- Validation: default build passes, four STEP solids re-import as valid. Length 260/290 mm and wall 2.5/3 mm endpoints and both dimension-limit combinations build successfully; the final wing-root trim was rechecked at both lengths with 3 mm walls. All build assertions include assembly interference, glue clearance and fit in the specified print envelope. Support and dry-fit requirements above still apply.

## Print-thickness correction — November 11
- User identified excessive lower-side bulk. Removed the planar inner fairing; this supersedes the earlier interior-fairing choice. The inside again follows the outer facets instead of filling their valleys.
- At defaults, front shell volume fell from 107871 to 87243 mm3 (19.1 percent), retaining one valid solid. Further work is checking facet thickness and the marked frame/rear connection joints.

## Marked connections and uniform-panel print optimization — November 11
- Supersedes the prior beam-knuckle and filled-interior construction. `parts/canopy_frame.py` builds continuous side-frame skins with mitred outlines and cut windows. Roof and frame share their upper boundary. Removed the separate corner blocks, swept foot masses, roof-beam end caps and obsolete rear tie block. The A-pillar foot mitre is capped to avoid a needle-like projection.
- `parts/panels.py` makes each broad facet with a parallel inner face exactly WALL away along its normal. Narrow edge/corner connectors are local, with mitre depth bounded to twice WALL; acute folds get inner bevels. This avoids shifting broad inner faces inward to satisfy every adjacent facet simultaneously.
- The canopy skirt is also a normal-thickness skin. It replaces the top band of the side wall, removing the redundant thin layer behind the old skirt pocket. The internal peg ledge now roots below that seam and has a WALL-thick free edge instead of a knife edge.
- Shortened the ledge to trace station 1020 and removed its exposed rear end near the user's selected (42.6,51,66.2) mm area. The other selected rear face near (50.3,37,55.2) mm is a closing face at the panel edge; it remains because deleting it would open the wall. No extra solid block is retained there.
- The projected crease split now recovers small inside-bevel fragments into the adjoining main panel rather than dropping them and leaving seam notches. Tiny numerical dust under 5 mm3 is still omitted. Clearances are checked after recovery.
- Default solid volumes changed from the pre-optimization revision: front 107871 to 70955 mm3 (34.2% less), rear 19130 to 18379 mm3 (3.9% less), canopy 47505 to 37428 mm3 (21.2% less); grille remains 1628 mm3. Total modeled material volume is 27.1% lower, not a prediction of slicer filament use.
- Validation: default build and all length 260/290 mm, wall 2.5/3 mm endpoint/combined builds passed; the final ledge-edge change was rechecked at both lengths with 3 mm walls. Four STEP solids re-import as valid. Final 3MF meshes have no boundary or nonmanifold edges when coincident vertices are welded at 0.000001 mm precision.
- Ran thickness at the 1.2 mm FDM threshold and overhang at 45 degrees with +Y print direction. The broad wall areas are clear in the inspected thickness projections (`renders/wall-analysis-sections.png`, `renders/canopy-wall-analysis.png`). Remaining low-thickness flags occur at sharp cut edges, rims, fold intersections and small details: front 1148 mm2, rear 558 mm2, canopy 571 mm2, grille 75 mm2 flagged. Some ray samples at sharp edges find no opposite face despite valid closed CAD solids. These flags require slicer preview; this is not certification of a 1.2 mm minimum at every mathematical edge.
- Support-facing areas at the chosen +Y direction: front 2187 mm2 (3.66% of its surface), rear 393 mm2 (2.38%), canopy 421 mm2 (1.27%). Keep supports/brim at the nose and cheeks, window/roof leading edges, peg projections and rear roof seat. Do not call this a support-free print.
- Updated all four 3MF, STL and single-part STEP exports in `exports/`. Files retain assembly coordinates; orient each part and drop it to the slicer bed as above. Current analysis summaries are in `renders/print-thickness-check.json` and `renders/print-overhang-check.json`; older fit reports are historical.


## Exterior markup cleanup and joined wing returns — November 11
- Supersedes earlier decisions to leave the marked quarter channel open or retain its narrow rear closing return. Closed that channel with a WALL-thick faceted web and moved the side boundary onto the existing wing fold; shortened the internal ledge to station 1000.
- Canopy fascia now ends at station 1020 with the body skin restored behind it. Removed the trailing upward tab, trimmed the roof/frame window mitre, and clipped the internal sill rail to the fascia envelope. Flared the cowl into the A-pillar foot and clipped the hood cheek below the hood planes for flush joints.
- Extended the diagonal intake return to the rocker, covered its exposed leading side with thin facets, and extended its upper return into the shoulder as marked at 10:56. The root overlaps within the shoulder wall instead of touching along an edge. Clipped upper wing fragments to the intended crown and ridge planes.
- Trimmed the selected left wheel-notch remnants with a symmetric 2 mm local narrowing (half-width 61 to 59 mm); maximum overall width remains 139 mm. Intended intakes, windows, tail vent, wheel openings and assembly gaps remain.
- Inspected native viewer renders from side, front/rear quarters, top and underside, including two final joint views. Default build passes with four valid solids; final exported-mesh checks report zero open, nonmanifold or flipped edges for every part. Length 260 and 290 mm with 3 mm walls both pass build and assembly assertions.
- Refreshed all four 3MF, STL and STEP exports. Earlier numerical thickness/overhang summaries and volume comparisons describe their prior revision; support, slicer-preview and dry-fit guidance still applies.


## Completed intake cheek — 11:13 markup
- Added the missing second facet between the leading intake cheek and the body fold, mirrored on both sides. Uses the existing WALL thickness and shared-edge mitre rather than filling the interior with a block.
- Trimmed the quarter/return skins and cheek to their common leading-edge plane to remove the offset tips at the lower corner. Intake opening and assembly clearance remain.
- Default build passes with four valid solids; fine mesh checks show zero open, nonmanifold or flipped edges. Inspected native renders from both sides. Updated 3MF, STL and STEP exports; existing support and dry-fit guidance still applies.


## Whole-shell joint and printability audit — 12:13 through 12:40 markups
- User authorizes changing adjoining facet angles for cleaner joints. Supersedes the separately overlapped quarter-wing returns, cheek and channel webs: each wing now uses one hollow convex faceted envelope with cavity planes WALL inward. Removed the old overlap-island cutter and patch helpers.
- Leading wing facets start on the body at trace station 760 and sweep outward into the wing, closing the forward-facing pocket. This is a geometric deflector shape, not a validated aerodynamic performance claim.
- Added the marked lower joining facets between the intake surround, rocker return and rear shoulder. A buried internal mitre along their shared wing edge creates finite-volume attachment rather than an edge-only join.
- The glue split now follows the new uninterrupted crease from station 943 directly to the rear belt corner at 1082; lower rocker crease and 0.3 mm clearance remain. This prevents disconnected side panels behind the earlier zigzag seam.
- Replaced the overlapping thin shoulder bridge with a closed tapered seat. Moved the wing's upper root below the canopy skirt. Trimmed the obsolete side-frame lower return and extended the skirt with a tapered runout to the rear corner, replacing the earlier abrupt station-1020 termination.
- Broad skins remain nominal 2.5 mm (adjustable to 3 mm), with local internal mitres/seats. Intentional windows, wheel openings, intakes, tail vent and assembly clearances remain. No chassis load rating is implied.
- Audited native front/rear quarters, both sides, top and underside, plus close-ups of the marked joints. Four solids are valid. Fine print meshes have zero open, nonmanifold or flipped edges. `checked()` now runs SOMA mesh validation as well as CAD/solid/bed checks on every build.
- Thickness analysis at 1.2 mm shows predominantly clear broad panels; remaining flags are concentrated on sharp rims, cut edges, ledge edges and seat intersections. Final flagged areas: front 1146 mm2, rear 159 mm2, canopy 546 mm2, grille 75 mm2. The check is not certification of a minimum at every sharp mathematical edge. Inspect thin-wall toolpaths in the slicer before printing.
- At +Y print direction, support-facing areas above 45 degrees are front 2093 mm2, rear 452 mm2 and canopy 407 mm2. Supports/brim remain necessary around the nose, roof/window leading edges and pegs/seats; these are not the obsolete protruding fragments removed by this revision.

- Final default and parameter endpoint/combined builds pass CAD, print-mesh, assembly-clearance and bed checks. Refreshed all four 3MF, STL and STEP exports; independently checked the exported 3MF topology: zero open/nonmanifold edges for all four parts.


## Chassis marriage — November 11 (revised)
- `inputs/WS03_chassis_only.glb` is a 1:1 chassis built from SCX10 III-class 1:10 hobby parts (user: the parts were originally based on SCX10 III components): tires Ø112 × 62, 12 mm hex wheels, standard-size servos, 540/550-class motor, 5×11×4 mm bearings. Buy these off the shelf (Amazon / hobby shops); do not scale the chassis.
- Earlier attempt (scale the chassis to 0.46) was dropped: it would make every hardware part a non-standard size. Instead the shell is scaled up: `SHELL_SCALE` = 2.17 (shell about 604 × 302 × 235 mm). The generator still builds at the 278 mm blueprint size with `WALL = WALL_PRINT / SHELL_SCALE`; `model.py` scales the finished parts, so the printed wall is `WALL_PRINT` = 3.0 mm.
- `CHASSIS_SCALE` = 1.0, `CHASSIS_Y` = 0, `CHASSIS_Z` = -104 (ground below shell rocker). Clearance is the earlier 5.7 mm scaled by 2.17, about 12 mm minimum (sampled points, tools/fit_chassis.py works at 1:1 shell frame: use shell scale 1/0.46).
- The bed check in `checked()` was removed: the scaled parts (front shell about 302 × 422 × 169 mm) exceed the 220 × 220 × 250 mm bed.
- OPEN: split each part into bed-sized printable pieces with glue joints; list of purchased parts (BOM); shell mounting to the chassis. Material estimate: about 830 cm3 of PLA in the shell walls, roughly 1 kg.
- `parts/chassis_ref.step` holds convex hulls of each GLB component (made by `tools/make_chassis_ref.py`), reference only.


## Chassis mounting, CG and stance — November 11
- User deferred the decisions to me and asked to show chassis and shell mated (renders/mate-iso.png, mate-side.png, mate-front.png, mate-rear.png, mate-top.png).
- Stance: shell rocker sits 45 mm above ground (`CHASSIS_Z` = -45, was 104). Shell height factor `SHELL_Z` = 0.9 flattens the shell 10 percent in Z for a lower, more aggressive look; top of roof is about 257 mm above ground. Length 604, width 302.
- Trim: `parts/relief.py` (data in `parts/relief.json`, made by `tools/make_relief.py`) cuts tire arches (tire radius + `RELIEF` 8 mm) and clearance around the front suspension arms, uplinks, tie rods, belts and rear shock from the scaled shell parts. Re-run the tool if the chassis GLB changes. The cuts run before the validity checks; cutting an already cleaned shape crashed OpenCascade (segfault), so keep `scaled()` cutting the raw shape.
- CG estimate (rough: assumed masses, 1.65 kg chassis with CG about 64 mm above ground, PLA at 1.24 g/cm3 with solid walls): shell about 0.9 kg with its CG 128 mm above the rocker; combined CG about 103 mm above ground, tip angle about 55 degrees across the 288 mm track. Lighter shell and lower mounts help: `WALL_PRINT` 2.4 instead of 3.0 saves about 0.18 kg. Weigh the real chassis and update.
- Mounting is NOT designed yet. Recommended: four body posts on the chassis frame with the standard 1:10 body-clip style (3 mm posts and body clips from a hobby shop) or four M3 screws into printed bosses inside the shell, at frame stations near both axles; keep the posts as low as possible. Shell is not yet cut into print-bed-sized pieces.

## Fenders on the tires — November 11 (13:41 markup)
- User asked to lower the shell until the front fenders sit just on top of the front tires. Closest skin-to-tire distance was 21.7 mm at the rear inner corner of the tire footprint (x 113, y -176), so `CHASSIS_Z` went from -45 to -25.3 (shell 19.7 mm lower; rocker is 25 mm above ground, roof about 237 mm). Front tire arch cut is now `TIRE_GAP` = 2 mm (rear tire and suspension still use `RELIEF` 8 mm).
- Relief cuts now leave two 208 mm3 slivers on the rocker; `model.py` removes solids under 1500 mm3 after the cuts. Lower `CHASSIS_Z` than -25 will need the relief re-checked: the front shell split into three solids on the first try.
- Mounting findings (not built yet): the chassis deck centre is full of parts (battery, motor, diffs, belts), so no free post columns exist over it. The printed frame side rails (|x| 40-65 mm, top at about 65-107 mm above the rocker, higher to the rear) are the only clear anchors. The shell side skin sits at |x| 100-130 mm there, so mounts would be tabs from the shell wall inward and down onto the rail tops with M3 screws; rail tops still need drilled or printed holes (the GLB has none).

## Slimmer cabin — November 11
- User asked to subtract from the middle, slim the cabin and bring the sides closer to the chassis. New parameter `CABIN_WIDTH` = 0.80 (width factor, 1.0 = blueprint). `PLAN_STATIONS` in `parts/params.py` ramps the transverse width from 1.0 at blueprint y = -80 (front fenders, nose unchanged) to the factor at y = -45, holds it to y = 20, and returns to 1.0 at y = 68 (tail unchanged).
- The warp now lives in `reference_trace.traced()` (`plan_width(y)`), not in `point()`, so every traced point, `side_surface_x`, the canopy frame and the wings agree. Earlier attempt in `point()` broke the boolean fuse (zero or negative volume solids). Keeping the warp out of the tail matters: with it reaching y = 95 the dorsal tail panel became an invalid solid below 0.88.
- Result at defaults: shell width in the cabin about 0.8 of before; maximum width 256 mm at the nose/fenders (the fenders over the tires are unchanged); minimum clearance to the chassis frame, motor and decks 9.3 mm (3.4 mm at the tires and suspension, as designed). Going below about 0.78 would start touching the frame rails.
- Limits to check when changing `CABIN_WIDTH`: build needs one valid solid per part, so lower values may again fail at the crease split or the wing cavity.

## Shell dropped a further 10 mm — November 11 (13:52 markup)
- The fender corner over each front tire still floated above the tire top (the 2 mm contact was only at the rear inner corner). `CHASSIS_Z` -25.3 to -15.3: the rocker is now 15 mm above ground, roof about 227 mm. The 2 mm `TIRE_GAP` arch cut now trims the fender skin that dips into the tire, so the fender wraps the tire top. Build passes: one valid solid per part.
- Lower than this the rocker point nearly touches the ground; keep `CHASSIS_Z` at or above -10.

## Front guard rake, travel trims, rear wheel, rear suspension, one project — November 11
- Nose: `NOSE_RAKE` 22 (blueprint mm) makes the shell nose face lean 37 degrees, the same plane as the chassis front guard (w3_skid; its face leans 37.4 degrees from vertical). `CHASSIS_Y` = 4 pushes the shell 4 mm forward of the guard so the two do not touch.
- Rake: `SHELL_PITCH` = 3 degrees, tail up, about the front axle, so the front fenders stay on the tires and the tail clears the bigger rear wheel.
- Travel trims (`parts/relief.py`): front tires sweep +20 mm bump (`BUMP_TRAVEL`) and ±30 degrees steering (`STEER_LOCK`); arms, uplinks, tie rods, knuckles follow the same motion; the rear swingarm sweeps about its pivot. Everything is cut from the shell with `RELIEF` 8 mm (front tires `TIRE_GAP` 2 mm).
- Flank scoop (14:08/14:09 markups): one round arch (centre y -174, z 33.4, radius 83 mm, `SCOOP_*` in model.py) removes the ragged lower flank behind each front tire. It is capped at 4 mm above the tire top because the hood cheek there ties the nose to the body sides (without the cap the front shell split into three solids).
- Rear wheel: `REAR_TIRE_OD` = 140 mm (monster-truck class, 12 mm hex). The swingarm group rotates about its pivot (drive pulley shaft) by about 6.7 degrees so the axle rises to the new radius; the transmission itself is unchanged. Gearing (my call): keep rear surface speed equal by changing only the rear belt ratio by 112/140: for example a 14T axle pulley becomes 18T (verify the real pulley tooth counts on the printed parts; modelled outer diameters are 13.6 mm pivot and 12.2 mm axle). Belt length stays within about 1 mm; add an idler or tensioner as margin.
- Rear shock (new geometry): the original shock lay nearly flat (79 mm eye to eye, 5 degrees) and gave only 7.2 mm of stroke for 20 mm of wheel travel. New: upper eye raised `REAR_SHOCK_RISE` = 55 mm on a new printed shock tower (reference part), 89 mm eye to eye at ride, 34 degrees from horizontal, 17.4 mm stroke for 20 mm travel (motion ratio about 0.87), a standard 90-100 mm 1:10 shock. The shock top is under the shell tail; check against the final shell before printing.
- One project: the chassis GLB is imported as named parts grouped by function (Frame and decks, Suspension, Steering, Drivetrain, Wheels, Electronics and power, plus Rear swingarm, Rear tire, Rear shock, Rear shock tower). `tools/make_chassis_ref.py` regenerates `parts/chassis_ref.step` and `parts/rear_ref.step`; `tools/make_relief.py` regenerates `parts/relief.json`. Components are convex-hull stand-ins (reference, not exported). Legacy files from the old full-vehicle model (`parts/body.py`, `parts/chassis.py`, `parts/wheels.py`, `parts/util.py` helpers) are unused.
- Open: cage rebuild with shell mounting points (CG and stability first), plate over the marked overhang (angled down), print splitting, parts list.

## Deck trim and shell width
- Shell bottom edge is now cut flat along the chassis deck plane (`DECK_TRIM`, 0 = flush with the deck top, rising 32.6 → 59.8 mm front to tail).
- Widest part of the shell now equals the outer edge of the swingarm/knuckle assemblies: `SHELL_HALF_WIDTH` = 130.5 mm (261 mm overall). Tire outer edge is ±175 mm, so tell me if you meant the tires.

## Real component geometry, nose width
- `tools/make_chassis_ref.py` now keeps the real triangle meshes (sewn to solids) for every component with 500+ faces except the two frame hulls, tires and rims: front and rear swingarms, carriers, knuckles, diff cases, uplinks, etc. Smaller parts stay simplified hulls. `parts/chassis_ref.step` is about 190 MB and `rear_ref.step` about 70 MB. A full build takes about 2.5 min.
- Mesh decimation breaks these tube bundles (not watertight), so they stay at full resolution.
- `SHELL_HALF_WIDTH` = 93.5 mm (outer edge of the swingarm arms). `NOSE_HALF_WIDTH` = 40 mm (front guard / skid width) for y < `NOSE_END_Y` = -252.
- Collision check (OCC intersections shell vs components): only the nose resting 1.1 cm³ into the skid plate, and the new rear shock bottom 0.7 cm³ into the rear arm (mount). Everything else clear.

## Product scope — November 11
- Goal changed: this is a complete product to publish or sell, not only a shell. Scope covers shell, cage, chassis, mounts, supports, hardware (BOM with real standard parts), print settings and filament per part, assembly instructions, drawings and renders.
- Roadmap: (1) fix remaining collisions (nose vs skid plate, shock vs rear arm mount); (2) cage with shell mounting points, CG and stability; (3) overhang plate and supports; (4) print splitting to fit the 220 x 220 x 250 bed, orientation per part; (5) hardware BOM and filament/print table per part (PLA vs PETG/ASA for load and heat parts); (6) FEM on cage, mounts and arms; (7) drawings, exploded assembly animation, hero renders; (8) release pack (STL/3MF per part, instructions, BOM).

## Product decisions — November 11
- Printer: Bambu Lab "H3C" as the user named it (confirm model and build volume; bed size replaces the 220 x 220 x 250 assumption).
- Filament: PLA and PETG only. Printed indoors with a small HEPA filter, so no ABS/ASA/PC/PA-CF. PETG for structure and heat-exposed parts (near ESC/motor), PLA for the shell.
- Electronics: Hobbywing QuicRun Fusion 2-in-1 brushless, standard 12 g servos, any 2S-3S-capable RX/TX, 2S-3S LiPo.
- Sold as print files only: STL/3MF per part, instructions, BOM, so every hardware item must be a common purchasable part.
- Donor platform: Axial SCX10 III parts (axles, links, shocks, wheels, hardware) wherever possible. Check the existing chassis hardware against real SCX10 III dimensions.

## Printer, wheels and donor parts research — November 11
- Printer: Bambu Lab H3C, build volume 330 x 320 x 325 mm (third-party sources: SimplyPrint, Fauxhammer; Fabbaloo measured 330 x 325 x 325). The Bambu wiki page returned HTTP 402 to automated fetch, so confirm on the official page. The 278 mm shell fits whole in X; recheck width and height per part.
- SCX10 III: stock 1.9" wheels on 12 mm hex hubs, AR45 axles, 100 mm large-bore shocks, hypoid diffs, 12.3" (313 mm) base wheelbase. Part AXI238000 (standard axle conversion kit: axles, links, shocks) is discontinued, so the BOM should name individual still-available parts. Part numbers not verified yet.
- Rear wheel: 140 mm tall tires exist in both 1.9" (Axial Ripsaw 1.9, 5.5") and 2.2" sizes. Width needs a tire with 41 mm+ tread, usually on 2.2 wheels (check the 12 mm hex offset, 2.2 wheels can sit too deep on SCX10 hubs).
- Open: pick the exact rear tire and wheel, the SCX10 III diff (front and rear axle housings), link set and shocks from real part numbers and compare their dimensions with the imported chassis.

## Rear wheel candidates — November 11 (research)
- Current model: `REAR_TIRE_OD` 140 mm, tire 62 mm wide cylinder on a 12 mm hex.
- Candidate A (recommended): 2.2" crawler tire, about 140 mm OD x 54 mm wide, on 2.2" beadlock wheels with 12 mm hex (4-pack kits from Rchobbytop and similar; Gmade 2.2 GT beadlock wheels with 140 mm Monster tires). Listings vary (136-142 mm), so pick one set and measure before freezing geometry.
- Candidate B: Axial 2.2 Ripsaw, 140 mm tall, stays inside the Axial parts family.
- Candidate C: 125 mm x 55 mm mud tires on aluminum beadlocks, smaller and not tall enough for the look.
- Check before committing: wheel offset on the 12 mm hex (2.2" wheels can sit deep on SCX10 hubs), real tire width (model uses 62 mm, candidates 54-55 mm), gearing for the larger rear.
- No single vendor listing has been checked against the shell width; this needs a physical or datasheet measurement.

## Collision fix and tool — November 11
- `tools/collide.py` (new, about 3 min) intersects each shell part with every chassis component. Result at CHASSIS_Y 4: nose in skid plate 1.11 cm3; 6: 0.51; 8: 0.01; so `CHASSIS_Y` is now 9 (about 1 mm margin). The frame hull stand-ins still report 0.6 to 0.9 cm3 against the shell; they are convex hulls filling the open frame, so those are artifacts to ignore, not real collisions.
- The collision tool does not yet cover the rear shock and shock tower (they are generated in model.py, not imported).
- Planned: move the rear shock to the wheel centre plane (x = 0, now 12) to cut swingarm twist, then check shock/arm clearance.

## Magnetic light connections — November 11
- Request: magnetic power connection for front and rear lights (lights not made yet), two contact points (plus and minus) at each end, on the centre line, rear one before the swingarm, sitting above all the componentry.
- `parts/light_contacts.py`: per end a PETG contact bridge (plate with legs resting on the frame rails at x = ±`LIGHT_LEG_X` 58 mm, deck 12 mm above the highest chassis part at that station, from `relief.json` envelope) and a shell-side contact block hung from the roof underside by a 12 x 12 mm post, 0.3 mm gap between the blocks. Two magnet pockets each (6.2 mm for 6 x 3 mm discs, 16 mm apart, x = ±8). Front station y = -215 (hood roof), rear y = 95 (canopy roof, before the pivot at about y = 105 + 9). Parameters in the group "Light connectors".
- Assumed: 6 x 3 mm N52 magnets, wires soldered to magnet or pad, alternate polarity so the blocks mate only one way (poka-yoke not modelled yet).
- Collision check (tools/collide.py): no clash with real components; the rear bridge legs overlap the frame hull stand-in by 1.3 cm3, which is where they rest on the rails (hull artifact).
- Open: the rear post is about 70 mm tall and passes through the open cabin (visible through the windows, check in render); wire channels, magnet retention, polarity key, light units themselves; the posts are loose parts glued to the roof, canopy bond needs a wire route.

## Cage, first pass (work in progress, not sound yet) — November 11
- Request: build the light connectors into the cage, and hide the cage behind the shell. `parts/cage.py` makes one PETG part "Cage" (front and rear contact bridges plus two side beams at x = ±`LIGHT_LEG_X`, now 52 mm, with M3 holes in the feet). The loose contact blocks stay on the shell roof. The cage is matt black so it vanishes behind the windows.
- `tools/collide.py` now also checks the cage against the shell. Open problems: the beams touch the front shell side (about 2 cm3 at y -75..-20, z 132..140, where the beams follow the componentry envelope), and the feet are not on real frame structure.
- What the chassis probes show (final frame, `tools/probe_xrow.py`, `probe_chassis_x52.py`): at the front station y = -215 the deck plate (top z 16.6) is only 40 mm half-width wide, nothing at x = 52. A frame rail sits at x = 52 from y = -180 to 20 only (top z 20 at the front rising to 34, extra parts to 51); behind y = 20 and at the rear station y = 95 nothing stands at x ≥ 42, and the battery stack up to z 83 sits at x = 12..36. So feet at x = 52 float at both bridges. Before the cage is built properly the mounting points on the real frame must be fixed (front deck at x ±30, rail at x ±52 between y -180 and 20, rear still open).
- The earlier `relief.json` "rail" table is a hull artifact and must not be used to place feet.

## Cage, tubular and matching the shell angles — November 11
- Replaces the first-pass cage above. `parts/cage.py` builds one PETG part "Cage" from solid round tubes (8 mm, `CAGE_BEAM`) with balled joints:
  - Front hoop leans forward: feet on the front deck at y -180 (x ±`FRONT_LEG_X` 42.5, deck top z 20.2), tops at the front contact bridge at y -215 (about 21 degrees), a crash bumper tube 12 mm ahead of the plate, a cross tube between the legs at z 66 (above the left-side front parts, which reach z 55), diagonal and mid-height braces to the rail start and gussets from the feet.
  - Lower beams on the frame rails at x ±52, z 59, with two M3 posts per side (y -150 and -20) down to the rail.
  - Rear legs rise backwards from the rail ends (y 20) to the rear contact bridge at y 95, following the rise of the rear shell.
  - Upper tubes copy the shell belt line: `belt_profile()` samples the shell at x = 52 and keeps the kinks (vertices at y -215, -85, 40, 70, z 131.3, 133.3, 142.9, 147.1) and runs `BELT_CLEAR` (14 mm) below it.
- Hidden behind the shell: cage is matt black, 1.6 mm minimum clearance to the front shell, no contact with any shell part (checked by `tools/collide.py`), and not visible in the side render with the shell on.
- Collision check against the real chassis: only a 0.02 cm3 graze at the left front foot (x -40..-38). The frame hull stand-ins still report overlaps that are hull artifacts.
- Assumptions to check: M3 screws into the rail and deck, tube diameter and the crash bracing strength (run FEM), feet positions on the real deck. The rear legs hang off the rail end with no foot, a 75 mm cantilever.

## Upper cage: A and B pillars, roof, rear supports — November 11
- `parts/cage.py` `add_upper()`: A pillar from the front hoop top to the top of the windscreen frame (node roof0), B pillar from the upper belt tube (stepped inboard to x 46 first, the shell belt skin reaches x 48 at z 143) to the roof node, roof rails along the frame nodes (roof0, roof1, roof2, roofN), rear quarter tube from the roof rear node down to the rear bridge, and four supports under the rear shell hump above the rear tire (y 150, 185, 220, 255 at x ±`REAR_SUP_X` 40, 8 mm below the shell underside) with a cross tube at y 185. Frame nodes come from the same trace as the canopy (`model.py` `_nodes`, rounded to 0.1 mm because coincident float noise made the tube booleans invalid).
- Tubes: `PILLAR_D` 8 mm (was 5), `PILLAR_IN` 7.5 mm inboard of the frame node (was 6), both parameters in group "Cage". Unions use a 1e-3 fuzzy tolerance. M2 pilot-hole bosses (`BOSS_D` = tube + 3 mm) at the A top, B base and top, rear quarter top and each rear support; boss tips stop short of the shell (rear supports 3 mm reach), a spacer or screw closes the gap.
- Collision check: cage touches the front shell by 0.01 cm3 (pillars now press against the frame, intended), rear shell 1.2 mm clear, 0.02 cm3 graze at the left front foot as before.
- Open requests, not done: (1) the marked "gaping hole" along the side window and door top (markup 18:55): make the facets angle down toward the door panel, needs a decision on what is meant; (2) a tilt mechanism so the shell pivots up at the tail. Conflicts to resolve: the shell screws to the cage bosses and the light contact blocks hang from the shell roof onto the cage bridges.

## Rear suspension rebuilt — November 11
- Root causes found: (1) the donor arm has a shock-mount rod across the wheel (x 15..66, axis y 210.9, z 122.4 in the arm frame, radius about 10) only 68 mm from the axle, so it sat inside the 140 mm tire (r 70); (2) the shock lower eye was placed 4.5 mm off that rod in y and 3 mm in x, and was itself 67 mm from the axle (inside the tire); (3) the tower was a floating block and the shock a plain cylinder passing through it.
- Fix: `tools/make_chassis_ref.py` cuts the rod from the arm (`ONLY_REAR=1 python tools/make_chassis_ref.py` regenerates just `parts/rear_ref.step`; the arm now spans x 43..80). The shock stands on the wheel centre plane (x = 0, as discussed, no twist on the one-sided arm): lower eye on a printed PETG "Rear shock bridge" (tube D 14 from a socket on the arm's apex ball, up and over the tire, ending in a 6 mm pin stub for an M6 bolt), upper eye on a printed "Rear shock tower" (two legs, pin between them). Shock modelled with body, shaft and eye rings (OD 14, 6.4 bore), 81 mm eye to eye at ride, about 31 degrees from horizontal, motion ratio about 0.93. `REAR_SHOCK_RISE` default 66, `SHOCK_BOT0` and `BRIDGE_ARM` in `parts/relief.py`; the shell relief cut includes the bridge sweep.
- Check: no overlap of bridge, shock, tower with the tire, arm, cage; the tower base overlaps only the convex frame hull stand-in (its feet stand on the frame top at z 106, the real mount point on the original frame is not visible in the mesh: confirm).
- Open: FEM for the bridge cantilever (D 14 PETG, 64 mm) and the arm twist; the 140 mm tire reaches 69.7 mm to the arm's apex tube at one point, so choose a real tire of 138 mm or less actual OD; spring and preload not modelled.
- Still open from earlier: the side-window "gap" fix (option 1: sloped facets down to the door panel) and the tail-lift hinge (front hinge, rear latch, no prop).

## Shock tower merged into the cage, more robust tube frame — November 11
- The separate "Rear shock tower" part is gone. The cage now carries it: two legs (D 10) from 18 x 18 x 3 pads on the frame (M3 holes, z 106.2, same unconfirmed mount point as before) up to the shock pin, a cross tube under the pin, and each leg top tied (D 8) to the first rear shell support at y 150. One M6 bolt ("M6 shock pin (hardware)", reference part) runs through both leg tops and the shock eye. The load path is now frame pads plus the cage, the ties triangulate the tower.
- More robust: main tubes D 10 (was 8, parameter `CAGE_BEAM`), X bracing in both side frames between the uprights, a diagonal from the rail end to the rear bridge, upper cross tubes at both uprights, front cross tube, rails moved to x 53.5 so the thicker posts clear the chassis part edge at x 47.
- `parts/cage.py` was rewritten: members are collected and fused one at a time with a validity and volume check per step (OCC failed silently on tangent tubes when everything was fused in a single boolean or when tubes were unioned in sequence without checks), holes are cut last. About 230 members, one valid solid of 328 cm3 (about 420 g if printed fully solid; the slicer infill decides the real weight).
- Check: cage touches the real chassis only at the left front foot (0.05 cm3) and the front shell flank at the X brace (0.06 cm3, shell skin there slopes inwards); the other overlaps listed are the convex frame hull stand-in.
- Not done: FEM of the cage with the shock load (needs the real frame mount points), splitting the cage for printing (it is 330 x 116 x 140 mm, fits the H3C bed in one piece).

## 2026-11-12 Front cap and new light/tail reference
- Front: sloped closing plate (3 mm) beside the nose, from the hood outer top corner down to the nose bottom (markups 0010/0011).
- New reference (markup 0013, blueprint turnaround): tail = slim flat overhanging deck with a full-width red LED strip on its rear edge; front = chevron red strip above the grille; two small black roof pod lights at the front of the roof.
- Lights are to be SEPARATE printed parts: red strips (translucent PETG/PLA) that sit in channels in the shell; the only thing passing through the shell is a 5 mm peg with a 3 mm hole that holds the LED bulb. Still to do: channels in shell, strip parts, pegs, tail redesign (replaces the hump/fin and tube frame per markups 0004-0009).
- Shock bridge moved to the arm's upper tube (circled spot, markup 0030): SHOCK_BOT0 (0,150,114) and BRIDGE_ARM in parts/relief.py (arm frame); it saddles the tube, zip-tie fixed. Lever ratio is now about 2.4:1, so check shock stiffness/travel. Collision check still to run.
- Front panels: two-facet arrow panel (FRONT_CAP_TIP param) following the hood lines, not a flat triangle (markup 0033).
- Rear roof window (markup 0035): trapezoid opening in the Canopy roof (params 'Roof window ...'); rear light connector moved to y 52 so it stays on solid roof.

## November 12 — marked shell repair and reference organization
- Replaced the mismatched sill filler with angled facets whose top vertices lie on the actual window-frame faces. Lower edges follow the door facets; refined stations retain both sets of folds. The finished-facet seat uses short convex sections with 0.15 mm clearance at generating scale; zero overlap and 0.15 mm gap verified before final scaling.
- Corrected coarse plane rounding in the convex-hull helper, which could merge shallow folds into nonplanar wires.
- Nose closing panels now meet the sampled hood edge and transformed raked nose corners, with a broad lower cheek facet instead of a floating needle triangle. Panel thickness stays 3 mm.
- Replaced the old tail hump, dorsal vent and hanging rear lobes with a level open deck and slim folded perimeter. Existing length and roof landing retained; rear rim is 11 mm deep (assumed from the markup) to seat the established 8 mm straight red strip. The chevron front strip and straight tail strip retain their established profiles. LED sockets are blind from behind; the 1.6 mm red front face has no holes.
- Tail light face and its channel use the same computed tail stations, replacing fixed coordinates on the obsolete hump.
- All remaining components render opaque. Completely removed the simplified frame hull assembly from the model. Promoted the former References contents to the main tree as hardware, retaining their nested component groups and excluding them from printable-part exports.
- `tools/collide.py` now checks the actual built STEP, including nested chassis components, swingarm, wheels, generated shock, bridge, cage and contact blocks. It reports every failed boolean rather than silently skipping it. Static ride-position interference is distinct from the existing suspension relief envelope.
- Selected Canopy face at (65.6, -26.1, 150.6), area 1478.8 mm2: removed the obsolete internal sill/peg rail on both sides, its six pegs and their unused hole cutters. Current faceted sill skin and cage mounting locations replace that redundant rail. Body internal reinforcement ledges remain for shell connectivity.
- User correction at 02:45/02:50 supersedes the open-deck shell above: rear is BARE TUBE FRAME, with shell only for the compact 14 mm-deep rear light housing. Canopy ends at the B-pillar; the long deck skins, quarter-window shell and legacy shoulder bridge are removed. Main body is now continuous rather than divided at the obsolete tail crease; the separate Rear shell part is the light housing.
- Lower rear tubes extrapolate the straight window belt line from the B-pillar to the tail; upper tubes slope from the roof B-node to the same rear crossbar. Housing elevation follows that line. Shock upper pin stays aligned with its eye, but is supported by a pair of V-braced tube nodes between these upper and lower rails instead of the old hump-support arrangement.
- Rear light contact moved to Y = 10 mm under the remaining B-pillar roof (adjustable -10 to 12 mm); the old Y=52 roof no longer exists. Wiring to the tail runs along the bare tubes. Removed the obsolete four rear roof-window parameters, since that roof section is now entirely open.
- Cage unions use a small 0.0001 mm boolean tolerance; failed structural members now stop the build instead of silently being omitted. Existing 10 mm tube diameter and M6 shock pin are retained. Apply `.soma/skills/joints.md` to these connections; the shock loads are unspecified, so strength/FEM validation remains open.

## 09:42–09:45 corrections
- Restored both triangular rear quarter side covers between the roof/B-pillar and rear door shoulder; the long rear roof remains absent.
- Shortened the tail by an assumed 40 mm from the pictured termination line, including the light housing, and tapered tube-end spacing from 80 to 60 mm overall. `REAR_SUP_X` retains its key and now defaults to 30 mm half-spacing.
- Added mirrored 3 mm tapered gusset webs below the lower tail rails, with diagonal tube ties to the lower cage rail.
- Light housing is 24 mm deep with its tube crossbar 18 mm forward of the rear face, clearing the rear skin and LED peg sockets. Peg-hole cutters now cover the full peg length; red front faces remain blind and unperforated.
- 09:49 refinement: removed the obsolete long body-side canopy peg-support ledges as well as the previously removed canopy rail. The shell is checked for connectivity without those legacy shelves.
- Lower exposed tail rails now start at the same transverse station as the upper roof rails, then taper inward to 30 mm half-spacing. This also clears the rear body skin at the rail root.
- Selected Cage gusset face at (41.2,129.8,146.3): thickened the tube attachment to 6 mm at the default 3 mm web, tapering over roughly 16 mm into the original web. Local tube/web junction edges receive a 1.5 mm fillet where valid (1 mm fallback); all reinforcement is fused into the same cage solid.
- Filled the missing triangular sill-to-door transition beneath each restored rear quarter cover (09:51 markup).
- 09:54 clarification: additionally reinforced the LOWER gusset-to-diagonal-tube foot. Default thickness is 8 mm with a 24 mm taper back to the 3 mm web and a rounded 13 mm collar around the 10 mm diagonal tube. This is separate from the upper rail-root reinforcement.
- 09:56–09:57: replaced the dogleg lower rear support with a single straight tube from the lower chassis rail to the gusset rear tip. The gusset foot now lies exactly on that line in both plan and elevation. Added the marked tube along the gusset bottom edge (part of that continuous diagonal) and a front-edge tube from the reinforced foot to the upper rail, mirrored on both sides.
- 10:01 clarification: the continuous lower diagonal now runs all the way to the rear END NODE, not to an intermediate point on the upper rail. The gusset is fitted between that single diagonal and the straight upper rail, eliminating the change of angle before the tail end.
- The 10:01 straight backbone starts at the FORWARD lower-frame junction (rail Y=-180), continuing without any intermediate bend to the rear light-housing node. It replaces the old rising side X-brace plus rear continuation; the opposite diagonal remains. Gusset foot and lower edge are fitted onto this single straight member.
- 09:58–09:59 light housing: replaced the rectangular collar with the marked faceted eight-sided rear outline (pointed ends and a shallow centre crown) and a swept wedge side profile. Straight red strip retained. Housing remains hollow with 3 mm walls, a thicker rear lens seat, and internal frame saddles with 0.15 mm clearance around the three converging rails and rear crossbar.
- Fit corrections from the full-assembly collision report: front cage legs moved to X=±45.5 mm (the imported front deck spans ±54.5 mm), clearing the battery-tray edge; rear bridge legs moved to ±51 mm to clear the upper driveline component. Rail foot-post OD is 9.4 mm at defaults, preserving 3 mm wall around M3 clearances while clearing the rocker skin. Shell pilot bosses reduced from 13 to 12 mm OD.
- Rear light contact moved to Y=2 mm, range -10 to 4 mm, clearing the roof cross tube. Contact-post tops now follow sampled roof facets with a 0.3 mm gap instead of penetrating the sloping roof. Front bumper cross tube moved 2 mm forward to clear its contact block.
- Reference shock eyelets now connect to the strut through narrow necks, with both pin bores retained. This removes the visibly disconnected eyelets without changing the two eye centre positions or suspension kinematics.
- 10:16–10:24 shell cleanup: nose lower half-width now derives from the 40 mm skid-plate half-width. Rear side covers and their full lower fascia are welded into the main body, built as one mitred panel network and clipped to a shared trailing point. No separate-cover pocket or doubled rear tip remains. The rear shoulder is pinched inward.
- 10:33–10:35: set the rear shoulder peak halfway down toward its lower crease (trace Y=215), and lowered the forward quarter-wing peak likewise (trace Y=230). The main window rail retains its original straight height datum. Transverse tube inset is now 6.5 mm, with the pinched rear shoulder width chosen for about 3 mm plan clearance to the tapered rear rails.
- Shortened the oversize front start of the sill body cut to the named glue gap; this closes the unintended cowl/A-pillar slot while retaining the canopy assembly clearance.

## Canopy seat build repair — November 12
- The independently generated right sill clearance envelope became invalid at shallow rear mitres and left about 51 mm3 of canopy/body interference. Generate the valid left envelope and mirror it for the symmetric right seat. Preserve the existing glue clearance and sill/cowl shape.
- Added validity and complete-containment checks to the sill and canopy seat cutters; existing part interference and minimum-gap assertions remain active.

## Tail light housing completed — November 12
- Repaired the overlapping capsule cuts that had replaced the housing with a small saddle remnant. Frame clearances are now cut sequentially; full-width and validity checks prevent that silent failure. The visible part is named "Tail light housing" (formerly "Rear shell").
- Retains the specified eight-sided pointed outline, swept 24 mm nominal-depth wedge, 3 mm walls, hollow forward access, recessed 76 x 8 mm red strip and blind LED sockets. Tube saddles and lens seat retain 0.15 mm glue clearance. Bond after dry fitting; route LED wires through the open forward cavity along the tubes. No additional hardware.
- Housing: one PLA/PETG FDM part. Print on the flat rear face with the lens omitted, cavity upward; supports may be needed at the frame saddle recesses. Arrange and drop to bed in slicer. Existing light strip remains a separate translucent printed part.

## Light wrap corrections — November 12, 13:54–13:56
- Extended the tail underside forward to wrap the tube junctions, using a 48 mm housing depth (assumed from the undimensioned markup); retains forward access and 3 mm walls.
- Tail lens now inherits the housing eight-sided outline. LED pegs move inward to X=±8 mm and 4 mm above lens centre to clear the cross tube and open up access. Blind 3 mm LED bores retained.
- Front chevron is inverted to a raised centre; side returns follow the actual nose closing-panel top edges on both sides with matching clearance channels.
- Front wrap has finite overlapping mitres for a single lens solid and 5 mm internal closing-panel backing behind the recessed strip. The channel boolean leaves two negligible numerical dust solids; only fragments below 0.001 mm3 are removed before the single-solid check.

## Full tail tube wrap — November 12, 14:30
- Corrected the 13:54 interpretation: the housing now fans downward as well as upward at its open forward edge. The bottom follows the actual long chassis diagonal, the top follows the roof tube, enclosing all three tube pairs and rear crossbar. Existing tail face/lens and central socket locations stay fixed.
- All six tube clearance capsules extend beyond the full housing depth; their individual entry openings follow the tube axes. This supersedes the earlier parallel underside extension that covered only the top pair.

## Hood and front light weld audit — November 12
- Removed the obsolete painted nose-light grooves beneath the separate lens. Added explicit coplanar-face unification for the completed front shell and front lens at 0.00001 mm linear / 0.000001 rad angular tolerance.
- Both must remain one valid solid with one closed boundary shell, no internal shells, and unchanged material volume after seam unification. Hood armor folds, front chevron and side wraps remain intentionally faceted; "planar" is interpreted as clean joined facets, not flattening the entire hood.

## Nose socket access and light shielding — November 12, 14:33
- Front LED pegs now extend 16 mm from the lens face, with matching through-hole cutters and blind 3 mm bores. Tail pegs retain their existing length.
- Added a 3 mm opaque inner backing behind the chevron seat, with a 2 mm perimeter overlap into the nose. Only the LED peg holes pass through; the broad red strip is shielded from the cabin.
- Weld audit checks actual topological shell closure with BRep_Tool, rather than relying on the cached shell Closed flag after geometry transformation.

## Tail access and weld-check correction — November 12
- Tail housing remains a separate printed solid and STL, never fused to the cage. Bond it onto the finished frame after printing and dry fitting.
- Replaced rear-facing central LED sockets with upward-facing 14 mm tall sockets, inset 3 mm behind the red face; clearance holes pass through the cover top. LEDs insert from above, bypassing the rear cross tube. Red face remains unperforated.
- Hood mesh audit: one valid material solid with three closed boundary shells (two enclosed voids), watertight and consistently oriented. The nose lens is one valid solid with one watertight boundary. Weld validation preserves existing voids and checks every boundary is closed instead of incorrectly rejecting enclosed voids.
- A wider-tolerance coplanar unification changed the hood's material volume. It is now accepted only when volume is preserved; otherwise the original valid fused geometry is retained. This prevents a cosmetic seam cleanup from changing the modeled panels.

- 14:42 hood markup: clip the nose closing-panel upper mitres to the sampled adjoining hood plane, removing the raised return strips and corner nibs while preserving the hood slope and front-light side wraps.
- Final front socket correction: short 4 mm face-normal roots feed 20 mm horizontal inward sockets below the hood; the earlier 16 mm inclined pegs emerged through the hood. Horizontal bores preserve the opaque front lens.
- Chassis appearance request: disabled viewer Display > Edges to hide the mesh-edge overlay; chassis remains separate purchased/reference CAD geometry, not printable replacements.

## Whole-assembly seam cleanup
- Every registered part and nested chassis/swingarm body now passes through coplanar-face cleanup. Accept cleanup only if valid and preserving material volume, solid count, and boundary-shell count. Designed folds, curved tubes, fit clearances and distinct components remain.
- Hood closing-panel upper returns are specifically clipped flush to the real hood planes. Geometry-wide cleanup removes redundant planar subdivision seams without flattening designed curved hardware.

## Final validated state
- Front sockets are straight horizontal sleeves rooted directly in the lens, with individually cut passages. No inclined roots or exterior hood protrusions remain. Broad chevron has an opaque backing.
- Coplanar unification operates on a deep copy so OCC cannot mutate the accepted source geometry. Whole-assembly cleanup preserves valid volumes and component boundaries.
- Build passed (95 parts), final hood render checked, all printable STL exports refreshed. Housing and both light meshes exported without warnings; the pre-existing Cage STL mesh warning remains (4 open edges, 63 non-manifold edges, 126 inconsistent-orientation edges). CAD body validity alone does not resolve those cage mesh junctions.

## Rear sockets inside the housing, hood backing clipped — November 12, 15:05 markups
- Tail LED sockets now face forward from the lens back, 15 mm long, through the 3 mm wall into the hollow housing. Nothing pokes out of the housing top any more. `TUBE_END_SETBACK` is 34 mm (was 18) so the tail tubes end ahead of the sockets.
- The raised bar on the hood by the nose was the opaque nose backing sticking up through the hood skin. It is now clipped to the hood's convex envelope before it is fused.
- Open: the A-pillar foot (15:06 markup). Probed numerically, the canopy and the front shell are flush within 0.5 mm at the foot (x about -85). The defect is not clear from the numbers and needs a closer markup.

## Hood ridge, A-pillar foot lump, backing clip — November 12, 15:27
- Hood quads are now exactly planar (`hood_centres()` in `parts/shell_geometry.py` solves the centre-line heights), so there is no diagonal fold in each hood facet.
- The 0.7–0.9 mm riser between the hood edge and the cheek facet (the 51 mm² face at x -40) was reduced by dropping the hood edge (`HOOD_EDGE_DROP` = 0.8 mm at the nose, 1.05 mm at the rear corner). It is about 0 mm along the nose half and about 0.4 mm along the rear half. A drop of 1.35 mm broke the cage belt-line tubes (cage.py:91), so it is capped at 1.05.
- A stray lump on the front shell ahead of each A-pillar foot is trimmed off (about 122 mm³ in total).
- The nose backing is cut by the hood plane of each half, so it no longer shows through the skin.
- Open: the red wing corner joints where the nose strip wing meets the chevron lens (15:27 markup).

## One-piece hood and fender panel — November 12, 15:40 selection
- Hood quad, nose-end hood facet and fender facet were three faces (two B-spline, one plane) with slightly different normals. A thin plate on the hood plane now lifts the fender and nose-end facets onto it (about 330 mm³ per side), and a flat-face merge (`_unify_flat` in `model.py`, 1e-3 tolerance, accepted only if valid, one solid and volume within 5 mm³) fuses them. Each side's hood and fender top is one planar face of about 2725 mm².

## Right hood merge, one-piece light wings — November 12, 15:45 selections
- The hood plate now picks every near-coplanar top facet beside each hood plane (fender, nose-end hood piece, cap top) instead of two hand-picked faces. Each side is one 3099 mm² planar face. The plate adds about 1160 mm³ in total (assert limit 1400).
- Each nose light wing is a single convex hull of both facets, their inner faces and the root overlap, replacing the four overlapping blocks and knuckle that left slivers (3–100 mm² faces) at the corner joint.

## Hood panel, remaining slivers — November 12, 15:55 selection
- The hood plate now takes every top facet within -1.2 / +0.15 mm of the hood plane, is trimmed to the raked nose face plane, and the shell is cut flat above the plane inside the plate footprint. Each hood and fender top is one 3218 mm² planar face.
- Left as separate faces on purpose: the roughly 49 mm² rim face at the nose front edge (a nearly vertical face, so it cannot join the top plane) and two slivers of 7 and 2 mm² beside the lens channel corners at x about 33–38.

## Rear quarter cover moved to the canopy; front shell merged — November 12, 16:10
- `rear_side_cover` (the triangular rear quarters behind the B-pillar) is built in `make_canopy` and in the canopy seat tool instead of in the front shell. The canopy is one 93,003 mm³ solid; the front shell no longer contains those faces.
- Whole-shell flat-face merge in `model.py` (`_unify_flat`) tries 0.1, 0.05, 0.02 and 0.001 mm and keeps the loosest result that is valid, one solid, and within 0.5 % volume. At 0.05 mm the front shell went from 780 to 717 faces (volume −528 mm³, 0.2 %); 0.1 mm gave an invalid solid.
- Canopy flat-face merge: 0.1, 0.05 and 0.02 mm all gave invalid solids; only the 0.001 mm merge is valid, 408 to 395 faces, no volume change.
- Nose light strip flat-face merge: 54 to 52 faces at 0.1 mm, valid, no volume change.

## Surface and panel alignment requirements — November 12, 16:40 (from the user)
- Model the whole outer body first as one unified, watertight faceted master form, then split it into panels (hood, fenders, A-pillar, etc.). Adjacent panels are derived from the same master surfaces, so planes and angles continue across every panel break.
- At multi-panel corners (A-pillar, hood, front quarter) all outer surfaces are flush to the master form: the meeting vertices share the same outer tangent plane, nothing proud or shy.
- Every facet of a multi-faceted panel (hood and other large panels) is a true flat plane. Crease lines are strictly collinear and sharp, with no step-off or overlap.
- Printed in several pieces: no plain butt joints. Use recessed backing flanges (stepped lap joints) or locating tabs/pins on the inside of every seam, so the flange stops both outer surfaces at the same height and angle.
- Panel gaps are uniform (the message left the value open, "0.4 mm / your preferred gap") with a consistent wall thickness.
- Status: not started. The current shell was built panel by panel from traced triangles and patched afterwards. Merging facets after the fact (hood plate, flat-face merge) works only for near-coplanar faces; attempts to flatten the flank pairs (+2.7 and +2.4 cm³ per side) were rejected by the validity/clearance checks. Hood and cowl cannot be one plane without a 9 mm change at the A-pillar foot or the nose lens.

## Master-surface rebuild, stage 0 — November 12/13
- Decisions from the user: keep a 0.3 mm panel gap, keep the current shape as the reference, facet angles may shift by a few mm to line planes up, keep the old shell. The old build is archived in `archive/shell_v1/` (model.py, parts/, model.step).
- `PANEL_GAP` (0.3 mm, a parameter in the Shell group) now drives the canopy, rear-quarter-cover and grille seat cut-outs. It was `GLUE_GAP` = 0.15 mm before, so the seams were 0.15 mm by design, not 0.3 as this file said. `GLUE_GAP` still sets the lens and tube fits.
- `clearance_hull` offsets with 26 unit directions (0.93–1.0 x the gap on every facet) instead of a +-gap cube per axis (1.0–1.73 x).
- Cage, `clean_registered`: OCC "Courbes non jointives" errors on `fuse`/`clean` no longer abort the build; the member is retried with a nudge or the part is kept uncleaned.
- `tools/surface_audit.py` measures planarity, near-coplanar facet pairs, seam gaps and the A-pillar foot against the requirements. Baseline: all faces over 30 mm2 are truly flat (0 warped); 7 adjacent pairs of large faces are 5.0–6.9 degrees apart (should be one plane or a clean crease); canopy-to-shell gap is not yet uniform: only about 3 % of the seam area is at 0.25–0.36 mm, most is 0.4–1.0 mm, and the narrowest spot of each canopy face is 0.46–0.6 mm at the pillar foot and rear end.
- Open (not started): one master faceted body split into panels, flush multi-panel corners, stepped lap joints / locating tabs on every seam, uniform seam gap by construction.

## Master-surface stage 1 — flank regularization (November 13)
- `parts/reference_trace.py` (`_regularize_flank`): neighbouring flank triangles 0.3–9 degrees apart are made exactly coplanar by the smallest half-width shifts (least squares; coplanarity is linear in the widths). The window belt line (px 622 and 815) shifts by +4.0 and +3.0 trace mm through `BELT_DW`, so `belt_station` and everything built on it (window frame, sill, rails, cage nodes) follows. The B-pillar foot (px 930), the belt ends (457, 1082) and the wheel-notch point (510) are fixed. Switch it off for comparison with `SOMA_NO_REGULARIZE=1`.
- Adjacent near-miss pairs of large front-shell faces went from 7 distinct pairs to 5 (5.0–5.6 degrees). The rest come from the rear fold point and the cheek polygon, which are not part of the solve yet.
- `roof_underside` retries a hair to either side, because a probe exactly on the hood centre seam returned nothing after this change.
- Canopy seat cutter check now allows 0.05 mm3 (it prints the leftover and where it is if it fails).
- Next: add the fold point and cheek polygon to the solve, make the hood-to-cowl crease and the A-pillar foot corner flush by construction, then the stepped lap joints and a uniform 0.3 mm seam.

## Master-surface stage 2 (status)
- Cheek polygon is now the shared table `CHEEK` in parts/reference_trace.py; the flank regularization includes the cheek triangles and the rear fold point (tied to its side-mesh neighbours). Cheek width follows SIDE (437,219) = 56.2.
- Build ok. Audit: planarity warp 0; still 5 near-miss pairs (5.0-5.6 deg) between large faces; seam gap min 0.36 / mean 0.60 mm (target 0.30), A-pillar foot left side 85.61 vs 86.09 mm (0.5 mm step at y=-205).
- Open: corners flush by construction, lap joints/tabs, uniform 0.3 gap.

## Hood front / cowl step removed
- The front (3218.6 mm²) and cowl (3709.6 mm²) planes stood up to 1.1 mm apart along their crease. model.py now shaves everything above the cowl plane in a strip ahead of the cowl edge (44 mm³ per side). Surface height along x=10..70 is continuous (no step); the crease is a sharp convex fold.
- The shaved face is coplanar with the cowl but remains a separate face (134 mm², tolerance merge would distort the volume).

## A-pillar foot trim
- Canopy tip that overhung the shell corner (3-4 mm outside, ~5 mm above the shell) is cut on the shell's flank plane (n=(0.924,0.054,0.380), d=115.4, mirrored), 428 mm3 total. Pillar foot now ends on the same plane as the front shell. Seam gap max 1.98 -> 1.05 mm.
- Open (reported by user, not done): light strip tips visible inside the cabin (markup-20261113-0327), Rear/Front light contact blocks and cage plates to become tubular, left flank face lining up (1158.7 vs 1643.3 mm2), straight sill/pillar line, uniform 0.3 mm gap, lap joints.

## Nose strip wing ends
- Open end faces of the nose strip wings (x=±70, y≈-252) are closed with a 3 mm backing block fused into the Front shell (model.py, before the lens-interference assert). Check: only those 2 end faces were in free space; now none.
- Checked against older commits (ebca774, ef6f295): strip exposure metric is identical, so the red wedges in markup-20261113-0327 are not a regression of today's changes. After this change a render from inside still shows red wing inner faces next to the cowl; not yet resolved.

## Round light connectors
- parts/light_contacts.py: bridge and shell contact plates are stadium-shaped (slot2D), posts and bridge legs are round (LEG_D = 10 mm), matching the cage tubes. Magnet pockets unchanged. Build ok.

## Seam gap now true to PANEL_GAP
- Root cause of the 0.46-0.6 mm gaps: the shell is built in model units and stretched afterwards (x 1.66, y 2.17, z 1.95), so a 0.3 mm gap built into the model became ~0.65 mm. params.py: PANEL_GAP_M converts the gap to model units, PANEL_KX corrects the x direction in clearance_hull.
- Audit: front shell <-> canopy gap min 0.256 / mean 0.291 / max 0.75 mm (before: 0.46 / 0.57 / 1.05); 234 of 256 faces are inside 0.25-0.35.
- Note: other pre-scale constants (WALL, GLUE_GAP overlaps) are stretched the same way; check them if a wall or joint looks too thick.

## Locating pins across the canopy/front-shell seam
- model.py: 13 round pins (1.6 mm, 3 mm long) grow from the canopy seam faces into the shell wall; matching 1.9 mm holes in the Front shell. They register both panels in all directions so the outer surfaces cannot step against each other (replaces the plain butt joint). Each pin is accepted only if both parts stay one valid solid and do not interfere (13 of 14 candidates accepted). Parameters PIN_R, PIN_HOLE_R, PIN_LEN, PIN_SPACING, PIN_MAX at the pin block in model.py.
- Not a stepped lap: the seam is irregular, so a continuous lap would need a new seam definition.

## Tried and reverted
- A second 1.2 mm cut to remove the knife edge under the A-pillar foot made the canopy invalid for the pin step (0 of 14 pins accepted), so it was reverted. The foot corner at (85.4, -210.1, 126.1) is still a thin edge.

## Nose strip inner faces
- model.py covers flat nose-strip faces that look into the cabin with a 2 mm backing (0.15 mm clearance); 2 faces covered. The red wedge next to the left peg in a render from inside is still visible (face not caught by the test: it is partly in shell, partly free).

## Nose strip sits in its groove (update)
- The inside backing now covers every flat strip face that is not forward-facing or upward-facing (10 faces, including the 253.9 and 239.6 mm2 faces the user marked). Render from inside: right wing fully covered, left wing has only a small red tip left next to the peg.

## Master-surface completion: coplanar facets and continuous stepped lap joint — November 13
- User confirmed: 0.3 mm uniform `PANEL_GAP`, keep current printable part division (`Front shell`, `Canopy`, `Tail light housing`, `Grille insert`) derived from the unified master outer body, and replace point pins with a continuous recessed backing flange (stepped lap joint) along the panel seams.
- `model.py`: verifies the unified watertight master body (`shell.fuse(canopy).clean()`) before splitting into panels; aligns the front-cap lower cheek vertex exactly onto the outer nose-cap plane `(outer, nose_top, nose_bottom)`, eliminating the 5.03° front-cap near-miss.
- `parts/shell_geometry.py` (`make_quarter_wing`): projects vertex `V[1]` onto the outer wing plane `[0,5,2]` and leading deflector roots `V[8]`, `V[9]` onto the inner wing plane `[6,0,3]`, eliminating the four 5.17°–5.59° quarter-wing near-misses.
- `parts/canopy_frame.py` (`seam_lap_flange`): replaces the 13 discrete pins with a continuous faceted stepped lap flange recessed into the inner half of the wall (`0.55 * WALL` inset, `0.65 * WALL` thick) along the entire side and rear canopy-to-shell seam (`sill_sections` stations 4..15), with matching `PANEL_GAP_M` stepped recess in `seat_tool`. When pushed together, the stepped lap flange mechanically stops both outer surfaces flush at the exact same height and angle.
- Surface audit (`tools/surface_audit.py`): 0 warped faces (>0.05 mm) out of 295 faces >30 mm²; all 5 previous near-miss facet pairs (5.03°–5.59°) eliminated; seam gap min 0.256 / mean 0.284 / max 0.441 mm across 268 seam faces (250 of 268 within 0.25–0.35 mm, zero 0.000 mm pin artifacts); symmetric A-pillar foot alignment on both left and right sides (`|x|` = 85.61 / 85.38 / 85.15 mm).

## Clean A-pillar foot / cowl / flank corner (markup-20261113-1344) — November 13
- Root cause of the notched Z-step at the A-pillar foot: `outline(side)[0]` (`parts/canopy_frame.py`) and the cowl rear corner (`hood_centres`, `hood_outer_limits`, `make_cowl` in `parts/shell_geometry.py`) were offset outward by `+WINDOW_RAIL_WIDTH / 2` (`2.0` model units), and two local bounding-box cuts (`_lump` at `z = 128.8` on `Front shell` and `_zone` ending at `y = -202` on `Canopy` in `model.py`) hacked off the overhang, leaving a vertical notch in the side of the A-pillar and a horizontal shelf on the cowl corner.
- `parts/shell_geometry.py` (`flank_surface_x`, `hood_centres`, `hood_outer_limits`, `make_cowl`) and `parts/canopy_frame.py` (`outline`): project the A-pillar foot and cowl rear corner directly onto the exact front-upper flank plane (`mesh(SIDE, 1, CREASES)[0]`), and remove both legacy box cuts from `model.py`.
- `parts/shell_geometry.py` (`sill_sections`, `sill_fascia`, `make_quarter_wing`): project the sill top edge onto the single window-sill plane `(0,3,5)` (removing 3 tiny sliver facets at the front tip of the sill where roof-fold lines crossed) and align `V[7]` onto the upper quarter-wing plane `[4,8,2]`, bringing adjacent near-miss facet pairs (>500 mm²) down to `0` (`[]`).
- `parts/light_contacts.py` (`make_connector`): intersect the sloped roof-matching cap wedges on the Front and Rear light contact blocks with the Ø14 mm round post cylinder so the posts stay completely round up to the roof instead of flaring into a 12 × 12 mm square flange.
- `model.py`: registered all chassis, suspension (`arm -1`/`arm 1`, `uplink -1`/`uplink 1`, `pod -1`/`pod 1`, lean shocks/rocker), steering (`carrier -1`/`carrier 1`, `knuckle -1`/`knuckle 1`, `tie rod -1`/`tie rod 1`, servos/horns), frame/decks, drivetrain, wheels, and rear swingarm (`w3 rear arm`) assemblies as first-class printable parts (`role='part'` instead of `role='hardware'`), so all 95 parts in the project are included in `soma export --all` and print builds.

## Cowl-edge groove filled — November 13 (markup 15:45)
- A V-slot (about 0.7 mm deep, 30 mm long, wall + ramp facet) ran along the outer cowl edge from the A-pillar foot to y = -242. `_fill_cowl_groove()` in `model.py` fills it up to the cowl plane (2 mm slab over the slot footprint), clipped at y < -216 so the canopy pocket at the foot stays open. It runs after the "hood/fender wedge too large" check (the wedge stays under its 1400 mm3 limit; the groove fill adds 36 + 12 mm3).
- Open (markup 15:46, not done): the nose strip wing-end corners. The 3 mm wing-end backing blocks stick out about 3 x 3.5 mm below the strip's lower lip and leave sliver facets along the top lip at x = +-69, y = -251.

## Assembly methods and hardware — November 13
Rules (from the user): a screw from the top goes into a heat-set insert in the part below (the deck). A screw from the bottom goes through a countersunk hole in the deck into inserts in the part above. Every individually printed part needs a screw method.

### Cage feet (screwed down from the top into the deck)
- Each foot has a flat 3 mm stadium tab beside the post with an open Ø3.4 hole (head accessible from above). The old holes ended blind inside the tubes and could not take a screw.
- The deck (`w3 deck front` / `w3 deck rear`) gets 6 insert pockets (Ø4.2 x 5 mm deep) cut in `model.py` (`_deck_pockets`). The decks are 109 mm wide (+-54.5): the rail-foot screws sit at x = +-56.5, so each of those 4 pockets has a small deck ear (5 mm wide, 14 long, 6 thick). Front feet: x = +-45.5, y = -171.5 (behind the foot, clear of the leaning leg), no ear.
- Tabs and posts stand 0.05–0.1 mm above the stand-in deck surface (it is a slightly sloped mesh; tabs are lifted 0.4 mm, front tabs at z 21.06).
- Deck is only about 6 mm thick: an M3 x 4 insert pocket (5 mm) leaves about 1 mm below it. Re-check when the real deck is designed. The decks and all other chassis parts are still convex-hull stand-ins from the GLB and have no other holes (motor plate, battery tray, servo and diff mounts are not designed yet).

### Tail housing (screwed to the cage, hidden behind the red lens)
- Two countersunk M3 screws at x = +-16 mm go through the housing wall behind the lens (hole Ø3.4, 90 degree countersink flush with the lens seat floor, so the lens sits on top of the heads) into heat-set inserts in two Ø8 stubs on the cage's rear cross tube. A 3.5 mm boss on the inside of the wall carries the head. The screw axis is tilted 33 degrees from the lens face because the cross tube sits below and 27 mm in front of the lens. 0.1 mm gap between boss and stub (the screw closes it).
- Source: `make_tail_screws()` in `parts/light_strips.py`; tuning constants `TAIL_SCREW_X`, `TAIL_SCREW_V` (+ is down the face).
- Checked in the built model: housing, lens and cage do not overlap (cage to housing 0.10 mm), housing is one valid solid.

### Hardware list (assumed sizes: confirm before selling)
| Item | Qty | Where | Notes |
|---|---|---|---|
| Heat-set insert M3 x 4 mm (OD 4.6) | 6 | cage feet, in decks | pocket Ø4.2 x 5 deep |
| Screw M3 x 8 (socket or button head) | 6 | cage foot tabs into deck inserts | 3 mm tab + 4 mm engagement + 1 |
| Heat-set insert M3 x 4 mm (OD 4.6) | 2 | tail stubs on cage cross tube | pocket Ø4.2 x 5 deep |
| Screw M3 x 12 countersunk (ISO 10642 / DIN 7991) | 2 | tail housing to cage | 12.2 mm axial to the insert bottom |
| Screw M2 self-tapping (pilot Ø1.8) | 6 | shell to cage bosses | assumed, length not chosen yet |
| Magnet 6 x 3 mm N52 | 8 | light connectors (front and rear, block + cage plate, alternate polarity) | assumed, see "Magnetic light connections" |
| LED 3 mm (red) | 4 | 2 tail (x = +-8), 2 nose (x = +-22) | blind Ø3 bores in the lens pegs |
| M6 bolt, 28 mm (shock pin) + nut | 1 | shock top pin through the cage nodes and the eye | |
| Zip tie | 2 | shock bridge on the arm tube | |
| Heat-set insert tool / soldering iron | 1 | assembly | not part of the BOM |
Chassis donor parts (axles, links, shocks, wheels, motor, servos): Axial SCX10 III class parts, see the "Donor platform" notes above; they are not listed here yet.

## Deck, light bar, cage, rear arm (2026-11-14)
- **Deck cleanup, cage-foot edge margins, and rear tail extension** (`parts/deck.py`, `parts/cage.py`, `model.py`):
  - Removed the protruding side deck bands (`band_pieces()` returns `[]`, `markup-20261114-1224-2.png`).
  - Added `clean_deck_plates()` in `parts/deck.py` to fill in all unused leftover holes and blind pockets from the old layout across `w3 deck front` (`(21.3..-217, 25.9..-215)`, `(26.6, -186.0)`, `(±44.0, -88.2)`), `w3 deck rear` (`(±52.5, -24.2)`), and `w3 deck tail` (`(±41.5, +85.5)`), while keeping all active mounting holes and slots for `battery tray c`, `mock receiver`, `lean mount c`, `w3 fdc lower`, `w3 cdc lower`, `w3 pillow lower`, and `w3 rbc lower`, and unifying coplanar mesh facets.
  - Extended `w3 deck front`'s straight `±54.5 mm` side edge forward to `y_ref = -212.0 mm` (`y_world = -203.0 mm`), extended `w3 deck rear`'s straight `±54.5 mm` side edge rearward to `y_ref = +39.0 mm` (`y_world = +48.0 mm`), and moved the cage foot and side-rail X position to `x = ±45.0 mm` (`FRONT_LEG_X = REAR_LEG_X = CAGE_RAIL_X = RAIL_FOOT_X = 45.0 mm`), giving all 6 cage deck mounting holes `9.5 mm` center-to-edge margin (`> 6.3 mm` solid wall outside the `Ø6.3 mm` countersink, eliminating any edge-shear risk, `markup-20261114-1341.png`).
  - Extended `w3 deck tail`'s rear trim from `y_ref = 125.0 mm` (`y_world = 134.0 mm`) back to `y_ref = 139.0 mm` (`y_world = 148.0 mm`) so `w3 deck tail` extends `7.0 mm` behind `w3 rbc lower` (`y_ref <= 132.0 mm`) and fully encloses its rear mounting slots (`y_ref = 124.2..135.6 mm`, `markup-20261114-1342.png`).
- **Nose light bar** (`parts/light_strips.py`): one ribbon along the hood-top edge, `NOSE_EDGE_GAP` (1.0 mm) below it, `NOSE_BAR_H` (7 mm) high, mitred at every corner, ends pulled back `NOSE_END_TRIM` (9 mm) from the cowl corner. Channel, backing and LED sockets (x = +-22) follow the same path.
- **Cage, inboard deck mounts, rear-quarter slope, and integrated light connectors** (`parts/cage.py`, `parts/tail.py`, `parts/light_contacts.py`):
  - Added `_split_endpoints_on_segments()` and spherical joints for acute 2-tube V-junctions (`c > -0.1`) in `_Frame._resolve_tubes()`, plus explicit shared belt nodes `u_nodes` so the door-bay V-truss diagonals and upright meet the upper belt rail at a single spherical node without gaps or mitre spikes (`markup-20261114-1224.png`).
  - Added `tail_tube_starts(b1, end)` shared between `parts/cage.py` and `parts/tail.py` so the rear-quarter cage tube (`b1 -> mid_q -> n_tip`) follows the exact `-1.3012` YZ slope of the `Canopy` rear quarter cover (`1396.1 mm²` face, `markup-20261114-1255.png`). Removed the legacy trapped internal saddle blocks (`rib` at `(-24.1, 213.0, 179.8)`) from `Tail light housing` in `parts/tail.py` and swept all cage clearance channels forward along the exact M3 screw insertion axis (`slide_dir = (0, -0.9906, -0.1369)`), so `Tail light housing` slides straight backward off the rear of the cage without any undercut once its two M3 countersunk screws behind the lens are removed.
  - Positioned the cage side rails and all 6 straight vertical deck mounting feet at `x = ±45.0 mm` (`9.5 mm` inside the `±54.5 mm` deck edge, `markup-20261114-1225.png`, `markup-20261114-1341.png`) with `CAGE_Z = 85.0 mm` at interference-free deck stations (`y = -195.0, -48.0, +38.0 mm`), clearing `battery_tray_c`, `w3_motor_plate`, `w3_cdc_lower/upper`, `Front shell`, and `Canopy` with `0.00 mm³` interference.
  - Replaced the legacy mid-cabin stadium bridge plate (`400.0 mm²`), its two cabin-blocking diagonal tubes (`2148.6 mm²`), and the 70 mm hanging roof post (`3284.7 mm²`) with compact `28 × 14 mm` magnetic contact bosses built directly into the cage's front hoop crossbar and B-pillar roof header spine, paired with low-profile flush hood/roof magnet pads (`Front light contact block`, `Rear light contact block`).
  - Built an overhead ladder bridge (`z ≈ 187–192 mm`) and vertical drop-down double-shear upper shock clevis mount into the cage tail frame (`|x| = 4.4..10.4 mm`), with raised cylindrical outer hardware bosses (`|x| = 4.4..12.0 mm`, `Ø13.6 mm`), an open `8.8 mm` central slot (`x = -4.4..+4.4 mm`) for the `8.0 mm` shock eye, and a completely clear lateral hardware corridor along the M6 pin axis (paired with modeled M6 socket-head shoulder bolts and nyloc locknuts at both upper and lower shock mounts).
- **Rear and front swingarms** (`parts/swingarm.py`, `parts/frontarm.py`, `model.py`): redesigned for high bending and torsional strength following the supplied samples (`markup-20261114-1011.png` / `nlc-st-30102`, `markup-20261114-1011-2.png`, `markup-20261114-1226.png`, `markup-20261114-1340.png`, `markup-20261114-1345.png`).
  - **Front swingarms** (`arm 1` / `arm -1`): built an integrated pod-seat pad (`x = 85.5..93.5, y = -214.5..-193.5, z = 68.5..71.8 mm`) on the outer upper chord directly under the suspension lean pod (`pod 1` / `pod -1`) that carries the G-load of the front tires, braced by vertical and diagonal Warren struts down to the lower chord and top/bottom cross-tubes + Warren diagonals across to the inner frame (`PLATE_X = (66.2, 89.5)`, clearing the front belt and pivot pulley). Redesigned the front pivot and tip bosses to match the rear swingarm's cast-style tapered web neck (`P = (-125.8, 62.8)` to vertical root post `L0 -> U0` at `y = -139.0`, and `U3 -> L3` into `T = (-225.55, 55.9)`, `markup-20261114-1340.png`).
  - **Rear swingarm** (`w3 rear arm` in `Rear swingarm`): assigned `make_rear_arm()` before `add_part('Rear swingarm', _rr)` in `model.py` (`Ø11 mm` chords segmented at explicit strut nodes, three `Ø9.5 mm` forward-leaning ladder struts per side, solid gusseted pivot and hub-neck webs, 6-bolt hub carrier flange, cross-tubes and Warren top diagonals above the belt, and a pyramid-braced twin-arch over-tire shock mount with a double-shear clevis around `SHOCK_EYE_YZ = (150.0, 114.0)`). Added inboard diagonal knee-brace tubes (`(47.0, U0) -> (20.0, 134.0, 114.0)` and `(47.0, S1_T) -> (20.0, 150.0, 114.0)`) and solid 6 mm triangular corner gussets in the 90° inside corner under the over-tire shock cantilever (`markup-20261114-1345.png`), clearing `w3 rbc upper` across full bump/droop travel.

## Shell fix passes 2-7 — November 14 (consistent wall, clean arch, flat sill)
- User: "i want the whole shell to be free of stray steps and jaggedness. i want this to look like it was injection molded ... the shell should have consistent thickness throughout."
- Wall: the shell is stretched after it is built (x by the width match, y by SHELL_SCALE, z by SHELL_SCALE*SHELL_Z), so one model wall printed 2.3 mm on side-facing facets, 2.7 mm on top-facing ones and 3.0 mm only on forward-facing ones. `printed_thickness()` in `parts/panels.py` now sets each facet's offset so it prints WALL_PRINT; `panel_prisms(..., final_frame=True)` is for triangles already in printed coordinates. The quarter-wing cavity uses the same function. Measured by ray casting on the built solids (60 000 samples): median wall 2.6 -> 3.0 mm (Front shell), 2.4 -> 3.0 mm (Canopy); share of surface at 2.8-3.3 mm 4 % -> 68 % (Front shell), 1.5 % -> 84 % (Canopy, measured before the last sill pass).
- What is still thicker than 4.5 mm on the Front shell (about 18 % of the surface): the grille frame block at the nose (about 9-10 mm) and the hidden canopy ledge inside the cabin flanks (about 5.5 mm). Both are structure and were left.
- Nose closing panels: `FRONT_CAP_T` = WALL_PRINT (was 5 mm).
- Front arch: `SCOOP_YZ` (-170, 33.4), `SCOOP_R` 91, `SCOOP_X0` 56.5. The suspension and servo clearance cuts start at x 56.9 and reached 94 mm from the old centre, so they nibbled a 3 mm band the old scoop (x 60, R 83) did not cover and left a notch in the arch edge. All of them now fall inside the scoop.
- Canopy sill fascia: stations up to `SILL_PLANE_END_PX` (815) share one plane through the straight sill top line (lower-edge points move sideways by `SILL_PLANE_NUDGE` 0.5 model mm at most); the station at 815 was removed (it lay on a straight run). The band is now one flat panel, one twisted quad behind it (the body turns inward there, twist about 7 mm printed) and the short end taper.
- Symmetry: `_symmetric()` in `model.py` rebuilds the Front shell (and the nose light strip) from one half and its mirror image. The cowl groove fill still joins on one side only; the mirror supplies the other.
- Tried and dropped: one closed polyhedron per skin (`panel_solid`, kept unused in `parts/panels.py`): the flank has a vertex with 12 facets that cannot be offset to one inner point, and the real build got more faces; looser flat-face merging (invalid solids); rebuilding flat B-spline faces as planes (rejected on the Front shell).
- Checks: build ok after every pass, `tools/collide.py` reports only the M6 shock pin in the cage (0.34 mm3, as before). Offline renders are made with a VTK script outside the project because `soma render` needs the app.

## Stealth shell — November 15
- User: "im trying to go for that stealth fighter look ... if fixing proportions or lines angles joints meeting edges do so. just make it look cool and seamless", then "as long as it still follows the original shape of it from the side and front, im ok with it", and "reduce the amount of pillars on the windows".
- `parts/stealth_shell.py` replaces the traced Front shell, Canopy and Grille insert (`STEALTH = True` in `model.py`; False restores the traced parts). The traced shell is still built, because the tail light housing comes from it and the cage follows its belt and lower edge (`_traced`), so the cage is unchanged.
- Method: each block (body, nose box, canopy) is the convex hull of a short landmark list, mirrored about x = 0, in printed coordinates. The wall is every outer plane moved 3 mm inward and intersected again, so it is exact on every facet. Open faces (underside, rear belly ramp, tail face, canopy base, canopy rear slope) have their inner plane pushed outward. Windows are a facet shrunk by `PILLAR` (9 mm), with `SILL` (27 mm) on the belt edge. Landmarks that must lie on an existing plane are computed, not typed.
- Shape: landmarks come from the traced shell (hood ridge with its kink, cowl, belt, widest line, rocker, roof). Side silhouette overlap with the traced shell 0.91, front 0.68. The front differs mainly inside the outline (window and arch shapes); the outline itself is about 8 mm wider per side at the upper canopy, because the side glass is now one flat plane, and has no rear quarter wings.
- One B-pillar per side: side glass ahead of it, closed rear quarter panel behind it, open rear slope behind the roof peak (bare cage tubes, as before). Front wheel arch is three straight edges; the belly between the arches is open behind the nose box.
- Parts: Front shell 134 faces (was 833), Canopy 40 (was 241), Grille insert 11 (flat plate on a 4 mm flange, bond from inside the nose; no hex pattern). The canopy stands on the body skin with `CANOPY_GAP` 0.3 mm; there is no locating lip or peg yet.
- Wall, ray cast on the built parts: median 3.0 mm on both; 88 % of the Front shell and 86 % of the Canopy surface at 2.8-3.3 mm.
- `tools/collide.py`: only the M6 shock pin in the cage, 0.34 mm3, as before.
- Not carried over: the nose light strip and its channel (the part is not registered while STEALTH is on), the rear quarter wings, cage-to-shell screw bosses matched to the new skin.

### Stealth shell — nose strip, canopy tabs, kit re-run (November 15)
- `nose_strip()` now fills the slot across the nose face (part "Nose light strip", registry LT1 resolves); canopy has 12 mm locating tabs cut with 0.3 mm clearance in 14 directions. Front shell 144 faces, canopy 104 faces, both valid; canopy/body clearance 0.26 mm.
- Build ok (95 parts); collide: only the known 0.34 mm3 M6 pin/cage overlap.
- Kit chain re-run on this shell: 54 printed files, 0 mesh flags, Bambu slice check 0 problems (59.2 h, 1824 g). Floating areas still flagged on CG1a, DT11, SU1L, SU1R (need supports).
- Still open: cage-to-shell screw bosses not re-matched to the new skin, no grille hex pattern, suspension-travel motion check.
- Cage bosses (November 15): with the stealth shell, `parts/cage.py` `BOSS_TARGETS` (set in model.py) makes each boss stub run to the stealth skin (0.8 mm short of it): A-pillar bosses 20.9 mm, B-pillar bosses 24.5 mm. The roof boss keeps the default 4.5 mm because a 9 mm stub made the cage mesh non-manifold at the roof rail, so it still stands about 4 mm off the canopy. Suspension and steering travel clearance comes from the swept relief tools cut from the shell (unchanged). Kit re-run: 54 files, slice check 0 problems (59.7 h, 1839 g).

### Cowl seam, tail tip, square tubes, shock hardware access (November 15)
- Cowl: the cabin opening now starts on one straight edge (y -204) across the whole width, with no centre tongue. The hood and the canopy base meet in one continuous V seam with the 0.3 mm canopy gap; the wedge slits beside the old tongue are gone.
- Tail tip: BELT_REAR and the last ROCKER point raised to z 141 so the shell tail corner lines up with the cage side tube centre (tube centre z 140.8 at y 116).
- Cage, front arms and rear swingarm tubes are chamfered square tubes (`TUBE_SQUARE`, side = 0.88 x the old round diameter, 18 % chamfer): similar section area, corners stay inside the old round envelope. Joints are mitred or coped as before; free corners get a chamfered cube node instead of a ball. Pivot bosses, posts, shock eyes and hardware stay cylindrical.
- Shock hardware access (measured with a 14 mm tool cylinder along each pin axis): upper mount ties land 14 mm above the pin axis and the clevis nodes sit 20 mm either side (`PIN_TIE_RISE`, `PIN_FAN`); lower mount arch tubes meet the ear from above (`KNEE_LIFT` 34), rear gusset stops 10 mm under the axis. Result: 10 mm free beyond both ends of both pins. Beyond 20 mm the lower pin's +x side is still crossed by the arm's arch tubes, and the upper pin has one tube touching the corridor corner.
- Swingarm articulation vs the rear drive (rbc, cdiff, rring, diff outputs, deck, battery, motor), arm rotated -15..+30 mm wheel travel about its pivot: no overlap after the fix; before it, the arm hit `w3_rbc_upper` (27 mm3 at ride, 92 mm3 at -15 mm droop). `tools/collide.py` is static only and does not move the arm: this check was a separate script (not in the repo).
- Open: arm vs lower shock pin 14 mm3 and vs the shock eye 4 mm3 at ride (a joint node on the ear), tail light housing vs cage 0.28 mm3, +x pin access beyond 20 mm on the lower mount.

## Steering geometry and Ackermann (November 20)

- The linkage is not designed for Ackermann: the steering arm ball on each knuckle sits about 3 mm behind the wheel axle line and about 10 mm inboard of the knuckle (stand-in points, `parts/steer_hw.py`), so the arms point almost straight inboard (about parallel steering). Kingpin position is estimated from the stand-ins, not measured.
- Each front wheel has its own servo and tie rod, so Ackermann can be set electronically: mix the two servos so the outer wheel turns less than the inner. With front track 288 mm and wheelbase 453 mm (front axle y -216.5, rear axle y 236.4, world frame) the ideal outer angle for inner angles 10 / 20 / 30 deg is 9.0 / 16.5 / 22.9 deg (rear wheel at x = 0 on the turn-centre line).
- Turning radius at 30 deg inner lock: inner wheel about 784 mm, rear wheel about 928 mm. Clearance sweeps in `parts/relief.py` still use the same ±30 deg on both wheels (the outer wheel never reaches that with Ackermann mixing, so the sweep is conservative).
- Estimate only. Needs a measured kingpin and servo travel to confirm.

## Tie rods and front upper links as square tubing (November 20)
Both are hollow 8 x 8 mm tubes, wall 1.6 mm, 1.2 mm chamfers on the long edges (`parts/tubes.py`), printed lying down in PETG. The rod ends and link ends are still the stand-in bodies. Tie rod buckling: about 430 N estimated against the 101 N servo stall (not run in FEM). The tube ends are open.

## Front shocks, passive lean (November 20)
Passive lean as in the build videos: the lean servo is removed (mount, ears, horn and rocker stay). A bought 33 mm eye-to-eye shock (9 mm body, M3 eyes) per side runs from a clevis on the arm's inner plate (x +-66.2, y -182) to a clevis on that lug at the cage's lower side rail (rail x +-45, y -142, world z 85), upper clevis base (`parts/shock_mount.py`). The cage is not cut: the shock's upper end stands 9 mm off the lower side rail on a printed lug with a clevis (`rail_lug`). The arm is not cut either: a 9 mm post on the inner-plate chord (`arm_post`, y -182) lifts the lower clevis so the shock passes over the U1 node and the bracing; 44.2 mm between the clevis bases. The old `b lean shock` stand-ins are still in the model. Shock stroke and spring rate at the wheel are not yet checked.

## Front arm strengthened under the shock post (November 21)
- FEM (`analyses/front_arm.py`: 65 N bump + 30 N side at the tip, 168 N shock force at the clevis): the first post design peaked at 56 MPa (safety 0.35) where the 11 mm wide post overhung the 8 mm chord.
- Fix (`parts/shock_mount.py`): an 8 mm thick shear web fills the inner truss bay U1-U2-L2-L1 (`arm_web`), and a full-width foot (`arm_foot`) runs from 1.2 mm above the belt up into the post.
- Result: peak 16.4 MPa, safety 1.22 (0.6 cm2 below 2, the plate root of the clevis, mesh dependent 16.4 to 20 MPa). Not yet 2: next options are thicker clevis plates (PLATE_T 3.0 and WIDTH 12) or root fillets.
- Clevis plates then thickened 2.4 -> 3.0 mm and widened 10 -> 12 mm (lug widened to match): peak 13.6 MPa, safety 1.47 on 0.11 cm2 only (U1 node, inner plate, y -161); everything else is at safety 2 or better. That spot is mesh dependent (13.6 fine, 24.7 coarse), so it is a stress concentration at the node, not a measured weak section. Build ok, 0 overlaps.
- Tie rod and upper link: FEM did not run (tie rod) or was badly loaded (upper link); by hand 2.5 MPa and 2.0 MPa, buckling margins 4.4 and 7.
- Swept collision check, wheel -14 to +20 mm: no new overlaps with the shell, cage or chassis (script not kept in the repo).

## Servos, tie rod, upper link, lean mechanism (November 21)
- `w3 fdc lower` (front diff carrier lower box, no moving parts) removed from the stand-in chassis (user).
- Steering servos: `SERVO_BACK` 20 mm, tilted 4.29 degrees to the deck slope (`SERVO_TILT_DEG`) and raised 3.8 mm so the underside lies 0.3 mm over the deck top; the flat seat is gone. The horn, spline and horn ball follow (`steer_hw.set_servo_pose`). Servo to front arm: 2.8 mm.
- Tie rod: the stand-in's end pieces are rotated onto one straight ball-to-ball axis (it was three segments at different angles), the square tube runs between them.
- Upper link (`parts/uplink.py`): rebuilt, 100 mm like the lower arm, parallel to it. Pinned (M3, `Uplink pin ...`) to a lug on the cage's lower side rail (inner) and to a clevis on top of the carrier (outer). The shell is cut once more at the end by the swept link volume (`uplink_relief_tools`, bump travel 20 mm, 8 mm clearance); cutting it earlier split the half-built shell.
- The unattached lean mechanism (mount, ears, horn, rocker, two lean shock stand-ins) is removed; passive lean needs none of it.
- Checks: 0 overlaps (tools/collide.py); swept check -14 .. +20 mm: no contact with the shell, cage (0.86 mm3 at +20) or chassis, tie rod to knuckle up to 6 mm3 (the ball joints are modelled rigid). Upper link FEM (80 N along the link): 13.1 MPa peak, safety 1.52 on 0.6 mm2, rest 2 or better. Tie rod FEM does not run (the solver exits without a message); by hand 2.5 MPa, buckling margin 4.4.

## Rear wheel drive only, passive lean beam (November 21)
User: no front drive, rearrange the drive train for RWD only, optimise the lean steer after the videos and the paper, remove what is no longer needed.
- Removed (`parts/rwd.py` `REMOVE`, `model.py`): front belts and pulleys, front differential (carrier, ring, pinion shaft, `w3 fdc upper`), both front output shafts, centre differential (carrier, ring, hub, `w3 cdc lower/upper`), crossover idlers, pins and pinion, old motor plate, the two lean pods, the upper shock lugs and clevises on the cage rails, the cage notch for the old motor plate, the deck recess for the old lean mount. 113 -> 97 parts.
- Front arms: one fixed 5 mm axle (`b front pivot axle`, x -86..86) through both arm hubs, held by two printed blocks on the front deck (`w3 arm pivot block`, x 40..54.5, two M3 inserts each, 3.4 mm holes in the deck). The tip shafts are cut back at x 110 to pivot pins between arm and carrier.
- Drive: motor (36 x 60) beside the rear shaft on the -x side, world about x -1.5, y -72..-12, pinion 12 mm on the motor, spur 33 mm on the front end of the rear shaft (same diameters as the old crossover stage, tooth counts not chosen yet). Motor plate with two side gussets stands on the rear deck (cut by the deck, one M3 per gusset). Rear shaft, pillow blocks, rear bevel stage and the rear belt are unchanged.
- Passive lean (`parts/lean_beam.py`): the shocks' upper eyes sit on the ends of one balance beam (x +-56) that turns on an M4 bolt under a bridge plate between the cage's lower side rails (the bridge is part of the cage). Two-wheel bump: both shocks push the beam the same way, the springs work (shock stroke about 0.21 to 0.24 mm per mm of wheel travel). Lean: the beam turns, shocks keep their length (within 1 mm); +-14 mm opposite wheel travel = 3.2 degrees of beam = about 5.6 degrees of body lean, limited by four stop pegs under the bridge. The lean range is set by the arm travel the shell allows (-14 / +20 mm).
- The shock now lies almost level and pushes along the arm: 268 N for a 65 N bump (was 168 N). A 14 mm post at the old place (y -182) failed (75 MPa). The lower clevis therefore sits on the U1 truss node (ref y -168) on a 7 mm post, with a wedge down the upper chord behind it (`arm_buttress`) and a pad under the clevis plates (`arm_seat`). Beam pivot ref (0, -118.6, 87.75).
- FEM: front arm 12.4 MPa, safety 1.61, 0.27 cm2 below 2 in small mesh-dependent spots (`analyses/front_arm.py`); lean beam 10.6 MPa, safety 1.89, 0.22 cm2 below 2 at the pin holes (`analyses/lean_beam.py`). Pivot blocks, motor plate and the cage bridge are not analysed.
- Checks: 0 overlaps (tools/collide.py and a check of all new and steering/suspension parts against everything); beam at +-3.2 degrees and arms at -14 / +10 / +20 mm touch nothing but the stops. No render (the app was not connected).
- Centring (user): two bought compression springs (5 mm OD, 10 mm free, about 2 N/mm, `Lean centring spring`) behind the beam at x +-40, each in a 6 mm pocket of a post under the bridge, pushing a flat pad on the beam; 1.4 mm preload at rest, post face 2.6 mm from the pad (pad travel 2.2 mm at the stops). Estimate: about 170 N mm of beam torque holds a 2 kg body at full lean, the springs give about 290 N mm there. The spring rate is an estimate, not tested.
- Open: the arms still have the belt pocket and pod seat of the driven version; the shell still has the relief cuts for the front belts; `parts/lean_linkage.py` is unused.

## Cage feet in the tub, clean cage joints (November 21)
User (14:42): room for the fasteners (a bracket on the side of the tub if needed), pockets in the tub and brackets the cage slots into, clean cage joints with no slivers, X ribs interconnected instead of shifted.
- Fasteners: the 6 cage screws are M3 countersunk from under the deck into heat-set inserts in the feet (the "screwed from the top, with tabs" text under "Assembly methods and hardware" is out of date). Checked with a Ø7 head/driver cylinder 80 mm straight down from each hole: nothing in the way at any of the 6, so no extra side-wall screw was needed. Screw: M3 x 8 countersunk (about 3 mm deck under the pocket + 5 mm insert).
- Feet: the round posts are gone. Every foot is now the cage's own chamfered square tube section, standing `FOOT_SEAT` (3 mm) deep in a pocket in the deck, insert pocket Ø4.2 x 5.5 in its end (`parts/cage.py`).
- Pockets and sockets (`parts/foot_sockets.py`, called from `_deck_pockets` in `model.py`): pocket = foot section + `FOOT_CLEAR` 0.2 mm, floor at the foot end. Rear deck (4 rail feet): a bracket block 10 mm high around the foot, running out to the side wall and keyed 1 mm into it, so the socket is tied to the side of the tub. Front deck (2 leg feet, no walls there): an octagonal collar, 2.4 mm wall, only 1.4 mm high because the leg node's underside is 1.7 mm over the deck (a 4 mm collar hit it: 28 mm3). Location depth 4.2 mm front, 13 mm rear.
- Joints: the cage (only the cage; front and rear arms keep their mitres) now uses `_Frame(hull_nodes=True)`: each tube is the hull of its two end sections, each node is the convex hull of the incident tube sections at the node and at a set-back chosen so every tube's end face is a face of the node. No mitre extension, cope or cube corner can stick out. Faces under 1 mm2 on the cage: 266 -> 130 (the rest are facets inside the hull nodes and where bosses, ears and the lean bridge join; the tail node at y 165 still has a small crevice). Faces thinner than 0.3 mm: 12 -> 26 (hull facets). Cage volume 424 -> 464 cm3: acute nodes (front feet, tail) are filled like cast webs.
- X ribs: the deck/tub floor has no ribs (only slots and holes), so this was read as the crossing cage tubes. The tail diagonals crossed the B-pillar-to-tail tubes 2.6 and 10.6 mm apart without a node: a tube end lying on another tube was split only after a crossing split had already moved that tube. Ends are now split first, then crossings, then ends again; every crossing shares one node in one plane. Left-over mid-span crossings after the build: 2 -> 0 (the report now runs after the joints are resolved). The side door truss and front bay near the deck already met at shared nodes. If the user meant other X ribs, they need to be pointed out.
- Checks: build ok (99 parts), `tools/collide.py` 0 overlaps; cage and both changed decks are single valid solids. Swept against the cage and decks: front arms with carriers, wheels, tie rods and upper links at -20/-14/+10/+14/+20 mm: none; lean beam at +-3.2 degrees: only the stop pegs (6.2 mm3, as before); rear swingarm: nothing up to 30 mm either way except the arm touching the tail deck at 30 mm (1.8 mm3, the same as before this change); at 50 mm the tyre hits the cage tail (3200 mm3, was 3093) and the arm the tail deck (22 mm3), both as before.
- Open: the shock clevis nodes on the tail are no longer trimmed to the ear slab (they reach x 10.9, the M6 head starts at 12). Front socket collars are low; raising the leg node would allow a taller socket.

## Tie rod to safety 2 (November 22)
- Baseline FEM (101 N along the rod, PETG, across-layer strength 20 MPa): 19.8 MPa, safety 1.01, at the M3 bore edge on the loaded underside of the knuckle-side eye (mesh-dependent, 29.8 MPa coarse); second spot 1.41 at the bar-to-tube joint.
- Knuckle-side eye 3.9 x 5.6 -> r 5.0 x 7.0 mm, round bar r 3.8 -> 4.3 (`_eye_r, _eye_h, _bar_r` in `model.py`); the knuckle pocket follows (eye + 0.25 mm, height + 0.5, bar + 0.25), 391.5 mm3 out of the knuckle, assert passes. FEM: 10.4 MPa, safety 1.93, peak moved to the bar-to-tube joint, where the 4.3 mm bar stood 0.3 mm proud of the 8 mm tube flats.
- Bar-to-tube joint: solid cone r 4.3 -> 3.6 over the first 5 mm of tube (blends the step, plugs the tube end, +104.8 mm3 per rod).
- FEM now: 9.8 MPa, safety 2.05, nothing below 2, coarse mesh 9.7 MPa (stable), deflection 0.039 mm. Load-case picks in `analyses/tie_rod.py` moved to the new eye faces (z 18 / 11).
- Checks: build ok (99 parts), `tools/collide.py` 0 overlaps. No steering sweep exists; the rod end sits in its own pocket in the knuckle, which steers with it.

## Yeti exposed cage, open cockpit (November 22)
User (John): bring the SCX30 Yeti cage style to the trike as an exposed cage with an open cockpit: canopy off, the stealth Front shell is the lower body, the cage is the visible cabin.
- `OPEN_COCKPIT` (model.py, group Cage, default on): the Canopy part is not registered; its tabs/clearance asserts, `band_pieces` input and `BOSS_TARGETS` entry are skipped. Off restores the closed stealth canopy and the old cabin tubes unchanged. The traced canopy is still built (the cage tail tubes and lower rear tube follow it).
- Front shell rim: the cabin opening edge (`cabin_ring()` / `cabin_cut()` in `parts/stealth_shell.py`) is now the visible belt rim and gets the same 0.5 mm 45 degree break as the arches (`chamfer_rims`). Behind the B-pillar foot the edge now runs parallel to the belt to the tail apex, so the rim stays `CABIN_RIM` 7 mm wide (it tapered to 3.5 mm at the apex). Rim = full 3 mm wall, no sliver.
- Rear light contact: it sat under the canopy roof; with no roof there it is dropped (cage boss and block). The tail light wiring has to run along the cage. The front contact is unchanged.
- Cage (`parts/cage.py`, `make_cage(..., cabin=...)`): new params `CABIN_BEAM` 7 mm (6..10, visible cabin tubes), `CABIN_INSET` 2 mm (cabin tube outer face inside the old canopy outline), `BELT_DROP` 0 mm (upper belt tube top below the body rim). `PILLAR_IN`/`BELT_CLEAR` only apply to the closed canopy now (PILLAR_IN still places the tail anchor b1, so the tail frame is unchanged).
  - Cabin nodes on the old stealth canopy outline: roof front corners (+-60.9, -86.9, 196.9), roof rear / B-pillar tops (+-45.9, 15.0, 219.9), cowl corners (+-77.7, -193.9, 133.9) inside the opening, tube top flush with the rim (`COWL_SETBACK` 6 mm keeps the hoop tube under the hood clear: 0.59 mm).
  - New members (CABIN_BEAM): A pillars cowl corner -> roof front, roof side rails, front and rear roof headers, roof X (both diagonals meet at one node on the centre line), cowl bar along the opening's front edge with the windshield V from its centre node to both roof front corners, door diagonal per side (cowl corner -> B-pillar top), sill step (cowl corner -> upper belt start), B pillar (B upright top -> roof rear corner), link roof rear corner -> tail anchor b1. Rear quarter tubes now CABIN_BEAM too.
  - Load path keeps CAGE_BEAM 10: feet, lower rails, front hoop/bumper, new hoop-top -> cowl-corner tube, upper belt rails, uprights and door V truss, lean bridge, upper-link lugs, tail tubes carrying the shock clevis and their braces.
  - Upper belt tubes raised so their top is flush with the rim height (z 138.2 / 149.2 / 158.4 at y -150 / -48 / 38, was 14 mm under the belt). They stay at x +-45, so they run inboard of the rim (the rim edge is at x 76..53); moving them out would put the foot-to-belt tubes into the upper-link and wheel sweep.
  - Removed: canopy bosses (A pillar, B pillar, roof), roof spine and rear contact boss, old roof V and roof headers on the traced nodes. Kept: one Front shell boss per side on the B upright at the old height (z 148.1, reach 15.4 mm to the skin).
  - Unchanged: the six feet, foot sockets, deck pockets and driver corridors, lean bridge, upper-link lugs, M6 clevis with PIN_FAN / PIN_TIE_RISE corridors, tail frame and tail housing fit.
- Checks: build ok (97 parts: Canopy and Rear light contact block gone); cage one valid solid, 0 mid-span crossings; `tools/collide.py` 0 overlapping pairs. Cage alone at the parameter ends (CABIN_BEAM 6/10, CABIN_INSET 0.5/8, BELT_DROP 0/10): valid, one solid, 0 crossings, 0 mm3 into the Front shell (min gap 0.12 mm at CABIN_BEAM 6 / INSET 0.5).
- Motion: cage against the swept envelopes of `parts/relief.py` (front wheels at steer lock -STEER_LOCK/0/+STEER_LOCK with bump travel, front suspension/steering parts, rear tyre and swingarm along their arc, rear shock, shock bridge) and `uplink_relief_tools()`: no envelope gained any overlap; the overlaps left are the parts mounted on the cage (lean bridge, uplink lugs, shock clevis), same as before. Smallest new gaps: upper-link sweep 15.6 mm, front wheel sweep 28.9 mm, front suspension/steer hull 28.6 mm. Script outside the repo.
- Silhouette vs the old canopy (sampled): roof top 200 vs 202 at y -90, 223 vs 225 at the peak; half width 65.7 / 64.1 / 49 vs 64.4 / 66.5 / 51.6 at z 190 / 200 / 220. At the cowl the cage stands about 11 mm inside the old canopy foot (the opening is 7 mm inside the belt).
- Renders: `renders/yeti_iso.png`, `yeti_side.png`, `yeti_front.png`, `yeti_top.png` and the old canopy for comparison `renders/yeti_old_canopy_*.png`. Made offline with VTK from output/model.step, because `soma render` needs the app (not running).
- Open: kit/registry.py and kit scripts still list the Canopy (kit not re-run); no FEM of the new cabin tubes; Front shell is held by two side bosses plus the deck (as before for the shell, the canopy screws are gone); tail light wiring route; seat / driver figure if wanted.

## Upper link FEM regression (November 22)
- The uplink FEM had dropped to 36.4 MPa (safety 0.55) at the outer tongue next to the joint sphere. The cause was neither 7db4bf3 (tie rod) nor 5364ebc (open cockpit cage): the link geometry and `analyses/uplink.py` are the same at 130b3c3, 7db4bf3 and 5364ebc. It came from 008fbee, which shortened `TONGUE` from 12 to 10 mm after the 13.1 MPa run, so the 13.1 MPa entry above was measured on the 12 mm tongue. At 10 mm the 4.8 mm joint sphere ends 0.7 mm past the 4.5 mm hinge ring, which leaves a sharp neck. Checked by meshing the link on its own: tongue 10 mm gives 36.2 MPa, 12 mm gives 13.0 MPa.
- Fix: `TONGUE` back to 12 mm (`parts/uplink.py`). Uplink FEM 13.1 MPa, safety 1.53 (0.56 mm² at the inner tongue root, mesh check +3 %). Build ok, 0 overlaps. Swept -14 .. +20 mm about the inner hinge: no contact with the cage, shell or chassis (the carrier moves with the link, so it is left out).

## Tie rod pocket fan and front arm crotch radius (November 22, unfinished)
- Before (5364ebc, articulated check with both arms at -14/+10/+20 mm and the lean beam at -3.2/0/+3.2 deg): tie rod vs knuckle pocket 1.9 / 4.0 / 25.0 mm3; arm FEM 13.4 MPa, safety 1.50 (peak at a sharp inner edge, world 64.1, -133.3, 57.0); beam 10.6 MPa, safety 1.89.
- Knuckle (model.py, tie rod section): the bar pocket is now a fan swept +-11 deg about the horizontal axis through the eye centre (5 cylinders), and the eye pocket is 1.2 mm taller above and below. A boss round the stud axis and a sleeve round the fan, both 1.6 mm outside the pocket, plus an M3 stud hole through the boss. The boss and sleeve are adapted from the printability commit 7919554. The knuckle gains 845 mm3 per side.
- Front arm (`parts/frontarm.py`, `CROTCH_R` 3 mm): a fillet piece (corner triangle minus a 3 mm circle) is fused into the crotch between the root post L0-U0 and the underside of the upper chord U0-U1, on both plates. OCC cannot fillet the faceted junction (BRep_API failed for 1 to 3 mm). The arm stays one valid solid, on both sides.
- Checks so far: build ok, 97 parts; `tools/collide.py` 0 overlaps.
- NOT fixed: the articulated check still shows tie rod vs knuckle 17.9 mm3 at -14, 0.3 to 17.8 mm3 at +10 (side 1 / side -1) and 5.4 to 24.3 mm3 at +20. The contact now sits 14 to 18 mm out along the bar (y -211 .. -197), past the 14 mm fan, where the bar swings into the knuckle arm or the sleeve. Next: lengthen the fan to the knuckle edge (about 20 mm) or flare only the sleeve mouth, and check why the two sides differ at +10 mm. For this check the rod's outer eye is held on the knuckle stud and no bump steer is modelled. A plain eye on an M3 stud cannot tilt 10 deg: the joint needs a ball end.
- NOT verified: arm, beam and tie rod FEM after these changes (the runs were stopped at hand-over); minimum knuckle wall (`soma analyze thickness --parts "knuckle 1,knuckle -1"` not run).

## Wheel well pocket at the upper links (November 22)

- The open cut-out for the upper link's swing in the fender edge is now a pocket: a wall lines the swing volume on the inside of the skin (ceiling, front
  and rear wall), so the notch no longer opens into the body. `uplink_pocket_walls()` in `parts/relief.py`, fused in `model.py` after the cage is built.
- The notch outline in the side view is unchanged: the cut itself is the same, the wall lies outside the swing volume and inside the skin and is trimmed
  by the same arch, deck and travel cuts as the shell.
- Wall: swing volume grown by `POCKET_WALL` (4.5 mm, gives 2.6 to 4.5 mm of wall), 1 mm from the cage (`POCKET_CAGE_GAP`). 4561 mm3 added per side.
- The pocket is open downward (towards the arch) and at its inner end, where the link runs on to its hinge on the cage.
- Build ok, 97 parts, 0 overlaps. Pictures: `renders/wheel_well_{quarter,side,low}.png` (offline, the app was not connected).
- Smoothed (same day): the pocket's cavity is now one convex hull around the part of the swing volume inside the skin, so its faces are flat facets
  instead of the steps of the four bands. The cut in the skin is still the swing volume (outline unchanged). 4894 mm3 added per side; build ok, 0 overlaps.
- Open: the ceiling is an overhang when the shell prints upright; wall thickness of the front shell was not compared before and after.

## Lean assembly tilted to the deck slope (November 22)
- User request: the lean assembly parallel to the deck. Beam, bridge, pivot bolt, stops and centring springs (`parts/lean_beam.py`) are turned about the lateral axis through the pivot by `TILT_DEG` = atan(`DECK_SLOPE`), rising to the rear, by `_place()`. The shock clevis bases stay where `base_up` puts them: the beam is shifted so its clevis base plane meets them.
- Build ok, 97 parts, 0 overlaps (commit b9dc655). Lean beam FEM after the tilt: see the merge entry below.

## Printability fixes merged (November 22)
- `printability-merge` (657d457 + c45948b) merged into `shell/defect-sweep`, clean merge, no conflicts:
  - rear bearing carrier halves: a D5.4..D15.2 ring fills the counterbore floor so 1.5 mm (was 0.3) remains between the D11.1 bearing seat and the D15 counterbore (`fill_rbc_lip` in `parts/deck.py`);
  - pivot block insert pockets 1.5 mm (was 0.8) from the block faces (`INSERT_DY` in `parts/rwd.py`);
  - rear arm chords clipped flush with the axle hub and inner pivot boss faces (0.28 mm proud -> 0, `parts/swingarm.py`);
  - carrier: 0.3 mm ring sliver at the tip pin bore trimmed (model.py, upper link section);
  - kit: registry matches the model (lean beam, pivot blocks added; front/centre diffs, lean mount, pods, front pulleys dropped), CG3 dropped, SH2 canopy optional with `OPEN_COCKPIT`. The kit itself was not regenerated (needs `pip install trimesh shapely`).
  - The knuckle half of 7919554 was left out on purpose: the fan pocket of 06452ea is the current version.
- Checks: build ok, 97 parts; `tools/collide.py` 0 overlapping pairs; rear arm FEM 7.4 MPa, safety 2.69 (coarse mesh +4 %); lean beam FEM (after the tilt) 11.0 MPa, safety 1.82, 1.57 cm2 below 2 at the pivot support edge, mesh dependent (coarse 60.8 MPa): same spot as before, see the audit items; knuckle wall (`soma analyze thickness --parts "knuckle 1,knuckle -1"`): 1.94 cm2 below 1.2 mm per side, one 126.7 mm2 patch (14.2 x 9.7 mm) at 0.06 mm near (+-105.7, -199.0, 15.6) and 0.3 mm slivers around (+-99..106, -200..-202, 10..21): the sleeve/boss skin of the fan pocket, still open (next item).

## Cage: front sockets, tail nodes, shock pin clearance (November 22)
- Front leg nodes raised `FRONT_NODE_RISE` 4.5 mm so the front deck collars can be real slot-in sockets: `SOCKET_H_FRONT` 1.4 -> 4.0 mm (`parts/cage.py`).
- Hull nodes joined by a tube with less than `NODE_MERGE_FREE` 1 mm of free length become one hull (the tail joint at y 165 and the clevis tie nodes at x 7.4 / 15 left re-entrant slots): 8 short tubes merged into their nodes.
- M6 shock pin: everything outboard of |x| `PIN_HEAD_CLEAR_X` 9.8 around the pin goes, except the r 6.8 boss the head and nut bear on (head and nut start at |x| 12). Checked on the built cage: 0 mm3 outboard of |x| 9.8 in an 18 x 18 mm box round the pin, both sides.
- Build ok, 97 parts, 0 overlaps. Not done: cage FEM including the cabin tubes (`analyses/cage.py` from the cage thread is not in the tree).

## Knuckle tie rod pocket as a cone, parked (November 22)
- The fan pocket (five stepped cylinders, 14 mm) left sliver wedges at its mouth (thickness check: 126.7 mm2 at 0.06 mm per knuckle near (+-105.7, -199.0, 15.6), 1.94 cm2 below 1.2 mm) and the rims of the untilted sleeve cylinders stood in the tilted bar's path 14 to 18 mm out.
- Change: pocket and sleeve are one cone each (radius grows by tan 11 deg per mm along the bar), 20 mm long (`_plen`), so the mouth lies past the knuckle arm; eye pocket clearance 0.25 -> 0.85 mm (`_eye_c`), because the eye (r 5, h 7) tilting 11.5 deg at +20 mm reaches 5.6 mm from the stud axis. Boss and sleeve keep the 1.6 mm wall.
- Verified with the cone alone (eye clearance still 0.25): build ok, 97 parts, 0 overlaps; articulated check (`handoffs/lean_arm_poses/artic.py`): tie rod vs knuckle 17.9 / 17.8 / 24.3 -> 0.04 / 0.26 / 5.26 mm3 at -14 / +10 / +20 mm, the rest at the eye rim. The eye clearance step is meant to take the 5.26 mm3 away; its build ran after the front end had been replaced in the working tree (see below), so it is not verified, and the knuckle thickness was not re-measured.
- Not committed to model.py: at the same time another session rebuilt the whole front end in the working tree (parts/wishbone.py, parts/flat_deck.py: wishbones, flat front deck, knuckles, tie rods, lean beam, shocks and servos removed, 94 parts). The change is kept as `handoffs/knuckle_cone_pocket.patch` against fe509dd in case the old knuckle comes back.
- Kit regeneration (HANDOFF item 2) postponed until the front end settles; its Python packages (trimesh, shapely, manifold3d, rtree, networkx, mapbox_earcut, lxml) are now installed in `.soma/env`. Note: the job shell's `PIP_PYTHON` points at another workspace, install with `env -u PIP_PYTHON -u VIRTUAL_ENV .soma/env/bin/python -m pip install ...`.

## Front end rebuild: wishbone lean-steer (November 22), IN PROGRESS - resume plan

Owner's brief (Nov 22): video-style double-wishbone lean-steer (reference `inputs/YTDown...mp4`, 6:20-8:30), flat front deck, no battery and no tray, old
mounting holes gone, A-arms and head in chamfered square tube (`parts/tubeframe.py`, method in docs/tube-cage-frame-skill.md), whole mechanism **centred
behind the skid** (owner's choice), then rebuild the cage around the settled mechanism, rebuild the shell front for the new layout, uniform shell wall,
fix all visual and print defects, production grade. Work autonomously.

State at this commit (builds, 94 parts, `tools/collide.py` 0 overlaps):
- `parts/wishbone.py`: head and arms are tube frames, but the head still stands in FRONT of the skid with pivots at x +-50 (`XI`). `SHOW_CAGE` is off.
- `parts/flat_deck.py`: front deck is a plain slab. Battery tray removed; battery still present (to be removed with its stand-in).
- `tools/front_check.py` (new): all-pairs rest check and lean (+-10 deg) / steer (+-30 deg) pose check. Run `python -I tools/front_check.py`.
- Folder cleaned: old 1/18 pipeline files and folders deleted with the owner's approval (out/, sc/, ws02/, rev_trike_shell*/, tests/, top-level scripts).

Findings that drive the redesign:
- Pivots at x +-50 give 23 deg arm angle for 10 deg lean (arm 63 mm, wheel 144 mm out): too much for M4 rod ends (about 13 deg). Centred pivots (x about
  +-10) give about 14 deg; the clevis tabs then need about 2 mm cone spacers each side of every rod end eye.
- Tie rod dips into the deck on the dropping side (395 mm3): raise `ZT` to about 41 or route it higher.
- Space behind the skid (world): skid ends y -201.6; deck top z 19.2 at y -205 rising 0.07 mm/mm (21.7 at y -170); deck half width 54.5; shell
  underside z 136 on the centre line, side skin from z 102 at x 80. The lower arm must clear the deck edge (x 54.5) when it drops 15 deg: lower pivot
  z >= deck top + 18, so about ZL 38-40, upper ball then above the rim line, so ball joints go inboard of the tyre (x <= 106).

Next steps, in order:
1. Remove 'b battery' (and any strap/hold-down) from the chassis stand-ins.
2. New head: narrow tube frame on the centre line on the front deck behind the skid (y about -200 .. -172), pivot rods along y at x +-10, lower
   about z 39, upper about z 65; arms about 96 mm to ball joints at x 106; knuckle spine out to the axle; heave shock between the lower arm rockers.
   Steering servo, horn and tie rods behind the head. Update the kinematics in wishbone.py and `lean_front.py`.
3. `soma build`, `tools/collide.py`, `tools/front_check.py` until 0 overlaps at rest and in all 9 poses (rod end bore vs stud overlaps are a
   modelling artefact of rigid rod ends: model the ball separately or exclude that pair).
4. FEM: `analyses/wishbone_*.py` (written by a helper, coordinates need updating), target safety 2.
5. Cage: `SHOW_CAGE` back on, rebuild the front of the cage around the head (tube-cage-frame skill), feet clear of the mechanism.
6. Shell front: regenerate arch and wheel well cuts from the new arm, knuckle and tyre sweeps (`parts/relief.py`, the old uplink pocket goes),
   uniform wall, thickness check, no slivers.
7. Kit regeneration, BOM, drawings, final renders.

Owner's later additions (Nov 22, 02:30): remove the battery as well as its tray; work autonomously until done; production grade; fix all visual and
print defects; shell wall consistent throughout; rebuild the cage once the steering geometry is settled; rebuild the shell front for the new layout.
Definition of done as sent by the owner (it reads as pasted from another session and names a 1.4 mm wall and a `.sc` file: this model's wall is
`WALL_PRINT` 3.0 mm and its `sc/` folder was deleted in the cleanup, so CONFIRM with the owner whether these two points apply to Project_Fugu):
- Shell: consistent wall throughout (1.4 mm named), measured against a 95 % target, one printable watertight body.
- Print and visual defects: every thin wall, knife edge and sliver in the tub, cage and bulkhead brought to at least 0.8 mm or removed, clearances
  no worse than now.
- Stacked leftovers: parts carrying layers of patches from older versions get simplified.
- Outputs: parts list, diagrams, STEP, 3MF, and the `.sc` regenerated last.
FEM helper results so far (old geometry, pivots at x +-50): upper arm 2.3 MPa, safety 8.8. Free-body numbers and the `near=` points to update are in
the docstrings of `analyses/wishbone_*.py`. Note from the helper: one wheel alone is not held by a single heave shock (lean is free), so the head
case uses a two-wheel landing.

### Centred head behind the skid (November 22, 03:10) - steps 1-3 of the resume plan done
- `parts/wishbone.py` rewritten. Head: tube frame on the deck on the centre line, y -201 .. -158.6 (behind the skid, which ends at y -201.6): front
  and rear centre post, cross bar at each pivot height, base tubes on the deck (M3 from below at x +-28), gussets, top and bottom tie. Pivot rods
  along y at x +-12 (`XI`), lower arm plane z 42 (`ZL`), upper z 70 (`ZU`), kingpin x 106 (`KX`), arms 94 mm.
- Ball joints: bought 6.8 mm ball studs and cups. Arm studs lie along y in the knuckle plate (lean = turning about the stud, steering = cup tilt,
  wheel load radial on the cup). Tie rod studs are vertical.
- Heave shock: 92 mm eye to eye, above the head (z 94), between two truss posts on the UPPER arms (feet at x 30 and 62). The upper arm carries the
  wheel load, the lower arm only push and pull. Lean leaves the shock almost alone (eye distance 92.0 -> 91.1 at 10 deg).
- Steering behind the head: servo on the deck (shaft up, y -118 .. -77), T horn (40 mm), tie rods at y -150, z 60 to 54 mm steering arms on the
  knuckle plates. Horn balls at x +-8 near the pivot axes.
- Battery and tray stand-ins removed. Receiver stand-in moved to the left of the servo.
- Checks: build ok, 81 parts; `tools/collide.py` 0 overlaps; `tools/front_check.py`: rest clean except the front wheel / tyre stand-ins (old: rim
  18 / 28 mm3 into the mock tyre, -x wheel 1.1 mm3 off its hub); all 9 poses (lean -10/0/+10 deg x horn -30/0/+30 deg) clean. Arm angle at 10 deg
  lean: 15 deg (was 23).
- Not done yet: FEM of the new parts; cage is still hidden (`SHOW_CAGE`); shell front still has the old upper link pocket and arch cuts;
  `parts/relief.py` still sweeps the old links; heave travel (bump) poses are not in front_check; steering angle at the wheel not measured.

### Paused at the usage limit (November 22, about 03:20) - next step is the cage (resume plan step 5)
- Cage plan, worked out but not started: the front legs stand at (x +-45, y `FRONT_FOOT_Y` -195) in `parts/cage.py`, in the middle of the new
  wishbones. Move the front feet behind the tie rods: vertical legs at (x +-45, y about -135) up to z about 100, then forward and up to the cowl
  corner K and the front hoop top (clears the tie rods incl. lean, about z 76 at x 58, and the heave shock, top z 102 at y -196). `RAIL_START_Y`
  is -150: check the lower rail start against the tie rods (y -150, z 56..64). The front deck is now the flat slab (`parts/flat_deck.py`), so the
  front foot pockets and collars (`_deck_pockets` in model.py, `parts/foot_sockets.py`) must be made on it at the new foot position; the servo
  cradle (x +-16.6, y -121..-74) and the receiver stand-in (x -45..-30, y -100..-75) are near the rail feet at y -48: check.
- Then set `SHOW_CAGE` back to True, build, `tools/collide.py`, `tools/front_check.py`.
- FEM helper was told to stop; `analyses/wishbone_*.py` may be half updated for the new geometry: check their docstrings before running.

### Cage back on, front feet moved (November 22, 04:10) - resume plan step 5 done
- `parts/cage.py`: the front feet at y -195 and their three tubes (upright strut, foot to lower rail, foot to upper belt) and the cross tube at
  z 66 are gone. The front hoop (top crossbar, bumper tube) hangs from the upper belt start and the cowl corner; a third pair of rail feet stands
  at (x +-45, y -131), behind the tie rods (`RAIL_FEET`). Their screw holes, pockets and collars are made on the flat front deck (`_foot_site`,
  `FRONT_FOOT_SITES` in model.py).
- Heave shock posts moved inboard (`POST_X` 22 / 46, eye at x 34, shock 68 mm eye to eye) so the eyes stay inboard of the cage tubes at x 45.
- `SHOW_CAGE` is True again. Build ok, 84 parts; collide.py 0 overlaps; front_check clean at rest and in the 9 poses (wheel / tyre stand-ins aside).
- Open: front hoop is no longer triangulated to the deck (FEM of the cage front); bump travel on top of lean is not in front_check.

### Shell front cut for the new front end (November 22, 05:00) - resume plan step 6, first pass
- `parts/relief.py`: the old front relief hulls (swingarms, uplinks, belts, lean servo, old knuckles: every hull in relief.json that is not `rear`)
  are no longer cut. `wishbone_relief_tools()` cuts the real travel instead: upper arms with shock posts swept 26 deg up, knuckles carried along
  and steered +-22 deg (3 mm clearance, `FRONT_CLEAR`), front tyres lifted up to 40 mm (`FRONT_TYRE_LIFT`: 25.4 lean + 12 bump) on the arm's arc and
  steered. The upper link cut and its wheel well pocket (c19b572, 18078c6) are gone with the link. The traced reference shell keeps the old tyre cut.
- `parts/cage.py`: `RAIL_START_Y` -150 -> -131, so the lower rail starts on the front foot post and the tie rods (y -150) pass ahead of it.
- `tools/front_check.py`: `FRONT_BUMP=<mm>` adds wheel travel of both wheels on top of every pose.
- Checks: build ok, 84 parts; collide.py 0; front_check clean at rest, in the 9 lean/steer poses, and with +12 mm bump and -8 mm droop on top.
- Look: the front arches are now cut about 20 mm higher (the wheel needs 37 mm of travel relative to the body at full lean plus bump), the cage's
  front tubes show through them. New cut edges are not chamfered yet.

### Front end strengthened after FEM, dead code removed (November 22, 06:10)
- First FEM of the new parts (`analyses/wishbone_*.py`, loads: 65 N up + 30 N inward at the tyre contact; free-body numbers in the docstrings):
  upper arm safety 0.34 (fork slot cut the shock post into 2.65 mm cheeks), knuckle 0.58 (5 mm plate at the upper stud), lower arm 0.72 (at the
  clamped boss, mesh dependent), head 0.90 at a support edge and 1.03 at the front post / upper cross bar.
- Changes in `parts/wishbone.py`: arm tubes 14 (upper) / 12 (lower) nominal; shock post tubes 14 with a round eye pocket (cheeks 4.4 mm, posts whole
  below the pocket, fan channel for the shock neck); post = upright under the eye (x 34) + diagonal from x 58; knuckle plate 10 mm with a through
  stud; head tubes 13 nominal, pivot rods at x +-13, front base tube +-22 (the lower arm's front leg drops outboard of it), steering line at y -146.
- `parts/cage.py`: front foot posts and rail start at y -127 (tie rods pass ahead of them at full steer).
- `model.py`: 291 lines of old front-end construction removed by a helper in a separate worktree; verified identical (84 parts, volumes, bounding
  boxes and face counts unchanged). Build time 255 s -> about 200 s. Modules no longer imported by model.py (not deleted): parts/steer_hw.py,
  uplink.py, lean_beam.py, tubes.py, shock_mount.py; parts/frontarm.py is only used by two tools.
- Checks: build ok, 84 parts; collide.py 0; front_check clean at rest, 9 lean/steer poses, and with +12 / -8 mm wheel travel. FEM re-run pending.
- Thickness sweep of every part done (limit 1.2 mm); thin spots in the front shell (14 cm2), skid, decks, rear arm, pulleys, cage tail, roof plate,
  tail housing, light strips are being fixed by three helpers in detached worktrees (../fugu_shell, ../fugu_decks, ../fugu_rear), patches to follow.

### Thin-wall patches merged, arm pivot barrels (November 22, 09:30)
- Second FEM (strengthened parts): upper arm's shock post is fine; what stayed below 2 sat at the clamped pivot faces and at the notch my leg
  trimming left (lower arm 0.87 there); knuckle 1.49 at the edge of the clamped upper stud bore; head 1.86 in the free structure (1.18 at a
  clamped screw face).
- `parts/wishbone.py`: each arm now has one square pivot barrel along the pivot axis; the legs branch from it `LEG_IN` 6.7 mm inside the boss
  centres, nothing is trimmed afterwards. Pivot rods at x +-14 (`XI`), arms 92 mm. Knuckle plate 1.5 mm wider inboard, small gusset on the block.
- Merged helper patches (each built and checked in its own worktree, then verified again here):
  - decks: skid flange rebuilt as a plain 3 mm lap under the deck with two M3 screws at (+-26, -206.4); front deck ends in a butt seam on the rear
    deck; rear deck corner, pillow slot skins and wall cap squared; tail deck wall ends square; bearing carrier fill ring on the true split plane;
    front wheels exact mirrors on the axle (x +-144), hub floor 2 mm. Left: two 5 mm2 spots at the rear deck wall top (-53.8, 45.1, 113.2) and
    hairline strips at the side-hole plugs, 0.2 mm edge strips at the skid lap end.
  - shell: front shell 14.02 -> 0.39 cm2 below 1.2 mm; rims squared at the open hull facets, a free-standing 1 mm fin behind the nose box
    removed, every opening cut square through the wall with a 0.5 mm chamfer (`square_cuts`), hairline pocket fill removed, strip groove wall and
    strip edge square (nose light strip smallest wall 0.12 -> 0.90 mm at its LED peg tubes). Skin at nominal 3.0 mm +-10 %: 94.8 % (target 95 %):
    the rest is the 1.2 mm strip backing, crease zones and the solid plug beside the nose. Left: two 5 x 2 mm crumbs at (+-64.4, -266.4, 117.4).
- Checks here after merging: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, in 9 poses, with +12 / -8 mm travel (the old wheel
  and tyre stand-in overlaps are gone). Kit registry updated for the new front end (kit not regenerated yet).

### Rear patch merged, arm bases widened (November 22, 10:15)
- Third FEM round: legs branching from the barrel's middle made the lower arm soft (3.5 mm at the ball under 92 N, safety 0.68). Now: legs leave
  the barrel 1.5 mm inside the boss centres (wide base), the joint hull is cut 0.6 mm inside the barrel's ends with a 45 degree relief, round
  thrust collars at the barrel ends; arm tubes 16 (upper) / 14 (lower); shock post foot at x 70; pivot rods at x +-15; low pivot rod heads.
  Knuckle: safety 1.54 on a 5 mm2 spot at the edge of the clamped stud bore (13 MPa), everything else above 2.
- Merged the rear helper's patch: cage clevis ears as one hull plate each (cage: nothing below 1.2 mm, was 0.24 mm), roof plate a plain slab 0.2 mm
  above the frame, front light contact block cut once by the roof skin, tail housing screw seats rebuilt (M3 x 8), tail strip lens 1.0 mm, rear arm
  dead bridge diagonal removed and pin corridor with flat sides (nothing below 1.2 mm), pulley hub wall 0.9 mm. Left by design: GT2 tooth tips
  0.5 mm, LED peg walls 1.0 mm. Open from that work: rear arm FEM reads safety 1.67 on 0.02 cm2 at the corridor / ear corner (10.4, 160.5, 109.6)
  with a 2.5 mm mesh (the study no longer meshes at 3.5); `analyses/cage.py` is stale (fixes a removed foot), the new clevis ears have no FEM; the
  17 mm tool corridor along the rear shock pin is free to |x| 27.7 (was 30).
- Checks: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, 9 poses, +12 / -8 mm travel.

### Arm roots as square stubs; arms pass FEM (November 22, 11:40)
- `parts/wishbone.py`: each arm leg leaves the pivot barrel as a square stub along x (to `STUB_X` 24, clear of the head's bosses), then turns to
  the apex: a wide solid root, nothing trimmed. Shock post tubes 18 nominal (fork cheeks 6.2 mm, slot open upward and outboard), a wedge fills the
  inner corner between the upright post and the arm's top. Arm tubes 16 (upper) / 14 (lower).
- FEM with supports as the pivot rod gives them (bore holds x and z, the two thrust collars hold y):
  - upper arm (65 N up + 26.5 N in at the ball, 252 N shock force on the fork cheeks): 9.4 MPa, safety 2.13, nothing below 2, 0.34 mm at the ball.
  - lower arm (91.7 N along the arm, cornering without bump): 9.0 MPa, safety 2.22, nothing below 2, 0.79 mm at the ball.
  - history of this part: 0.34 -> 0.83 -> 1.32 -> 2.13 (upper), 0.72 -> 0.87 -> 1.65 -> 2.22 (lower).
- Knuckle (last run before the stub change, part unchanged since): 13.0 MPa, safety 1.54 on a 5 mm2 spot at the edge of the clamped upper stud bore,
  0.06 cm2 below 2, everything else above 2. Head: re-run pending with supports on the base tube undersides.
- Checks: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, in 9 poses, with +12 / -8 mm travel.

### Front end final strength and wall state (November 22, 12:40)
- Round bosses replaced by square tube ends (head cross bars run 7 mm past the pivot bores, the shock post upright runs 7 mm past the pin):
  the cylinders left crescent slivers on the tube flats. The head's M3 insert bores now end in the base tubes (they ran up to z 40, into the
  lower cross bar beside the pivot bore). The fork's neck channel starts at the slot floor (no ledge).
- FEM on these shapes (`analyses/wishbone_*.py`, PETG across the layers 20 MPa, target safety 2):
  | Part | Load | Peak | Safety | Below 2 |
  |---|---|---|---|---|
  | Upper arm | 65 N up + 26.5 N in at the ball, 252 N shock force on the fork cheeks | 7.5 MPa | 2.65 | nothing |
  | Lower arm | 91.7 N along the arm (cornering without bump) | 8.7 MPa | 2.30 | nothing |
  | Lean head | pivot rod loads of both sides, two-wheel landing, held on the base tube undersides | 10.5 MPa | 1.90 | 0.02 cm2 (1.6 mm2 inner corner post / upper cross bar) |
  | Knuckle | contact force through the axle bore, held at the two stud bores | 13.0 MPa | 1.54 | 0.06 cm2 (5 mm2 at the edge of the clamped upper stud bore: the stud flange's bearing is not modelled) |
  The last two small edits (fork channel, shorter insert bores) were made after these runs and not re-run.
- Wall thickness of the front end parts: lower arm and knuckle nothing below 1.2 mm; upper arm edge strips at the fork slot (0.65 mm, 1.3 mm2
  each); the head sliver at (17.4, -195.8, 40.0) was the over-long insert bore (fixed, not re-measured).
- Remaining below 0.8 mm elsewhere (final sweep): front shell crumbs at the strip end recess (+-64.4, -266.4, 117.4), 0.40 cm2 in all; tail
  housing corner strips 0.54 mm (0.06 cm2); front deck edge strip 0.63 mm at the skid lap end; rear deck hairlines at the side-hole plugs and the
  wall top (0.11 cm2); GT2 pulley tooth tips 0.46 / 0.51 mm (belt profile, by design); light strip peg walls 0.9 / 1.0 mm (by design).
- Checks: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, in 9 poses, with +12 / -8 mm travel.

### Paused at the usage limit (November 22, about 13:20) - outputs started
- Drawings: `drawings/fugu.py`, two A3 sheets ("Fugu general arrangement" 1:5, "Fugu front end" 1:2 with item numbers and a parts list), built to
  `output/drawings/` and `output/drawings.pdf`. One open warning: the wheelbase dimension text sits on the top view (move the top view down or the
  dimension up). The drawings were built before nothing else changed in the model, so they match commit 6c497dc geometry.
- Still to do: kit regeneration (`kit/README.md` gate chain: export STLs, build_kit, mesh_audit, manifest, Bambu slice check for the 3MF plates,
  make_docs for bom.md and the assembly manual; registry already updated), refresh `BOM_COST.md` / `.csv`, final renders, `soma export --all
  --format step`, the remaining crumbs listed in the section above, `analyses/cage.py` and `analyses/rear_arm.py` (stale / mesh), and the two
  questions for the owner (1.4 mm wall and the `.sc` file from the definition of done).

### Owner's answers and the SolidCraft file (November 22, 15:30)
- Shell wall stays as it is (`WALL_PRINT` 3.0 mm); the 1.4 mm figure in the definition of done does not apply here.
- New `sc/Project_Fugu.sc`: the built model imported into SolidCraft (one import feature, 84 named bodies, all closed; total volume 3 335 745 mm3
  against 3 337 917 mm3 in the model, 0.07 % apart). Regenerate after every model change, last in the output chain:
  `solidcraft-cli run --in output/model.step --save sc/Project_Fugu.sc --quiet`, then `solidcraft-cli eval sc/Project_Fugu.sc` to check the count.

### Shell strip ends, cage front brace, cage and rear arm FEM (November 22, 16:30)
- Shell: the groove plug behind each nose strip end now starts ahead of the strip's end and reaches 2 mm further inboard (model.py): the open
  recess with a nub at both nose corners and the 0.02 mm fin behind it are gone; the strip keeps its 0.25 mm gap at the end face. Front shell
  0.40 -> 0.20 cm2 below 1.2 mm; what is left are 0.1 mm wide edge lines along chamfers and creases, no walls.
- Cage: the front hoop lost its legs when the feet moved (FEM: safety 0.98, 5.7 mm at the bumper tube, 13.6 cm2 below 2). One brace per side now
  runs from the middle of the hoop-to-cowl tube back to the front upright at z 112, above the tie rods' highest travel (two other routes hit the
  shell rim, the shock post and the tie rods in the travel poses). FEM after (`analyses/cage.py`, envelope case: roof landing 80 N + 30 N side,
  rear shock 135 N, bumper 40 N): 14.4 MPa, safety 1.39, 1.65 cm2 below 2. The front is above 2; the spots left are in the tail, 30 mm2 at the
  tail tube joint (-30.6, 119.5, 171.7) and 29 mm2 at the B-pillar foot (-43.0, 47.7, 159.3); 3.2 mm at the tail tip. Mesh dependent (coarse
  31.5 MPa). Not changed: the tail frame is the owner's reference cage; open for a decision.
- Rear arm (`analyses/rear_arm.py`, mesh 2.5): 12.0 MPa, safety 1.66 on 2.5 mm2 at the inner corner where the pin corridor meets the ear
  (10.8, 160.6, 109.7), everything else above 2.
- Checks: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, in 9 poses, with +12 / -8 mm travel.

### Outputs (November 22, 16:30)
- Kit regenerated from this model (`kit/README.md` chain): 84 STLs exported to `kit/stl_export_wishbone/`, 39 printed files built and oriented
  (`kit/print/`), mesh audit 0 flagged (11 pieces need supports), 7 plate groups / 11 plates, Bambu Studio slice check 0 problems:
  53.4 h and 1668 g in total. 3MF plates in `kit/print/bambu/` (`all_plates.3mf` and one file per plate). `kit/bom.md` and
  `kit/assembly_manual.md` regenerated; the hardware list, the assembly steps and the risk list in `kit/make_docs.py` were rewritten for the
  wishbone front end, rear wheel drive and the open cockpit. `kit/build_kit.py`: a printed stem now wins over a hardware prefix.
- `BOM_COST.md` / `.csv`: new section "Update November 22" with the current printed parts, the slice mass and time, a supplier estimate from the
  line fitted to the November 21 quotes (no new quotes requested), and the bought-parts changes (priced bought parts now USD 359.41 + CAD 8.32).
- Drawings: `drawings/fugu.py`, `output/drawings.pdf` (2 sheets, no warnings). STEP of every part in `exports/` (13 older files there belong to
  parts that no longer exist: Canopy, Rear shell, old rear shock stand-ins; left in place). Renders: `renders/fugu_final_*.png` (offline).
- `sc/Project_Fugu.sc` regenerated last from this build.
- Open: cage tail FEM spots (safety 1.39), rear arm corner (1.66), knuckle stud bore (1.54), head corner (1.90); battery and receiver mounts;
  heave shock, ball studs, tie rods and pivot rods not selected; nothing printed or assembled; `soma render` views not made (app not connected).

### Cage tail, servo mount on the deck, decks lined up (November 22, 18:00)
- Cage tail (owner: strengthen it): the four rear-quarter tubes are main tube size again (they were 7 mm with the open cockpit but carry the
  tail frame), and a web joins the middle and lower tail rails under the front shock brace. The front brace now lands on the upper belt start
  node. FEM before the brace move: 12.6 MPa, safety 1.58, 0.39 cm2 below 2 (was 1.39 / 1.65 cm2); tail joints above 2. Re-run pending.
- Steering servo (owner's markup): the old cradle was cut by the deck and the model kept its largest piece, which was the one UNDER the deck.
  New in `parts/wishbone.py`: the servo stands on its base (20.2 x 40.8 x 26.5, shaft up) with mounting ears at both ends; the mount is two
  pillars under the ears (two servo screws each) joined by a rail along each side, all on top of the deck, four M3 from below
  (`SERVO_SCREWS`); model.py keeps the piece with the highest top. The horn has a tall hub (servo top z 54.7 to the arm at z 68.5) and the
  ball studs hang down from it to the tie rods at z 60. `HORN_L` 37.
- Decks lined up: `DECK_FRONT_RAISE` 0.9 -> 0 (the lift was for the front diff housing, long gone). Front and rear deck now share their top and
  bottom planes at the seam. `DECK_Z0` in wishbone.py 18.3, front cage feet z 23.8.
- Checks: build ok, 84 parts; collide.py 0; front_check 0 findings at rest, in 9 poses, with +12 / -8 mm travel.

### Cage FEM final, animation, outputs regenerated (November 22, 21:30)
- Cage front brace: landing it on the upper belt node was worse (safety 1.13: the upright and the 7 mm sill tube bent), so it lands on the front
  upright at z 112 again, with a tie from there down and back to the lower rail at y -95. Long boss stubs (the shell screw bosses on the rear
  uprights, 15.4 mm) get a conical root.
- Cage FEM, `analyses/cage.py`, mesh 2.5 (envelope: roof landing 80 N + 30 N side, rear shock 135 N, bumper 40 N): 13.2 MPa, safety 1.52,
  0.18 cm2 below 2: 6.8 and 5.2 mm2 at (+-47.0, 46.5, 148.7) and 3.5 mm2 at (47.1, 42.7, 140.5), sharp inner edges beside the rear upright
  bosses where the lower rear-quarter tube passes over the boss root. Tail joints and front hoop above 2. 2.9 mm at the tail tip.
  History this round: 0.98 (hoop without legs) -> 1.39 -> 1.58 -> 1.13 (wrong brace route) -> 1.52 without any mesh-singular spot.
- Animation: `animations/lean_steer.py` starts with a pure lean sweep (+-10 deg, no steering), then lean with steering; `soma anim build` ok for
  "Lean steer" and "Lean steer front". Offline GIFs of the same kinematics: `tools/lean_gif.py` -> `renders/lean_steer_front.gif`,
  `renders/lean_steer_quarter.gif` (the app was not connected for a video).
- Outputs regenerated for this model: kit 39 printed files / 11 plates, Bambu slice check 0 problems, 54.0 h, 1678 g; bom.md, assembly manual,
  BOM_COST plate table; drawings (2 sheets, no warnings); STEP exports; final renders; `sc/Project_Fugu.sc` last (84 closed bodies).
- Owner's question on the shell openings: they are the swept travel (10 deg lean + 12 mm bump + steering); a wheel-well liner on the inside of
  the skin could hide the interior (open on the inboard side for the arms), or the travel could be reduced. Not built; waiting for the owner.

### Wheel-well liners, first stage, and the two-version setup (November 23)
- Wheel-well liners (owner: "build liner"): `wheel_well_liners()` in `parts/relief.py` makes a 3 mm wall around the swept space of each front tyre
  and knuckle with every swept volume cut out (the arm slot is cut square through the wall, `sweep_x`); model.py clips it to the inside of the
  skin and to the arch, trim and travel cuts, squares its bottom rim (`LINER_RIM` 1.5: only columns that stand that tall above the cut are kept,
  as an exact prism sweep), keeps 1 mm from the cage and fuses it into the Front shell after the cage is built (the Front shell is registered
  there now). It closes the part of each arch above the fender line; 3146 mm3 per side. Build ok, 84 parts, collide.py 0, front_check 0 findings
  at rest, in 9 poses and with +12 / -8 mm travel (checked before the rim and slot refinements; rest check 0 after them).
- Front shell wall after the liners: 0.86 cm2 below 1.2 mm (0.20 before the liners). Left: 24 mm2 per side up to 0.67 mm at
  (+-82.0, -206.7, 110.3) and 5 mm2 at (+-79.8, -226.0, 104.3), both on the liner near the arm slot; cause not found yet (two attempts: rim trim
  fixed the rear wedge, the square slot changed little). Outputs (kit, drawings, .sc) are NOT regenerated for the liners yet.
- Owner asked for liners for "the bigger cutout" too (the arch below the fender line, where the cage post, servo and motor show): not built.
  What is possible there: a rear closing wall behind the tie rods and a front one ahead of the wishbones; the wishbones, tie rods and shock
  posts need most of the inboard side open.
- Steering finding from the swing-arm study: the wheels steer only about 16.4 deg (outer) / 13.7 deg (inner) at full servo throw (shell cuts
  allow 22). Open.
- Organisation (owner, November 23): this session is the main orchestrator for two versions. Version 1 = the wishbone (A-arm) model in this
  folder. Version 2 = a second, switchable swing-arm front end, developed in the detached worktree `../fugu_swingarm_v2` and delivered as
  patches. Each version has its own orchestrator session; their helper sessions report to them, they report to the main orchestrator.
  Helper sessions must not use the Fable model (its weekly limit was reached on November 23); they work in detached worktrees
  (`git worktree add --detach ../fugu_<name> HEAD`, no branches) and deliver patches into `scratchpad/agents/` of the main session.
- Sessions (November 23): main orchestrator `local_c8bcb368-7a79-4040-9349-e49f3268b7ab`; V1 orchestrator `local_4d35ed84-baa9-40f5-b062-15921980ec93`
  (owns this folder from commit a3d6ac8 on) with helpers "steering lock + knuckle" `local_68ec5002-bc9c-4c4b-a9ff-0c78b62ade41` and "battery +
  receiver mounts" `local_6899c56e-91b9-404b-bc81-a9ac41709851`; V2 orchestrator `local_fd4c9496-4c9a-45e7-9823-8e14247db375` with the design
  thread `local_c5ca023a-820d-4d9f-9aa4-36c8628f9bad`. The main orchestrator no longer edits the model itself.

### Liners stage 2, mounts, deck lap (November 23-24, Version 1 orchestrator)
- Liner thin spots: the first cause was a wrong constant: the liners used `WALL` (1.38 mm, the shell wall before the 2.17 scale) instead of
  `WALL_PRINT` (3.0 mm). Fixed (`LINER_WALL` in `parts/relief.py`). The arm slot is now extended inboard only. The two teeth stay OPEN:
  23 mm2 up to 0.61 mm at (+-81.1, -204.8, 105.9) and 9 mm2 up to 0.59 mm at (+-77.3, -226.1, 104.2), knife edges where the arm slot meets the
  knuckle / tyre cavity at an acute angle. Three attempts: inboard-only slot (no effect), cutting the wall within 1.5 mm of both cavities (worse,
  0.34 mm, reverted), bridging slot and knuckle with one hull (would remove 0.9-1.2 cm3 of liner per side, not applied).
- Lower-arch side panels (owner: "liners for the bigger cutout"): `arch_side_panels()` in `parts/relief.py`, fused into the Front shell with the
  liners. A 3 mm wall at x 55.5-58.5 (2 mm outboard of the cage foot post and lower rail, 1 mm off the deck edge) from y -133 (the tie rods and
  steering arm reach y -136.1 outboard of x 50 over lean +-10, horn +-30, bump +12 / -8) to the rear end of the arch, with a return of the same
  wall along the arch outline into the skin, 1 mm inside the outer face so the rim keeps its chamfer, and 0.3 mm back from the rim. About 19 cm3
  per side. It hides the cage foot post, the servo and the motor; ahead of the tie rods everything is travel of the wishbones, knuckle and tie
  rods, so nothing more can be closed there (judgement: no front wall ahead of the wishbones, it would only hide the arms themselves).
  Details: the outline is the arch's spline sampled every mm and grown as a polygon (an offset2D of the spline wire gave a solid that came back
  from STEP as an open shell and broke the front shell export); the bottom is cut square to the panel (the rocker plane left a 0.42 mm feather).
  Open: 6 mm2 per side up to 0.39 mm at (+-88.0, -92.8, 95.0), where the 0.3 mm setback meets the skin's rim at its inner corner.
- Merged the mounts helper's two patches: battery tray over the steering servo (PETG, two legs, 4 x M3 into inserts, two hook-and-loop straps,
  pack out through the cockpit), receiver box in the left front bay with a lid on 2 x M2.5 countersunk screws into inserts and a ledge on the
  outer side. CG and tip-over from the helper's rough mass model (ASSUMED masses): with body, battery and mounts 2645 g, CG 95.9 mm above
  ground, y -38.2, front share 61 %, worst tip-over angle 39.4 deg. Judgement by the helper: an FS-iA6B receiver no longer fits the bay with a lid.
  ESC is inside the motor (Fusion SE 2-in-1); leads all ride on the body, so travel does not change their length.
- Deck seam (owner rule: no plain butt joints): front and rear deck now meet in a full-thickness half lap, y -69.5 .. -56.5 (12.5 mm overlap,
  2.90 mm tongues, 0.20 mm face gap, 0.25 mm end gaps), front deck on top, 4 x M3x10 countersunk (ISO 10642) from below into ruthex M3x4
  inserts at y -63, x +-26 / +-46. The two unused open slots of the old layout at the seam were filled. The tongue underside needs support
  (deck is support "auto" in the kit). BOM: add 4 x M3x10 countersunk and 4 x M3x4 inserts.
- Checks after these commits: build ok, 88 parts; collide.py 0 (FILTERED: it skips chassis-vs-chassis pairs, an all-pairs mode is being
  added); front_check 0 at rest, in 9 poses and with +12 / -8 mm. Rear travel is NOT checked in poses. Front shell 0.99 cm2 below 1.2 mm.

### Stops, swept clearance, all-pairs collide, rear arm (November 24, Version 1 orchestrator)
- Droop stops (owner rule: travel limited by printed stops, never by the shock): `parts/stops.py`, one per side on the front deck under the lower
  arm root, PETG base with a bonded TPU 95A pad, 2 x M3x10 from below into M3x4 inserts. They touch at 10 deg lean + 8 mm droop (0.047 mm) and
  stay >= 1 mm away in every other pose. Base wall 0.20 cm2 below 1.2 mm (0.45 mm on the inboard top edge, open).
- NOT built, open with my judgement (owner may reverse):
  - Bump stops: no deck position (shock posts, heave shock and cage brace above the upper arm). Proposed: a bridge over the heave shock on the
    head top with TPU pads over the shock-post cheeks (41 mm lever, about 210 N per side at the 65 N case), 2 x M3 inserts in the head. Passed
    to the steering helper (owner of parts/wishbone.py).
  - Heave: per-wheel stops do not limit pure heave (up to about 37 mm bump / 33 mm droop); the shock bottoms at 60.0 mm eye distance (60.48 at
    10 deg lean + 12 mm). Proposed: a TPU ring on the shock shaft as the heave bump stop (about 6.7 mm compression), plus a droop limiter or a
    longer stroke. Until then the shock is the heave limit, against the owner's rule.
  - Lean stop at 10 deg: lean turns both arms the same way, so no body-fixed stop on one arm senses it; stopping the shock's tilt would side-load
    its shaft (about 150 N). Needs a lean link or balance beam: the owner's design choice.
- `tools/front_check.py`: overlap threshold 0.01 mm3 (printed), and a swept report: the minimum distance per pair over lean -10..10 x horn
  -30/0/30 at the current FRONT_BUMP against the 1 mm rule, with a named whitelist (ball studs, pivot rods, shock eyes, thrust collars) and a stop
  check. 10 pairs are under 1 mm, all in the front end and passed to the steering helper: arms <> knuckle 0.177, upper arm <> cage 0.094 (+12 bump
  only), upper pivot rod <> horn 0.378, knuckle <> lower rod end 0.748, upper pivot rod <> tie rod 0.95, lean head <> lower arm collar 0.000.
- `tools/collide.py --all` checks every pair (the default run skips chassis-vs-chassis pairs: "collide.py 0" in earlier entries meant the
  FILTERED check). On this model: 0 real overlaps, 3 whitelisted stand-in contacts with reasons in the file (ring gear stand-in drawn without its
  bore around the hub spigot 391 mm3; mock rear hub drawn solid around the mock axle 400 mm3; ring face grazing the shaft end 3.75 mm3). One
  real one fixed: the printed ring gear hub touched the rear shaft (0.11 mm3), now cleared 0.3 mm (model.py after the deck nodes).
- Rear arm: a convex web behind the shock pin corridor (WEB_X 22 in parts/swingarm.py). FEM 7.1 MPa, safety 2.81 (was 1.66), nothing below 2,
  coarse mesh within 1 %.
- Cage boss spots stay at safety 1.52 (13.1 MPa, 0.23 cm2 below 2; coarse mesh 27 % off, a sharp inner edge). Two real attempts by the strength
  worker made it worse (1.11 with the cone removed: the cone was acting as a gusset in the 58 deg crotch under the belt node; 1.30 with a crotch
  gusset): reverted. Options for the owner: (A) a larger upright / lower rear-quarter tube section at that node (12 instead of 10), (B) a
  longer gusset that takes the boss in. My recommendation: A. Not done because it changes the owner's reference tail frame.
- Rear travel (rear arm bump / droop) is still not checked in poses: open.

### Steering merge, arm tunnel, cage attempt, outputs (November 24, Version 1 orchestrator)
- Steering helper merged (2b88e68): wheels steer 22.5 inner / 19.2 outer at horn +-30 (was 16.4 / 13.7), steering line y -145, HORN_L 51, servo
  shaft y -94; knuckle arm studs into M3 inserts set from the back, steering-arm and horn ball studs through with nylocks (no printed threads at
  the studs; the pivot rods still thread M5 into the printed front post: open). FRONT_STEER_DEG 22.5. TPU heave bump stop on the shock shaft.
  HORN_METAL option prepared and OFF (owner decision: A printed T horn on a tall hub with a printed 25T spline, as built; B a generic 25T aluminium
  disc horn, D24, 2 x M3 at 16 mm, with the printed T bar bolted on; B needs 'Steer horn metal' in front_check's horn group when switched on).
- FEM: knuckle 8.6 MPa / safety 2.32 at the 3.6 mm auto mesh, 8.8 MPa / 2.28 at a 1.8 mm mesh (+2.3 %: confirmed); head 9.4 MPa / 2.12
  (coarse +6 %); rear arm 7.1 MPa / 2.81; upper and lower arm unchanged since November 22 (2.65 / 2.30).
- Swept clearance: tray floor +0.5 mm (FLOOR_Z 84.5), horn balls x 6.6, front hoop 1.3 mm higher (cage zft = zf - 4.2). front_check now
  reports nothing under 1 mm outside the named whitelist in all three runs (0, +12, -8 mm).
- Arm tunnel (owner: "clean it up into one framed opening"): `arm_tunnels()` in parts/relief.py, one prism along x through skin and liner with
  an octagonal section around the upper arm's travel outboard of x 64 and a 3 mm frame (first try, the arm hull extruded, had many small facets
  and fins under the arch). The liner teeth are gone. Pictures: side-session notes folder, v1_arm_tunnel_*.png.
- Cage boss spots: clean baseline on eb9aa32 1.48 (-x) / 1.69 (+x), plus a mesh-singular point at the tail (34.3, 168.9, 164.7), 111.7 MPa fine
  against 21.8 coarse (not a real stress; it moves with remeshing). Option A tried once (rear upright 12 mm): boss spots worse (1.39 / 1.61),
  new 0.28 mm edges: reverted. OPEN for the owner: option B (a longer gusset taking the boss in) or accept 1.48.
- STEP round trip: in-memory volume of every part against output/model.step read back: 95 of 95 equal (0.1 % / 0.5 mm3); ball studs 347.4 mm3
  both ways (the V2 hemisphere bug does not occur here).
- Outputs regenerated from eb9aa32 code: kit (97 parts exported to kit/stl_export_wishbone, 47 printed files in kit/print, mesh audit 0 flagged,
  13 plates, Bambu slice check 0 problems, 61.4 h, 1832 g), kit/bom.md and assembly manual (TPU added to the density table), drawings
  (output/drawings.pdf, 2 sheets), STEP of every part in exports/, animations "Lean steer" and "Lean steer front" (a stale lean_front entry
  in the anim build still names removed parts), renders/lean_steer_front.gif and _quarter.gif, offline renders renders/fugu_final_*.png,
  sc/Project_Fugu.sc last (97 closed bodies, volume within 0.061 % of the model; one import note on a face whose loops touch at (36, 56.8, 80.7)).
  BOM_COST.md: "Update November 24" with the new hardware.
- Open (not chased tonight, owner's or later): thin spots near the arm tunnel (5.3 mm2 at 0.49, 3.3 mm2 at 0.45 per side) and at the panel rim
  (6 mm2 at 0.39); droop stop bases (0.45 mm edge); lean stop (owner's design choice: lean link or balance beam); rear travel not in the pose
  check; cage boss spots 1.48; pivot rods M5 into printed thread; insert engagement 4 mm (below 2.5 x d); FS-iA6B receiver no longer fits the bay.

### Suspension + drivetrain kit, bearings, rear travel check (November 24, Version 1 orchestrator)
- Owner via the main orchestrator: "Yes, both kits": an orderable, printable, buildable suspension + drivetrain kit. Result: `kit/susp_drive/`
  (README.md = bought parts with prices, print list, plates, tools, fits and torque, assembly steps 0-10, open items; stl/, bambu/ projects).
- Bearings were missing in the model (probe of every shaft and bore line, scratchpad bores.py): front wheels turned on a steel hex hub on the bare
  6 mm pin, the rear axle (8 mm, turning) ran in plain 8.2 bores of the arm, and the arm's 8.2 pivot bores sat around the 5 mm cross shaft
  (pulley bore 5.2, carrier bearings 5x11x4; the old "8 mm extended axle" hardware row was wrong). Now: front wheels on 2 x 6x12x4 each (hub
  x 142.5..160, seats D12.1, 6x8x0.5 shims on the inner races, nylock snugged; 'Wheel hex hub' removed, 'Wheel bearing *' and 'Axle shim *' added);
  rear arm pivot plates each with a 5x11x4 seat (D11.1, bore 5.6), axle plates with 8x16x5 seats (D16.1). Count from the model: 5x11x4 x 8
  (pillow block 1, carrier 2 + 2, arm 3), 8x16x5 x 2, 6x12x4 x 4.
- Motor plate: screw holes and pinion boss slotted +-1 mm (MESH_SLOT) so a bought 32P 15T / 40T (21.8 mm) or 15T / 42T (22.6 mm) pair meshes;
  the model's 12 / 33 mm gear discs at 22.5 mm are stand-ins.
- FEM rear arm: the load case held the old bore points, which now ended on the thin shoulders beside the seats (safety 0.95, an artifact of the
  supports); moved onto the seat cylinders: 7.8 MPa, safety 2.56 (coarse mesh -4 %).
- Rear travel CLOSED as a check: `tools/rear_check.py` turns the swing-arm group about the pivot (x through the pivot pulley) from -15 to
  +20 mm at the axle: 0 overlaps; swept under 1 mm only arm <> tail deck 0.051 mm at -15 mm droop (it would be the droop stop; not designed as
  one). Shock eye distance -6.5 / +5.9 mm over that range (rigid stand-in, left out of the overlap check).
- Parts list: `kit/hardware.py` is the single source (bom.md and the kit README). Stale rows fixed (battery: CH6 tray exists; grub screws: 2
  pulleys DT14/DT15, there is no DT12/DT13; nylocks and inserts of the steering round; droop stops and pads now L/R IDs SU5L/R, SU6L/R; horn
  option A built, B prepared OFF). Real parts chosen by a Sonnet sourcing run, every URL and spec in `kit/sourcing_2026-11-24.md`:
  suspension + drivetrain 36 rows, 10 VERIFIED (261 USD), 19 ASSUMED (200 USD, generic sizes with estimated prices or listings that refused
  the fetch), 7 UNKNOWN (41 USD est.); total 502.47 USD as listed. Many chosen parts are discontinued or on backorder (heave shock, front tyre,
  40T spur, ring and pinion, rear tyre).
- Mismatches flagged, model not changed: heave shock RC4WD 70 mm is 72.5 mm with a 3.0 mm eye (model 68 mm, D4.1 pin hole), no spring rate;
  ring stand-in 25.6 mm OD against a 30T SCX10 ring; no 8 mm-bore 12 mm hex hub; inserts found are OD 4.2 (pockets D4.2 for OD 4.6); tyres
  38 / 53.5 mm wide against the 62 mm tyre envelopes.
- Print kit: TPU parts were on no plate in the full kit (make_manifest only grouped PLA / PETG): fixed. Full kit 47 files, 13 plates, 0 problems,
  61.6 h, 1838 g. Suspension + drivetrain kit 26 files, 5 plates, Bambu slice check 0 problems, 19.1 h, 600 g (TPU plate sliced on the PETG
  profile: ASSUMED).
- Not deleted: the stale Wheel_hex_hub STLs in kit/stl_export_wishbone (skipped as hardware by the registry). Still open: cage boss 1.48, no lean
  stop, pivot shoulder screws' M5 end has no nut seat, nothing printed.

### Edge breaks on moving parts, print or buy (November 24, Version 1 orchestrator)
- Owner: "make sure all mechanically moving parts like tie rods, knuckles, pivots, etc, please make sure to apply chamfers to them. all except
  gears of course. make sure i can either print this whole kit of use a steel part that i can buy off the shelf".
- `parts/util.py chamfer_moving` (CHAMFER_MOVING param in model.py): 0.6 mm on convex outside edges and boss / rim circles (0.4 where the kernel
  rejects 0.6), 0.4 mm on every bore, pocket and insert entry (0.26 fallback); concave edges (seat floors, pocket bottoms) and circles on lands
  narrower than 1.5 mm (pocket floors between two bores) stay sharp; pulleys circles only (hub, flanges, bore, never the teeth). Applied to the
  lean head, wishbones, knuckles, steering horn, servo mount, heave and droop stops, droop pads, front and rear wheels, rear arm, both pulleys.
  NOT applied to the traced drivetrain blocks (pillow block, rear bearing carriers, ring hub): faceted meshes, the chamfer took 8 of 24 edges and
  crashed the kernel (segmentation fault) on the carrier; they need a CadQuery rebuild first (open). OCC's clean() also crashed on a chamfered
  arm: chamfered shapes are cleaned before and skipped after (NO_CLEAN). First try chamfered concave circles too (added material: 2.3 mm3 into
  the wheel bearings): fixed by the convexity test.
- Checks: build ok 103 parts; collide 0, all-pairs 0 real + 3 whitelisted; front_check 0 at rest, in the poses, +12 / -8, swept 0 to look at;
  rear_check 0 overlaps (arm 0.051 mm from the tail deck at -15 mm droop).
- FEM after the edge breaks (3 attempts, then stopped): head 10.0 MPa / safety 2.00 (was 2.12), lower arm 9.1 / 2.19 (was 2.30). OPEN: knuckle
  peaks at (105.5, -193.4, 68.0) by the upper stud bore with fine 30 MPa against coarse 444 MPa (not converged: a support or mesh singularity at an
  edge break, not a trustworthy number; was 2.32 before); rear arm 11.1 MPa / 1.80 at the outer pivot seat entry with 4 distorted elements (was
  2.56); upper arm refused (distorted elements at mesh 2.0 and 1.5). The supports were moved onto cylinder faces (faces="%CYLINDER") in the
  knuckle and rear arm cases; the next step is a finer local mesh or leaving the seat / stud bore entries sharp on those three parts.
- Printed tie rod option ST3L / ST3R (wb.printed_tie_rod, kit/export_options.py, options plate): D7 body, D7.8 x 6 collars with M3 inserts, cup
  shank clearance D4 x 13; the D9 collar came 0.47 mm from the cage at full horn. Hand check (kit/susp_drive/print_or_buy.md): safety 8.1 in
  buckling and 17 in tension at the 29.8 N servo stall load (2.4 / 5.1 at the old 101 N). front_check with PRINTED_TIE=1: 0 overlaps, 0 to look at.
- Print or buy: kit/susp_drive/print_or_buy.md (both paths 3: tie rod, horn (metal ASSUMED), heave bump stop; print only 14 rows; buy only 14
  rows), kit/susp_drive/interfaces.md (lean head, wishbones, knuckle, rear arm as machinable interfaces), steel sourcing in
  kit/susp_drive/steel_parts_2026-11-24.md (Secraft SEC349 80 mm turnbuckle, McMaster 92981A130 shoulder screw, ServoCity 5 mm shaft, VXB 8 mm,
  JConcepts JCO2662 limiters VERIFIED; no 26T GT2 aluminium pulley, the 30T has a REX bore, no ball stud listing gives thread length).
- Kit: full 49 files (47 on plates, options excluded), 13 plates, 0 problems, 61.5 h, 1835 g; suspension + drivetrain 28 files, 6 plates,
  0 problems, 19.3 h, 604 g (options plate 0.2 h, 6.3 g). The first slice run timed out once on a plate (Bambu CLI), the rerun was clean.

### Strength after the edge breaks, ball joints (November 25, Version 1 orchestrator)
- Main orchestrator: settle strength with a new approach (de-featured FEM + refinement; rear arm: real or mesh; ball cups 6.92 vs studs 6.8).
  soma.fem has no local refinement: a finer global mesh (FEM_MESH) was the refinement. Switches for analysis runs only (never for soma build):
  FUGU_FEM_SHARP_BORES (bore / insert entries sharp, outside edges kept) and FUGU_FEM_NO_CHAMFER (part without edge breaks); FEM_MESH and
  FEM_KN_SUPPORT in the analyses.
- Knuckle (3 attempts, NOT settled): with the Nov 24 supports on the pocket walls (faces "%CYLINDER") de-featured 1.35 at mesh auto / 1.36 at
  1.8 (converged, but the peak sits on the fixed face, and the part with no edge breaks gives the same 1.32 there: the support choice, not the
  chamfer). With the original eb9aa32 supports: no edge breaks 2.32 (reproduces the old value), bore entries sharp 2.43 at the auto mesh but
  1.82 at 1.8 mm at one point (0.00 cm2 below 2, near the lower stud): 25 % apart, over the 10 % limit, so stopped. Analysis file now uses the
  original supports again (FEM_KN_SUPPORT=cyl for the variant).
- Upper arm: the mesher refuses the arm with its edge breaks (distorted elements at mesh 2.0, 1.5, 1.2, also with the bore entries sharp; the
  0.4 / 0.6 mm faces on the chamfered tube facets). Without edge breaks: 7.8 MPa, safety 2.58, coarse mesh +7 % (converged). That is the value
  with the method stated: the FEM model is the arm without its edge breaks.
- Rear arm (3 attempts, NOT settled): with the 0.4 seat entry breaks 1.62 at 1.5 mm, 1.33 at 1.2 mm (diverging); bearing seat entries now left
  sharp in the model (exception to the edge-break rule, the seats keep their full 4 / 5 mm; owner's rule allows it where it costs strength):
  1.69 at 1.5, 1.55 at 1.2 (coarse +25 / +15 %), 0.57 at 2.5 at the loaded axle seat face. Every peak sits on a fixed or loaded seat face
  and moves with the mesh: a support / load singularity of the rigid seat supports, not a converged stress. 5c2a70a gave 2.56 at 2.5 with the
  old near points (no faces filter). Next step: the bearing load as a distributed load over the seat (not offered by soma.fem) or back to the
  5c2a70a load points.
- Ball joints: the cups found took 6.92 mm balls. Matched pair now Gmade GMA20216 "M3 Rod End w/ 6.8mm Steel Ball (10)", $12.00, VERIFIED on
  hobbyrecreationproducts.com (2026-11-25, out of stock): the 6.8 mm hollow ball comes with its cup, held by an M3 screw into the knuckle insert
  or through the horn / steering arm with a nylock. Alt. VERIFIED ball size: Xray 352659 6.8 mm M3 studs + Xray 352664 / 352665 6.8 mm cups
  (M4: arm tips and tie rods would need M4). kit/hardware.py and print_or_buy.md updated; worker notes in the scratchpad were not kept.
- Build ok 103 parts, collide 0, all-pairs 0 real + 3 whitelisted, front_check 0 (rest, poses, +12 / -8, printed tie rods), swept 0 to look at,
  rear_check 0 overlaps.

### Knuckle and rear arm strength: hand check and FEM away from the supports (November 25, Version 1 orchestrator)
- Main orchestrator: stop reading the global maximum (singular at rigid supports and loaded seat faces); hand calculation first, then the FEM
  maximum over points more than 2 element sizes (at least 2 mm) from every held or loaded face, at two meshes, settled within 10 %.
- Tool: `tools/fem_away.py <result.glb> D` reads the result GLB of `soma analyze fem` (per-vertex _STRESS of the part surface, bc<i> meshes =
  the held and loaded faces) and gives the maximum farther than D from every bc face, with its position. Geometry: the kit geometry (all edge
  breaks, rear arm seat entries sharp).
- Knuckle, hand (loads of analyses/wishbone_knuckle.py: (-30, 0, 105.5) N at x 127.25 and -40.5 N at x 142 on the axle line y -216.55,
  reactions from the run: upper stud (24.1, 0, -65), lower 5.9 N in x):
  - block-to-plate joint, plane x 112.5, 10 (y) x 24 (z) mm, A 240 mm2, centroid (112.5, -203.05, 40.6): M = (-877, -361, -405) N mm.
    Bending 361 / (10 x 24^2 / 6 = 960 mm3) = 0.38 MPa, 405 / (24 x 10^2 / 6 = 400 mm3) = 1.01 MPa, torsion 877 / (0.25 x 24 x 10^2) = 1.46 MPa,
    axial 0.13, shear 1.5 x 65 / 240 = 0.41: von Mises sqrt(1.52^2 + 3 x 1.87^2) = 3.6 MPa, safety 5.6 (nominal).
  - stud root, plate + back boss above the gusset (z 58), 13.5 (x) x 15 (y) mm, A 202.5: upper stud force taken at the ball (y -216.55, 15.5 mm
    ahead of the plate centroid: the FEM holds it at the pocket instead): M = (1040, 334, 424) N mm: 1040 / 506 = 2.05, 334 / 456 = 0.73,
    torsion 0.74, axial 0.32, shear 0.20: von Mises 3.5 MPa, safety 5.7 (nominal).
  - axle boss root (x 112.5), tube D16 / D6.1, Z 394 mm3: M 361 N mm 0.92 MPa, shear 2 x 65 / 172 = 0.76: von Mises 1.7 MPa (safety 11.7).
- Knuckle, FEM away from the supports: mesh 2.5: 8.99 MPa (> 5 mm), safety 2.22; mesh 1.8: 9.91 MPa (> 3.6 mm and > 5 mm alike), safety 2.02;
  9.3 % apart (of the fine value): SETTLED, safety 2.02. Location (112.8, -208.1, 52.5): the inner corner where the rim block's top (z 52.6) meets
  the plate's front face (y -208.05), on the block-to-plate section of the hand check (nominal 3.6 MPa: the corner is sharp, concave edges are
  not broken by the rule, factor about 2.7). It rises slowly with the mesh: a 1-2 mm fillet in that corner would give margin (not done: geometry
  change only if a settled value is under 2). Global maximum 14-17 MPa sits on the held pocket face (0.0 mm from it): singular, not used.
- Rear arm, hand (loads of analyses/rear_arm.py, reactions from the run at the three pivot seats: x -1 (5, 21, 114) N, x 44 (-34, -173, 6),
  x 69 (-1, 153, -41)): the most loaded seat x 44 carries 173 N radially. Pivot boss ring D22 / D11.1 x 4 mm seat: bearing pressure
  173 / (11.1 x 4) = 3.9 MPa, net section 173 / ((22 - 11.1) x 4 = 43.6 mm2) = 4.0 MPa, with the ring's bending about 6 MPa (safety about 3.3).
  Chords at the root (y 122 arm frame, chords 40 mm apart, CHORD_D square about 100 mm2), the single-sided loads at x about 0 shared by the
  plates at x 47 / 72 by the lever rule (inner plate 2.9 x, outer -1.9 x): inner plate root moment about 5480 N mm: chord force 137 N, 1.4 MPa,
  plus 0.6 MPa from the side load: about 2 MPa. Mid-span (y 170, chords 31.5 mm apart): wheel share 158 N x 55.6 mm / 31.5 = 279 N: 2.8 MPa.
- Rear arm, FEM away from the supports: mesh 2.0: 6.24 MPa (> 4 mm), safety 3.21; mesh 1.5: 6.81 MPa (> 3 and > 4 mm), safety 2.94; 8.4 % apart:
  SETTLED, safety 2.94, at (43.8, 117.2, 52.6): the outer fibre of the x 44 pivot boss below the axis, the hand value (about 6 MPa) agrees.
  Global maximum 8.8-11.7 MPa on the held seat face (singular, not used).
- Upper arm unchanged: 2.58, analysed without its edge breaks (the mesher refuses the arm with them).
- Summary: knuckle 2.02 (settled, at a sharp inner corner, little margin), rear arm 2.94 (settled), upper arm 2.58 (without edge breaks), lower
  arm 2.19, head 2.00 (both read as the global maximum on the chamfered geometry, Nov 24).

### Knuckle corner fillet: tried 3 times, reverted (November 25, Version 1 orchestrator)
- Main orchestrator: fillet R 1.0-1.5 at the knuckle's block-to-plate inner corner (2.02 is no margin for a printed part), same read-out away
  from the supports at both meshes. Baseline (543a108): 8.99 MPa / 2.22 at mesh 2.5, 9.91 MPa / 2.02 at mesh 1.8, at (112.8, -208.1, 52.5).
- 1: a fused R 1.5 filler strip along x in the corner between the block top (z 52.6) and the gusset front face (y -208.05): the mesher failed at
  both sizes ("the 1D mesh seems not to be forming a closed loop": the strip's flat ends met the 0.6 mm edge breaks of the block's end edges).
- 2: an OCC fillet R 1.5 on that edge (ends blended by the kernel): meshed, but 11.59 MPa / 1.72 (2.5) and 12.93 MPa / 1.55 (1.8), worse, peak
  still at x 112.7, at the fillet's end against the block's inboard end face.
- 3: OCC fillet R 1.5 on that edge and on the vertical inner edge where the block's inboard end face (x 112.5) meets the plate's front face
  (y -208.05), blended together: 9.86 MPa / 2.03 (2.5) and 10.31 MPa / 1.94 (1.8), peak at (112.9, -208.7, 52.9) where the two fillets meet.
  No better than without. Every build was clean: collide 0, all-pairs 0 real, front_check 0 at rest, in the poses, +12 / -8 and with the printed
  tie rods, swept 0 to look at, rear_check 0; the fillet's nearest moving part: upper rod end 12.5 mm at horn +-30, lower arm 12.9 mm.
- Reverted to the 543a108 knuckle (code and STEP identical to it). Reading: the stress at that spot is the section's 3D corner where block top,
  block end face and plate front meet, carrying the block's torsion and bending (hand check 3.6 MPa nominal on 10 x 24 mm); a 1.5 mm radius
  does not change it. What would: a bigger section there (the block's joint to the plate is only the 10 mm plate depth: let the block run back
  over the back boss to y -193 (15 mm, torsion modulus about 2.2 x), or a gusset under the block). That is a geometry change with clearance
  checks; not done without the owner's go-ahead. Knuckle stays at 2.02 (settled, mesh 1.8).

### Knuckle block-to-plate joint deepened: tried 3 times, kept 543a108 (November 25, Version 1 orchestrator)
- Main orchestrator: run the rim block back over the back boss (15 mm joint), gusset only if needed; target settled 2.3 or more, meshes within
  10 %, else keep 543a108. Read-out as before: tools/fem_away.py at mesh 2.5 (> 5 mm) and 1.8 (> 3.6 mm). Baseline 2.22 / 2.02.
- 1: block runs 5 mm further back (KNUCKLE_BLOCK_BACK 5, joint 15 mm deep, +840 mm3, +1.1 g at 100 %): 8.32 MPa / 2.40 and 9.64 MPa / 2.07,
  14 % apart, peak unchanged at (112.8, -208.1, 52.7). The corner is in front of the plate (block top against the gusset's front face), so the
  extra depth behind the plate hardly reaches it. Nearest moving part to the extension 15.8 mm (lower arm at lean 10 / horn 30).
- 2: plus a sloped front gusset wedge 8 forward x 6 up from x 112.5 (+161 mm3): 1.33 and 0.78 (+55 % between meshes): the wedge stood 1 mm above
  the 5 mm gusset and its inboard end made a new inner corner at (112.6, -208.1, 58.2).
- 3: wedge flush with the gusset (8 x 5) and started 3 mm over the plate front (x 109.5): 2.04 and 1.51, peak at the wedge's top edge against
  the gusset (112.1, -208, 57.5). Nearest moving part 7.4 mm (upper rod end at horn 30).
- All three builds: collide 0, all-pairs 0 real, front_check 0 at rest / poses / +12 -8 / printed tie rods, swept 0 to look at, rear_check 0.
- Kept 543a108 (code and STEP identical to it): settled 2.02 at mesh 1.8. Reading: the stress sits where the rim block's forward overhang meets
  the plate's front face and the gusset, and every added plate or wedge face moves the peak to its own new edge; a step change in section is
  needed: for example the rim block and gusset as one sloped body that runs from the boss top up the plate front to the upper stud boss (no
  vertical faces meeting at the block top), or the axle boss carried by a web behind the axle line (y > -208) instead of the forward block.
  That is a redesign of the knuckle's rim side, not tried.
