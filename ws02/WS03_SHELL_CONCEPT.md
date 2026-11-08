# WS-03 shell concept skin (WS03_SKIN=concept)

Build: `WS03_SKIN=concept python body3_build.py && WS03_SKIN=concept python split_shell3.py` -> `out/mono3_concept/`. Default (no env) is the unchanged current skin in `out/mono3`. Tests: `WS03_SKIN=concept pytest tests/test_w3.py`. GLB: `tools_skin/export_glb.py`; renders: `tools_skin/render_compare.py`.

## Style translation
- Kept from the reference: angular hexagonal canopy and flat-sided pods, cowl hump rising to the canopy, open vented engine hood (second louvre bank over the motor), side intakes, rear fender over the rear wheel, wing at the back (our stepped wing, unchanged), pink accent lines as 1.4 x 0.7 mm engraved grooves (flank diagonals, sill line, hood and engine-deck stripes) to be filled with paint.
- Adapted: same hardpoints, hinge ears, 3-piece split (cuts -165/-300), rear travel channels and cage cut-outs; the roof is raised (max +10 mm at x -215) rather than lowered so nothing inside is cut; pods are flat-topped (y 86, x -150..-205) with a hard rear corner.
- Dropped: reference wheels, front/rear drivetrain, mirrors, roof snorkel, the GLB's four-wheel layout (the GLB is a noisy 4-wheel buggy, 141k tris, not watertight, so it was used for proportions only; the two drawings drive the styling).
## Results
Pieces watertight and fit bed; swing sweep 0..35 deg at 1 deg: 0 hits; 11 WS-03 body/interior/assembly/mass tests pass; clearance script clean. Printed mass 855 g vs 848 g (+7 g); total 2307 vs 2300 g; front share 64.2 % both. Thin-wall ray sample: 5.6 % of points under 1.2 mm vs 2.6 % for current (groove/louvre edges) - not tuned.

## Rev 2 - silhouette rebuild (hump, chisel nose, wide rear pods)
Reference traced from drawings 54/55 (tools_skin/ref_outline.py): x scaled on the 450 mm wheelbase, z on the tyre (0.44 mm/px). Overlays are in WS03_concept_{top,side,iso,front}.png.
Changes: plan chisel nose (half width 26 at x 30, was 38) with faceted flare; rear pods 92 mm half-width from x -176..-293 (was 86 peak/70); canopy block (hull, base half 46, top half 40) rising to z 112 between x -135 and -290 so the canopy top is z 131 (cage included, was 101) - bbox height 136 -> 157, width 172 -> 184. Roof tabs, hood, nose and wing deck stay on the old roofline: top_z() is kept for the frame's tab stations (w3_frame untouched), _tz() is the real surface; tab posts reach up to the taller roof.
Not matched, and why: front shoulders (x +15..-123) stay at 52 mm: the front arm sweep envelope (up to z 125 at x -30) is cut out of the skin up to y 100. Rear deck stays at z 96 (ref 130): the wing feet and roof-gill geometry sit on the old deck. Cowl z 70 at x -105 (ref 101): roof tab at x -100 and the motor louvres.
| x | half-width cur | new | ref | top z cur | new | ref |
|---|---|---|---|---|---|---|
| 30 | nan | nan | 38 | nan | nan | 57 |
| 0 | 44 | 43 | 60 | 48 | 48 | 72 |
| -52 | 46 | 52 | 85 | 64 | 64 | 81 |
| -105 | 52 | 50 | 90 | 68 | 70 | 101 |
| -200 | 83 | 92 | 91 | 101 | 131 | 126 |
| -290 | 70 | 92 | 91 | 95 | 96 | 130 |
| -350 | 54 | 54 | 81 | 97 | 97 | 122 |
| -400 | 49 | 49 | 40 | 89 | 89 | 111 |
| bbox current | L 468 W 172 H 136 | | | | | |
| bbox new | L 468 W 184 H 157 | | | | | |

Skin printed total 879 g (was 848, +31 g; limit 900), total 2331 g, front share 63.9 %. 11 body/interior/assembly/mass tests pass, clearance clean, swing sweep 0 hits 0..35 deg (1 deg), body and pieces watertight. Thin-wall sample under 1.2 mm: 4.4 % (current 2.4 %).

## Rev 3 - full silhouette match (merged mirrored cage a4c6502)
Side polyline now follows the reference: nose 40, hood 62 at x -5, windscreen base 84 at x -72, roof 124..130 over x -151..-290, deck 122 at -327, 111 at -400, tail face to z 105 (was 83). Section flanks steeper (38 mm half width still at z 130), pods 92 mm with a shoulder plane at z 46..52 from x -150 to -335 (rear pods wider than the canopy), chisel nose 20 mm half width, hood 52 over the arm sweep, flare to 90 behind x -123, windows grown to 8 mm margin. Roof magnet tabs are unchanged in the frame (w3_frame untouched; top_z() still answers with the old roofline); posts rise from the pads to the taller roof (4.5 mm foot, slimmer post kept inside the flank). Wing (stepped, unchanged design) lifted 22 mm with the deck (parts/w3_tail.py DECK_DZ). Canopy cage slab 6 mm over the roof.
Numbers (before / new / reference):
| x | half-width cur | new | ref | top z cur | new | ref |
|---|---|---|---|---|---|---|
| 30 | nan | 24 | 38 | nan | 42 | 57 |
| 0 | 44 | 52 | 60 | 48 | 59 | 72 |
| -52 | 46 | 52 | 85 | 64 | 83 | 81 |
| -105 | 52 | 53 | 90 | 68 | 101 | 101 |
| -200 | 83 | 92 | 91 | 101 | 135 | 126 |
| -290 | 70 | 92 | 91 | 95 | 130 | 130 |
| -350 | 54 | 60 | 81 | 97 | 119 | 122 |
| -400 | 49 | 49 | 40 | 89 | 111 | 111 |
| bbox current | L 468 W 172 H 136 | | | | | |
| bbox new | L 472 W 184 H 164 | | | | | |
Skin pieces: 186 g -> 277 g; all printed parts 848 -> 940 g; total 2392 g, front share 63.6 %.
Checks: pieces watertight and bed-sized (tallest piece 164 mm); swing sweep 0..35 deg at 1 deg: 0 hits; 132 tests pass (WS-03, drive, strength, balance), 1 xfail; clearance clean; thin-wall sample under 1.2 mm: 2.7 % (current 2.4 %).
Pre-existing failures, also on a4c6502: tests/test_w3.py::test_strength_factors (singular FE matrix) and tests/test_assembly.py (legacy chassis).
Hardpoints that cannot move: the front lean/steer linkage envelope (arms, uplinks, tie rods reach z 125 at x -30 and y 100), so the skin over x +15..-123 stays 52 mm half width (ref 60..90); the ref front shoulders there would sit inside the swinging arms.
