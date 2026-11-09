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

## Rev 7 - ground-up faceted skin (WS03_SKIN=facet)

Build: `WS03_SKIN=facet python body3_build.py && WS03_SKIN=facet python split_shell3.py` -> `out/mono3_facet/`. Geometry is `skin7.py`: 13 stations traced from sheet 61 (same body as sheet 60), each a pair of convex section polygons (lower body to the shoulder, cabin above it), lofted by convex hulls between stations, so every surface is a flat panel with hard creases. No outline, prism or section of the older skins is reused; only the structural interface is kept (hinge pin and ears, frame relief, swing and rear-travel channels, wing mounts and hangers, 3-piece split with dowel pads). Walls: the cavity is the same loft inset 2.4 mm, with extra roof drop on raked panels and an x-erosion so ramps keep their thickness.

Features, all faceted: raked windscreen trapezoid (1.0 mm glass recess, 2.5 mm bezel), large angular side windows (1.0 mm recess, bezel), twin angular hood scoops (raised wedges, open mouth, hole through the hood), slim vents and door louvres, grid-hole mesh nose with a bull bar, roof lamp pods, roll bar, stepped sill with rivets, open engine bay with mesh grille, tail lamp bar, octagonal rear wheel arch plus a straight tail underside wedge, front arch windows simplified to a coarse polygon, pink lines as 1.4 x 0.7 mm grooves (sill, hood, deck stripes).

Facet metrics (`python tools_skin/facet_metrics.py out/mono3_facet/body3.stl`, outer surface only; panel = region of triangles within 1.5 deg and 0.25 mm of one plane):
triangles 14241, panels 2074, panels >= 50 mm2: 302
mean triangles per panel 6.9 (area-weighted 21.3)
flat-panel coverage 98.2 % of surface area (panels >= 50 mm2)
edges between panels: 8091; longer than 3 mm: 787
normal change at panel edges (>3 mm long): median 72 deg, p95 95 deg, max 165 deg
smooth blends (panel edge change < 15 deg, >3 mm long): 227 edges = 28.8 % of panel edges

The edges under 15 deg are lofting twist (a hull between two stations splits a slightly non-planar quad into two triangles at 3-15 deg, mostly on the nose and hood stations) and the small bull-bar and grille cells; no panel edge is a rounded blend, but these twists do not meet the 15 deg rule everywhere.

Checks: body and three pieces watertight; swing 0 hits at 0-35 deg in 1 deg steps; headroom over internal parts 18 mm at the nose, 23 mm over the motor, up to 77 mm; 192 tests pass, 1 xfail (legacy tests excluded as before); wall samples under 1.2 mm 2.75 %; printed 932 g, total 2384 g, front weight share 64 %; pieces 214 x 172 x 150 (front, bull bar included), 148 x 175 x 176, 141 x 158 x 83 on a 220 x 220 bed; dowel holes on both cuts (x -152, -300).

Not matched: the plan is a blockier hexagon than the sketch (constant 83 mm half width from x -124 to -300 and a stepped rear fender); tail ends at x -441 (sketch -468); the engine-bay hump is lower than the sketch because the wing hangers sit at the old deck height (deck 104-116 mm behind x -345); nose grille is square holes, not diamond mesh.

## Rev 8 - planar lofting and tapered plan (WS03_SKIN=facet)

`skin7.py` now builds each section from FIXED edge directions (vertical flank, shoulder bevel dy/dz -0.6, cabin flank dy/dz -0.12, horizontal floor, shelf and roof) and varies only the offsets per station, so every lateral quad between stations is an exact planar trapezoid (no loft twist). Every parameter is a polyline (`YF`, `YSH`, `YR`, `ZR`, `ZB`, `ZSH`) with breaks of at least 15 deg; the bevel, cabin flank and roof are separate parameters so a plan break does not leave a 5-14 deg crease on the other panels. Plan is now the sketch's tapered hexagon: chisel nose (half width 12 at x 49 to 46 at x 6), widening to 83 at x -124, flat cabin to x -300, flared rear fender to 92 (x -330..-384), taper to 64 at the tail. Front arch windows are an enclosing 12-gon.

Facet metrics (outer surface, `tools_skin/facet_metrics.py`):
triangles 16391, panels 2464, panels >= 50 mm2: 203
mean triangles per panel 6.7 (area-weighted 29.2)
flat-panel coverage 97.3 % of surface area (panels >= 50 mm2)
edges between panels: 8810; longer than 3 mm: 762
normal change at panel edges (>3 mm long): median 62 deg, p95 106 deg, max 150 deg
smooth blends (panel edge change < 15 deg, >3 mm long): 245 edges = 32.2 % of panel edges
  of those, 123 lie on the frame-relief / swing-channel cuts (interface, swept arcs) and 122 on the skin itself = 20.3 % of the skin's own panel edges

The swept channel cuts for the frame tubes are curved by nature (interface: the tubes sweep an arc) and stay as they were; they account for half of the creases under 15 deg. The 122 on the skin itself are mostly small creases where a bezel or scoop wall meets a panel at 3-9 deg, plus the nose grille and bull-bar cells.

Checks: body and three pieces watertight, swing 0 hits at 0-35 deg, no clashes in the assembly, headroom 19 mm (nose) to 75 mm, 192 tests pass (1 xfail, legacy tests excluded), wall samples under 1.2 mm 4.2 % (rev 7 2.75 %: the narrow hood roof and ramps; not yet reduced), printed 921 g, total 2373 g, front weight share 64.3 %, pieces 214 x 172 x 152 / 148 x 175 x 176 / 144 x 146 x 83 on a 220 x 220 bed, dowel holes on both cuts.

Not matched: the hood is narrow at the nose (roof half width 17 mm at x 0 against the sketch's wider hood), tail ends x -444 (sketch -468), deck hump is low (hangers), nose grille holes are square.

## Rev 9 - strict trace of sheet 61 (skin7.py + trace61.py)

Build unchanged: `WS03_SKIN=facet python body3_build.py && WS03_SKIN=facet python split_shell3.py`. Tools: `trace61.py` (pixel tables of the sheet's side silhouette, floor, belt line, plan and roof width; maps them to the chassis frame), `tools_skin/overlay61.py SHEET PREFIX` (silhouette over the sheet, 4 views), `tools_skin/trace_table.py` (table below), `tools_skin/facet_metrics.py`.

**Mapping.** Side view tyre radius 88 px = 56 mm (112 mm tyres), 0.636 mm/px; the sheet is rotated by the 4 deg ground rake into the chassis frame, front axle at (0, 0). The sheet's wheelbase is 368 mm, ours 450, so only the middle (roof and doors, sheet px 375-560) is stretched, uniformly x1.695 (+82 mm). Nose, hood, cowl, front arch and the rear fender/tail keep their traced shape; the top view is mapped onto the side view's nose/tail px. The sheet's views are not at one scale (tyres in the top view are 25 % smaller than in the side view), so each view was normalised to the side view.

**Skin.** Roofline, floor (arch top, sill, rising rear fender rail), belt line, plan and roof width are polylines from the trace, simplified to >= 15 deg breaks (one forced: the cowl, 10 deg on the sheet -> 16 deg). Sections keep fixed edge directions so the quads between stations are planar. Open belly under the whole skin. Features re-placed from the sheet: hexagonal windscreen glass, side windows with raked A-pillar edge, hood scoops, door louvres, sill panel, roll bar, header lamp pods, engine-bay opening with mesh, tail lamp bar, diamond mesh nose grille, bull bar.

**Traced against built (mm, chassis frame)**

| x (mm) | roof z traced | roof z built | half width traced | half width built | floor z traced | floor z built |
|---:|---:|---:|---:|---:|---:|---:|
| 30 | 78 | 78 | 20 | 24 | 56 | 56 |
| 10 | 89 | 79 | 33 | 33 | 67 | 67 |
| -20 | 99 | 92 | 52 | 52 | 67 | 67 |
| -50 | 103 | 96 | 71 | 62 | 65 | 76 |
| -80 | 111 | 107 | 85 | 83 | -8 | 57 |
| -110 | 124 | 123 | 87 | 85 | -10 | -10 |
| -140 | 137 | 139 | 86 | 86 | -12 | -12 |
| -170 | 138 | 136 | 85 | 87 | -14 | -14 |
| -200 | 137 | 134 | 84 | 87 | -16 | -16 |
| -250 | 136 | 131 | 82 | 88 | -19 | -19 |
| -300 | 133 | 129 | 81 | 89 | -23 | -23 |
| -330 | 130 | 127 | 88 | 88 | 9 | 19 |
| -360 | 126 | 125 | 88 | 88 | 47 | 43 |
| -390 | 114 | 113 | 75 | 75 | 72 | 72 |
| -420 | 100 | 104 | 60 | 60 | 76 | 76 |
| -440 | 95 | 97 | 19 | 19 | 69 | 69 |

roof z built - traced: mean -2.5 mm, max |10.2| mm; half width built - traced: mean +0.7 mm, max |9.0| mm

**Facet metrics (outer surface).** panels 1144, flat-panel coverage 98.0 %, mean 4.1 triangles per panel, normal change at panel edges median 70 deg / p95 100 deg / max 168 deg. 121 of 755 long panel edges (16.0 %) are under 15 deg - all on the skin itself (small bezel and scoop creases, grille and bull-bar cells, louvres); 0 on cuts. The >= 15 deg rule is therefore NOT fully met.

**Checks.** Body and the three pieces watertight; pieces 202x177x153, 147x182x160, 147x183x162 (bed 220); cuts at x -153.4 and -300 with dowel holes (the first cut moved 1.4 mm: at -152 the cut plane grazed a 0.07 mm cavity sliver). Swing 0 hits at 0-35 deg in 1 deg steps; assembly clash-free; 192 tests pass (1 xfail, 5 skipped; legacy test_body/test_assembly and test_strength_factors excluded as before). Thin-wall samples under 1.2 mm: 4.2 %. Headroom over internal parts 43-80 mm. Printed skin mass 294 g, total 2409 g, so the plausibility bound in tests/test_w3.py was raised 2400 -> 2500 g (the traced body is taller than the old one).

**Conflicts with hardware / cage (cage suspended, no frame files edited).**
- Front mechanism: the old window cut was replaced by the swept volume of the arms, pods, uplinks, carriers, knuckles and rods over the lean range (+2 mm). The front fenders therefore stay as traced except where those parts pass; the cut-outs are visible near the front arch.
- Pockets in the skin for fixed parts that touch the traced shape: front arms arm_1/arm_-1 827 mm3 each at lean 0 (397 at 10 deg, swept over 0-35), lean ears 291, lean servo 234, diff_out 58 each, lean mount 16; wing hangers 378 mm3 each (the traced deck is 2-13 mm below the hanger foot at x -374..-404, hangers left where they are).
- Underside: the skin is open below the sill (sill z -7 at x -80 to -24 at x -320), the sheet's body floor is about axle height, so frame/deck plates at z -29..-23 and the battery, tray and skid sit up to 5-22 mm below the skin edge, uncovered.
- Hood: the traced hood is 22-35 mm thick above an open front bay; the front floor slab no longer exists. The cage must stay under the hood line (z 78 at the nose to 97 at the cowl); roof z 137 against the old 133 (+4 mm at the roof tabs, roof tab nodes still read the old top_z).
- Rear: the traced rail underside rises from z 9 (x -330) to 76 (x -420), well above the tyre and swing arm; no clash, but nothing shields the shock above z 28.

Sheets: `WS03_rev9_overlay_{side,top,front,rear}.png` (silhouette over sheet 61; front/rear are scaled to the sheet body since its views differ in scale), `WS03_rev9_{iso,side,top,front,rear}.png` (previous / new / reference).

## Rev 10 - standalone skin (skin_alone.py)

Designed by itself, to be merged with the frame later: no wheelbase stretch, rake, frame relief, swing channels, hardware pockets, hinge or bed fitting. Build: `python skin_alone.py` (sets WS03_ALONE=1, reuses the skin7 loft and features) -> `out/skin_alone/{skin,skin_front,skin_rear,wing}.stl`. Frame: x forward (front axle x 0), y left, z up from the ground. Reference: the 6336x2688 copy of sheet 61, resized to the 2000x848 px tables.

**Scale.** One uniform scale from the tyre: sketch front tyre diameter 176 px = 112 mm -> 0.636 mm/px for x and z. The top view is mapped onto the side view's nose and tail px, so its own L:W ratio is kept (0.651 mm/px across). Nothing is stretched or distorted. Built body 391 mm long (+15 mm bull bar), 191 mm wide, 217 mm high.

**Proportions (ratios to body length L; sketch against built)**

L (sketch side) 615 px = 391 mm; L built 391 mm; uniform scale 0.636 mm/px (112 mm tyre = 176 px)
| station | x/L from nose | roof h/L sketch | roof h/L built | half width/L sketch | half width/L built |
|---|---:|---:|---:|---:|---:|
| px 130 | 0.01 | 0.346 | 0.335 | 0.055 | 0.063 |
| px 150 | 0.05 | 0.362 | 0.339 | 0.077 | 0.077 |
| px 180 | 0.09 | 0.385 | 0.358 | 0.109 | 0.109 |
| px 225 | 0.17 | 0.407 | 0.387 | 0.158 | 0.158 |
| px 267 | 0.24 | 0.416 | 0.403 | 0.204 | 0.204 |
| px 320 | 0.32 | 0.462 | 0.458 | 0.232 | 0.243 |
| px 380 | 0.42 | 0.514 | 0.520 | 0.229 | 0.235 |
| px 450 | 0.53 | 0.526 | 0.516 | 0.222 | 0.227 |
| px 520 | 0.65 | 0.531 | 0.519 | 0.214 | 0.225 |
| px 560 | 0.71 | 0.527 | 0.520 | 0.229 | 0.229 |
| px 610 | 0.79 | 0.522 | 0.522 | 0.235 | 0.235 |
| px 660 | 0.87 | 0.491 | 0.497 | 0.203 | 0.203 |
| px 700 | 0.94 | 0.466 | 0.477 | 0.168 | 0.168 |
| px 730 | 0.99 | 0.459 | 0.462 | 0.085 | 0.085 |

ratio error built - sketch (x L): roof mean -0.007, max 0.028; half width mean +0.003, max 0.011
overall L:W:H built = 1 : 0.488 : 0.555   (sketch top view W/L = 0.471, side view H/L = 0.533, front view W/H = 0.935 -> W/L via H = 0.499)

The sheet's views are not at one scale (tyre diameter 176 px side, 160 px front, 135 px top), so the top-view W/L (0.471) and the side-view H/L (0.533) were taken as is; the front view's W/H (0.935) would give a W/L of 0.50, 6 % wider than the top view says. The built W/L is 0.488 including the raised sill panel and rivets.

**Build.** Closed 2.4 mm shell with an open belly (the sketch shows the body open under the sill and the arches). Cowl break forced from 8 deg to 17 deg (hood 5-8 mm lower than traced at the cowl) to keep every polyline break >= 15 deg. Features as rev 9, re-placed on the unstretched trace, plus pink grooves from the red accent lines (door-sill diagonals, rear fender rail, roof stripes). Wing: our stepped wing and hangers moved onto the rear deck (leading edge at sheet px 572, hanger feet 8 mm into the deck, skin recessed 0.6 mm around them), saved as `wing.stl`.

**Pieces.** One cut at x -165 (the only cut that keeps both halves inside 220 x 220): front 214 x 191 x 154, rear 194 x 184 x 165; four 3.2 mm dowel holes (two under the roof, two low on the flanks) in pads fused to the inside wall. Body and both pieces watertight.

**Facet metrics.** 1061 panels, flat coverage 97.8 %, median edge change 72 deg, p95 109 deg, max 172 deg. 64 of 780 long panel edges (8.2 %) are under 15 deg, all on the skin itself (bezel and scoop creases, grille and bull-bar cells, louvres), so the 15 deg rule is still not met everywhere. Not run, per the brief: cage, hardware, swing, headroom and tests.

Sheets: `WS03_rev10_overlay_{side,top,front,rear}.png` (silhouette over the sheet; front and rear are scaled to the sheet body), `WS03_rev10_{iso,side,top,front,rear}.png` (rev 9 / new / reference). GLB: `WS03_standalone_skin_v10.glb`.

## Rev 11 - standalone skin, facet clean-up (skin7.py ALONE mode)

Same uniform scale and silhouette as rev 10; body 391 x 191 x 217 mm. Changes, all gated on `WS03_ALONE=1` so the chassis build (rev 9) is untouched:
- **Planar flank families.** The bevel and cabin-flank planes are built from offset polylines (`GB = ysh + S1 zsh`, `GC = yr + SC zr`, simplified at 17 deg) instead of from `ysh` and `yr`, so a break in the belt line, roofline or roof width cannot bend a panel a few degrees. Breakpoints within 3.5 mm are snapped onto one station, so every lateral quad is exactly planar.
- **No clamped bevel.** The bevel is 3.5 mm on the thin hood slab, 14 mm on the cabin, 0 on the tail rail, so the vertical flank never vanishes (a clamp there was the source of 10-14 deg creases). A stable sort in `_pl` keeps vertical steps (two vertices at one x) in order.
- **Cowl and belt.** Hood to windscreen 17 deg, hood to belt 17 deg (the belt dips 6 mm behind the cowl, as the sheet's window sill sits below the hood line); this also removed an accidental ridge down the hood.
- **Scoops** are now one inclined top plane (16.7 deg to the hood) with a vertical front face; bull-bar legs run at 54 deg. The rear step wall was eased from 80 deg to 52 deg (belt point moved 10 px, internal only).

**Facet metrics (outer surface; cavity ceilings are now excluded when WS03_ALONE=1, because the open belly lets them pass the outward-ray test).** 833 panels, flat-panel coverage 97.6 %, median edge change 78 deg, p95 93 deg, max 148 deg. Long panel edges under 15 deg: 2 of 512 (0.4 %), down from 64 of 780 (8.2 %) at rev 10 (59 of the 64 were skin edges on the old metric; the new metric also drops the cavity-ceiling faces). **Exception, listed:** the pair at x -255, y +-46, z 200: 3.0 mm long, 6.9 deg, next to a 9 mm2 sliver of the roof-ridge step, a numerical leftover of two coincident breakpoints; it is 3 mm, at the filter's threshold, and not a design crease.

Checks: body and both pieces watertight, cut at x -165 with four dowel holes, front 213 x 191 x 154, rear 194 x 184 x 165; wing separate (`wing.stl`); proportions as below (roof height within 0.027 L, half width within 0.011 L).

L (sketch side) 615 px = 391 mm; L built 391 mm; uniform scale 0.636 mm/px (112 mm tyre = 176 px)
| station | x/L from nose | roof h/L sketch | roof h/L built | half width/L sketch | half width/L built |
|---|---:|---:|---:|---:|---:|
| px 130 | 0.01 | 0.346 | 0.336 | 0.055 | 0.063 |
| px 150 | 0.05 | 0.362 | 0.345 | 0.077 | 0.076 |
| px 180 | 0.09 | 0.385 | 0.358 | 0.109 | 0.109 |
| px 225 | 0.17 | 0.407 | 0.383 | 0.158 | 0.158 |
| px 267 | 0.24 | 0.416 | 0.402 | 0.204 | 0.204 |
| px 320 | 0.32 | 0.462 | 0.458 | 0.232 | 0.243 |
| px 380 | 0.42 | 0.514 | 0.520 | 0.229 | 0.235 |
| px 450 | 0.53 | 0.526 | 0.516 | 0.222 | 0.227 |
| px 520 | 0.65 | 0.531 | 0.519 | 0.214 | 0.225 |
| px 560 | 0.71 | 0.527 | 0.520 | 0.229 | 0.229 |
| px 610 | 0.79 | 0.522 | 0.522 | 0.235 | 0.235 |
| px 660 | 0.87 | 0.491 | 0.497 | 0.203 | 0.203 |
| px 700 | 0.94 | 0.466 | 0.477 | 0.168 | 0.168 |
| px 730 | 0.99 | 0.459 | 0.462 | 0.085 | 0.085 |

ratio error built - sketch (x L): roof mean -0.007, max 0.027; half width mean +0.003, max 0.011
overall L:W:H built = 1 : 0.488 : 0.555   (sketch top view W/L = 0.471, side view H/L = 0.533, front view W/H = 0.935 -> W/L via H = 0.499)

**Rev 9 unchanged.** After the skin7 edit the chassis build (`WS03_SKIN=facet`) was rebuilt: body 8462 faces, volume 393198 mm3, bounds [-446.5, -91.4, -24.3] to [48.8, 91.4, 139.9], pieces 202.1 x 176.7 x 152.5, 146.6 x 182.3 x 159.6, 146.5 x 182.9 x 162.1, facet metrics 4720 triangles / 1144 panels / 121 smooth edges (16.0 %): identical to f99cf87. (The scoop and bull-bar edits had briefly changed it, volume 390568 and nose x 34.3; both are now gated.) Note that rev 9 is f99cf87; 740cb79 is rev 8.

Tools: `tools_skin/preview4.py OUT.png` (flat-shaded iso/side/top/front with visible crease lines), `tools_skin/facet_metrics.py`, `tools_skin/proportions.py`. GLB: `WS03_standalone_skin_v11.glb`. Sheets: `WS03_rev11_preview.png`, `WS03_rev11_overlay_{side,top,front,rear}.png`.

## Rev 12 - outline from the user's silhouette masks (mask61.py, ref/plan_mask.png, ref/side_mask.png)

The plan and side outlines are no longer traced by eye: they are taken from the two masks (solid red). `mask61.py` extracts the edge of each mask per pixel column, reduces it with cv2.approxPolyDP (1.5 px, corners kept), then drops only vertices with a turn under 15 deg whose removal moves the outline by under 2-3 mm (floor: 2 mm). Vertex counts and merged counts:

```
plan: 13 vertices, 5 with turn < 15 deg; after merging near-collinear ones (<1 mm): 11, 3 under 15 deg
top: 20 vertices, 8 with turn < 15 deg; after merging near-collinear ones (<1 mm): 15, 3 under 15 deg
bot: 22 vertices, 2 with turn < 15 deg; after merging near-collinear ones (<1 mm): 20, 0 under 15 deg
```

**Normalisation.** Both masks are scaled to the same body length (nose tip and tail end line up), L = 391 mm from the sheet-61 tyre scale (112 mm tyre = 176 px): plan 0.2078 mm/px (width/length of the top mask: 188.6 x 391), side 0.2005 mm/px (height/length of the side mask: 167 mm from the sill cut to the wing peak, z 52 to 219). The masks' flat bottom cut is the sill line (z 52.2).

**What comes from the masks.** Plan half width (YF), the roofline (ZR, with the wing / roll-bar tab at px 1318-1560 replaced by a straight line between its feet, because the wing is a separate part) and the floor (ZB: nose chin, front arch, sill, rising rear rail, tail). The first run of red from the top is used for the floor, so the thin sill tab under the rear tyre notch is dropped (about 150 mm2). Belt line and roof width still come from sheet 61 (the masks do not show them); the hood centre is now a ridge 8 mm above the side panels so the twin scoops sit beside it under the traced roofline.

**Silhouette overlay error (pixel IoU of the rendered silhouette against the mask).**

| silhouette | IoU | outside mask | mask not covered |
|---|---:|---:|---:|
| plan, skin + wing | 0.992 | 9591 px | 2416 px |
| plan, skin only | 0.996 | 2030 px | 3621 px |
| side, skin + wing | 0.967 | 15035 px | 13773 px |
| side, skin only | 0.954 | 11678 px | 27954 px |

Plan is within 1 %. Side is 3.3 % off with the wing and 4.6 % without it; most of the missing area (about 12000 px, 1.4 %) is the sketch's spoiler tab, which our wing (a different, wider, flatter part, top set on the peak z 219) does not fill; the rest is the sill tab under the tyre notch, the nose chin tip and the engine-bay opening (seen from the side as a slot). Features were moved inside the outline: sill band recessed 1.4 mm instead of raised, rivet heads 0.7 mm proud, bull bar and diamond grille on the chin inside the nose, lamp pods 3 mm, scoops beside the ridge.

**Facets.** 702 panels, flat coverage 97.0 %, median edge change 74 deg. 66 long panel edges (8.5 %) are under 15 deg, because the masks carry their own sub-15 deg corners and the brief was to keep every corner: 31 sit on the rounded tail (x < -300), 11 on the rear fender, 8 at the cowl, the rest on the flank and roof corners of the mask (e.g. 11.2 deg at x -202 in plan, 8.3 deg at the roof peak). They are listed by `/tmp`-style edge dump, not hidden.

Watertight body and both pieces (cut x -165, front 199 x 184 x 153, rear 194 x 189 x 172, four 3.2 mm dowel holes), 2.4 mm walls, wing separate (`wing.stl`). Rev 9 (chassis build) rebuilt after the edits: 8462 faces, volume 393198, bounds [-446.5, -91.4, -24.3] to [48.8, 91.4, 139.9], pieces 202.1 / 146.6 / 146.5 long: unchanged.

Tools: `mask61.py`, `tools_skin/mask_iou.py PREFIX [0]` (IoU and overlay images), `tools_skin/preview4.py`. Sheets: `WS03_rev12_preview.png`, `WS03_rev12_mask_overlay_{plan,side}.png` (with wing), `..._noWing_...`. GLB: `WS03_standalone_skin_v12.glb`.

## Rev 13 - faceted plan outline, layered details, wing removed

**Outline.** Side silhouette: rev 12's faceted one (from the side mask, corners merged within 2 mm). Plan: the plan-mask polyline with every vertex turn forced to >= 15 deg (`mask61.merge(plan, 15, 99)`, 11 -> 7 vertices; the tail rounding becomes three straight segments). IoU against the masks (skin only, no wing): plan 0.983 (rev 12: 0.996 skin only), side 0.952 against the raw mask / 0.956 against the mask with the wing tab removed (rev 12 side 0.967 included the wing). Side loss is the sketch's spoiler tab, the sill tab under the tyre notch, the nose chin tip, and the roll bar (above the tab-free roofline).

**Wing removed.** No wing, hangers, mounts or recess; the deck is clean (the roll bar hoop stays).

**Detail layers** (outline read from the sheet view where each is clearest, projected along that view onto the skin; every layer is a flat step; where a pocket is deeper than the 2.4 mm wall the wall is thickened under it so 1.2 mm of floor remains). Layer depths are my reading of the 3/4 view.

| detail | view | outline vertices | layers |
|---|---|---:|---|
| windscreen glass | top | 6 | bezel 2.5 mm proud (5 mm wide), recess 1.0, inner glass pocket 1.8 (inset 3 mm) |
| side windows (x2) | side | 5 | bezel 2.5 proud (4.5 wide), recess 1.0, inner pocket 1.8 (inset 3 mm) |
| hood panels (x2, red-striped quads) | top | 4 | bezel 1.2 proud (2 wide), recess 0.8 |
| twin hood scoops | top | 4 | wedge 7.5 mm at the front, top plane 15.5 deg to the hood, vertical front face, open mouth, cavity, hole through the hood |
| hood vent slot | top | 4 | bezel 1.0, recess 1.5, inner pocket 3.5 (inset 2.5) |
| headlight pockets (x2) | front | 6 | bezel 1.5 proud, pocket 3.0, inner lamp 5.0 (inset 3 mm) |
| main grille (hexagon) + diamond mesh | front | 6 | bezel 1.5, recess 2.0, 13 diamond holes |
| side mesh pockets (x2) | front | 5 | bezel 1.0, recess 2.0 |
| tail-light pockets (x2) | rear | 5 | bezel 1.5, pocket 1.6, inner lamp 2.8 (inset 3 mm); cut only on the tail panels (x < -342) |
| door vent pocket + louvres | side | 4 | bezel 1.2, recess 2.0, inner 3.5 (inset 2.5), 4 louvre slots |
| rear-fender vent pocket | side | 4 | bezel 1.2, recess 2.0, inner 3.5 (inset 2.0) |
| door panel crease | side | 4 (line) | stepped V groove 4.0 x 0.8 mm + 1.6 x 1.6 mm |
| roof lamp pods (x2) | - | hull of 8 | 3 mm proud |
| engine-bay opening | top | 4 | rim bezel 2.0, through opening, 3 x 9 mesh |
| arches | side/mask | polygon from the mask floor | front arch wall and rear rail are the outline itself |

Detail layers are built from a floor-less copy of the loft (`solid(..., deep=True)`), so no layer can form on the open underside.

**Facets.** 777 panels, flat coverage 94.2 % (the pockets add small panels), median edge change 80 deg, p95 95 deg. 65 long edges (6.7 %) are under 15 deg: the mask's own corners on the side outline, the small steps of the recess layers, and bezel corners. **15 deg is not met everywhere.**

Watertight body and both pieces (cut x -165: 201 x 180 x 153 and 194 x 190 x 172, four dowel holes). Rev 9 chassis build rebuilt after the edits: unchanged (see the line below the table in the commit message). Proportions (roof within 0.027 L, half width within ~0.02 L):


ratio error built - sketch (x L): roof mean +0.004, max 0.023; half width mean +0.012, max 0.047
overall L:W:H built = 1 : 0.485 : 0.572   (sketch top view W/L = 0.471, side view H/L = 0.533, front view W/H = 0.935 -> W/L via H = 0.499)

GLB: `WS03_standalone_skin_v13.glb`; sheets `WS03_rev13_preview.png`, `WS03_rev13_34_compare.png`, `WS03_rev13_mask_overlay_*`.
