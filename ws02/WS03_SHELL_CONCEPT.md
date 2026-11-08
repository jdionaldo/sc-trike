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

## Rev 4 - skin leads (frame and hardware untouched)
Verified: frame, chassis, arm, drive and every other w3 part build byte-identical with and without WS03_SKIN=concept; only the wing hangers differ (the wing is 22 mm higher on the taller deck). parts/ differs from a4c6502 only in w3_tail.py (DECK_DZ).
New this rev: nose beak to x 55 (ref 55) with an 18 mm half-width chisel tip; shoulder shelf from x -85 (z 76) stepping down to z 52 at x -205, half-width 75 at x -105 (arm arches are cut out of it by the window cut); gap scan: inner roof is 25-76 mm above the tallest internal part at every 40 mm station (13 mm only at the beak tip, x 40, ahead of any hardware; 19 mm over the hinge lug).
| x | half-width cur | new | ref | top z cur | new | ref |
|---|---|---|---|---|---|---|
| 30 | nan | 29 | 38 | nan | 51 | 57 |
| 0 | 44 | 52 | 60 | 48 | 61 | 72 |
| -52 | 46 | 52 | 85 | 64 | 83 | 81 |
| -105 | 52 | 75 | 90 | 68 | 101 | 101 |
| -200 | 83 | 92 | 91 | 101 | 135 | 126 |
| -290 | 70 | 92 | 91 | 95 | 130 | 130 |
| -350 | 54 | 60 | 81 | 97 | 119 | 122 |
| -400 | 49 | 49 | 40 | 89 | 111 | 111 |
| bbox current | L 468 W 172 H 136 | | | | | |
| bbox new | L 493 W 184 H 164 | | | | | |

| dimension (mm) | before | new | reference |
|---|---|---|---|
| length | 468 | 493 | 523 |
| width | 172 | 184 | 182 |
| height above floor | 136 | 164 | 156 |
| nose tip x | 30 | 55 | 55 |
| canopy top z | 110 | 138 | 130 |
| deck z at x -400 | 90 | 112 | 111 |
Skin 283 g (was 186), all printed 946 g, total 2398 g. 132 tests pass (+1 xfail); clearance clean; swing 0 hits 0..35 deg at 1 deg; pieces watertight, largest 220 x 184 x 154 (no extra split needed); wall sample under 1.2 mm: 2.0 % (current 2.4 %).
Still short of the reference: front shoulders at x -52 (52 vs 85 mm, 33 mm short) and x -105 (75 vs 90), because the lean linkage swings to z 120 at x -40 inside y 52..115; tail ends x -438 (ref -468, 30 mm short) at the rear wheel arch limit; top-view tail taper 49 vs 40 mm at x -400.

## Rev 5 - old skin features stripped, reference features as geometry (image 59)
Removed from the concept skin: old flank intake scoops, nose LED holes, hood scoop, roof gill banks, hourglass canopy cut and cage, shoulder bevel (shoulder_cut) and the old rear fender flare. Kept: shell, hinge ears and pin, frame relief, wheel and swing channels, 3-piece split (cuts now x -150 / -300: the front piece was 227 mm, bed is 220), tab posts, wing mounts, tail-lamp face recess.
Feature checklist (ref_features() in body3_build.py):
| reference feature | state |
|---|---|
| hexagonal glazing opening, 45 deg rim, raised bezel | present (cut + 3.6 mm bezel struts), opening is 70 mm wide (roof flat is 76), ref glass is ~136 wide |
| raked windscreen | present as the raked roof panel (z 84 at x -72 to 124 at -151), opening cut through it |
| side window with angular lower edge | present, 0.8 mm recess in the flank |
| door panel with big diagonal crease | present as a raised 4 mm ridge on the diagonal, not a two-plane panel |
| second sill panel, stepped thick pod, rivet dots | present: 3 mm step panel z -25..-6 and r 1.6 mm domes every 14 mm on both sides |
| door intake grille (louvred slots) | present: 4 through-slots 30 x 2.4 mm each side |
| slim vent behind the door | present: 3 vertical through-slots each side |
| hood/shoulder vent grille | present as 3 slots in the shoulder shelf at x -306..-322 (ref has it at the rear shoulder; no front one: arm sweep) |
| mirror / lamp pods on roof corners | present (10 x 10 x 7 mm blocks at x -150, y +-36) |
| roof ridge, integrated roll bar, rear lamp bar | present: 2.5 mm ridge x -236..-296; roll bar 15 mm tall at x -240 braced back to the deck; lamp bar 3 mm proud on the tail face |
| open engine bay with vented hood cutout, mesh grille | present: 60 x 60 mm opening in the deck x -300..-360 and a 3 x 11 cell mesh across its rear edge x -360..-375 |
| rear fender, big polygonal wheel arch | arch present (straight-edged hull trim over the tyre and arm travel); the old flare is gone and no new fender flare was added |
| angular tail and tail lamp | present (tail face to z 105, lamp recess + bar) |
| chisel nose, centre badge boss, lower splitter | present: beak to x 62, 5 mm boss, 3-sided splitter wedge |
| shoulder facets running into the arch | partial: one shelf stepping down from the cowl, cut into arches by the arm window; no extra facet planes |
| pink accent lines, 1.4 x 0.7 mm grooves | present: door diagonal, sill, rear fender, shoulder shelf, deck stripes (not the front shoulder wedges) |
| x | half-width cur | new | ref | top z cur | new | ref |
|---|---|---|---|---|---|---|
| 30 | nan | 29 | 38 | nan | 51 | 57 |
| 0 | 44 | 52 | 60 | 48 | 61 | 72 |
| -52 | 46 | 52 | 85 | 64 | 77 | 81 |
| -105 | 52 | 75 | 90 | 68 | 104 | 101 |
| -200 | 83 | 95 | 91 | 101 | 128 | 126 |
| -290 | 70 | 95 | 91 | 95 | 133 | 130 |
| -350 | 54 | 60 | 81 | 97 | 119 | 122 |
| -400 | 49 | 44 | 40 | 89 | 111 | 111 |
| bbox current | L 468 W 172 H 136 | | | | | |
| bbox new | L 502 W 190 H 171 | | | | | |

| dimension (mm) | before | new | reference |
|---|---|---|---|
| length | 468 | 502 | 523 |
| width | 172 | 190 | 182 |
| height above floor | 136 | 171 | 156 |
| nose tip x | 30 | 62 | 55 |
| canopy top z | 110 | 145 | 130 |
| deck z at x -400 | 90 | 112 | 111 |
Skin 283 g, all printed 946 g, total 2398 g. 132 tests pass, clearance clean, swing 0 hits 0..35 deg at 1 deg, pieces watertight, headroom 25-76 mm (13 mm at the beak tip). Wall sample under 1.2 mm: 3.6 % (was 2.0 %): the slots, mesh cells and ridge edges; not tuned yet.

## Rev 6 - traced profiles, contour height field, shoulders, glazing, scoops (reference sheet image 60)

Build unchanged: `WS03_SKIN=concept python body3_build.py && WS03_SKIN=concept python split_shell3.py`. Trace: `python tools_skin/trace_ref.py IMAGE60` writes `skin_trace.npz` (side roofline, plan half width, front section, contour height field); `skin_hf.py` turns the field into a closed height-field cap that `solid()` intersects with the plan, side and section prisms (and offsets by 2.4 mm for the cavity). Sheets: `WS03_rev6_{iso,side,top,front,rear}.png` (previous / new / reference, red = traced outline).

Scale: x from the side view (front axle px 200 = x 0, 0.862 mm/px, wheelbase 450), top view mapped onto the same x extent, z so the body height (256 px) is 169 mm above the frame floor (z -26), y so the top-view body width is 170 mm. Nose clamped to x 45-49 (reference 43) because the hinge ears sit at x 21; tail kept at x -438 (reference -468), the rear wing hangers and rear-arm channels set that.

What changed
- Profiles come from the trace, not by eye: roofline (nose 63 -> hood 86 -> raked windscreen to the header at x -171 -> flat roof z 129-133 to x -290), plan (narrow nose, 83 mm half width from x -124, 84 at the rear fenders), pods clipped by the traced plan (no more fixed y 92 shoulders).
- Contour field: z(x, y) = roof(x) - (Hc(x) - H(x, y)) x 169 mm, floored at z 20 and smoothed (2.5 mm grid). The roof is flat to about 15 mm off the centre line and falls off in ~60 degree flanks (z 98 at y 40, 57 at y 60, 22 at y 70 at x -250); the engine-bay hump stays high and wide (z 139 to y 40 at x -350). This is the shoulder cut: the old shelf and pods are gone.
- Windscreen: raked trapezoid, half width 45 at the base (x -100) to 35 at the roof header (x -164), glazing 1.0 mm below the surface (1.4 mm of skin left), raised 1.5 mm bezel 5 mm wide around it.
- Side windows: large raked polygons (rising front edge x -188 z 99 -> -206 z 123, angular lower edge to x -292), 1.0 mm recess, 1.5 mm bezel.
- Hood scoops: twin raised angular wedges (7 mm at the mouth, flush behind), open cavity, mouth slot and a through hole in the hood, mirrored; slim vents (3 x 2.4 mm slots) behind the side windows; louvre slits on the door; lamp pods at the roof corners.
- Kept from rev 5: door ridge, stepped sill with rivets, roll bar and roof ridge, engine-bay opening with mesh grille, tail lamp bar, badge boss, splitter, sill/fender/deck pink grooves. Dropped: the door-diagonal and shoulder pink grooves (they ran along the flank crease and made non-manifold edges); the door ridge carries that line.
- Split: cuts at x -152 / -300 with registration dowels, four 3.2 mm holes (two under the roof, two low on the flanks) per cut in pads fused to the inside of the wall (use 3 mm pins, e.g. filament offcuts). Pieces 201 x 172 x 136, 148 x 172 x 173, 140 x 168 x 152 (bed 220 x 220).

Checks (all with WS03_SKIN=concept): body and the three pieces watertight; swing sweep 0 hits at 0-35 deg in 1 deg steps; headroom over internal parts 19 mm (nose) to 76 mm, 22 mm over the motor; 192 tests pass, 1 xfail (legacy `tests/test_body.py`, `tests/test_assembly.py` and `test_strength_factors` excluded, as before); wall samples under 1.2 mm 2.8 % (rev 5 3.6 %, default skin 2.6 %); printed parts 930 g, total 2382 g (rev 5 2398 g), front weight share 63.7 %.

Numbers (previous = rev 5, ref = traced image 60; nan = engine-bay opening or front arm window)

| x | roof z prev | new | ref | half-width prev | new | ref |
|---|---|---|---|---|---|---|
| 30 | 51 | 59 | 60 | 29 | 29 | 29 |
| 0 | 61 | 67 | 68 | 52 | 52 | 54 |
| -50 | 77 | 80 | 80 | 52 | 52 | 69 |
| -100 | nan | 86 | 86 | 73 | 72 | 81 |
| -150 | nan | 107 | 108 | nan | 85 | 81 |
| -200 | nan | 129 | 128 | 95 | 83 | 79 |
| -250 | 131 | 133 | 131 | 95 | 82 | 78 |
| -300 | nan | nan | 131 | nan | nan | 81 |
| -350 | nan | nan | 139 | 60 | 84 | 82 |
| -400 | 111 | 111 | 124 | 44 | 54 | 78 |

| bbox | L | W | H |
|---|---|---|---|
| prev | 502 | 190 | 171 |
| new | 489 | 172 | 172 |
| ref (trace) | 515 | 170 | 169 |

Height field: skin surface z vs the traced contour field z_ref(x,y)
| x | y=0 new/ref | y=20 | y=40 | y=60 |
|---|---|---|---|---|
| -60 | 81/82 | 85/82 | 81/82 | nan/73 |
| -120 | 93/95 | 93/95 | 93/95 | 70/83 |
| -180 | 132/133 | 132/133 | 121/123 | 55/93 |
| -240 | 146/131 | 146/128 | 101/103 | 51/64 |
| -300 | nan/132 | nan/127 | nan/102 | nan/67 |
| -350 | nan/139 | nan/139 | 119/138 | 45/123 |
| -400 | 111/112 | 111/119 | 111/124 | nan/114 |
mean |dz| 8.4 mm, max 78.6 mm

Not matched / flagged
- Front shoulders: the plan is traced (nose to 59 mm half width at x -3, 79 at x -87) but the lean-linkage window (arm sweep, y 52-100, x +15..-123) is still cut out of the skin; at x -50 the half width is 52 mm against a traced 69. This is the open arch with exposed wishbones the reference shows.
- Tail ends at x -438 (reference -468) and is narrower at x -400 (54 against 78 mm).
- Dropped pink grooves on the door diagonal and shoulder; the lap joint tried first (tongue and rebate) was dropped for dowels because its 1 mm layers left self-overlaps in the exported STLs.
- The STL exporter welds near-coincident vertices (sub-micron tangent sheets between features); `body3_build.main` separates such pairs by 12 microns and drops collapsed slivers.
