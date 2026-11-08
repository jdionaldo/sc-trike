# WS-03 shell concept skin (WS03_SKIN=concept)

Build: `WS03_SKIN=concept python body3_build.py && WS03_SKIN=concept python split_shell3.py` -> `out/mono3_concept/`. Default (no env) is the unchanged current skin in `out/mono3`. Tests: `WS03_SKIN=concept pytest tests/test_w3.py`. GLB: `tools_skin/export_glb.py`; renders: `tools_skin/render_compare.py`.

## Style translation
- Kept from the reference: angular hexagonal canopy and flat-sided pods, cowl hump rising to the canopy, open vented engine hood (second louvre bank over the motor), side intakes, rear fender over the rear wheel, wing at the back (our stepped wing, unchanged), pink accent lines as 1.4 x 0.7 mm engraved grooves (flank diagonals, sill line, hood and engine-deck stripes) to be filled with paint.
- Adapted: same hardpoints, hinge ears, 3-piece split (cuts -165/-300), rear travel channels and cage cut-outs; the roof is raised (max +10 mm at x -215) rather than lowered so nothing inside is cut; pods are flat-topped (y 86, x -150..-205) with a hard rear corner.
- Dropped: reference wheels, front/rear drivetrain, mirrors, roof snorkel, the GLB's four-wheel layout (the GLB is a noisy 4-wheel buggy, 141k tris, not watertight, so it was used for proportions only; the two drawings drive the styling).
## Results
Pieces watertight and fit bed; swing sweep 0..35 deg at 1 deg: 0 hits; 11 WS-03 body/interior/assembly/mass tests pass; clearance script clean. Printed mass 855 g vs 848 g (+7 g); total 2307 vs 2300 g; front share 64.2 % both. Thin-wall ray sample: 5.6 % of points under 1.2 mm vs 2.6 % for current (groove/louvre edges) - not tuned.
