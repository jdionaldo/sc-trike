# WS-03 strength fixes, in priority order

Source: `WS03_STRENGTH.md` (26 of 49 rows are below their minimum on the current `ws03-integrated` geometry). "Verified" = re-run with `w3_strength_fixes_try.py` (geometry patched in memory); "est." = scaling estimate (bending ~ r^3, buckling ~ r^4), not re-run. Nothing in `parts/` was changed by this review.

## 1. Front arm: couple from the 61 mm wheel offset (FS 0.39 at 3 g one wheel, min 3.0; 0.99 braking; 2.0 cornering)
Cause: the wheel is about 61 mm outboard of the arm's bearing pair, which is only 18 mm apart, so 3 g makes a couple of ~140 N on the two planes that must cross the belt gap through the 2.8 mm U0/L0 ties (worst member U0i-U0o). Without that couple the arm would be 2.2.
- `parts/w3_style.py`: `YO` 15.5 -> 36 (outer plane further out, halves the couple; check the belt/clearance, the outer hub and the rod clearance), `TIE_R` U0 2.8 -> 5.0, L0 1.6 -> 3.5, U3 2.8 -> 4.0, L2 2.4 -> 4.0, rails `RT` 2.4 -> 3.2, `RO` 4.5 -> 5.0, `RW` 3.5 -> 4.0. Verified: bump 2.68, braking 7.85, kerb strike 4.89.
- Plus a second lean-rod lug on the outer plane (rod to both planes) or a second rocker arm: est. bump >= 3.2.
- If the YO change is impossible: move the carrier bearing inboard (shorter shaft) or add a bearing on the carrier so the 18 mm pair is not the only reaction.
- Print: outer face up (as now); lattice tubes across the planes are the weak direction, keep them >= r 2.7.
- Whole-axle landing on one wheel (abuse, FS 0.20) will not be survived by any reasonable arm: a lean-servo or rod fuse is the right answer, not a thicker arm.

## 2. Carrier kingpin cantilever tube (FS 0.73, min 3.0)
Tube axis (y) is the bed normal: bending is across the layers (15 MPa). Fix: `CAR_RC` 4.5 -> 6.0 and print the carrier on its side (y axis horizontal): FS = 0.73 x 2.37 x 2.0 = 3.5 (est.). Alternative: a 3 mm steel rod through the tube.

## 3. Rear swing arm shock hoop cross tube B-C (FS 0.92 at 3 g, 0.68 sustained, 2.1 cornering, 2.8 braking)
- `parts/w3_shock.py`: `HOOP_R` 6.5 -> 10 (20 mm OD): verified bump 1.88, sustained 1.8 (min 1.5, ok). To reach 3.0 add a diagonal brace from the lug plate end C back to the leg foot A1 (est. >= 3). Check the skin hole/relief size for the 20 mm tube.
- Do not thicken `LEG_R` alone (verified: r8 legs make the bump slightly worse, 1.59).
- 1 m drop (FS 0.12): the arm is good for a flat drop of about 0.1 m onto the rear wheel (243 N, 31 g on the rear wheel). No printed arm survives 1 m; use a long progressive bump stop (more tyre/shock travel) and do not drop-test the car; with fix 3 expect roughly 0.2 m (est.).

## 4. Cage frame (FS 1.45 front bump, 1.46 kerb, 1.56 cornering, 1.58 rear shock, 1.18 sustained shock tab, 1.62 hinge/nose impact)
- Front: ring `PS1-FN`, `PS2-PL`, `PE1-PL`, `FN-PL`, `PS2-PM`, `PM-PS1`, `PE1-PS2` in `parts/w3_frame.py` EDGES 3.0 -> 4.5: verified front bump 4.8 (rear tab case 1.86). Alternatively bolt the front diff case's other ears to the base plate so only 10 % of the pivot reaction enters the cage: verified 3.6.
- Rear: also `B1-FPB`, `R1-FPR`, `K2-FPB`, `R3-K2`, `B1-R1`, `PE1-B1` 4.0/4.5 -> 5.5: verified rear shock-tab case 2.81 (and front 4.7); tab sustained case rises with it (est. 1.7).
- Hinge/nose impact (1.62): `BT-CBT` bumper bar r 4.5 -> 5.5 (est. 2.4); the lug plates themselves are fine (FS 9 to 16).
- Print: pieces print z up, so steep and vertical tubes load across the layers; a tilt of the frame pieces on the bed (45 deg) would help the vertical tubes but needs supports. Feet: M2.5 into a 3 mm disc is only 3.0-4.9; make `FOOT_Z` discs 5 mm thick if reactions grow.

## 5. Servo tower ear screws (FS 1.15, min 2.0)
The 2.5 mm plate stands vertical, so the 62 N screw loads act across the layers. Fix: `TWR_X` plate 2.5 -> 4.0 mm and print the tower on its back (x axis up) with supports under the feet: est. 1.15 x 1.6 x 2.0 = 3.7. Use brass M2 inserts if the servo is changed.

## 6. Kingpin 4 mm steel (FS 1.32, min 2.0)
Combined 1.5 g lateral + 2 g braking at 68 mm. Fix: Ø5 mm steel (`KP_D` 4 -> 5, boss and hole to match): x1.95 = 2.6; Ø6 gives 4.5.

## 7. Wing foot screw under a hand press (abuse FS 0.68, min 1.0)
10 N on a blade tip pulls the single M2.5 screw with 254 N. Fix: widen the foot to 20 mm (`y0f/y1f` +-10) or add a second screw: est. 1.4. The hanger itself is fine (aero 1.5 g FS 48, press 2.6). Keep printing the hanger on its side (current).

## 8. Upper link buckling (FS 1.69, min 2.0)
`uplink` bar radius 3.0 -> 4.0: Euler load x3.2 = 5.3 (est.). Fits the 9 mm pin boss.

## 9. Lean rocker at servo stall (FS 1.94, min 2.0; 1.09 when a 3 g bump drives the rod)
`PLATE` 4 -> 6 mm: est. 2.9 at stall. Keep printing it flat. The servo, not the rocker, limits the rod force at a bump (it will be back-driven; consider a servo saver).

## Other low rows covered by the above
Rear arm cornering 2.12 / braking 2.76 / drive 2.27 (all limited by the B-C hoop cross tube; fix 3 should clear them), front arm kerb strike 2.19 (fix 1).

## Not low (for the record)
Hinge lugs, pin and magnet pad (FS 7 to 138), frame foot screws 4.9, tower feet 7.9, base plate deck 3.7 under the tower/diff couple and 25 (inertia), front hub bearing seat 4.8, knuckle V 2.07 (just above its minimum), wing hangers 48 (aero), blade 2.8 and prong screws 5.6 (10 N press).

---

## Applied on `ws03-fix-arms` (arms, linkage and mounts)

Before -> after (FS, min in brackets); the review was re-run on the new geometry (`python w3_strength_review.py`). Mass 2252 g (+31 g), front share 62.9 % (unchanged).

| row | before | after | change |
|---|---|---|---|
| Front arm 3 g bump | 0.39 (3.0) | 3.09 | `YO` 15.5 -> 25 (outer plane 9.5 mm further out; 30 clashed with the tyre at full lean), U0/U3 nodes raised 4.1/2.8 mm so the hub-end ties could grow (U0 r 6.5, U3 r 5.6; L0 1.7, L2 2.4 stay belt-limited), new ties across the belt gap at U1 (r 4.5) and U2 (r 3.8), upper inner rails r 3.2, outer rails r 5.0, outer web r 4.0, top lattice r 3.4; outer hub extended to the outer plane; plane ends squared to the bed and to y = ya + YO + 4 |
| Front arm abuse (3 g axle) | 0.20 (1.0) | 1.54 | same |
| Front arm kerb strike / cornering / braking | 2.19 / 2.03 / 0.99 (3.0) | 4.22 / 4.60 / 7.18 | same |
| Carrier kingpin tube | 0.73 (3.0) | 3.36 | `CAR_RC` 4.5 -> 7.5 at z 20 (the lower fix, R 6, only reached 1.7), boss r 6.5, kingpin hole through; print on its side would add x2 |
| Kingpin | 1.32 (2.0) | 2.57 | `KP_D` 4 -> 5 mm steel |
| Upper link | 1.69 (2.0) | 2.54 | elliptical bar 6 (y) x 9 (z) mm |
| Knuckle V | 2.07 (2.0) | 2.9 | tubes r 3.0 -> 3.5, stud hole through the larger ball caps |
| Lean rocker stall / servo-driven bump | 1.94 / 2.19 | 4.73 / 5.50 | `PLATE` 4 -> 6 mm, grown aft (the +x face stays against the horn; `w3_scene.py` places it at `XR + 2 - PLATE`) |
| Servo tower ear screws | 1.15 (2.0) | 2.3 | tower plate 2.5 -> 5 mm (feet move with it so the screw holes stay at the same x) |
| Rear arm 3 g bump / +lateral | 0.92 / 0.92 (3.0) | 2.48 / 2.27 | `HOOP_R` 6.5 -> 10 (20 mm cross tube), `LEG_R` 7.0, rear top/bottom lattices and end ties r 4.3 (belt hull r 8); STILL BELOW 3.0 |
| Rear arm cornering / braking / drive | 2.12 / 2.76 / 2.27 | 4.13 / 6.29 / 3.89 | same |
| Rear arm sustained | 0.68 (1.5) | 2.06 | same |
| Rear arm 1 m drop | 0.12 (1.0) | 0.33 | not survivable (flat drop about 0.15 m); use bump stops, do not drop-test |

Findings that differ from the list above: the proposed diagonal brace from the lug-plate end C to the leg foot A1 made the rear arm WORSE in the FE (bump 1.88 -> 1.38: it pulls the load through the top lattice tube 1pi-2po), so it was not built; thicker legs also shift the weak point to that lattice (leg r 8: 2.1). The rear arm bump factor is limited by the leg A1-B / lattice 1pi-2po at about 2.5; reaching 3.0 needs a shorter lug cantilever (move the shock lug plate towards the leg plane) which changes the shock geometry. Front lower ties (L0, L2) cannot grow: they sit between the belt hull (z -7.7) and the tie-rod pass-under (z -11.4).

Print orientation (per part): arm outer face up as before (lattice and ties across the planes are the weak direction, all >= r 3.2 now); carrier on its side (kingpin tube axis horizontal) if possible, otherwise as before with FS 3.36 already computed across the layers; knuckle with the hub axis horizontal; rocker and uplink flat; tower on its back (x axis up) with supports under the feet; rear arm plane normal up as before.

Not done here (other builders' files): cage frame rows (`w3_frame.py`), wing foot screw (`w3_tail.py`). `w3_frame.py` reads `SK.HOOP_R` for the rear upper shock lug disc (2 x HOOP_R), so that disc grows from 13 to 20 mm diameter with the new cross tube.

### Rear arm follow-up (3 g bump 2.48 -> 3.06, + lateral 2.27 -> 3.09)
`REAR_PL` rails 3.0 inner / 6.0 outer (zigzag 3.0 / 4.5), end ties 5.5 at offset VL 14 (`REAR_TIE`), lattices 5.0, `HOOP_R` 10, `LEG_R` 7. The FE now uses the same constants (the rail A2-axle stub and end ties were hard-coded before). Cornering 7.2, braking 9.1, drive 6.9, sustained 2.26. Added mass +9 g (2261 g total), front share 62.7 %. 1 m drop stays below 1.0 (abuse; use bump stops).
