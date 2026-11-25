# Decision log

## E0 Audit (baseline commit 131af50)
- Build ok (247 s, 95 parts). `tools/collide.py`: 4 overlapping pairs: Nose light strip in Front shell 78.1 mm3, Rear contact block in Canopy 226.1 mm3, cage vs motor plate 16.4 mm3, M6 shock pin vs cage 0.34 mm3 (pin through its bore, intended).
- Printer: NOTES.md says "H3C" (330 x 320 x 325 mm = Bambu H2C class), the user's saved Bambu projects are for a **Bambu Lab P2S, 256 x 256 x 256 mm**. The kit is sized for the P2S plate (5 mm margin) so it also fits the larger machine. NEEDS USER: confirm which printer is the target.
- Mesh audit of the exported STLs: Front shell has 2 enclosed voids (watertight but cavities), Cage has 4 non-manifold edges at one 0.1 mm spot. Front shell 423 mm and Cage 479 mm are longer than the bed, Canopy 329 mm too.

## E1 Collisions (user: "refine it")
- Nose light strip: trimmed against the Front shell, 77.7 mm3 removed (strip now touches the groove floor, glue face). Alternative (shifting the strip) would change the visible light line.
- Rear light contact block: cut against the Canopy roof, 226.1 mm3 removed of 1.6 cm3. Magnet pockets are unaffected (checked: part stays one valid solid).
- Cage left rail: notched 56.8 mm3 around the motor plate edge (x -41.6..-39.1, y -68.8..-61.8). The notch is a box cut through the 10 mm tube; FEM of the rail is still open, treat as a weak spot.
- Result: 4 overlapping pairs -> 1 (M6 pin in its bore, whitelisted). Build ok 256.6 s.

## E2 Kit prep (user: "refine it and prep it as a kit. use the skill you just made")
- Bed: P2S 256 x 256 x 256 mm, 5 mm margin, 22 mm between parts (10 mm gave "gcode path conflicts" on PETG plates with supports). Alternatives: H2C-class 330 x 320; rejected as the target because the user's saved projects (and the slicer profile used for the check) are P2S, and a 256 mm kit also fits the larger bed.
- Split: Front shell (423 mm) -> 2 pieces at y -125.4, Canopy (329 mm) -> 2 pieces at y -29.3, Cage (479 mm) -> 3 pieces. Cut planes are chosen within +-7 % of an even split where the section area is smallest. Joints: round pins (Ø8 for the 10 mm tubes, Ø1.6-2.0 in the 3 mm shell walls) 6 mm long into holes +0.15 mm, plus CA glue.
- Rear half of the Front shell is two disjoint side panels (SH1b1/SH1b2): printed as separate files (mesh audit flagged 2 bodies).
- Mesh repair before splitting: Front shell had 2 enclosed void shells, filled (dropped); Cage had one non-manifold edge at (37.0, 145.3, 172.4), the sliver face was dropped. Neither changes visible geometry. Better fix: remove the cause in the CAD (open).
- Orientation: best of 6 face-down poses by overhang area, bed contact and a tall-and-thin penalty, floating regions checked on the best 3. Result: 7 parts still have floating regions (CG1a, DT11, LT1, SH1a, SH1b1, SU1L/R); they carry supports in the Bambu projects (slice check passes).
- Registry: 36 designs, 52 printed files. Hardware (bought stand-ins) = anything named b_*, mock_*, servos, tyres, shock, pins.
- Material: PETG structure (decks, arms, diff cases, cage, contact blocks), PLA shell and lid, translucent PLA light strips (printed on their own plate).
- BOM part numbers: VERIFIED in retailer listings: Hobbywing QuicRun Fusion SE HWI30404317 (1800KV) / HWI30404318 (1200KV), Axial AXI43005 1.9 beadlock wheels 12 mm hex, Integy C26651RED 100 mm shock (listed for SCX10 III). Everything else ASSUMED or UNKNOWN in bom.md.
- Metrics vs previous commit (131af50): static interferences 4 -> 1 (whitelisted M6 pin in bore); printed files 0 oriented/bed-sized -> 52; mesh audit 0 flagged (open meshes 2 -> 0 after repair); Bambu P2S slice check: 11 plates, 0 problems, 59.3 h, 1804 g (slicer numbers).
- Not done: FEM of cage/shock load; tilt/hinge; 6 motion/collision sweeps (steering lock, bump, swing); symmetry check; assembly drawings; real chassis BOM part numbers; mounting of shell to cage uses M2 screws and bosses that exist in the model but were not individually re-verified; PETG filament preset in the Studio projects is the PLA preset from the saved project (swap AMS slot 4 to PETG).

## E3 Shell mesh polish (user: "go with recommendations... polished like it was injection molded", then "both")
- Print-mesh cleanup only. `kit/build_kit.py` now runs `kit/polish_stls.py` on the shell parts (Front shell, Canopy, Tail light housing, Grille insert, Nose and Tail light strips) after repair and before splitting (`--no-polish` skips it). manifold3d `simplify(0.05 mm)` collapses sliver and coplanar triangles. A part is accepted only if it stays one closed manifold with the same body count, volume moves by < 0.1 % and the bbox by < 0.05 mm; otherwise the original is kept and the reason logged. The 0.3 mm PANEL_GAP seams are untouched.
- Result on the current export: Front shell 5968 -> 2870 faces, Canopy 1176 -> 816, Tail light housing 15000 -> 1630, Nose strip 5254 -> 698, Grille unchanged. Tail light strip kept original (volume -0.146 %, over the 0.1 % limit).
- The CAD is NOT changed. The window/crease slivers remain in the generated B-rep: rebuilding the canopy side frame as one polyhedron (`panel_solid`) changed nothing (canopy faces 373 -> 375, small 74 -> 73, dust 114 -> 115), so it was reverted. They come from the transformGeometry stretch (planes become B-splines) and the other panel builders, not from the frame prisms.
