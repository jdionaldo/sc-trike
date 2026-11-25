# Interfaces of the parts with no off-the-shelf metal equivalent

There is no stock metal part for the wishbones, knuckles, lean head or rear swing arm. Below is what a machined version must keep so it drops in for the printed one: hard points, bores, fits and fixings. Take the full shape from `exports/<part>.step`. The STEP is the printed part, with the 0.6 / 0.4 mm edge breaks.

The coordinates are the model frame at ride height: millimetres, X to the right (+x is the right side seen from behind), Y toward the tail, Z up. The values come from `parts/wishbone.py` and `parts/swingarm.py` (constants named in brackets) and from the built model of 2026-11-24.

Fit words:
- **slip:** shaft clearance 0.1-0.2 mm.
- **press:** bearing seat at the bearing OD + 0.1 mm in PETG. Machined aluminium needs a real press fit: for example, an 11 mm seat at 11.00 +0/-0.01.

The +x part is listed; the -x part is its mirror image in x.

## Lean head (SU1), fixed to the front deck

| Feature | Position | Size and fit |
|---|---|---|
| Upper pivot axes | x ±15.0 (XI), z 70.0 (ZU), along y | D6.1 bore through both posts; slip on the 6 mm shoulder of the ISO 7379 screw |
| Lower pivot axes | x ±15.0, z 42.0 (ZL), along y | as above |
| Front post | centred y -195.28 (HY0), 11.44 thick (TS) | front face at y -201.0, 0.6 mm behind the skid |
| Rear post | centred y -159.04 (HY1), 11.44 thick | the screw head bears on its rear face |
| Arm barrel space | between the posts, y -189.56 to -164.76 | 24.8 mm long, 0.4 mm axial running gap each side |
| Deck fixing | (±16, -195.28) and (±28, -159.04), from below | 4 x M3 into heat-set inserts (pockets D4.2 x 5) |

## Upper wishbone (SU2) and lower wishbone (SU3)

| Feature | Position | Size and fit |
|---|---|---|
| Pivot barrel | axis x 15.0, z 70.0 (upper) / 42.0 (lower), y -189.56 to -164.76 | D6.2 bore: 0.2 mm running clearance on the 6 mm shoulder (ream by hand) |
| Ball joint (tip) | ball centre x 106.0 (KX), y -216.55 (KY), z 70.0 / 42.0 | M3 ball cup for a 6.8 mm ball. Its shank runs along -x into the apex boss (D4.1, M3 insert or rod); the cup must tilt 20 deg |
| Arm length | 91.0 mm pivot axis to ball centre (ARM_L), both arms | parallel and equal arms |
| Heave shock eye (upper arm only) | pin axis along y at x 34.0, y -183.2, z 94.0 (SHOCK_EYE) | D4.1 pin hole through two fork cheeks, about 6.2 mm each (POST_D 18). The chosen shock eye is 3.0 mm: M3 pin plus a sleeve, or a 3.1 mm hole in a machined part |

## Knuckle (SU4)

| Feature | Position | Size and fit |
|---|---|---|
| Kingpin | through the two ball centres x 106.0, y -216.55, z 70.0 and 42.0 | vertical, no inclination, no caster |
| Arm ball studs | axes along y at (106.0, z 70.0) and (106.0, z 42.0) | M3 thread into inserts set from the back of the plate: clearance D3.3 at the front, insert pocket D4.2 from the back face 7.5 mm deep (UPPER_INSERT_Y); stud thread 12 mm |
| Stub axle | axis along x at y -216.55, z 40.6 (KY, ZC), boss from x 112.5 to 142.0 | D6.1 bore, slip on the 6 mm axle; boss end face at x 142.0 (the inner shim seats on it) |
| Wheel bearings (in the wheel, not in the knuckle) | 6x12x4 at x 142.5-146.5 and 156.0-160.0 (WHEEL_BRG_X) | 6x8x0.5 shims on both inner races, M6 nylock at x 160.5 |
| Steering arm ball stud | vertical axis at x 101.0, y -145.0 (STEER_ARM_XY); ball at z 60.0 (ZT) | D3.3 through the arm plate (z 47.0 to 51.5), M3 nylock below; ball 6.8 mm |
| Steering geometry | tie rod 93 mm ball to ball, to the horn ball at (6.6, -145.0, 60.0) | 22.5 deg inside / 19.2 deg outside at ±30 deg of horn |

## Rear swing arm (DT11)

The arm pivots about x, through the centre of the pivot pulley.

| Feature | Position | Size and fit |
|---|---|---|
| Pivot axis | y 114.65, z 63.68 at ride height | 5 mm cross shaft, turning. The arm rides on three 5x11x4 bearings (seats D11.1 x 4 at x -3..1, 42..46 and 67..71; PIVOT_SEATS). The bore beside each seat is D5.6, clear of the shaft |
| Pivot plates | x -9..1 (inner, beyond the drive block), 42..52 and 67..77 | 10 mm wide bosses, OD 22 |
| Axle axis | y 236.43, z 54.70 at ride height, 122.1 mm from the pivot | 8 mm axle, turning in two 8x16x5 bearings (seats D16.1 x 5 at x 47..52 and 67..72; AXLE_SEATS) |
| Belt line | between the plates, pulleys at x about 52.7 to 65.7 | 2GT-300, 6 mm wide; 26T on the cross shaft, 30T on the axle |
| Shock lower eye | pin axis along x at y 154.6, z 103.6 at ride height; ears at abs(x) 4.4 to 10.4 | D6.4 hole (PIN_BORE), 8.8 mm slot between the ears (EAR_GAP) for an 8 mm eye; M6 x 30 + nylock |
| Travel checked | -15 mm droop to +20 mm bump at the axle (-7.1 to +9.4 deg) | `tools/rear_check.py`: 0 overlaps |
