# Strength-first print plan for the articulating parts

Scope: front swing arms (SU1), rear swing arm (DT11), uplinks (SU2), lean rocker/horn/mount (SU5, SU7, SU4), steering carrier and knuckle (ST1, ST2), tie rods (ST3), steering horns (ST4).
Material strength used everywhere: printed PETG, 40 MPa along the layers, **20 MPa across them**. Required safety factor 2 (allowable 10 MPa across, 20 MPa along).
All loads are ASSUMED (2.6 kg vehicle, 60 % on the front axle): landing on one front wheel 65 N up (about 8 g) plus 30 N cornering side load, tyre contact patch 56 mm under the axle;
steering servo at stall (15.5 kg.cm = 1520 N.mm); lean servo the same class. Nothing here is measured. Treat it as a screening check and test real parts (proof-load section at the end).

## What was checked and how

| Check | Tool | Parts |
|---|---|---|
| Solid FEM (CalculiX through `soma analyze fem`), pivot bores held, load at the shaft bores | `analyses/front_arm.py`, `analyses/rear_arm.py` | front arm, rear arm |
| Beam-model FEM (existing) | `tools/front_arm_fea.py`, `tools/arm_fea.py` | front arm 95 % of its 18 MPa working limit at bump 50 + side 30; rear arm 31 % |
| Section check (weakest slice, area and section modulus, Euler buckling) | `tools/strength_check.py`, results in `analyses/strength_check.md` | tie rod, uplink, steering horn, knuckle, carrier, lean horn, lean rocker |
| Orientation candidates (height, overhang, bed contact) | `tools/orient_check.py` | all of the above |

The solid FEM cannot be run on knuckle, carrier, uplink, tie rod and the lean parts: they are faceted meshes with no bores to hold, and the pin positions would have to be guessed. They get the section check instead.

## Results

| Part | Result | Verdict |
|---|---|---|
| Front arm (L/R) | Solid FEM: highest 21.7 MPa at the pivot bore edge (partly a support-edge artefact), 174 mm2 patches at 0.96 safety against the 20 MPa across-layer value; tip deflection 1.4 mm. Shock force left out (conservative at the pivot end). | Too low as printed standing on its edge. With the plates flat the in-plane stress runs along the layers (40 MPa): safety about 1.8 at an 8 g landing, about 3.7 at 4 g. Thicken the pivot end (see "Design changes") to reach 2 at 8 g. |
| Rear arm | Solid FEM: only 0.13 cm2 (13 mm2) of the whole arm is below safety 2; the peak of 323 MPa at (50, 128, 44) is a sharp-corner spot where the mesh check failed (distorted elements), so it is not a reliable value. Tip deflection 0.67 mm. The beam model says 31 % of the working limit. | Passes away from that one spot. Inspect the corner at (50, 128, 44) (near the pivot, underneath) and add a fillet; re-run with a finer mesh (`Study(mesh=...)`). |
| Tie rod | 5.6 MPa axial at the servo stall force (101 N), 56 % of 10 MPa allowable. Euler buckling load 39 N pinned-pinned: **a stalled servo pushing the rod in compression buckles it** (ratio 2.6). | Strength is fine in tension, **buckling is not**. Stiffen the middle (thicker or an I-section) or limit the servo travel/torque. |
| Uplink | 1.9 MPa, 19 %. Euler 161 N against 80 N applied (ratio 0.5). | OK. |
| Steering horn (printed, 2.3 mm thick) | 15.8 MPa best case, 450 MPa if loaded about its weak axis. | **Fails.** Use the servo's own aluminium 25T horn (a purchased part) instead of the printed one. Do not print this part. |
| Knuckle | 41 MPa best case (load along the strong axis), 103 MPa weak axis, at an assumed 40 mm lever. | **Fails the assumed case.** The lever arm and pin positions need confirming; if they hold, the weakest slice must grow by about 4x in section modulus. |
| Carrier | 44 MPa best case, 79 MPa weak axis (assumed 30 mm lever). | **Fails the assumed case**, same as the knuckle. |
| Lean horn | 11.8 MPa best case, 84 MPa weak axis (stall torque at the root). | Marginal at best. Use the servo's own horn or thicken the root. |
| Lean rocker | 14.0 MPa best case, 94 MPa weak axis. | Over. Thicken the arms or print in PETG-CF. |

These numbers scale linearly with the load. At half the loads (4 g landing, half the stall torque in use, which is what a servo actually delivers continuously) the arms and the rocker pass, the knuckle and carrier come close to the limit, and the printed horns still need metal.

## Orientation rules

1. **Pin axis vertical.** Every bore with a steel pin or shaft stands vertically: perimeters run round the bore without a seam crossing the pin load, and the bore prints round.
2. **Load plane in the layer plane.** Plates, links, horns and arm sides lie flat. In-plane tension and bending run along the extrusion lines (2x the across-layer strength).
3. **Never put the main bending across the layers.** Stand a part up only where a cross-member must be loaded along its own axis (arm cross-tubes are short and carry shear, accepted).
4. **Seams on the least loaded face.** Z-seam aligned (not random) on the outer, unloaded edge, away from bores.
5. **Walls over infill.** Strength comes from perimeters: 6 walls on structural parts, solid (100 %) for horns and tie rods, gyroid 60-80 % elsewhere.
6. **Supports** easy-peel (tree, 0.2 mm interface gap) only under truss tubes and pod lugs, never inside a bore that takes a pin; drill or ream bores after printing.
7. **Material.** PETG for everything structural; PETG-CF (or PA-CF) for the arms, rocker and carrier if the loads above are real (about +30 % stiffness, more heat margin; dry the filament). PLA nowhere near the arms.

## Per part: before and after

| Part | Kit orientation now | Strength orientation | Height | Overhang area | Walls / infill |
|---|---|---|---|---|---|
| Front arm | on its edge (-z down), 42 mm tall | plate flat, outer or inner plate down (+/-x), pivots vertical | 31 mm | about 5100 mm2 (was 3200) | 6 / 60 % |
| Rear arm | -y down, 150 mm tall | plate flat (+/-x down), pivots and axle bores vertical | 90 mm | about 11500 mm2 (was 4400): supports under the shock bridge | 6 / 60 % |
| Tie rod | on its edge (+x down), 47 mm tall, no bed contact | flat (+/-z down) with a 5 mm brim | 13 mm | about 420 mm2 | 6 / 100 % |
| Uplink | flat (-x down) | unchanged | 6 mm | 600 mm2 | 6 / 60 % |
| Knuckle, carrier | flat on the largest face | unchanged until the pin axes are confirmed | 26 / 28 mm | small | 6 / 70 % |
| Lean rocker / horn | on a side | unchanged (plate flat) | 8 / 5 mm | small | 6 / 80-100 % |
| Steering horn | flat | do not print: servo aluminium horn | | | |

The kit change is in `kit/build_kit.py` (`STRENGTH_FACES`: front arm, rear arm and tie rod may only stand on the listed faces) and `kit/registry.py` (walls and infill). **The kit has not been regenerated**: the build chain needs the Python packages trimesh and shapely, which the SOMA Python does not have, so run it where they are installed.

## Design changes the results call for (not done yet)

1. Steering horn: replace the printed horn with the servo's aluminium horn in the model and the bill of materials.
2. Tie rod: add a mid-span rib (I-section), or move to a 4 mm steel rod with printed ball-cup ends.
3. Knuckle and carrier: confirm the real load path, then grow the neck sections (about 4x section modulus) or switch to PETG-CF.
4. Front arm: thicken the plates around the pivot bores (bores r 9 mm sit close to the edge) and add a 1.5 mm fillet where the truss tubes meet the plates.
5. Lean rocker and horn: thicken the root or use metal horns.
6. Re-run `tools/strength_check.py` and the two FEM studies after each change.

## Proof-load tests on the first printed set

- Front arm: clamp the pivot bores, hang 2 kg (20 N) at the tip bore for 10 minutes, measure the deflection (FEM: 0.4 mm per 20 N). Then 6.5 kg (65 N), no crack, deflection under 1.5 mm.
- Tie rod: push it in compression between two stops to 40 N: it must not bow.
- Steering: lock the wheels on a high-friction mat and drive the servo to full travel; check horn, rod and knuckle for white stress marks.
- Pins and bores: every bore gets its steel pin test-fitted before assembly; ream, do not force.
