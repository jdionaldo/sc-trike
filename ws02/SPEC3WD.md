# WS-03: 3WD lean-steer reverse trike (form and function)

Decisions (from the user's direction; scale is free, 1/18 is no longer a limit):

1. Front suspension and lean: per-wheel swing arm in the side (x-z) plane. Arm is a plate shaped like an inverted V
   (peak carries the lean drive link), rear end pinned on a sideways (y) axis, front end carries the knuckle carrier.
   A hidden upper link of equal length keeps the carrier upright (parallelogram) so caster stays constant.
   Left arm down / right arm up leans the body; wheels lean with the body.
2. Steering: knuckle (C-hub) on a caster kingpin; tie rod parallel to the arm so it does not change length as the arm
   swings; one steer servo per wheel.
3. Servos: inside the tub, long axis along the body, shaft along y (horn sticks out the side, swings in the x-z plane).
   Two per side (lean, steer). Lean horn is short and the link lands near the arm pivot for leverage.
4. Drive (3WD, bevel gears): motor, spur stage, centre diff (axis along x), front shaft to a bevel pinion on the
   front diff ring (lateral axis), rear shaft to a bevel pair that feeds the rear swingarm pivot shaft, then belt to the
   rear axle. The front diff outputs are coaxial with the two front arm pivots, so the arms swing about the drive axis.
   Each front arm carries a belt (or gear train) from the pivot to the carrier, then a lateral shaft and a dogbone with
   a universal joint on the kingpin axis to the wheel axle. Belts and gears run inside printed covers.
5. Shell: stays the base.stl-derived monocoque; stretch or widen it as the layout needs, cut windows where the arms
   leave the body, belt/gear covers and wing fenders styled to match the shell. Reference photos: arms exit under the
   red shell, skid plate in front, wing plates on the arms.
6. Bought parts (verify sizes before buying): 1/10 or 1/18 4WD diff and bevel sets, CVD dogbones, GT2 belts, 12 kg short
   servos (40 x 20 x 19.3), 2830 motor; motorcycle RC donors (for example the 1/4 Losi Promoto-MX) for swingarm, shock and tire.

Stages
- S1 layout study with overlap check, shown in the live window (ws02/layout3wd.py).
- S2 front arms, carrier, drive parts, servo mounts; kinematics and interference in all poses.
- S3 drivetrain parts (centre diff, shafts, bevel housings) and rear swingarm change.
- S4 shell stretch, windows, covers; tests, report, BOM, push.

## S2 kinematics result (front3wd.py)
- Lean limit set to 30 deg (35 deg needs a 55 deg arm swing). Arm length 100 mm: arm swing +-42.7 deg, wheel moves back 26.5 mm at full lean, wheel travel +-68 mm.
- Lean horn: lug 24 mm from the pivot at 20 deg above the arm, horn 28 mm at -40 deg rest, rod 24 mm, shaft at (-77.4, -17.0): horn range +-19 to 24 deg over the full lean range.
- Steer: tie rod parallel to the arm (inner point = pivot + steering arm vector), so lean never changes its length.

## S2 parts (parts/w3_front.py, w3_scene.py, w3_check.py) - done
- Printed and print-checked (left and right): arm (belt housing + inverted-V peak), arm cover, upper link, carrier (post + upper kingpin tab; the kingpin hangs from it), knuckle (block + web + steering arm column), tie rod, lean rod.
- Lean horn 28 mm, shaft (-71.4, -18.8), rest -40 deg, rod 30 mm (worst horn angle 29 deg). Steer horn 12 mm above the rod inner point, rod inner point 26 mm below the arm pivot axis, steering lever 16 mm inboard of the kingpin; the rod stays clear of the arm at any swing because its offset is mostly vertical.
- Zero interference over lean -30..+30 deg in 5 deg steps, each with steer 0, +17 and -17 (39 poses), both tie rods solved in all of them.
- Both wheels steer the same way (rotation about +z for both).
- Not yet checked: 1 mm clearance to bought parts, belts/pulleys/dogbone as solids, cantilevered kingpin strength, arm cover vs shell, ground clearance of the knuckle web (z -29 vs ground -41.5).

## S3 drivetrain decisions
- Tires: skinny off-road 83 x 24 front, thick big off-road 112 x 62 rear.
- Rake: chassis pitched nose-down 4 deg, so the platform rises toward the rear middle. In the chassis frame the rear axle sits 8.6 mm below the swingarm pivot (arm points down 6 deg) and the drivetrain axes stay level at the front axle height.
- Gearing: motor 15T to centre diff ring 45T (module 0.8, centre distance 24 mm), 3:1. One bevel set for both ends, module 1.0, 12T pinion / 30T ring, 2.5:1. Front belt 22T to 18T (0.82), rear belt 20T to 22T (1.1). Target 8.2:1 rear, 6.1:1 front (front tire is smaller). Top speed about 34 km/h at 3S.
- Layout: front diff axis (arm pivots) at x -100, ring on its +y end; bevel pinion shaft level with the diff axis, y +18.5, running back to the centre diff (axis along x, y +18.5). Motor above the centre diff (z +24), 15T pinion meshing its ring. Rear shaft continues back to the rear bevel set at x -250, whose lateral output is the rear swingarm pivot. ESC above the shaft, battery in the nose bay.

## S3 parts (parts/w3_drive.py, w3_check_drive.py, w3_drive_scene.py) - done
- Wheelbase stretched to 360 mm so the rear bevel case clears the 112 x 62 rear tire; rear arm pivot (bevel apex) at x -272, rear axle (-360, -10.7) at the 4 deg rake. Shaft line at y +21 (front pinion shaft, centre diff axis, rear shaft).
- Split housings (shafts lie in the z = 0 split plane, both halves print split-face up, cavities open upward): front diff + bevel case, centre diff case (window on top for the motor pinion), rear bevel case. 5 x 11 x 4 bearing seats on every shaft, M2.5 bolts.
- Slotted motor plate (vertical 8 mm slots for the 16 mm motor pattern: mesh adjustment), battery tray and ESC tray with fore/aft slots, rear swingarm housing with belt cavity (8 x 16 x 5 axle bearing, 5 x 11 x 4 pivot bearing; printed with supports because of the bearing-seat ledge) and cover.
- Housing cavities clear every gear and shaft block; layout overlap check clean.
- Not yet checked: rear arm and belts placed in the assembly, 1 mm clearance to bought parts, shell around the new drivetrain, bolting of the motor plate and trays to the tub (S4), tests and report.

## S4a shell (mono3_build.py, split_shell3.py, w3_interior_check.py) - first pass, NOT good enough visually
- The extracted base.stl skin is stretched (x 1.9, y 1.17) and hollowed at 0.5 mm voxel pitch (decimated to 400k faces), windows cut automatically from the swept front mechanism (lean -30..30), rear arm notch; split into 4 watertight pieces that fit the 220 x 220 bed.
- Interior fit: everything sits inside the shell except the lower diff housing (belly is open).
- Visual quality is poor: the extracted skin has no nose and ragged flanks after the windows. Next: build the body procedurally (plan, side and roof facets from the base silhouettes, panel recesses) instead of stretching the extract.

## S4b body rebuild (body3_build.py, split_shell3.py, w3_interior_check.py) - done
- Procedural faceted wedge from the base.stl silhouettes (plan, side, section with 11 deg tumblehome), mapped to the 3WD frame (x 1.19, y 1.17), 2.4 mm wall, fully open belly. 318 mm long, 135 wide, roof 90 above the belly; the nose is low and the roof peaks over the rear middle.
- Cut-outs: one angular window per flank (hull of the swept front mechanism + 4 mm), rear-arm notch, through louvres and a triangular vent, two 0.8 mm recessed paint panels per flank, roof access hatch (separate snug lid, 0.25 mm gap).
- Four watertight pieces (left/right x front/rear) fit the 220 x 220 bed; nothing inside pokes through the skin; the front mechanism clears the body at every lean/steer pose.
- Still to do: deck and internal mounts (slotted deck, servo pockets, tub walls), belt covers/fenders, nose skid plate, shell-to-chassis fixings, tests/report/BOM, tail detail.

## S4c (final pass) - done
- Front track widened to 269 mm (wheel centres), lean limit 25 deg, same 100 mm arms; arm/servo/wall stack shifted out 6.5 mm to clear the front diff case.
- Servo wall plates hang from ears on the front diff case; slotted decks follow the body plan; rear deck screws into pads on the body skirt, front body hangs on two posts and roof bosses; halves join with seam screws.
- ESC moved over the battery in the nose bay with the roof hatch above it; wing fender plates on the knuckle carriers; nose skid plate.
- Body details from the references: honeycomb triangular vent, louvres, recessed panels, screw heads, nose light-bar pocket, antenna post.
- tests/test_w3.py (44 tests) and w3_assembly.check_global pass over lean -25..25 and steer 0/+-17.

## S5 body finish
- Added: glass canopy recess on the roof, 1.2 mm raised roof spine from tail to nose, honeycomb grilles over the motor, tail light slot, smaller diagonal flank panel, vent shifted to clear it, paint/decal guide (WS03_PAINT.md).
- Tried and dropped: panel gap grooves (they made the shell non-manifold at the panel corners) and a rear tire fender (no room for a fixing between the body tail and the tire; needs a longer tail piece).
- Still plain compared with the references: the body is a prismatic wedge (flat roof planes and straight flanks); no compound curves, side pods or nose fascia.

## S6 snub nose
- The pointed nose is now a blunt, angular snub nose (front face 70 wide, 26 tall, chamfered corners) with four horizontal cooling slots (52 x 3 mm) through the face into the battery bay. The body stays angular (no curved surfaces). Skid plate narrowed to 72 mm to match.

## Mock drivetrain (w3_mock.py)
- Every bought drivetrain part is placed as a simple solid and checked in the assembly: centre diff carrier, ring gear and 15T motor pinion; front diff carrier and bevel pinions; front pulleys (20T pivot, 16T tip) and GT2 belts inside the arm cavities (they ride on the arms through the lean range); dogbone joints on the kingpins; front wheels (tire ring, rim barrel, outer disc, hub, axle) steering with the knuckles; rear tire ring and rim, 8 mm axle, rear pulleys (20T/22T) and belt; receiver. Front belt is 20T to 16T (0.8) so the pulleys fit the 7.5 mm cavity.
- Zero clashes over lean +-25 with steer 0 and +-17.

## S7 profile from the owner's sketch
- Side profile redrawn from the sketch over the RT-1 sheet: truncated nose with a slanted front face (four cooling slots), roof rising steadily toward the rear, tall rear hood with a rearward scoop that overhangs the front of the rear tire (to x -340, z 88), rear face and tail light slot. Plan: narrow nose, widest mid body (148 mm at x -189), tapering to a narrower tail.
- The flank window now starts at |y| 30 (it was 46) so the servos hang in the open "wheel opening"; the roof stays as a narrow canopy over the front mechanism. Posts moved in to y +-16, hatch narrowed to 48 wide.
- Not taken from the sketch: the solid pillar between the wheel opening and the side window (the arms sweep there) and the open tail underside (the gearbox is enclosed instead).

## S8 markup pass
- From the marked-up renders: rear scoop raised and lengthened (tip x -378, z 105, flat top), tail left open under a hood (rear bulkhead at x -243 with a shaft tunnel, hood underside at z 50) so the gearbox and rear arm show; nose widened to 88 mm; 3 mm rocker panel armor band along the lower flank (x -240..-122, z -24..-12); rear body piece split at x -165 so it stays under the 220 mm bed (213 mm).
- Motor plate now bolts to the rear bulkhead (two screws from behind); the rear deck passes under the bulkhead through a notch.
- Fixed a generator bug: the open-belly sweep also carved the rear bulkhead away.
- Not done from the markup: the front frame/cowl around the front wheel opening (the arms sweep through it).

## S9 shoulder frame and flat nose
- Front opening: only the servo level (|y| 30..52, z up to 25) and everything outboard of the walls (|y| > 52) are cut now, so the upper body shoulder stays as the opening's top beam, with the nose block as the front pillar and the rear body as the rear pillar.
- Nose: flat vertical front face (x 17.7, z -2..30, 76 mm wide) with four cooling slots; the bottom is angled back (z -2 at the face down to z -26 at x -35, about 25 degrees).
- Upper-link pivot: the wall boss pointed inboard; replaced by a printed standoff (w3_uplink_standoff) between the wall and the link.
- Clash sweep (lean 0, +-12, +-25 with steer 0/+-17): 0 clashes.

## S10 mass, strength
- w3_mass.py: about 1.6 kg total (printed about 510 g with 1.2 mm walls and infill, bought about 990 g, 110 g misc), 61% of the weight on the front axle, CG 45 mm above the ground, static roll-over 71 deg, rolls over at 5.4 m/s on a 1 m radius if it did not lean (it leans, so the real figure is higher).
- w3_strength.py: kingpin raised to 4 mm steel (factor of safety 2.3 to 5.5); the printed tie rod would buckle at 29 N, so the tie rods are 3 mm steel turnbuckles (printed part kept as an envelope); every other checked part has a factor of safety above 6.

## S11 styling pass
- Arms, covers, upper links, servo walls and the rear swingarm and cover are now mesh-built (parts/w3_style.py) with tapered, chamfered outlines; the lower arm peak is capped at 20 mm so it clears the upper link at full swing (the two links are 40 cos(theta) apart).
- Snub nose: front face overhangs (top at x 30, bottom at x 8), underside slopes back at 45 deg to the floor at x -20; angled skid plate (40 mm along the slope) screws into bosses on the underside; posts moved to x -29, ESC to x -79.5..-33.5, receiver to x -75..-51.
- 0 clashes over lean/steer poses, 112 tests.
