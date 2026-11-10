# WS-03 skin from `WS03_graft_v3_after.sc`: hollowed, mounted on the cage, cage updated

Branch `ws03-skin-fit` (from `ws03-integrated` 2e89515, with `ws03-fix-motor-clash` merged).  Nothing merged to main.

## What the .sc really contains (read this first)

`WS03_graft_v3_after.sc` holds **two skins**.

* The eight graft meshes from `ws03-panel-skin` (end_front, mid_front, mid_rear, end_rear, pods, rack, spoiler; hollow, 2.4 mm) are still in the file, but **four of them are hidden**
  (`geometry_0..3`): the user hid them.
* Visible, and built by hand on top of them: parametric lofted bodies `FrontShell` (solid, 2195 cm3), `RearShell` (solid, 658 cm3, with a hatch pocket), `RearCabin` (a hollow tunnel,
  1.6 mm wall, closed rear bulkhead, open belly), plus the mesh bodies pods (`geometry_4/5`), roof rack (`geometry_7`) and spoiler (`geometry_6`).  A hidden `RearTransition` loft and
  a 347 k-face scan (`rev_trike_mesh-og`, reference) are also there.

I took the **visible** set as "the good solid base" (that is what the user sees; the solid lofts are what needed hollowing).  The hidden graft pieces were not used.  If the old
graft pieces were meant instead, say so: the pipeline below is mesh-in, mesh-out and takes any watertight source.
All coordinates in the .sc are stored 1000 x too large (1 unit = 0.001 mm); real size 362 mm long, 203 mm wide, 121 mm high (+ rack).  Source meshes, in mm: `ws02/skin_src/`.

## 1. Hollowing (`skin_hollow.py`, `skin_user.py`)

* Uniform inward wall 2.4 mm.  Every vertex of the outer surface moves to the intersection of its incident face planes shifted inward by 2.4 mm (least squares where more than three
  planes meet), so the **outer surface and all creases are untouched** and the cavity keeps hard creases.  The cavity is then swept out downward (belly) and across the joint end:
  outer solid minus cavity = open-belly shell.
* Where the material between two outer surfaces is thinner than 2 x 2.4 mm (a pocket floor over the belly, acute sill edges) the cavity is cut back with 3 mm blocks, so those places stay
  **solid** (no wall under 2.17 mm anywhere; measured: cavity surface to outer surface min 2.17, 1 % 2.25, median 2.40 mm).  Nothing is thinner than the 1.2 mm limit.
* Already hollow, kept: `RearCabin` (1.6 mm wall).  Its closed rear bulkhead gets a window as big as the rear cavity opening (a 5 mm frame stays) so the cage tubes can pass.
* Kept solid: pods (12 x 16 x 13), roof rack bars, spoiler (3 mm blade): all thinner than 2 walls.  The spoiler's two legs ended 1.3 mm above the deck: 4 mm posts into the deck wall make it
  one piece.
* Pieces: `front` (x -148.4 .. 33), `mid` (cab, -205.9 .. -148.4, with rack and pods), `rear` (-336 .. -205.9, with spoiler).  Joints are plain rims; each joint has 4 bosses (2 under the roof,
  2 on the flanks), each drilled 3.2 mm x 7 mm from the joint plane on both sides for a 3 x 12 mm steel dowel.
* All three pieces and the welded body are watertight, one body each; they fit the 220 x 220 bed (front 181 x 185 x 121 mm, mid 58 x 176, rear 131 x 202).

## 2. Pose (skin frame -> chassis frame)

x offset **-148.4 mm**, z offset **+19 mm**, **no scale**.  Nose tip at x +33 (3.6 mm ahead of the cage's bumper bar), belly rim on the deck's underside (z -29), cab roof inner at z 90.6.
The earlier skin was 468 mm long, y +-86; this one is 369 mm long (336 to the tail) and +-101 wide: the rear wheel (x -394 .. -506) now sits behind the tail, the front tyres
(inner face y 113) are 12 mm outside the widest point of the skin.

## 3. Changes to the cage (`parts/w3_frame.py`, `body3_build.py`)

* `body3_build.top_z / hw_in` now ask the user's skin (roof underside height, inner half width) so the cage's tab nodes follow it (`WS03_SKIN=old` restores the wedge).
* Roof rails behind the cab run under the hatch pocket floor: `RAIL_Z = 40.5` for R3, XN and the rear tab node R2 (11 mm tubes, 1.6 mm clear of the pocket floor underside z 47.6).
* Rear tab station moved from x -352 (behind the new tail) to x -318, y 34.
* Magnet tab stations on every skin piece: nose roof (FT), hoop roof (N1), cab roof (MU), rear deck (R2), each +-y: pad with a 6 x 2 mm magnet pocket on the cage, boss with pocket on the skin.
  The old hoop tab node HT is on no tube since the motor bypass, so that station sits on the bypass corner N1.
* The old rear wing (screwed onto the old tail hood at x -374 .. -483, behind the new skin) is **off** (`WS03_WING=1` brings it back); the user's skin carries its own spoiler.

## 4. Skin trimmed for the mechanism

Only after the cage was adjusted: the front arms, pods, upper links, tip shafts, tie rods, belts and diff outputs pierce the flank where the user's body is 202 mm wide.
`arm_slot` intersects them with the skin over lean -20..20 (3 deg steps) x steer -17/0/17, joins the pierce points of consecutive poses with convex hulls, adds 2 mm and simplifies to an angular
polygon (x -116 .. 7, z -34 .. 71, open to the belly): a wheel arch on each flank.  The frame's tubes and pads are cleared with the swing channels used before, so the skin still opens on
its nose pin; the rear tyre and arm have the same arch as before.  **The skin's outer shape changes only by these arches, the joint bosses' inside and the tab bosses' inside.**

## 5. Later user requests (applied)

* Roof rack and spoiler **removed** (the old rear wing was already off). The two roof pods stay.
* Shell carried back over the rear wheel: a fourth piece `tail` (convex hull of the user's tail face and a smaller face over the tyre, hollowed 2.4 mm, open belly, x -329 .. -469, 140 x 124 x 63 mm).
  The tyre + swing-arm travel arch (25 mm up, 20 mm down, +3 mm) and the arm are cut out of it, so the skirts end at the arm and the arm travel is free. Joint rear|tail has 4 dowel bosses like the others.

## 6. Results

* Pieces (all watertight, one body each): front 93.6, mid 43.6, rear 121.3, tail 41.9 cm3 hollow; welded skin 300 cm3.  Fit check (`fit_check.py`): no assembly item touches skin material.
* Swing sweep 0..35 deg: clean (40 deg touches the frame, beyond the range).  `check_global` clean at rest, lean/steer +-20/17.
* Mass 2298 g, CG x -160.2 -> **front share 64.4 %** (kept).  To hold it the tungsten plate moved from the nose to under the tail deck (x -320) and is 4 mm instead of 3 mm (56 g): the heavier, further-forward skin and the missing wing had pushed it to 66.5 %.
* Tests: 230 pass, 2 skipped, 1 xfail (rear 1 m drop, as before); 3 `test_monocoque_half_prints` fail exactly as on the base branch (need the old mono_left.stl). `test_solver_reproduces_old_factors` expectation 4.6 -> 4.36 (legacy frame factor, still > 2).
* Strength (`WS03_STRENGTH.md` regenerated): all rows ok except the known 1 m rear drop. The wing rows are stale (wing off).
* Support (`support_check.py`): every skin point is within 62 mm of a cage member (0.1 % beyond 60 mm, rear flanks); 4 magnet stations + nose hinge hold the skin; the rear flanks (x -240..-320, |y| 85-101) remain the least supported spans (up to 62 mm): an outrigger pair would be the next cage addition.
* Images/GLBs: `skin_fit_out/` (assembly and skin-only GLB, 4 views, 8 close-ups).

## 7. Re-split (user request): longer front, mid moved back, open rear top

* Joints now at chassis x -205.9 (front|mid), -263.4 (mid|rear), -329.4 (rear|tail): `front` runs from the nose to the old end of the cab (239 x 185 x 131 mm: needs the P2S 256 bed, `test_body_pieces` uses 256 for the body pieces), `mid` is moved back 57.5 mm (58 mm long), `rear` is 66 mm long.  Dowel bosses are made on the welded skin at the new joints (roof bosses at the mid|rear joint at y +-26, between the roof rails).
* Top of `rear` opened: the deck is cut through over the whole piece (4 mm short of each joint) with a 12 mm frame all round; the cage rails show through.  The rear magnet bosses fall inside the opening and are gone: the rear is held by its dowels to mid and tail; the old rear tab pads stay on the cage.
* Re-checked: no clashes, swing sweep clean to 35 deg, 4 watertight pieces, front share 64.5 % (plate 5 mm, 70 g), mass 2292 g, 231 pass (3 legacy mono fails as before).

## 8. Correction: open the hatch pocket, delete the tail

* The pocket in the rear deck (the marked section) is cut through its floor (walls stay); the earlier whole-rear-roof opening is gone.
* The `tail` piece is deleted (skin ends at x -329 again, spoiler/rack already removed). Three pieces: front 239 mm (P2S bed), mid 58, rear 66.
* Checks: no clashes, swing clean to 35 deg, 231 tests pass (3 legacy mono fails as on base), mass 2283 g, front share 64.9 % (plate 6 mm, 84 g).
* Rear suspension redesign: not started, see the open question in the session.

## 9. Gap fill (user marks)

* Side view (rear quarter between the cab sill and the rear shell, through which the cage showed): closed with a faceted 2.4 mm skirt wall on each side, deck line (z -29) up to the rear shell's flank rim, x -207 .. -331, one planar panel per segment of the simplified rim line (`skin_user.side_skirts`).  Merged into the rear piece before the cuts, so tubes/arm relief still apply; no clashes at rest or in the +-20/17 lean poses, swing clean to 35 deg, all pieces watertight.  Before/after: `skin_fit_out/renders/skirt_{before,after}_{side,top,front34}.png`.
* Top-view and front-3/4 triangles at the fender corners (the arm windows' corners): NOT closed.  The arm slot is the swept pierce region of the front arms, pods and links over lean +-20 / steer +-17; its upper part starts at y 53.5 (checked: starting it at y 80 puts 443 mm3 of each arm inside the skin), so those corner wedges are the clearance the lean travel needs.  Closing them needs a smaller lean range or a relieved panel; say which.
* Mass 2319 g, front share 64.5 %, 231 tests pass (3 legacy mono fails as on base).

## 10. Skirt follows the drawing, merged with the running board

The skirt is cut to the user's yellow outline (right edge as drawn, x -257 at the sill to -336 at the roof line); its leaning left edge is replaced by the cab's end plane (x -205) so the skirt is one piece with the cab's running board / sill.  No clashes, swing clean to 35 deg, 3 pieces watertight.  The fender-corner wedges are still open (arm clearance, see section 9).

## 11. Skirt facets follow the flank angles

The skirt no longer drops straight down: at each rim station the wall continues along the steepest descent of the flank face above it (facets with the established angles) to the deck line, and the cut uses the drawn slanted ends again (left edge from x -197 at the sill, right edge to -336 at the roof line).  Rocker extension: not done, see the open question.
