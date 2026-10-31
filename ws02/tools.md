# SolidCraft tools actually available

Discovered with `solidcraft-cli commands` (exposes the list below), `solidcraft-cli exec engine.describe '{"command":"<id>"}'`, and the MCP server (`mcp__solidcraft__*`: batch, execute, list_commands, describe_command, measure, inspect_design, body_topology, set_parameter, export, screenshot, save, open, new_design). Python 3.12 venv in `.venv` (system Python is 3.9).

CLI: `solidcraft-cli run script.json --out part.stl --out part.step` replays a command list; `eval`, `snapshot --section`, `script` also exist.

| Need | Commands |
|---|---|
| Sketch + constraints | sketch.create, sketch.line, sketch.rectangle.*, sketch.circle.*, sketch.arc.*, sketch.dimension, sketch.constraint.*, sketch.finish |
| Solids | solid.extrude (join/cut/new/intersect), solid.revolve, solid.sweep, solid.loft, solid.box/cylinder/sphere/torus/cone |
| Edge ops | solid.fillet, solid.chamfer, solid.draft, solid.shell |
| Holes/threads | solid.hole, solid.thread, plastic.boss |
| Patterns | solid.pattern.rectangular, solid.pattern.circular, solid.pattern.path, solid.mirror |
| Booleans/moves | solid.combine, solid.split_body, solid.move, solid.scale |
| Parameters | parameters.add, parameters.change, set_parameter (MCP) |
| Components/joints | component.create, joint.create, joint.limits, joint.drive, joint.solve, inspect.interference, inspect.clearance, motion.study |
| Measure | inspect.measure, inspect.center_of_mass, component.properties |
| Export | file.export, file.save_mesh (STL), STEP via `--out x.step` |

Differences from the brief: surfaces (surface.*), sheet metal, plastic (boss/lip/snap_fit), rib/web, motion studies and interference/clearance inspection ARE listed. The brief said they are missing; I will use them only after testing each, and still keep validate.py as the independent check. Exact parameter names are to be read per command with `engine.describe` before use; none are assumed.

## Verified behaviour (Phase 2)
- Script format: a JSON list of `{"command": id, "params": {...}}`; `solidcraft-cli run script.json --out a.stl --out a.step`.
- `solid.box` / `solid.cylinder` / `solid.cone` take `operation` (new|join|cut) and `targets: [body]`; the first call uses `operation: new, body_name`.
- Joins that only touch a face are refused ("faces flush"); overlap the host body by 0.4 mm. Coincident circular edges in a union fail with "no result"; offset the radius or build the shape as one revolve.
- `solid.chamfer` refuses a smooth edge and a blend taller than the wall; a 45 degree flange underside is built with `solid.revolve` or `solid.cone` instead.
- `sketch.create {plane: "XZ"}` has its sketch y running toward world -Z; `cad.revolve` flips it. `plane: "XY", offset: w` puts a profile at height w.
- `solid.cylinder` accepts `axis: "X"|"Y"|"Z"|[x,y,z]`.
- Surfaces, sheet metal, joints and interference tools exist in the command list but were not needed for Phase 2; Phase 3 tests the joint and interference commands before relying on them.
