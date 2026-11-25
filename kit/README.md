# Fugu kit pipeline

Gate chain (run from the project root; exit code of every stage must be 0):

1. `soma build` then `python tools/collide.py` (SOMA python: /Applications/SOMA.app/Contents/Resources/python/bin)
2. `soma export --all --format stl --detail fine --out <dir>`
3. kit venv (trimesh, shapely, manifold3d, numpy, scipy, networkx, rtree, mapbox_earcut, lxml): `python kit/build_kit.py <dir> --out kit/print` (repair, shell mesh polish via `polish_stls.py` (`--no-polish` skips), split to bed with pins, orient, oriented STLs, parts.json)
4. `python kit/mesh_audit.py kit/print/stl kit/print/mesh_audit.json`
5. `python kit/make_manifest.py` then `cd kit/print && python ../bambu_kit.py kit_manifest.json --check` (Bambu Studio CLI slice of every plate)
6. `python kit/make_docs.py` (bom.md, assembly_manual.md)

`kit/registry.py` is the part registry (every printed STL stem must resolve, step 3 fails otherwise). `kit/p2s_profile.config` is the printer/process profile extracted from the user's saved P2S project.

Suspension + drivetrain kit (front wishbones, lean head, knuckles, steering, stops, rear arm, belt drive, motor plate, wheels): after step 5,
`python kit/make_susp_drive.py`, then `cd kit/susp_drive && python ../bambu_kit.py kit_manifest.json --check`, then `python kit/make_susp_drive.py --docs`
(kit/susp_drive/README.md). Bought parts for both: `kit/hardware.py`.
