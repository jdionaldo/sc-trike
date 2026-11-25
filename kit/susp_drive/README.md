# Fugu suspension + drivetrain kit (Version 1, wishbone front end)

Front wishbone suspension, lean head, knuckles, steering, stops, rear swing arm, belt drive, motor plate, bearings, axles, wheels and tyres. 28 printed files on 6 plates, 19.2 h and 604 g by the Bambu Studio slice check (0 problems; the options plate, printed tie rods ST3L/R, is included: skip it on the steel path). Bought parts 506.47 USD as listed on 2026-11-24 (11 rows VERIFIED, 18 ASSUMED, 7 UNKNOWN). Nothing bought.

## Stated openly

- Cage boss spots at safety 1.48 (target 2): OPEN, outside this kit but the cage carries the rear shock top.
- No lean stop: lean turns both arms at once, so a stop on one arm cannot sense it; it needs a lean link or a balance beam (owner decision).
- Rear travel: now pose-checked by `tools/rear_check.py` from -15 mm droop to +20 mm bump at the axle (arm -7.1 to +9.4 deg): 0 overlaps; the arm comes within 0.05 mm of the tail deck at -15 mm (it would act as the droop stop, not designed as one). The shock changes length -6.5 / +5.9 mm over that range; the chosen rear shock's stroke is not read from its listing.
- Not printed: nothing in this kit has been printed, fitted or driven. Every fit above comes from the model.
- Wishbone pivot shoulder screws: the M5 end has no designed nut seat; an M5 into the printed front post would break the no-printed-threads-below-M6 rule.
- Heave shock: the chosen RC4WD 70 mm is discontinued, 4.5 mm longer than the model's 68 mm, has a 3.0 mm eye (model pin hole D4.1) and no stated spring rate (about 30 N/mm needed).
- Ring and pinion: the model's ring stand-in (25.6 mm OD) is smaller than a 30T SCX10 ring: check the carrier cavity against the real ring before printing DT7/DT8.
- Rear hub: no 12 mm hex hub with an 8 mm bore was found.
- Generic hardware (ball studs, cups, tie rods, shafts, rings, shims) has estimated prices; McMaster / Misumi pages could not be read by the sourcing run.
- TPU parts are sliced with the PETG profile of the saved project (no TPU profile in it): their time and grams are ASSUMED; switch the filament to TPU 95A in Studio.

## 1. Bought parts

Quantities are counted from the model (`Where` names its stand-in parts). Total = packs to buy x pack price. Retailer notes: `../sourcing_2026-11-24.md`.

| Item | Qty | Where (model) | Part / retailer | Unit USD (pack) | Packs | Total USD | Status | Note |
|---|---|---|---|---|---|---|---|---|
| Heave shock 70 mm (one shock between the upper wishbones) | 1 | Heave shock pins in the forks of SU2 (model: 68 mm eye to eye, about 10 mm stroke, about 250 N at full bump) | RC4WD Ultimate Scale Shock 70 mm RC4Z-D0004, Hobby ETC https://store.hobbyetc.com/parts/view/29506 (alt. RC4WD King 70 mm RC4ZD0037, AMain) | 20.99 (2) | 1 | 20.99 | VERIFIED | listing: 72.5 mm extended / 55.1 compressed, stroke 17.4 mm, eye bore 3.0 mm, body 8.8 mm; DISCONTINUED, not oil filled, very soft spring: no listing gives a spring rate (30 N/mm needed); 4.5 mm longer than the model's 68 mm, eye bore 3.0 against the model's 4.1 mm pin hole |
| Heave shock pin: M3 x 20 socket screw + M3 nylock (eye bore 3.0 of the chosen shock) | 2 | shock eyes in the forks of SU2 (model hole D4.1 for an M4 pin) | generic ISO 4762 M3 x 20 + DIN 985 M3 | 0.30 (1) | 2 | 0.60 | ASSUMED | est. price; with an M3 pin the fork hole D4.1 is 1.1 mm loose: sleeve 4 x 3 mm or shrink the hole when the shock is chosen |
| Wishbone pivot: shoulder screw ISO 7379, D6 x 45 shoulder, M5 thread | 4 | Pivot rod upper/lower x 2 sides through the lean head SU1 and the arms SU2/SU3 (model rod D6 x 48.7) | Zoro ZR1846-303H (6 x 45, M5, 18-8 SS) https://www.zoro.com/ampg-smooth-hd-skt-shld-scrw-6m5x45-18-8ss-zr1846-303h/i/G0819452 | 15.39 (1) | 4 | 61.56 | ASSUMED | page refused automated fetch (price from the search result); FIXING OPEN: the M5 end would thread into the printed front post (no printed threads below M6): an M5 nylock in front of the post needs about 6 mm of free space that is not checked |
| Ball joint: M3 rod end with its own 6.8 mm steel ball (matched pair), the ball held by an M3 screw | 4 | Ball stud upper/lower x 2 (ball on the knuckle plate) + Rod end upper/lower x 2 (cup on the wishbone tips) | Gmade GMA20216 M3 Rod End w/ 6.8mm Steel Ball (10), Hobby Recreation Products https://www.hobbyrecreationproducts.com/collections/gmade-komodo-kit/products/gma20216-m3-rod-end-w-6-8mm-steel-ball | 12.00 (10) | 1 | 12.00 | VERIFIED | listing opened 2026-11-25: M3 rod end and 6.8 mm steel ball sold together (OUT OF STOCK); one pack covers all 8 joints (4 arm, 4 steering). Replaces the separate stud + cup rows (the cups found earlier took 6.92 mm balls). Alt.: Xray 352659 6.8 mm M3 studs with Xray 352664 / 352665 6.8 mm composite ball joints, both VERIFIED on xray / redrc pages, but those cups are M4: arm tips and tie rods would need M4 |
| M3 x 16 socket screw (through the hollow 6.8 mm ball into the knuckle insert) | 4 | Ball stud upper/lower x 2 | generic ISO 4762 | 0.10 (1) | 4 | 0.40 | ASSUMED | est.; length to suit the ball height (not stated on the listing): thread 8-12 mm into the insert set 7.5 mm behind the plate face |
| M3 threaded rod 25 mm (or M3 x 25 set screw) for the arm tip cups | 4 | apex boss of each wishbone SU2/SU3 | generic | 0.20 (1) | 4 | 0.80 | ASSUMED | est. |
| Heat-set insert M3, OD 4.6 x 4 mm | 16 | knuckles 2 x 2 (arm studs, set from the back), arm tips 4, lean head base 4, droop stops 2 x 2 | Adafruit 4255 M3 x 4 brass (OD 4.2), 50 pack https://www.adafruit.com/products/4255 | 5.95 (50) | 1 | 5.95 | VERIFIED | listing OD 4.2 mm: the model pockets are D4.2 for OD 4.6 inserts, so with this insert shrink the pockets to D3.8 or buy OD 4.6 (RS PRO 204-0616, not opened); arm tip bores are D4.1 |
| Countersunk screw M3 x 10 (ISO 10642) | 8 | lean head SU1 to the front deck 4, droop stops SU5 to the deck 2 x 2, all from below into inserts | generic | 0.10 (1) | 8 | 0.80 | ASSUMED | est. |
| Front wheel bearing 6x12x4 (MR126) | 4 | Wheel bearing inner/outer x 2 in the printed front wheels DT16 (seats D12.1 x 4) | MR126-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/131896 | 10.99 (10) | 1 | 10.99 | VERIFIED | rubber sealed |
| Shim 6 x 8 x 0.5 mm (inner race only) | 4 | Axle shim inner/outer x 2: knuckle boss face and under the axle nut | generic RC shim 6 x 8 | 0.25 (1) | 4 | 1.00 | UNKNOWN | est.; no listing found |
| Front stub axle: M6 x 60 hex bolt ISO 4014 (18 mm thread) cut to 48 mm + M6 nylock DIN 985 | 2 | Axle pin x 2: x 118.6..166 in the knuckle boss SU4, the bearings on the shank | generic | 0.60 (1) | 2 | 1.20 | ASSUMED | est.; room for the bolt head inboard of the knuckle boss is not checked; snug the nylock only until the wheel turns freely with no play |
| Low-profile steering servo 40.8 x 20.2 x 26.5 mm, 25T | 1 | Steer servo in ST2 | AGFRC B44BLS V2, Amazon B07L83M8SM | 44.95 (1) | 1 | 44.95 | ASSUMED | page not opened today (503/429): price and backorder from the search result; size VERIFIED on 2026-11-18 |
| Servo horn screw (with the servo) | 1 | ST1 on the servo shaft | supplied with the servo | 0.00 (1) | 1 | 0.00 | ASSUMED | HORN_METAL option (metal 25T horn) is prepared in the model, off |
| Ball joint for the steering (in the same Gmade GMA20216 pack as the arm joints) + M3 x 20 screw through the ball, nylock | 4 | Steer stud knuckle x 2, Steer stud horn x 2 | Gmade GMA20216 (pack counted in the SU row); M3 x 20 ISO 4762 | 0.10 (1) | 4 | 0.40 | ASSUMED | screw est.; the 6.8 mm ball sits on the steering arm / horn, the screw passes through (D3.3) and takes the nylock |
| M3 nylock nut DIN 985 | 4 | Steer stud nut knuckle x 2, Steer stud nut horn x 2 | generic | 0.05 (1) | 4 | 0.20 | ASSUMED | est. |
| Tie rod M3 turnbuckle with two ball cups, 93 mm ball to ball | 2 | Tie rod x 2, horn to knuckle | generic M3 turnbuckle 1/10 RC | 3.00 (1) | 2 | 6.00 | UNKNOWN | est.; no listing opened |
| Self-tapping screw M2.5 x 10 (servo ears) | 4 | servo ears into the ST2 pillars | generic | 0.05 (1) | 4 | 0.20 | ASSUMED | est. |
| Motor + ESC 2-in-1, 540, 1800KV | 1 | b motor on the motor plate CH5 | Hobbywing QuicRun Fusion SE HWI30404317, Horizon Hobby https://www.horizonhobby.com/product/quicrun-fusion-se-for-crawler-540spec-1800kv/HWI30404317.html | 89.99 (1) | 1 | 89.99 | VERIFIED | in stock on the listing |
| Motor pinion 32P 15T, 1/8 in (3.175 mm) bore, steel | 1 | b motor pinion | ServoCity 15T 1/8 in bore 32P steel https://www.servocity.com/15t-0-125-1-8-bore-32p-shaft-mount-pinion-gear-steel | 5.99 (1) | 1 | 5.99 | VERIFIED | set screw not listed |
| Spur gear 32P 40T, 5 mm bore | 1 | b spur gear on the front end of the rear shaft (model D33) | Yeah Racing AXSC-034 40T hardened steel (5 mm shaft), alt. Axial AXI-3860 40T | 14.99 (1) | 1 | 14.99 | ASSUMED | both DISCONTINUED; 15T/40T meshes at 21.8 mm: the motor plate slots (MESH_SLOT +-1 mm) cover 21.5..23.5; a 42T 5 mm-bore spur was not found |
| Ring and pinion, steel (90 deg drive, rear shaft to cross shaft) | 1 | b rear ring on the ring hub DT10, pinion on the rear shaft end | Axial AXI232003 30T / 8T, https://www.axialadventure.com/product/AXI232003.html | 19.99 (1) | 1 | 19.99 | ASSUMED | DISCONTINUED, bores not listed; MISMATCH: the model's ring stand-in is 25.6 mm OD, a 30T SCX10 ring is larger: the carrier DT7/DT8 cavity must be checked against the real ring |
| Rear drive shaft, 5 mm hardened steel, 112 mm | 1 | b rear shaft front + b rear shaft (y -2.5..109.4), in 3 bearings | generic 5 mm linear shaft (McMaster / Misumi, cut) | 8.00 (1) | 1 | 8.00 | UNKNOWN | est.; listing not readable here |
| Cross (pivot) shaft, 5 mm hardened steel, 88 mm | 1 | x -10..78 through the carriers DT7/DT8, ring hub DT10, pivot pulley DT14 and the 3 pivot plates of DT11 | generic 5 mm linear shaft (cut) | 8.00 (1) | 1 | 8.00 | UNKNOWN | est.; no stand-in in the model (bore line probed) |
| Rear axle, 8 mm hardened steel, 100 mm | 1 | mock rear axle (x -24..76) in DT11, axle pulley DT15, rear hub | VXB 8 x 100 mm HRC60, 5 pcs https://vxb.com/products/8mm-100mm-hardened-linear-motion-shafts | 49.93 (5) | 1 | 49.93 | VERIFIED | price label ambiguous on the page (49.93 / 80.00) |
| Bearing 5x11x4 (MR115) | 8 | rear shaft: pillow block DT5/DT6 1, carrier DT7/DT8 2; cross shaft: carrier 2, swing arm pivot plates 3 | MR115-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/130884 | 11.49 (10) | 1 | 11.49 | VERIFIED | seat D11.1 |
| Bearing 8x16x5 (688) | 2 | rear axle in the swing arm DT11 (seats D16.1 x 5) | 688-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/131894 | 10.99 (10) | 1 | 10.99 | VERIFIED |  |
| Retaining ring DIN 471, 5 mm and 8 mm | 6 | 2 on the cross shaft, 2 on the rear shaft, 2 on the rear axle | generic assortment | 6.00 (100) | 1 | 6.00 | UNKNOWN | est.; no listing opened |
| Rear hub, 12 mm hex, 8 mm bore | 1 | mock rear hub: axle to the rear wheel DT17 | Axial AXI232046 12 mm hex hub (bore not listed) https://store.hobbyetc.com/parts/view/159353 | 11.99 (1) | 1 | 11.99 | UNKNOWN | no 8 mm-bore 12 mm hex hub found: bore a 12 mm hex hub out to 8 mm (2 mm wall) with a grub on an axle flat, or redesign the hub |
| GT2 closed-loop belt 2GT-300, 6 mm wide (150 teeth) | 1 | b gt2 belt r: pivot pulley DT14 26T to axle pulley DT15 30T | generic 2GT-300-6 | 7.50 (1) | 1 | 7.50 | ASSUMED | est.; listing 404; centre distance 122.1 gives 300.2 mm: no slack |
| Grub screw M3 x 4 | 2 | one in each printed pulley hub DT14, DT15 | generic ISO 4029 | 0.10 (1) | 2 | 0.20 | ASSUMED | est. |
| Rear shock 100 mm class, oil | 1 | Rear shock between the cage clevis and the arm bridge | Integy C26651RED (pair) https://integy.shop/products/rock-crawlers-hop-up-parts-c26651red | 36.99 (2) | 1 | 36.99 | ASSUMED | page refused (429): price from search; eye-to-eye, stroke and eye bore not read; model eye bore M6 |
| Shock bolt M6 + M6 nylock: M6 x 30 (lower), M6 x 35 (upper) | 2 | M6 shock pin (lower), M6 shock pin | generic ISO 4762 + DIN 985 | 0.50 (1) | 2 | 1.00 | ASSUMED | est.; lengths from the model clevis spans 20.8 / 24.0 mm |
| Socket screw M3 x 6 (motor face) and M3 x 10 (plate to deck) | 4 | 2 into the motor on a 25 mm pattern, 2 through the plate gussets into the deck | generic | 0.10 (1) | 4 | 0.40 | ASSUMED | est. |
| Screws for the pillow block and bearing carrier halves | ? | DT5/DT6 and DT7/DT8 to the decks | generic M3 | 0.10 (1) | 0 | 0.00 | UNKNOWN | count not taken from the traced carrier meshes |
| Front tyre 1.9 in, about 112 mm OD | 2 | mock tire x 2 on the printed wheels DT16 (bead seat 48.3) | Pro-Line Toyo Open Country R/T G8 1.9 PRO1021114 (pair) https://www.axialadventure.com/product/1-10-toyo-open-country-r-t-g8-f-r-1.9-rock-crawling-tires-2/PRO1021114.html | 24.99 (2) | 1 | 24.99 | VERIFIED | 113 x 38 mm; DISCONTINUED; alt. RC4WD Scrambler RC4ZT0144 104 x 43 (backorder); the model's tyre envelope is 62 mm wide |
| Rear tyre 2.2 in, about 140 mm OD | 1 | Rear tire on the printed wheel DT17 (bead seat 55.9) | RC4WD Mud Slinger 2 XL 2.2 RC4ZT0122 (pair, with foams) https://www.amainhobbies.com/rc4wd-mud-slinger-2-xl-2.2-scale-crawler-tires-2-rc4zt0122/p-qtqrtarqbc2xactz | 29.99 (2) | 1 | 29.99 | VERIFIED | 139.7 x 53.5 mm, ID 55.5 (0.4 mm tight on the bead seat); backorder; the model's tyre envelope is 62 mm wide |
| **Total** | | | | | | **506.47** | | |

## 2. Printed parts

Every file is oriented and packed: do not auto-orient in Bambu Studio. L/R parts have their own IDs (L = -x side, the left seen from behind).

| ID | Part | Material | Walls | Infill | Support | Face on the bed | Size mm | Plate |
|---|---|---|---|---|---|---|---|---|
| SU5L | Droop stop (L) | PETG | 4 | 60% | auto | model +x down | 10 x 23 x 14 | Front suspension and steering (PETG) |
| SU5R | Droop stop (R) | PETG | 4 | 60% | auto | model -x down | 10 x 23 x 14 | Front suspension and steering (PETG) |
| SU6L | Droop stop pad (L) | TPU 95A | 3 | 100% | off | model +y down | 6 x 10 x 8 | Stops (TPU 95A) |
| SU6R | Droop stop pad (R) | TPU 95A | 3 | 100% | off | model +y down | 6 x 10 x 8 | Stops (TPU 95A) |
| SU7 | Heave bump stop | TPU 95A | 3 | 100% | off | model +x down | 12 x 12 x 6 | Stops (TPU 95A) |
| SU4L | Knuckle (L) | PETG | 6 | 80% | auto | model -y down | 48 x 46 x 86 | Front suspension and steering (PETG) |
| SU4R | Knuckle (R) | PETG | 6 | 80% | auto | model -y down | 48 x 46 x 86 | Front suspension and steering (PETG) |
| SU1 | Lean head | PETG | 6 | 60% | auto | model +x down | 63 x 48 x 68 | Front suspension and steering (PETG) |
| SU3L | Lower wishbone (L) | PETG | 6 | 60% | auto | model +z down | 88 x 57 x 12 | Front suspension and steering (PETG) |
| SU3R | Lower wishbone (R) | PETG | 6 | 60% | auto | model +z down | 88 x 57 x 12 | Front suspension and steering (PETG) |
| ST1 | Steering horn | PETG | 6 | 100% | off | model +z down | 24 x 63 x 16 | Front suspension and steering (PETG) |
| ST2 | Steering servo mount | PETG | 4 | 30% | auto | model -x down | 22 x 55 x 27 | Front suspension and steering (PETG) |
| ST3L | Tie rod, printed (option) (L) | PETG | 6 | 100% | off | model +z down | 73 x 8 x 8 | Options (PETG, print only if you take the printed path) |
| ST3R | Tie rod, printed (option) (R) | PETG | 6 | 100% | off | model +z down | 73 x 8 x 8 | Options (PETG, print only if you take the printed path) |
| SU2L | Upper wishbone (L) | PETG | 6 | 70% | auto | model -z down | 89 x 58 x 38 | Front suspension and steering (PETG) |
| SU2R | Upper wishbone (R) | PETG | 6 | 70% | auto | model -z down | 89 x 58 x 38 | Front suspension and steering (PETG) |
| DT15 | Rear axle pulley 30T GT2 (6 mm belt) | PETG | 6 | 100% | off | model -x down | 21 x 21 x 13 | Drivetrain and wheels (PETG) |
| DT14 | Rear pivot pulley 26T GT2 (6 mm belt) | PETG | 6 | 100% | off | model -x down | 18 x 18 x 13 | Drivetrain and wheels (PETG) |
| CH5 | Motor plate | PETG | 4 | 40% | auto | model +x down | 46 x 21 x 60 | Drivetrain and wheels (PETG) |
| DT5 | Pillow block lower | PETG | 4 | 60% | auto | model -x down | 22 x 15 x 30 | Drivetrain and wheels (PETG) |
| DT6 | Pillow block upper | PETG | 4 | 60% | auto | model -x down | 22 x 15 x 30 | Drivetrain and wheels (PETG) |
| DT7 | Rear bearing carrier lower | PETG | 4 | 50% | auto | model -x down | 25 x 66 x 34 | Drivetrain and wheels (PETG) |
| DT8 | Rear bearing carrier upper | PETG | 4 | 50% | auto | model -x down | 25 x 66 x 34 | Drivetrain and wheels (PETG) |
| DT11 | Rear swing arm | PETG | 6 | 60% | auto | model +x down | 79 x 150 x 90 | Drivetrain and wheels (PETG) |
| DT10 | Rear ring hub | PETG | 4 | 80% | auto | model +x down | 22 x 22 x 9 | Drivetrain and wheels (PETG) |
| DT16L | Front wheel 1.9 in, 6-spoke (L) | PETG | 6 | 60% | off | model +x down | 53 x 53 x 34 | Drivetrain and wheels (PETG) |
| DT16R | Front wheel 1.9 in, 6-spoke (R) | PETG | 6 | 60% | off | model -x down | 53 x 53 x 34 | Drivetrain and wheels (PETG) |
| DT17 | Rear wheel 2.2 in, 6-spoke | PETG | 6 | 60% | off | model -x down | 61 x 61 x 46 | Drivetrain and wheels (PETG) |

Print or buy: every mechanical part has a printed version, a metal version or both: `print_or_buy.md`. Machinable interfaces of the parts with no stock metal version: `interfaces.md`.
Edge breaks: every part above that moves or carries a moving joint has 0.6 mm chamfers on its outside edges and 0.4 mm on every bore, pocket and insert entry (gear and pulley teeth excepted, CHAMFER_MOVING in model.py).

## 3. Plates (Bambu Studio slice check, P2S profile of the saved project, 0.4 mm nozzle)

Open `bambu/all_plates.3mf` or one plate file. PETG in AMS slot 4; the TPU plate needs TPU 95A (external spool, not through the AMS).

| Plate file | Time | Grams | Slice check |
|---|---|---|---|
| plate_01_Front_suspension_and_steering_1.3mf | 7.2 h | 232 | OK |
| plate_01_Front_suspension_and_steering_2.3mf | 0.1 h | 2 | OK |
| plate_02_Drivetrain_and_wheels_1.3mf | 10.4 h | 323 | OK |
| plate_02_Drivetrain_and_wheels_2.3mf | 1.3 h | 39 | OK |
| plate_03_Stops.3mf | 0.1 h | 1 | OK |
| plate_04_Options.3mf | 0.2 h | 6 | OK |
| **Total** | **19.2 h** | **604** | 0 problems |

## 4. Tools

- Soldering iron with an insert tip (heat-set inserts)
- Bench vise or arbor press and sockets 11 / 12 / 16 mm (bearings, outer race only)
- Hex keys 1.5 / 2 / 2.5 / 3 / 4 mm, 5.5 and 10 mm nut drivers, 6 mm drill (hand reaming)
- Circlip pliers (DIN 471 5 and 8 mm), hacksaw and file (cut the axle bolt and shafts)
- Blue thread locker (metal threads only), CA glue for TPU

## 5. Fits and torque

- Bearing seats are printed at OD + 0.1 mm (D11.1 for 5x11x4, D12.1 for 6x12x4, D16.1 for 8x16x5): a light press fit in PETG. Press on the outer race only, never on the shield.
- Pin and rod bores: arms D6.2 on 6 mm shoulder screws (0.2 mm running clearance, ream by hand); lean head posts D6.1; knuckle axle boss D6.1 on the 6 mm stub axle; arm and carrier bores beside a bearing D5.4-5.6 (shaft does not touch).
- Heat-set inserts: pockets D4.2 x 5 for OD 4.6 x 4 inserts (Adafruit 4255 is OD 4.2: use OD 4.6 inserts or shrink the pockets).
- Torque: printed parts take snug-plus-a-quarter-turn, not a torque value: M3 into inserts about 0.5 N m, M3 nylocks on ball studs until the stud stops turning, M6 axle nylock until the play is gone (the wheel must still spin), M6 shock bolts snug (eyes must turn). Thread locker (blue, medium) on metal-to-metal threads only (grubs on shaft flats, ball studs in metal), never on threads in PETG or PLA.

## 6. Assembly (in this order)

### 0. Test fit (do this first)

Print knuckle SU4R and the steering horn ST1 alone. Press an MR126 bearing into the wheel DT16 hub with a vise and a socket on the outer race (seat D12.1): it must go in with firm hand pressure; if it falls in, the seat is loose (print the wheel 0.1 mm smaller in X/Y compensation); if it cracks the hub, stop. Press one M3 insert, screw a ball stud in, snap a cup on.

Hardware: 1 x MR126, 1 x M3 insert, 1 ball stud + cup.

Check: bearing flush and square, stud tight, cup turns 20 deg without binding.

### 1. Lean head on the deck

Insert 4 M3 inserts into the base tubes of the lean head SU1 (soldering iron, 220 C, straight). Screw SU1 to the front deck from below.

Hardware: 4 x M3 insert, 4 x M3 x 10 countersunk.

Check: head sits flat, no rocking.

### 2. Wishbones

Ream the arm pivot bores (D6.2) of SU2 L/R and SU3 L/R with a 6 mm drill by hand until a 6 mm shoulder screw slides through without play. Push the four shoulder screws in from the rear through the head's rear post, the arm barrel and the front post. Insert M3 inserts in the arm tips (D4.1 bore: heat the insert slowly) and screw the M3 rods and ball cups on.

Hardware: 4 x shoulder screw 6 x 45 M5, 4 x M3 insert, 4 x M3 rod 25, 4 x ball cup.

Check: each arm swings 10 deg up and down by its own weight. OPEN: the M5 end of the shoulder screw has no designed nut seat (see open items).

### 3. Knuckles

Set 2 M3 inserts from the back into each knuckle SU4 L/R (pockets 7.5 mm deep behind the boss face). Screw the ball studs into them from the front. Snap the arm cups onto the studs (upper arm to the upper stud).

Hardware: 4 x M3 insert, 4 x ball stud.

Check: the knuckle turns 25 deg each way and rises with the arms without binding.

### 4. Front wheels

Press two MR126 bearings into each wheel DT16 (one from each end, outer race only). Slide a 6x8 shim onto the stub axle bolt, push the bolt through the knuckle boss from the inside, put the wheel on, the second shim, and the M6 nylock. Tighten the nylock only until the wheel has no play and still spins freely (about 1/4 turn after contact). Fit the tyre (glue or beadlock as the tyre requires).

Hardware: 4 x MR126, 4 x shim 6x8x0.5, 2 x M6 x 60 cut to 48 + nylock, 2 x front tyre.

Check: wheel spins 3 s or more from a flick; no axial play.

### 5. Heave shock and stops

Push the TPU bump stop SU7 over the heave shock shaft onto the eye neck. Mount the shock between the forks of SU2 with M3 x 20 + nylock (snug, the eye must turn). Glue the TPU pads SU6 L/R into the droop stops SU5 L/R (CA for TPU or contact cement), press 2 inserts in each stop and screw them under the lower arm roots from below.

Hardware: 1 heave shock, 2 x M3 x 20 + nylock, 4 x M3 insert, 4 x M3 x 10.

Check: push one wheel up 12 mm with the body leaned 10 deg: the bump stop meets the shock body; let it drop 8 mm: the lower arm meets the pad.

### 6. Steering

Screw the servo mount ST2 to the deck, stand the servo in it (4 x M2.5 self tapping into the pillars), centre the servo (1500 us) and fit the horn ST1 straight across. Put the ball studs through the horn ends (from below, nylock on top) and through the knuckle steering arms (from below, nylock under). Tie rods, steel path (default): Secraft SEC349 M3 turnbuckle 80 mm with a ball cup on each end; printed path: tie rod ST3L / ST3R from the options plate, one M3 insert pressed into each end collar, a ball cup screwed into each insert. Set both to 93 mm ball to ball and snap them on.

Hardware: 1 servo, 4 x M2.5 x 10, 4 x ball stud, 4 x M3 nylock, 2 x tie rod.

Check: at full servo throw the wheels steer about 22.5 deg inside / 19 deg outside, the same both ways; nothing touches the arch liners.

### 7. Rear drive shaft and carriers

Press MR115 bearings into the lower halves of the pillow block DT5 (1) and the rear bearing carrier DT7 (2 on the rear shaft, 2 on the cross shaft). Slide the spur gear onto the front end and the 8T pinion onto the rear end of the 5 mm rear shaft, lay it into the bearings; lay the cross shaft with the ring gear on the ring hub DT10 into its two bearings; check the mesh (slight backlash), then close with the upper halves DT6 / DT8.

Hardware: 5 x MR115, rear shaft 5 x 112, cross shaft 5 x 88, spur 40T, ring and pinion, ring hub DT10, 2 x DIN 471 5 mm.

Check: turning the spur by hand turns the cross shaft smoothly with no tight spot over a full ring turn.

### 8. Motor

Screw the motor to the motor plate CH5 (2 x M3 x 6, 25 mm pattern) with the 15T pinion (grub on the shaft flat). Set the mesh with a strip of paper between the gears, slide the motor in its slots, tighten. Screw the plate gussets to the deck (2 x M3).

Hardware: Fusion SE motor/ESC, 15T pinion, 4 x M3.

Check: paper strip comes out with a gear-tooth print but not torn; gears turn with a little backlash.

### 9. Rear swing arm

Press MR115 bearings into the three pivot plates of DT11 (faces toward the drive block) and the two 688 bearings into the axle plates (faces toward the pulley). Fit the 26T pulley DT14 on the cross shaft between the arm plates and slide the arm onto the cross shaft; DIN 471 rings at both ends. Put the 8 mm axle through the outer plate, the 30T pulley DT15 (belt on both pulleys first) and the inner plate; ring it. Fit the rear hub and the wheel DT17 with the rear tyre.

Hardware: 3 x MR115, 2 x 688, axle 8 x 100, belt 2GT-300, 2 x M3 x 4 grub, 4 x DIN 471, rear hub, rear tyre.

Check: arm swings freely through its full travel with the belt on; belt deflects about 3 mm under a finger; wheel turns when the spur is turned.

### 10. Rear shock

Bolt the shock between the cage clevis (M6 x 35) and the arm bridge (M6 x 30), nylocks snug.

Hardware: rear shock, M6 x 30, M6 x 35, 2 x M6 nylock.

Check: compress the rear by hand to the bump stop of the shock: the tyre does not touch the shell or the cage.
