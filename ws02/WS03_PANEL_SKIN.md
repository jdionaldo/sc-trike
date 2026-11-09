# WS-03 panel skin (branch ws03-panel-skin) - layered, panel-by-panel standalone skin

Build: `PYTHONPATH=. python pskin_export.py` (-> out/pskin/skin.stl, skin_front.stl, skin_rear.stl), `python tools_skin/pskin_export_glb.py OUT.glb`.
Checks: `tools_skin/pskin_iou.py`, `pskin_thick.py`, `pskin_render.py`, `pskin_compare.py`, `pskin_overlay.py`. Rev 9 chassis build untouched (nothing outside the new pskin_* files and tools was edited).

## Method (not a lofted skin)
- `pskin_core.py`: sheet-68 registration (plan x 0.6517 / y 0.65 mm/px, side 0.6258 x / 0.6546 z, fitted to the user's masks), a vertex/panel graph, T-junction detection, a planarity solve (every panel's vertices fitted to one plane, shared vertices shared; residual 1e-4 mm), panel orientation propagation, and a closed 2.4 mm wall: every vertex moved to the intersection of its incident panel planes shifted 2.4 mm inward (same topology, watertight by construction; a mitred-slab union was tried first and left pinch slivers).
- Layer A (`layer_a`, top view): 19 half-panels: hood centre, hood side (red quads), fender tops, cowl side, windscreen, A-pillar triangle, shoulder deck, three greenhouse glass strips, roof, rear gusset/quarter panels, deck, fender, tail. Plan outline = mask polygon (11 vertices); heights from the mask roofline and my reading of the side view. Checkpoint: `WS03_panel_A_plan_overlay.png`.
- Layer B (`layer_b`, side view): nose and rear zone = one bevel + one flank cell per station; door zone = panels traced from the sheet side view (door x3, front pillar x2, sill x3, rear door corner). Checkpoint: `WS03_panel_B_side_overlay.png`.
- Layer C (`pskin_detail.py`, `pskin_export.py`): grooves 1.2 x 0.7 mm (windscreen, side glass, hood panels, vent frame, headlights, grille, tail lights, bay rim, roof stripes, red sill/fender lines), through slots (hood vent 3, door louvres 4, quarter intake 5 per side, grille holes 12), twin hood scoops, engine-bay opening, mini spoiler + legs, two grab rails, 4 dowel pads/holes at the x -165 split. All cutters are collected and subtracted in one boolean (sequential booleans blew up).

## Numbers
120 panels (60 per half), skin 391.7 x 187 x 169.5 mm (length unchanged ~395: the masks fix it), volume ~291 cm3 (~360 g PLA at 1.24 g/cm3 solid; not slicer-tested). Skin and both pieces watertight (front 199 mm, rear 192 mm, bed 256). Wall median 2.38 mm, 2.8 % of samples under 1.2 mm (rim, groove edges).
Silhouette IoU against the user's masks (skin incl. spoiler; side vs the wing-tab-free mask): plan 0.972, side 0.944 (raw mask 0.93). Rev 17 was 0.984 / 0.952.
Facet rule: NOT met. 101 of 231 panel edges longer than 3 mm are under 15 deg; most are 0 deg splits between station cells (BV/LW strips) that should be merged into one panel, the rest are the plan outline corners the mask itself carries (11-13 deg) and the roof/deck break.

## Honest differences to sheet 68 (see `WS03_panel_cmp_{top,side,front,rear,q34}.png`, sheet left, ours right; renders are not registered to the sheet)
- Panel layout matches the sheet's big regions (hood, red hood quads, windscreen hexagon, greenhouse strips, roof, bay), not its many small lines: rear quarter swallow-tail, door diagonal creases, front fender flare shapes and the rear fender rail are not separate panels (grooves only for the red lines).
- Flanks are near-vertical flat walls with station seams; the sheet's flank is more sculpted. Nose chisel and front fascia are coarse; headlight/grille grooves projected from the front view land on the small nose panels, positions are approximate.
- Heights were solved to planarity and moved several mm (up to ~12 mm at shoulder vertices S3/S5, tail ridge) from the side-view reading; front/rear views were only used for detail placement, not as a height constraint.
- Wing/roll hoop off; spoiler and rails are rev 14 numbers placed by hand; no roof lamps, no bull bar, no side mirrors.
- The tool-chain was not run on the rev 9 chassis; it is independent.
