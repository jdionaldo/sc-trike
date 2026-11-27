# Print or buy, part by part (suspension + drivetrain kit)

The owner asked to "make sure i can either print this whole kit or use a steel part that i can buy off the shelf".

**Scope.** Every mechanical part of `kit/susp_drive` is listed below. The metal parts come from listings opened on 2026-11-24 (nothing was bought). Full notes are in `../sourcing_2026-11-24.md` and in the sourcing file for the steel parts, which is copied here as `steel_parts_2026-11-24.md`.

**Status words:**
- VERIFIED: the listing was opened and the dimension that matters was read.
- ASSUMED: the listing was opened but a dimension is missing.
- NOT OPENED: the retailer refused the fetch; only the search result was seen.

**Paths.**
- **Both:** a printed and a metal version, with the same interface.
- **Print only:** no stock metal part fits. A machined part needs `interfaces.md`.
- **Buy only:** the part cannot be printed safely.

## Both paths (printed or metal, same interface)

| Part | Printed version | Off-the-shelf metal version | Interface (both) | Status |
|---|---|---|---|---|
| Tie rod (2) | ST3L / ST3R, options plate. PETG body D7 with D7.8 x 6 end collars, one M3 insert each (cup shank clearance D4.0 x 13). Strength (hand calculation, below): safety 8.1 at the servo's stall load. front_check with the printed rods (PRINTED_TIE=1): 0 overlaps at rest and in the poses, nothing under 1 mm outside the whitelist (a D9 collar came 0.47 mm from the cage, hence D7.8) | Secraft SEC349 SUS303 M3 turnbuckle, 80 mm, R/L thread, rod 5.0 mm, 15 mm thread each end. https://macgregor.co.uk/secraft/SEC349.htm (pack of 2, price not on the page). Alt. Gator RC M3 titanium turnbuckle 80 mm, $8.99 for 2 | 93 mm ball centre to ball centre, M3 ball cups for 6.8 mm balls on both ends | metal VERIFIED (length, thread); printed passes 2 by hand calculation, not FEM |
| Steering horn (1) | No longer a print option: the fully printed horn's 25T spline shears at the servo's stall torque (hand check: about 17 MPa on D5.1 x 4.3, safety about 0.6). Kept in `../do_not_print/` only | Buy the aluminium 25T arm Hot Racing SH25TH01 ($10.88, HobbyETC, opened 2026-11-25: M3 holes at 16 and 20 mm, 5 mm offset) and print the T bar ST1, bolted on with 2 x M3 x 12 in slots of +-1 mm (the 16 / 20 mm are read as radii from the spline centre: ASSUMED until measured). Bar at stall: safety 2.8 at the inner bolt, 2.5 at the outer, 4.0 beyond the arm; bolt bearing 1.4 MPa (hand) | 25T servo spline; ball studs 51 mm from the spline centre | metal arm VERIFIED (spline, hole distances), radii ASSUMED. This row is now "buy the arm, print the bar" |
| Heave bump stop (1) | SU7: TPU 95A sleeve on the shock shaft | JConcepts JCO2662 rubber up-travel limiters, 10 mm long, fit 3-3.5 mm shafts, $10.20 for 8. https://www.amainhobbies.com/jconcepts-monster-truck-suspension-uptravel-limiters-8-jco2662/p717482 | on the 3-3.5 mm shock shaft at the eye neck; trim it to the SU7 length | VERIFIED |

### Printed tie rod: strength (hand calculation, same loads as the steel rod)

| Check | Value | Basis |
|---|---|---|
| Load | 29.8 N | Servo stall 15.5 kg cm = 1.52 N m on the 51 mm horn. The older load case used 101 N (`analyses/tie_rod.py`, earlier servo) |
| Tension | 1.15 MPa on 25.9 mm² (the D7 x D4.0 tube at the ends): safety 17 at 29.8 N, 5.1 at 101 N | 20 MPa PETG across the layers, a conservative value: the rod prints lying down, along its layers |
| Buckling (Euler, pinned at the ball centres, L 93 mm) | P = pi² x E x I / L² = 9.87 x 2000 x 105.3 / 93² = 240 N: safety 8.1 at 29.8 N, 2.4 at 101 N | E 2000 MPa for printed PETG (ASSUMED); I of the weakest section, the D7 x D4.0 tube: pi (7⁴ - 4⁴) / 64 |
| Insert in the collar | wall (7.8 - 4.6) / 2 = 1.6 mm (print at 6 walls, 100 % infill: solid); pull-out more than 300 N | Brass M3 inserts in PETG, ASSUMED typical, not tested |

Result: above 2 on every line, even at the old 101 N. The steel turnbuckle stays the default, because the printed rod's fits and insert pull-out are not tested.

## Print only (no stock metal part fits)

| Part | Printed version | Why no off-the-shelf metal part | Machined version |
|---|---|---|---|
| Lean head | SU1 | Custom four-pivot head of this lean-steer front end | `interfaces.md` (lean head) |
| Upper wishbone L/R | SU2L / SU2R | Custom 91 mm A-arm with the heave shock post; no RC arm has these hard points | `interfaces.md` |
| Lower wishbone L/R | SU3L / SU3R | Custom 91 mm A-arm | `interfaces.md` |
| Knuckle L/R | SU4L / SU4R | Ball studs along y into the plate, stub axle at the kingpin's y. RC knuckles (for example brass SCX10 III) are for C-hub portal axles | `interfaces.md` |
| Droop stop L/R | SU5L / SU5R | Custom base under the arm root | from `exports/Droop_stop_*.step` |
| Droop stop pad L/R | SU6L / SU6R (TPU) | Any 6 x 10 mm rubber pad works; none was sourced | none needed |
| Steering servo mount | ST2 | Fits this deck and servo | from STEP |
| Rear swing arm | DT11 | Custom single-sided arm with three pivot plates around the drive block | `interfaces.md` (rear swing arm) |
| Pillow block, rear bearing carriers, ring hub | DT5 / DT6, DT7 / DT8, DT10 | Traced from the donor chassis; no stock part | from STEP |
| Rear pivot pulley 26T | DT14 | No 26T GT2 aluminium pulley with a 5 mm bore was found; only 20T and 36T (Adafruit, discontinued) | none: printed only, or change the ratio |
| Rear axle pulley 30T | DT15 | ServoCity 30T GT2 (VERIFIED) has an 8 mm REX (rounded hex) bore and does not fit the round 8 mm axle | a REX-bore axle would allow it |
| Front wheel L/R, 1.9 in | DT16L / DT16R | Bought 1.9 in wheels drive on a 12 mm hex; these wheels carry their own 6x12x4 bearings on a fixed stub axle | none |
| Rear wheel 2.2 in | DT17 | A bought 2.2 in wheel with a 12 mm hex would fit the hex interface, but its offset on the 8 mm axle is not checked and none was sourced | none |
| Motor plate | CH5 | Fits this deck, with 25 mm motor screw slots | from STEP |

## Buy only (cannot be printed safely)

| Part | Why buy only | Chosen part (see `../hardware.py` for the price and status of each) | Printed fallback |
|---|---|---|---|
| Bearings 5x11x4 (8), 8x16x5 (2), 6x12x4 (4) | Rolling elements | MR115-2RS, 688-2RS, MR126-2RS (Hobby ETC, VERIFIED) | none |
| Ball joints 6.8 mm, M3 (8): ball + cup | Steel ball and a cup fit to a few hundredths of a millimetre | Gmade GMA20216 M3 rod end with its own 6.8 mm steel ball, 10 per pack, $12.00 (VERIFIED 2026-11-25: matched pair, out of stock); the hollow ball is held by an M3 x 16 / x 20 screw into the knuckle insert or through the horn / steering arm. Alt. pair, ball size VERIFIED: Xray 352659 6.8 mm M3 studs + Xray 352664 / 352665 6.8 mm cups, but the cups are M4 (arm tips and tie rods would need M4) | none |
| Pivot shoulder screws 6 x 45 M5 (4) | Steel running shoulder | McMaster 92981A130 (VERIFIED: 6 mm, 45 mm, M5 x 10); alt. Zoro M071110600050, 50 mm, $11.85 for 5 | none: a printed 6 mm pin would not carry the wheel load |
| Front stub axles M6 x 60 ISO 4014 cut to 48 + M6 nylock (2) | Bending at the knuckle boss | Accu M6 x 60 DIN 931 A4-80 (NOT OPENED) | none |
| Shafts 5 x 112, 5 x 88, 8 x 100 | Turning shafts in bearings | ServoCity 5 mm x 300 mm stainless (VERIFIED, cut both; 83 HRB, not hardened); VXB 8 x 100 HRC60 (VERIFIED) | none |
| Retaining rings DIN 471, 5 and 8 mm | Spring steel | RS 289-203 / 289-225 (NOT OPENED) | none |
| Shims 6 x 8 x 0.5 (4) | Inner race only, under the nut's clamp load | Minibearings W0060-FP-008-0050-S4, 100 pack (NOT OPENED) | possible as a 0.5 mm PETG washer (2.5 layers), not recommended: it creeps under the nylock |
| GT2 belt 2GT-300, 6 mm | Glass-cord belt | generic (listing 404) | none |
| Gears: 15T pinion, 40T spur, ring and pinion | Tooth load at motor torque | ServoCity 15T 32P (VERIFIED); Yeah Racing AXSC-034 40T (discontinued); Axial AXI232003 (discontinued) | none (the owner excluded gears) |
| Shocks: heave 70 mm, rear 100 mm | Oil dampers with springs | RC4WD 70 mm (VERIFIED, discontinued); Integy C26651RED (NOT OPENED) | none |
| Motor and ESC, servo | Electronics | Hobbywing HWI30404317 (VERIFIED); AGFRC B44BLS V2 (NOT OPENED today) | none |
| Heat-set inserts, screws, nylocks, grub screws | Threads in metal; no printed threads below M6 | Adafruit 4255 (VERIFIED, OD 4.2); generic | none |
| Tyres | Rubber | Pro-Line PRO1021114 front, RC4WD RC4ZT0122 rear (VERIFIED) | none |

## Counts

- **Both paths:** 2 parts (tie rod, heave bump stop). The steering horn is now bought arm + printed T bar (no all-printed horn): its hole radii are ASSUMED until measured.
- **Print only:** 14 rows (25 printed files counting L/R and the block halves), 5 of them with a machinable interface in `interfaces.md`.
- **Buy only:** 13 rows. A printed fallback is offered for one: the shims, not recommended.
