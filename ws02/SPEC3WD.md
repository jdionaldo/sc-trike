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

## S2 parts (parts/w3_front.py, w3_scene.py, w3_check.py)
- Printed and print-checked (left and right): arm (belt housing + inverted-V peak), arm cover, upper link, carrier (post + kingpin tabs), knuckle (block + steering arm column), tie rod, lean rod.
- Lean horn re-solved for the real lug height: horn 28 mm, shaft (-71.4, -18.8), rest -40 deg, rod 30 mm, worst horn angle 29 deg.
- Steering arm 28 mm behind the kingpin, 22 mm inboard. Zero interference at lean -30 to +30 deg in 5 deg steps (steer follows lean, 17 deg at 30).
- Not yet checked: 1 mm clearance to bought parts, steer-only poses, belts/pulleys/dogbone as solids, arm cover vs shell.
