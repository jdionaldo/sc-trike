# WS-03 bill of materials (bought parts)

All sizes below are assumptions from the 1/10 and 1/18 RC parts we planned around. Verify against the real parts before buying.

| item | qty | notes |
|---|---|---|
| Servo, Injora INJS15 23 x 12 x 27.5 (32 over the ears), 17.7 kg.cm at 7.4 V | 1 | lean (single, on the centreline, shaft aft); ear hole pitch 28 mm, shaft offset 4.5 mm, flange 5 mm below the top face are read off the drawing: verify |
| Servo, 12 kg short body 40 x 20 x 19.3 | 2 | steer x2 (one per side at x -100, unchanged); a single central steering servo was ruled out, see WS03_LEAN.md |
| Servo horn 25T, aluminium, small round (lean) | 1 | the printed V rocker screws to it with 4 x M2 (the horn sits on the 4.5 mm spline stub; the rocker is 4 mm thick, so no standoff is needed) |
| Servo horn, 12 mm (steer) | 2 | aluminium horns, M2 ball studs |
| Motor: Hobbywing QuicRun Fusion SE **1800KV** (HW30404317) 36 x 58.1 mm, 201 g, ESC built in | 1 | replaces the 2830 motor; at x -122, y -21, z 41 (see Motor placement) |
| ESC | 0 | none: built into the Fusion SE |
| LiPo 3S 1300 mAh 75 x 35 x 25 | 1 | on the printed cradle beside the drive shaft (x -77.5..-2.5, y -37.5..-2.5) |
| Receiver 6 ch with mixing | 1 | lean, steer, throttle mixes |
| Spur gears 32 DP (drivetrain redraw, see WS03_DRIVETRAIN.md): 13T motor pinion (5 mm bore), 2 x 27T idlers (AXI232033), 40T ring (AXI232034) | 1 + 1 + 1 | motor to centre-diff ring, 3.077 : 1 |
| Differential carrier, AR45 6-bolt, with AXI232002 locker on the centre one | 2 + 1 | front and centre diff |
| AXI232003 6-bolt HD gear set (30T ring / 8T pinion) | 2 | front diff and rear bevel case |
| Shaft coupler 3.175 to 5 mm | 1 | motor stub to the 5 mm rod |
| Shafts 5 mm: 2 x 102 mm (front pinion shaft, rear shaft; Arrma ARA330574 class), 1 x 50 mm (motor extension), 2 x 22 mm (idler pins), 1 x 70 mm (rear output) | 6 | uncut; lengths from `w3_stock.py` |
| Bearings 5 x 11 x 4 | about 30 | every shaft seat (28 in the new drivetrain) and arm pivot |
| Bearings 4 x 8 x 3 | 4 | arm tip and carrier |
| Bearing 8 x 16 x 5 | 2 | rear axle |
| GT2 3 mm belts and pulleys | 4 belts | front 20T to 16T (x2), rear 22T to 20T (x1, swapped for the ratio match), spare |
| Dogbone / CVD with universal joint on the kingpin axis | 2 | about 25 mm lateral room |
| Wheels: skinny off-road 83 x 24 (front) | 2 | 4 mm axle |
| Wheel: thick off-road 112 x 62 (rear) | 1 | 8 mm axle, 8 mm hex |
| Axle 8 mm (rear), 4 mm (front, tip shafts) | 1 + 4 | |
| Pins 3 mm steel (kingpins, link pivots) | 8 | |
| Ball studs / rod ends M2 | 8 | tie rods and lean rods |
| Turnbuckle rods with ball links, 61 mm centre to centre (M2 ball links) | 2 | lean rods from the rocker tips to the arm lugs (3D, not in one plane) |
| Screws M2 self-tapping | 8 | lean tower feet (4) and servo ears (4) |
| Steel turnbuckles 3 mm with ball ends, about 105 mm | 2 | steer tie rods (the printed tie rod is only an envelope; printed it buckles at 29 N against a 98 N servo stall) |
| Kingpins 4 mm steel, about 30 mm | 2 | hang from the carrier tabs |
| Rear coilover shock, 1/10 aluminium, about 55 mm closed / 80 mm open eye to eye (25 mm stroke), 3 mm eyes, adjustable spring, about 25 g | 1 | `b_rear_shock`, inside the body over the rear tyre, 12 mm left of the centre line. Suggested stock part: a 70 to 80 mm 1/10 crawler/buggy coilover with spring of about 22 mm OD (for example the generic aluminium '70 mm' / '80 mm' class sold by Injora or Yeah Racing; **check the eye-to-eye lengths and the eye width (about 5.5 mm) before buying**, the printed lug and tab are sized to those). A longer shock does not fit; a shorter one bottoms in bump. Spring rate: soft, about 0.3 to 0.5 N/mm at the shock |
| Turnbolts M3 x 14 with ball ends (or M3 screws, washers, lock nuts) | 2 | lower eye in the hoop lug, upper eye in the cage lug; each eye sits 0.4 mm off its boss (washer) |
| Screws M2, M2.5 and heat-set inserts | assorted | pads, ears, deck, housings |
| Antenna tube | 1 | tail post |

Estimated bought-parts mass about 600 to 700 g; printed about 650 g (infill); total about 1.3 kg.

## Stock drivetrain candidates (Axial SCX10 III parts list AXI03007, read 2026-11-02)

Names and part numbers are from the parts list; **dimensions are not in it** and must be measured or taken from the product page before cases are drawn.

| Part no. | Name in the list | Use here |
|---|---|---|
| AXI232003 | 6-Bolt Heavy Duty Gear Set (30T ring / 8T pinion, per retailer listings) | front diff gears |
| AXI232002 | 6-Bolt Differential Locker | diff carrier / spool option |
| AXI232026 | AR45 Differential Cover | reference for the carrier width |
| AXI232027 / 232028 | AR45P Universal Axle Set / Straight Axle Shaft | diff outputs |
| AXI232031 | Internal Metal Drive Gears | gear pairs for the centre / rear split |
| AXI232033 | Input Metal Gears 27T, 20T and 34T | motor-side reduction |
| AXI232034 | 40T Metal Spur Gear | reduction stage |
| AXI232035 | Transmission Shaft Set | shafts |
| list p.8, p.11 | Bearings 5x11x4, 5x10x4, 5x13x4, 10x15x4, 15x21x4, 4x8x3 | the 5x11x4 seats already in the housings match |

No printed part is cut: housings are drawn around the stock gears and the chassis lengthens as needed.

## Centre differential (kept, decided 2026-11-02)

The centre diff stays so the front axle and the rear wheel never fight each other (front-mean to rear speed mismatch is 0.4 % at 5 deg, 1.4 % at 10 deg and 3.8 % at full lock, plus the 83 mm front / 112 mm rear tyre difference, which a fixed split cannot absorb).
- Build it from the same Axial 6-Bolt Heavy Duty Gear Set (AXI232003) as the front diff: one stock part number for both diffs.
- The Axial 6-Bolt Differential Locker (AXI232002) fitted to the centre diff gives a lockable "crawl" mode on demand.
- Torque split is 50:50 by default; the front/rear speed ratio no longer has to match the tyre diameters.

## Motor placement (decided 2026-11-02)

Hobbywing QuicRun Fusion SE (36 x 58.1 mm, 201 g, ESC built in) goes on the side opposite the driveline: shaft line and gear cases are at y +21, so the motor sits at y -21, high (z about 32) at the rear, which brings the sideways centre of gravity from 4.9 mm to about 1.4 mm (centre of gravity left of centre) and the front weight share from 60.6 % to about 59 %. It is also the only position where the fit check (WS03_FIT.md) found room for the can.
Consequence: the motor pinion can no longer mesh directly with the centre-diff ring (they are 42 mm apart in y), so the reduction needs a cross-over stage: see 'Belt cross-over' above (belt and countershaft).

### Battery moved beside the drive shaft (2026-11-03)

The 3S 1300 mAh pack (75 x 35 x 25) now lies at x -77.5..-2.5, y -37.5..-2.5, z -11..14 on a printed cradle (`w3_battery_tray`: 3 mm floor on two ribs, end stops, short side lips, two pairs of strap slots, two screws into the base plate on the centreline side, grooved around the frame tubes). The centreline is free for the lean servo and its tower, which is open under the servo window. The skin has open channels for the pack's swing path. CG y +0.7 mm (was +1.4), CG x -167.8, front share 62.7 %. A 105 mm 3S 2200 mAh pack fits nowhere (fit scan); it needs about 30 mm more free length between the diff case (x -80) and the nose frame nodes (x -5), i.e. the front end ahead of the diff 30 mm longer. Buy: 2 hook-and-loop or silicone battery straps, 10 mm wide.

### Lean coilovers (2026-11-07)

The two rigid lean rods are replaced by two small coilovers from the rocker tips to the arm lugs; the single INJS15 sets the lean (servo angle 1.013 deg per degree of lean, +-20.3 deg for +-20 deg), the shocks give spring and damping.

| part | qty | notes |
|---|---|---|
| Micro coilover shock, 3 mm eyes, eye to eye 51.5 mm compressed / 75.5 mm extended (24 mm stroke), spring about 8 mm OD, 25 g | 2 | stock part: any 1:10 / 1:12 aluminium 'short' shock with that length, or a Redcat/Axial 70 mm class shock shortened by 5 mm; fit with oil 30-35 wt |
| Spring, 3-6 N/mm (17-34 lb/in) | 2 | stiffer than stock RC springs (0.3-1.2 N/mm): see below |
| Shock oil 30-35 wt (50 cSt) | 1 | damps the arm swing |
| M3 bolts 10 mm + nylon nuts | 4 | rocker tips and arm lugs (the printed eye holes are 3.2 mm) |

Geometry (neutral): rocker axis x -82, z 34.5; tip radius 17.3 mm, V half angle 71.9 deg; eye to eye 68.5 mm at lean 0 (71 % extension), 67.9 to 69.9 mm over lean +-20 deg at any steer (steer does not move the lugs), so the shocks keep 13 mm of compression and 5 mm of extension in hand. Torque: holding 20 deg of lean against the weight takes 3.9 kg.cm at the servo (about 11.8 N in each shock), 4.5 times under the 17.7 kg.cm of the INJS15; spring rate 3 to 6 N/mm keeps the sag under about 2 to 4 mm, 1 N/mm is only workable with the servo closed-loop on an IMU.

### Belt cross-over (2026-11-03)

The motor (y -21, z 41) cannot mesh the centre-diff ring (axis y 21, z 0) directly: 58.7 mm apart, with the diff cases filling z < 22 from x -205 to -80, so no spur idler fits. Instead the motor shaft runs aft above the case (x -151 to -218, 4 mm, needs a bearing block on the cage: not yet drawn) to a 16T GT2 pulley at x -213; a 6 mm GT2 belt (about 190 mm, to be matched to the pulley pair) runs to a 40T pulley on a countershaft at y 21, z 24 (4 mm shaft, x -218..-197) whose 15T pinion meshes the ring. Ratio 2.5 : 1 from the pulleys; the stock pinion/ring then add 3 : 1. Buy: 16T and 40T GT2 pulleys (5 mm / 4 mm bore as fitted), one GT2 belt, two 4 mm bearings. Added mass about 24 g behind the CG: front share 62.6 %.

### Motor moved aft (2026-11-03)

For the single central lean servo the motor moved 22 mm aft: the can now spans x -151..-93 (y -21, z 41), shaft end at x -167. The cross-over stage to the centre-diff ring (x -199..-193, pinion mock at x -197..-189, y 14..27) now has 30 mm to cover along x instead of 52, and 42 mm in y. Front weight share 62.7 % (was 64.1 %), CG x -167.8. The receiver went to x -56..-32 to make room for the lean tower.

## Rear coilover mounts (printed, hoop version, 2026-11-03)

| part | where | notes |
|---|---|---|
| Shock hoop (in `w3_rear_arm`, same part) | two 13 mm legs from the arm's outer-plane top rail (u 55 and at the axle) up behind the tyre to a corner at x -440 / z 36 (8 mm over the tyre), then a 13 mm cross tube over the tyre to a lug plate with a bolt boss, 3.2 mm hole along y | PETG; prints with the lower boss on the bed (the arm part is now 66 mm tall in print, supports on); hoop swings with the arm |
| Shock upper lug (in `w3_frame_rear`, same part) | plate on the rear hoop's cross tube (R2 to C262) with a boss, 3.2 mm hole | left side only, inside the skin |

The rear bevel case, arm pivot, pivot pulley and the cage nodes R1 and FPR sit 30 mm further forward than the stretched position (`PIVOT_SHIFT` in `w3_stretch.py`), so the swing arm is 122 mm pivot to axle (was 93 mm). The arm's top rail is bent into an asymmetric up-caret: it rises 16 mm over the first 30 % of the arm from the pivot (apex) and falls back over the remaining 70 %, while the bottom rail and bottom lattice stay straight so the belt runs between them. One hoop leg starts at the apex, the other at the axle end. The cage's R1 to R2 rail now bends inboard and up through a waypoint node RW (above the bevel case, clear of the arm).

The shock sits at y 12, inside the body. Eye to eye over the travel (arm angle -9.4 to +11.8 deg, 20 mm droop to 25 mm bump): 79.5 mm at full droop, 70.3 mm at rest, 60.5 mm at full bump: about 61 % extended at rest, 0.5 mm spare at full droop, 5.5 mm before bottoming (`tests/test_w3.py::test_rear_shock_length`). The skin's floor and rear lip are slotted where the hoop, shock and swinging skin cross (the swing channels), as for the swing arm.

## Integrated build (ws03-integrated, 2026-11-07)

Merged: 450 mm wheelbase and 4 deg rake with the caret swing arm and hoop-mounted coilover (ws03-rear-shock), single INJS15 lean servo with rocker and tower, battery beside the drive shaft and motor at x -122 (servo branch), simplified skin, new wing, covered canopy and windscreen (skin branch), and the dead-plate cleanup (cleanup branch).
- Rear shaft block spans about x -205 to -347: buy 5 x 150 mm stock for the centre-to-rear-bevel shaft (nothing cut).
- Tyres: all three 112 x 62 per the latest decision; the 83 x 24 and 8 mm / 4 mm axle lines above are from the earlier layout and must be re-checked when the front wheel part is final.
- Printed mass 671 g, bought 1184 g, total about 1965 g; front weight share 63.8 %, CG x -162.9 mm, 53.1 mm above ground (WS03_MASS_CG.md).

## Drivetrain redraw around stock parts (ws03-drivetrain, 2026-11-07)

Full part table, assumptions, ratio chain and shaft lengths are in `WS03_DRIVETRAIN.md`; all dimensions are in `w3_stock.py`. Stock numbers in use: AXI232003 (x2),
AXI232002 (x1), AXI232034 (40T spur, x1), AXI232033 (two 27T), AXI232027/232028 axle shafts (diff outputs, length to be checked), 5 x 11 x 4 bearings,
Hobbywing HW30404317 (1800KV). The earlier "Spur gears module 0.8", "Bevel sets module 1.0" and belt cross-over rows no longer apply.

## Weight balance (ws03-balance)

Front share 63.0 % to 64.4 % (target 64 to 65 %; equal load on all three tyres would be 66.7 %), total 2262 g to 2294 g, CG x -166.7 to -160.4, y 1.1, z 12.7 to 10.8 (CG height above ground 54.2 to 52.3 mm). Ladder in `WS03_MASS_CG.md`, `python w3_mass.py`.

| Item | Qty | Notes |
|---|---|---|
| Tungsten alloy plate 40 x 20 x 3 mm (about 17.5 g/cc, 42 g) | 1 | nose ballast, fills the carrier cavity (40.6 x 20.6 x 3.6). Lead instead: 40 x 20 x 4.6 mm for 41 g, needs the cavity and carrier 1.2 mm deeper (`PLATE` in `parts/w3_balance.py`) |
| Ballast carrier + lid (`w3_ballast_carrier`, `w3_ballast_lid`, PETG, 8 g) | 1 + 1 | hangs under the front deck (x -50..-5, y -12.6..12.6, z -35.7..-29, about 25 mm above the ground), floor against the deck underside, lid faces down; 3M VHB tape on the floor plus 2 zip ties through the floor slots round the deck. Not in `w3_parts.all_parts` yet: the integrator adds `w3_balance.build(P)` |
| 3S pack 125 g (75 x 35 x 25) | 1 | was 120 g; no room to move it forward (fit scan: 1.5 mm) |

Assumptions to weigh: small masses (85 g) now placed from an inventory (`MISC_ITEMS` in `w3_mass.py`); wing and tail print at 8 % infill (slicer setting). Optional: a rear tyre insert 15 g lighter would add +0.4 points.
