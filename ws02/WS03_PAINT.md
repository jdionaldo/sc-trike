# WS-03 paint and decal guide (body)

Recessed areas (0.8 mm deep) are meant for a contrasting paint; print the body in the main colour.

| area | colour | notes |
|---|---|---|
| Body shell (four pieces) | main colour (red/orange/yellow) | seam sits on the centre line, join with the seam screws |
| Canopy recess on the roof | gloss black | glass look; the roof spine runs through it |
| Roof access hatch lid | black or carbon wrap | sits over the battery and ESC, 0.25 mm gap |
| Two flank panels (low sill and the diagonal panel) | black | the diagonal split from the references |
| Triangular vent (honeycomb), louvre slots, roof grilles | leave open, back with black mesh | motor cooling |
| Nose light-bar pocket and tail light slot | white LED strip behind clear tape / red | |
| Wings (on the front carriers), skid plate | white / light grey | skid slots mirror the reference X pattern |
| Screw head circles | black dots | 12 per body half |

Decal positions: "REVERSE TRIKE" on the upper flank between the louvres and the front window edge (x -200 to -130), model mark on the tail slot.

## Rendered scheme
`python w3_paint.py [lean] [steer]` writes `out/WS03_painted.glb` with per-face colours (body red; canopy, flank panels and roof hatch black; rocker band grey; wings and skid white; gold gears and pulleys; blue electronics), and `blender -b --python blender/render_glb.py -- out/WS03_painted.glb out/renders/ws03` renders iso, side, top and front PNGs.
