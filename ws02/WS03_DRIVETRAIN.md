# WS-03 drivetrain around stock parts (branch ws03-drivetrain)

All numbers live in `w3_stock.py` (one source for the housings, the mocks, the layout blocks and the base-plate slots).
**F** = found in a source, **A** = assumption (typical value; the source search found no figure). Search 2026-11-07 on axialadventure.com, horizonhobby.com,
OzRC, Nankin, ServoCity, RobotShop, Arrma, hobbywing.com: retailers and manufacturers publish tooth counts and pitch, **not** ring OD, thickness, bore, bolt circle,
pinion length or carrier size, and no printed-design or STEP source for the SCX10 III 6-bolt diff turned up. **Measure the parts when they arrive**: every A below
is one constant in `w3_stock.py`, the housings and the slots follow it, and the base-plate slots give +-5 mm of fore/aft adjustment.

## Parts

| Part | Number | Facts | Status |
|---|---|---|---|
| 6-bolt HD gear set (front diff, rear bevel) | AXI232003 | 30T ring / 8T pinion, 3.75:1, 6 bolts ([Axial](https://www.axialadventure.com/product/AXI232003.html)) | F counts |
| | | 32 DP (module 0.794): pitch dia ring 23.81, pinion 6.35 mm | A (32 DP is confirmed only for the 40T) |
| | | ring OD 25.5, thickness 5.5, bore 11, bolt circle 15 (6 x M2), tooth tip 1 mm above the pitch plane | A |
| | | pinion head 10 long (face 4.5, back cone 1.5, hub 4), head OD 9, bore 5 (set screw on the 5 mm shaft) | A |
| | | 90 deg straight bevel, apex at the ring axis: pinion pitch plane 11.906 mm from the apex, ring pitch plane 3.175 mm from the apex | calc |
| 6-bolt differential locker | AXI232002 | fitted to the centre-diff carrier | F name |
| Differential carrier (AR45 6-bolt) | part number not read; see AXI03007 list | OD 30, length 30 (front) / 32 (centre); outputs through a 5 mm shaft | A |
| Output shafts | AXI232028 (straight) / AXI232027 | 5 mm; length not published; the arm-side stubs are 86 mm in `w3_scene.py` | A, **check length** |
| 40T metal spur (centre-diff ring) | AXI232034 | 40T, 32 pitch, pitch dia 31.75, OD 33.3 ([Axial](https://www.axialadventure.com/product/40t-metal-spur-gear-scx10-iii/AXI-3860.html)) | F; bore 10, width 6 A |
| Input metal gears 27T / 20T / 34T | AXI232033 | two 27T used as idlers; pitch dia 21.43, OD 23.0 ([Nankin](https://nankinhobby.com/products/axi232033-input-metal-gears-27t-20t-and-34t-scx10iii)) | F counts; pitch 32, bore 5, width 6 A |
| Motor pinion 13T, 32 DP, 5 mm bore | generic (Robinson Racing / Hot Racing class) | pitch dia 10.31 | not an Axial part, A |
| Motor | Hobbywing QuicRun Fusion SE 1800KV (HW30404317) | 36 x 58.1, 3.175 shaft, 16.5 exposed shaft, 201 g, ESC built in, 2-3S ([Hobbywing](https://www.hobbywing.com/en/products/quicrunfusionse)); mounting holes M3 on a 16 mm pattern not published | F; holes A |
| Shaft coupler 3.175 to 5 mm | generic | joins the motor stub to a 5 mm rod | A |
| Bearings 5 x 11 x 4 (MR115ZZ) | | printed seats 11.15 | F size from the parts list |
| 5 mm shafts | see below | | |

Gear mesh clearance: every spur centre distance is nominal + 0.20 mm, backlash 2 x 0.2 x tan 20 = **0.146 mm**. Each bevel pinion has a 0.8 mm shim stack behind it
(0.5 + 0.3 washers): backlash 2 x 0.8 x sin 14.93 x tan 20 = **0.150 mm**. Both lie inside the 0.1 to 0.3 mm window; trim the shims after a paint test.

## Layout (assembly frame, x forward)

- **Front diff**: ring axis along y at x -100; ring (tooth face y 18.8, back y 13.3) on the carrier's +y end; pinion head x -118.2 .. -108.2, pitch circle plane x -112.7.
  Pinion shaft bearings at x -123.2..-119.2, -134.2..-130.2 and -158.1..-154.0; output bearings unchanged (y -26.1..-22.0 and 30.0..34.1).
- **Centre diff**: carrier along x at y +21, x -234.7 .. -202.7, with the AXI232002 locker. The 40T spur ring sits on a printed hub (`w3_cring_hub`, flange bolted to the
  carrier's forward face, spigot through the gear), x -198.7 .. -192.7. Bearings 5 x 11 x 4 at x -239.2..-235.2 and -192.2..-188.2.
- **Rear bevel**: ring axis along y at x -332 (arm pivot), ring on a printed hub (`w3_rring_hub`) on the 5 mm output shaft; pinion head x -323.8 .. -313.8.
- **Shafts**: front pinion shaft x -212.7 .. -110.7 (102), rear shaft x -326.7 .. -224.7 (102). Each end sits 10 mm in a carrier hub or 7.5 mm in a pinion bore.
- **Supports**: no 5 mm shaft runs more than 40 mm between bearings. Front shaft bearings at x -121.2, -132.2, -156.1 (front case) and -190.2 (centre case): spans 11, 24, 34 mm.
  Rear shaft bearings at x -237.2 (centre case), **pillow block** `w3_pillow` at -268.5, rear case -299.8 and -310.8: spans 31, 31, 11 mm (`tests/test_w3_drive.py` asserts < 40).
  Gears have a bearing on each side: ring/carrier (both flanges), spur idlers and the motor-shaft pinion (aft and forward plate), bevel pinions (two bearings behind the head, 11 mm apart, 10 mm overhang).

## Cross-over from the motor to the centre-diff ring

The motor (x -122, y -21, z 41) cannot reach the ring (y +21, z 0, 58.7 mm away) with one gear. A single plane at x -198.7 .. -192.7 carries four spur gears
with axes along x: **13T pinion on a 5 mm rod joined to the motor stub by a coupler -> 27T idler -> 27T idler -> 40T ring**. The idlers cancel, the ratio is 40/13 = 3.077.
Positions (y, z): pinion (-21, 41), idler A (-5.9, 35.6), idler B (13.4, 25.7), ring (21, 0). Three meshes reverse the sense: set the ESC direction so the wheels roll forward.
The tower (upper half of the centre case) holds the bearings of all three shafts in two plates, one on each side of the gear plane; posts join them.

## Ratio chain

Rear belt pulleys swapped to 22T (pivot) driving 20T (axle) to bring the rear path near the front path (the mock radii are the same sum, belt length unchanged).

| stage | ratio |
|---|---|
| motor pinion 13T -> 27T -> 27T -> 40T ring | 3.077 |
| centre diff (50:50 torque, carrier speed = mean of the outputs) | 1 |
| front: 8T/30T bevel 3.75, belt pivot 20T -> tip 16T 0.8 | **3.00** |
| rear: 8T/30T bevel 3.75, belt pivot 22T -> axle 20T 0.909 | **3.41** |
| **overall (front path)** | **9.23 : 1** |

3S (11.1 V) x 1800 KV = 19 980 rpm no load -> **wheel 2 165 rpm** -> 112 mm tyre 12.7 m/s = **45.7 km/h no load, about 39 km/h at 85 % load**.
(1200 KV would give 31 km/h: use the 1800 KV.) The centre diff handles a front-to-rear shaft speed ratio of 1 : 1.136 at equal wheel speed (rear shaft 13.6 % faster); torque split at the
wheels 47 % front / 53 % rear; the corner mismatch (about 4 % at full lock) comes on top. The front share of weight is about 64 %, so the lockable carrier (AXI232002) is useful in loose going.

## Shopping list for the drivetrain

AXI232003 x 2 (front diff, rear bevel), AXI232002 x 1, carriers (AR45 6-bolt) x 2, AXI232034 x 1, AXI232033 x 1 (two 27T), 13T 32 DP 5 mm-bore pinion x 1,
3.175-to-5 mm coupler x 1, bearings 5 x 11 x 4 x 28, shafts: 5 x 102 mm x 2 (front pinion shaft, rear shaft), 5 x 50 mm rod x 1 (motor extension), 5 x 22 mm pins x 2 (idlers), 5 x 70 mm x 1 (rear output, y 8 .. 76),
shim washers 5 x 0.3 / 0.5 mm, M2 screws for the ring hubs. If a stock length is not sold, the lengths above leave 1 to 2 mm of play in the pinion bores, so a neighbouring length works without cutting the gears.

## Open items

1. Carrier hub and bearing: the real SCX10 III carrier has its own hub diameter; the 5 x 11 x 4 bearings are assumed to sit on the 5 mm output shafts next to the carrier.
2. Retention of the 40T spur on its hub (bore, lightening holes) and of the 8T/30T ring bolts: unknown until the parts are in hand.
3. The motor mounting hole pattern and the 13T pinion bore.
4. Motor position: the brief said x -100; the fit scan in `layout3wd.py` leaves only x -122 free (hoop, servos and diff case), so the motor stays at x -122.

## Results (ws03-drivetrain)

- `pytest tests/test_w3.py tests/test_w3_drive.py`: see the commit message for the count; every printed part single watertight body, inside the 256 mm bed, 3-perimeter walls >= 1.2 mm.
- Clearance (`WS03_CLEARANCE.md`): no overlaps; remaining sub-0.3 mm pairs are designed contacts (split faces, bearings in 0.15 mm seats, hub flanges on the carrier, shafts in 0.2 mm bores).
- Swing (`w3_swing.py`): clean at every degree to 35; 40 deg touches the front frame and battery as before.
- Mass 2.08 kg, CG x -167.2, **front weight share 62.9 %** (was 63.8 %: the transmission tower and the 40T steel gear sit aft); target 64 % would need the battery or the motor about 15 mm further forward.
