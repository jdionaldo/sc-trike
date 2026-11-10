# WS-03 body shell rebuilt from the Pepakura blueprint (sheet 71)

Branch `ws03-blueprint-shell` (from `ws03-skin-fit` 9f7f702). Nothing merged to main. Sheet: `sheet71.webp`.

## Pipeline
| step | file | what |
|---|---|---|
| 1 trace | `trace_flat.py` -> `flat_patterns.json`, `flat_P*.png`, `flat_patterns_traced.png` | every flat pattern of the layout: red cut line -> outline polygon (colour segmentation + contour), blue lines -> fold segments (Hough). Outlines only; the windows of P4/P5/P9 are not in the polygons |
| 2 facet / fold | `shell71.py` | 14 parts as facet strips, the rail topology following the traced patterns, 3D positions read from the five views (side/top/front/rear/perspective) in sheet mm, then scaled by `SCALE` = 1.46 (width 139 -> 203 mm like the previous skin; length 278 -> 406; height 102 -> 149), nose at chassis x +60, belly z -29. Every planar facet is thickened 2.4 mm inward (prism hull + edge joints, manifold3d) |
| 3 compare | `render_views.py` -> `overlay_final.png` | z-buffer renders in the sheet's five views, silhouette overlaid on the sheet (red = model, green = sheet) |
| 4 print / fit | `fit71.py`, `export71.py` | cuts: grille slots (P1), vent slots (P9), roof/windshield windows (frames), swing channels + rear travel channels of the cage, and the swept hull (+1.5 mm) of every front-mechanism part that touches a panel over lean -20..20 / steer -17..17; loose slivers dropped |
| 5 outputs | `stl/P*.stl`, `WS03_blueprint_shell.glb`, `shell71_report.json` | 15 meshes (14 sheet parts; P7 x2, L/R pairs), one named GLB node each |

## Result (honest)
* Built: all 14 parts, watertight, 2.4 mm walls (P4/P5 are solid 4.8 mm plates, not folded box sections), each fits a 220 x 220 bed (largest: roof frame 166 x 161), so no further split and no dowels are needed. Overall 399 x 169 x 146 mm.
* Hardware: 0 mm3 overlap with every assembly item over lean -20..20 x steer -17..17 (motor, servos, rear shock, rear arm and diff never touched a panel).
* Does NOT match the sheet 1:1. Silhouette IoU against the sheet views: side 0.45, top 0.58, front 0.56, rear 0.50, perspective 0.56. The panels are located from the views by eye and from an AI-generated sheet whose patterns are not geometrically foldable: tab numbers could not be used to derive the folds exactly. Folded flat-pattern areas were not reproduced.
* The front mechanism (arms, uplinks, tie rods) sweeps through the flank where the sheet puts P2 / front P8; those panels lose ~70 % (P2) and ~30 % (P8) of their volume to the arm window, so the front flank is open.
* The sheet's wheelbase does not fit the chassis (sheet shell 278 mm vs wheelbase 450 mm at 1:10-ish): the rear tyre sits behind the tail, the "rear wheel opening" is the gap between the P10 covers and the diffuser.
* Panels are butted at the sheet's tab edges, not joined: no dowel bosses, no gluing flange were modelled.
