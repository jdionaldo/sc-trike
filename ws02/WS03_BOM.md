# WS-03 bill of materials (bought parts)

All sizes below are assumptions from the 1/10 and 1/18 RC parts we planned around. Verify against the real parts before buying.

| item | qty | notes |
|---|---|---|
| Servo, 12 kg short body 40 x 20 x 19.3 | 4 | lean x2, steer x2; 49 mm flange screw spacing assumed, 120 deg travel assumed |
| Servo horn, 28 mm (lean) and 12 mm (steer) | 2 + 2 | aluminium horns, M2 ball studs |
| Motor 2830 about 1400 KV, 3.17 mm shaft | 1 | 16 mm mounting pattern |
| ESC 60 A, 46 x 38 x 33 | 1 | sits above the battery |
| LiPo 2S/3S about 62 x 20 x 14 | 1 | in the nose bay |
| Receiver 6 ch with mixing | 1 | lean, steer, throttle mixes |
| Spur gears module 0.8: 15T pinion, 45T diff ring | 1 + 1 | centre distance 24 mm |
| Spur gear diff (45T ring) | 1 | centre diff, axis along the body |
| Bevel sets module 1.0, 12T pinion / 30T ring | 2 | front diff and rear bevel case |
| Bevel gear diff carrier (front), outputs 5 mm | 1 | ring on the +y end |
| Shafts 5 mm (about 40, 55, 52 mm) and 5 mm output stubs | 5 | front pinion, rear, outputs |
| Bearings 5 x 11 x 4 | about 14 | every shaft seat and arm pivot |
| Bearings 4 x 8 x 3 | 4 | arm tip and carrier |
| Bearing 8 x 16 x 5 | 2 | rear axle |
| GT2 3 mm belts and pulleys | 4 belts | front 20T to 16T (x2), rear 20T to 22T (x1), spare |
| Dogbone / CVD with universal joint on the kingpin axis | 2 | about 25 mm lateral room |
| Wheels: skinny off-road 83 x 24 (front) | 2 | 4 mm axle |
| Wheel: thick off-road 112 x 62 (rear) | 1 | 8 mm axle, 8 mm hex |
| Axle 8 mm (rear), 4 mm (front, tip shafts) | 1 + 4 | |
| Pins 3 mm steel (kingpins, link pivots) | 8 | |
| Ball studs / rod ends M2 | 8 | tie rods and lean rods |
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
Consequence: the motor pinion can no longer mesh directly with the centre-diff ring (they are 42 mm apart in y), so the reduction needs a cross-over stage (a pinion on a short cross shaft, or two idlers) when the gearbox is redrawn around the stock Axial gears.

## Rear coilover mounts (printed, hoop version, 2026-11-03)

| part | where | notes |
|---|---|---|
| Shock hoop (in `w3_rear_arm`, same part) | two 13 mm legs from the arm's outer-plane top rail (u 55 and at the axle) up behind the tyre to a corner at x -440 / z 36 (8 mm over the tyre), then a 13 mm cross tube over the tyre to a lug plate with a bolt boss, 3.2 mm hole along y | PETG; prints with the lower boss on the bed (the arm part is now 66 mm tall in print, supports on); hoop swings with the arm |
| Shock upper lug (in `w3_frame_rear`, same part) | plate on the rear hoop's cross tube (R2 to C262) with a boss, 3.2 mm hole | left side only, inside the skin |

The shock sits at y 12, inside the body. Eye to eye over the travel (arm angle -12.4 to +15.5 deg, 20 mm droop to 25 mm bump): 79.5 mm at full droop, 70.9 mm at rest, 60.5 mm at full bump: about 64 % extended at rest, 0.5 mm spare at full droop, 5.5 mm before bottoming (`tests/test_w3.py::test_rear_shock_length`). The skin's floor and rear lip are slotted where the hoop, shock and swinging skin cross (the swing channels), as for the swing arm.
