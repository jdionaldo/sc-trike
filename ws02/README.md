# 1/18 lean-steer reverse trike

A 1/18 scale (250 mm long) RC reverse trike: two slim front wheels on a parallelogram lean linkage, one fat rear tire on a swingarm with the motor hidden inside it. Everything is generated from `params.py` through SolidCraft command scripts, exported as STL and STEP, and checked with an independent print and assembly validator.

## Status: read this first
- **Verified by test (`pytest tests`, 74 passing):** every printed part fits the 220 x 220 x 250 bed in its stated orientation, prints with no supports (overhang under 2 % of area, bridges 10 mm or less), is a single watertight body, and has walls of 1.2 mm or more. The assembly has no interference above 0.5 mm3 and at least 1 mm to bought-part envelopes in 9 poses (default, 15 and 30 degrees of lean each way, plus or minus 4.5 mm swingarm travel, and two combined poses). The body clears every moving part and wheel by at least 3 mm in the same poses.
- **Estimates, not measurements:** servo torque margin (30 % with the specified 3.0 kg.cm servo), mass (621 g), centre of gravity, print times, drivetrain current, thermal behaviour. Nothing has been printed or powered.
- **Unverified purchases:** no Amazon listing was confirmed. Tire, servo, receiver, battery, connector, gear and shock dimensions in `params.py` are assumptions; see `bom.md`.
- **Aesthetic gap:** the body was re-profiled to the reference heights (roof about 30 mm above the tub, tub walls lowered from 40 to 26 mm, rear tire and swingarm exposed between pod blades, front yoke exposed, no hood). It is low like the reference but still a smooth-capped shell, without the references' faceted wedge panels, diagonal two-tone split or front fender wings. See "Known limits".

## Deviations from the brief
- **No program button:** the Hobbywing unit is programmed through its yellow lead and a program box. The hatch gives access to the motor, not a button.
- **No separate BEC:** the built-in BEC (6 V at 4 A) feeds the servo and receiver.
- **Gearing:** 32 pitch gears (module 0.794). A 0.5 module train would put the motor axis inside the rear tire.
- **Swing pivot:** on the motor shaft axis, not the intermediate shaft.
- **Leads:** they leave through a radial slot at the pivot, not an axial hollow (a lead cannot U-turn in the space).
- **Chassis:** two sections, each in left and right halves: a 74 mm wide tub and a 93 mm wide cradle. The cradle is wider than the 0.55 x track body width because the hatch, pivot and swingarm need it.
- **Steering link anchors:** on a bracket bolted to the lower lean bar, not on the chassis, so the links never cross the chassis or the bar.
- **"Two modular rods":** read as the two `link_steer` rods (one per side); the servo drives the lean through one `rod_drive`.
- **Body:** panels butt-join; only the side panels and cage are keyed.
- **Servo:** below the lower lean bar (lug 6 mm, horn 8 mm, rod 10 mm) so the front stays low; it must be at least 3.0 kg.cm at 6 V for a 30 % torque margin. This is a purchase requirement.
- **Front pivots:** the front ear and roof beam became a separate 48 mm wide `front_yoke` that bolts to the chassis rear ear, so the lean arms sweep outside it.

## Layout
```
params.py            single source of truth (frozen dataclass)
kinematics.py        lean, steer, servo and rear travel solver (writes out/kinematics.json)
cad.py               command-list builder (geometry exists only as SolidCraft commands)
parts/*.py           one function per part returning a Part with its command list
build.py             runs every command list through solidcraft-cli, exports STL and STEP
validate.py          print checks and assembled-pose checks
assembly.py          places every part for a pose
renders.py           renders from the STL files; report.py: print plan, mass/CG, tip-over
tests/               pytest
out/commands|stl|step|renders   generated; commands replay any part
bom.md  print_plan.md  tools.md
```
Run: `uv venv --python 3.12 .venv`, install numpy matplotlib trimesh manifold3d pytest scipy rtree pymupdf fast-simplification, then `PYTHONPATH=. .venv/bin/python build.py`, `PYTHONPATH=. .venv/bin/python -m pytest -q tests`, `PYTHONPATH=. .venv/bin/python report.py`, `PYTHONPATH=. .venv/bin/python renders.py`. Needs `solidcraft-cli` on the path.

## Key numbers
Length 250 mm, front track 157.5 mm, wheelbase 193 mm. Lean 30 degrees per side (35 solved); steer 16.6 degrees at 30 degrees of lean (requirement 15); servo travel 35 degrees at 35 degrees of lean; rear travel 9 mm with a 34 mm shock and a spring of about 1.15 N/mm. Drive ratio 12.33:1, 4.97 m/s on 2S. Mass 621 g, about 49 % on the front, CG 44 mm above ground. Servo below the lower bar, front pivots on a narrow yoke: the tallest part of the front end is 45.6 mm above the lower pivot. Static tip-over: the CG stays inside the three-wheel support triangle at 0 and plus or minus 30 degrees of lean (smallest margin 29.4 mm, about 0.65 g lateral). Output in `out/mass_cg.json`.

## Print
See `print_plan.md` (orientation, material, infill, mass, time per part). Summary: 0.4 mm nozzle, 0.2 mm layers, 3 perimeters, 30 % gyroid, no supports. PETG-CF (or ASA, PC) for the four swingarm parts; PETG for the rest; never PLA near the motor. Pivot bores print with the bore axis vertical so layer lines wrap around the pin. Clearances: 0.2 mm sliding, 0.1 mm press, 0.3 mm gears; check with test prints of the hubs and the pivot parts first. Heat-set M2 inserts go in before assembly.

## Assembly order
1. Print everything. Press heat-set inserts into the chassis halves (tub bulkheads, cradle ring, ear servo pilots), lean bar bracket pilots and swingarm half B.
2. **Swingarm:** fit the motor into half A's pocket, tail toward the hatch opening, leads through the radial slot. Fit the pinion on the 2.3 mm shaft. Close half B on half A with four M2 screws. Bolt the gearbox plate to B's end face (two M2). Fit the gear train: pinion 12T, 60T and 15T on the 3 mm intermediate shaft, 37T on the 3 mm axle with the rear bearing in half A. Slide in the axle, fit the rear hub and tire. Fit the hatch (four M2) with the heat shim passed through its slot and folded flat against the plate.
3. **Chassis tub:** screw the right half to the left through the long M2 bolts, dowelled by the pins. Fit the lean bars between the ears on 3 mm pins; fit the servo to the rear ear (self-tapping M2) and the horn and drive rod.
4. **Front end:** pin the uprights to the bar ends (3 mm pins), press the kingpins and fit the hubs, add the stub axles, wheels, link brackets and the two steering links.
5. **Cradle:** bolt it to the tub with the four M2 join bolts; the left boss enters the swingarm cup, the right pivot plate (screwed on from outside) enters the hatch counterbore. Fit the shock.
6. Fit the battery tray and receiver tray, the battery and receiver; route and tie the leads at the floor slots.
7. Body last: side panels onto their pins, then the shoulders, roof, glazing, deck, rear bumper, and the bumper cage on its dowels. Glue the butt joints.

## Wiring
- Battery (2S, EC2) to the power unit's EC2 plug. Observe polarity.
- Throttle lead (white, red, black) into the receiver's throttle channel. **The red wire carries 6 V from the BEC: do not power the receiver any other way.**
- Servo into the receiver's steering channel.
- Yellow signal wire: leave coiled and tied for programming (program box) or an optional aux channel for drag brake.
- Set the BEC to 6.0 V with the program box unless the servo is rated for 7.4 V. Set the cell count to 2S manually (the manual warns the auto setting can misjudge a charged 3S).
- Transmitter: calibrate the throttle range per the manual (hold SET, turn on, then neutral, full forward, full reverse). Remove the pinion before calibrating.

## Thermal risk
The 2-in-1 unit sits inside a printed housing. The manual forbids an external system temperature above 90 C, and the ESC derates at 105 C. PETG-CF softens at roughly 75-80 C, so treat 70 C measured on the outside of the swingarm as the working limit, not 90 C. Heat paths: the unit's tail with the ESC is next to the hatch; a copper or aluminium shim (11 mm x 0.8 mm) runs from the unit through the hatch slot to the hatch's outer face; four 2.6 mm vent holes pass air through the hatch. Gearing is 12:1, far from the manual's 60:1 guidance for crawlers; the model estimates only 1.9 A at 3 m/s2, but motor speed is high, so verify.

**First-run temperature check:** pinion fitted, wheels off the ground, battery charged. Run 30 s at 25 % throttle, stop, measure the swingarm hatch with an infrared thermometer, and log it. Repeat with 60 s at 50 %, then a 2 minute drive. Stop and rework if any measurement exceeds 70 C, or if the ESC beeps twice (overheat protection). Only then run longer.

## First-power checklist
1. Weigh the car and the bought parts; compare with `out/mass_cg.json`.
2. Check every printed part for bore fit by hand before final assembly; all pivots turn freely with no play.
3. Confirm lean travel by hand: full left and right, no rubbing, steer follows lean in the same direction.
4. Wheels off the ground, pinion removed: power up, calibrate throttle, set 2S, confirm motor direction (CCW looking at the shaft; reverse it in the program box if the car drives backwards).
5. Fit the pinion and gears, confirm the mesh turns by hand with the hatch off.
6. Check the servo centres with the lean bar level; test lean with the transmitter and the servo horn at about 30 degrees.
7. Run the first-run temperature check above.
8. Drive on a smooth surface first; lean is servo-held, so expect it to tip if steered hard.

## Known limits and next steps
- **Body style:** 30 flat panels: a lofted, faceted cabin (raked black glazing, 45 degree shoulders, two-tone side bands with intake slots, fastback), a steep nose fascia over the front yoke, a spine deck with chamfered pod tops, arched pod sides showing the rear tire, and a bumper cage with Y-shaped light pockets. The lean arms sweep outside the narrow nose, as in the blueprint's plan view. It is still a flat-plate, low-poly skin: the references' smooth swooping surfaces need curved panels, which would need supports to print.
- **Colour:** yellow and black are tracked in the renders only, not in the STL files.
- **Weak points:** the intermediate gear shaft is supported at one end, the left pivot cup is 1.5 mm deep, and the servo windows leave the rear ear thin.
- **Assumed hardware:** servo spline, hex depth, EC2 plug size, gear and shock dimensions.
- **Not modelled:** screws, inserts, bearings, pins and the shock, other than as masses.
