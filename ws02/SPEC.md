# WS-02 rebuild: spec and plan

Replaces the 1/18 (250 mm) design. The 1/18 project stays in the parent folder, untouched, as the reference for code and validators.

## Locked from the user's WS-02 info
| Item | Value |
|---|---|
| Layout | Reverse trike, tilting, rear-wheel drive (gear + belt), PETG frame |
| Size | Length about 370 mm, width about 280 mm, wheelbase about 280 mm (scale factor 1.48 on the old design) |
| Motor | 2830 outrunner, about 1400 KV, 3.17 mm shaft, 28 mm dia x 30 mm, mounting holes 16 mm apart |
| ESC | 60 A, 2S-3S, BEC 6 V / 3 A or more, 46 x 38 x 33 mm |
| Pinion | 15T, 0.8 module, 3.17 mm bore |
| Servos | Two short-body servos, 12 kg.cm or more; body 40 x 20 x 19.3 mm, flange 49 mm, ear span 56 mm, shaft 8.6 mm from the end, 28.3 mm to the horn face, 33.1 mm overall (drawing) |
| Radio | 6 channels or more, two programmable mixes (lean and steer) |

## Derived (3S, 85 % of no-load speed)
- Tires scaled 1.48: rear 92 mm dia x 59 mm wide, front 77 mm dia x 24 mm wide (unverified; confirm against the kit).
- Drive: pinion 15T into a 60T spur (module 0.8, centre distance 30 mm), then a 15T:30T belt to the axle. Ratio 8:1, top speed about 7.9 m/s (28 km/h).
- Servo torque: 12 kg.cm is 1177 N.mm each.

## Plan
1. Params and layout: new bought-part sizes, 370 mm package, bed split (370 mm exceeds the 220 mm bed, so the chassis splits in length as well as left/right).
2. Kinematics: re-solve lean with servo 1 and steering with servo 2 (radio mixes them); decide where servo 2 mounts so its rod follows the lean.
3. Parts: chassis sections, lean bars, uprights and hubs, swingarm for the 2830 motor and belt, ESC and battery trays.
4. Body: built from the traced reference outlines at the new scale (low wedge, diagonal two-tone split, fender wings, exposed arms and shocks).
5. Validate (bed fit, overhang, walls, interference, clearance), mass/CG, tip-over, renders, docs.

## Status (stage 1 baseline)
- `ws02/params.py` scales the validated 1/18 layout by K = 1.48 (fasteners, walls, clearances and bought parts keep real sizes), then overrides tires, motor (2830), pinion/spur (15T/60T, module 0.8), belt stage (15T/30T GT2, 44 mm centres) and servos (40 x 20 x 19.3 mm).
- `ws02/kinematics.py` solves at 370 mm: steer and lean targets met, swingarm 70.3 mm, rear travel 13.3 mm.
- All mechanism parts build. The body does not build yet (its stations and pins need re-tracing at the new scale).
- Open mechanism issues from the interference check (default pose): link brackets vs tub, swingarm hatch vs chassis cradle and pivot plate (hatch/ring/tube sizes were tuned for the 24 mm motor), gearbox vs gears, lead slot, hub vs steering link (0.84 mm3).
- Not yet done: second servo (steering) and the lean servo mount redesign, ESC and battery layout, 370 mm bed split, body.

## Status (body v1, 370 mm)
- Mechanism, drivetrain (2830 motor, 15T/60T spur, 15T/30T belt) and a first angular body (hood, black canopy, pods with open rear deck, black lower bands, bumper, light cage) build and pass all 73 tests (print checks, interference in 9 poses, 3 mm body clearance).
- Mass about 1.12 kg, CG 61 mm above ground (estimates).
- Still open against the reference: front fender wings, pointed nose, true diagonal yellow/black split, hood retention, a second (steering) servo and its mount, ESC layout, bed split of the 370 mm chassis. The lean-steer still uses the single-servo coupling scaled from the 1/18 design.
