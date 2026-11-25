import math
import cadquery as cq
from .params import *
from .util import hull, fuse


def make_wheel(od, width, flip=False):
    """Knobby tire and purple multi-spoke rim, axis X, centred at the origin.
    Spokes face +X (outer side of a right wheel); flip=True faces them to -X."""
    Ro, hw = od / 2, width / 2
    Rc = Ro - KNOB_H
    Rr = Ro - TIRE_HEIGHT                      # rim outer radius
    # --- tire: ring with chamfered shoulders + staggered knobs
    prof = [(-hw, Rr - 5), (-hw, Rc - 35), (-hw + 35, Rc), (hw - 35, Rc), (hw, Rc - 35), (hw, Rr - 5)]
    core = cq.Workplane("XY").polyline(prof).close().revolve(360, (0, 0, 0), (1, 0, 0)).val()
    pitch = 2 * math.pi * Rc / KNOBS
    kt = pitch * 0.48
    kw = width * 0.30
    ctr = (cq.Workplane("XY").box(kw, kt, KNOB_H + 10).faces(">Z").chamfer(kt * 0.22)
           .val().translate((0, 0, Rc + (KNOB_H - 10) / 2)))
    sw = width * 0.24
    sh = KNOB_H * 0.9 + 35
    sho = (cq.Workplane("XY").box(sw, kt, sh).faces(">Z").chamfer(kt * 0.22)
           .val().translate((0, 0, Rc - 35 + sh / 2)))
    knobs = []
    for i in range(KNOBS):
        a = 360.0 * i / KNOBS
        knobs.append(ctr.rotate((0, 0, 0), (1, 0, 0), a))
        for s in (-1, 1):
            k = sho.translate((s * (hw - sw / 2), 0, 0))
            knobs.append(k.rotate((0, 0, 0), (1, 0, 0), a + 180.0 / KNOBS))
    tire = core.fuse(*knobs).clean()

    # --- rim: barrel, hub and tapered spokes in a plane near the outer side
    barrel = (cq.Workplane("XY").polyline([(-hw + 15, Rr - 38), (-hw + 15, Rr), (hw - 15, Rr), (hw - 15, Rr - 38)])
              .close().revolve(360, (0, 0, 0), (1, 0, 0)).val())
    x0 = hw - 70
    hub = cq.Workplane("YZ").circle(80).extrude(70).val().translate((x0 - 40, 0, 0))
    cap = cq.Workplane("YZ").polygon(6, 95).extrude(16).val().translate((x0 + 30, 0, 0))
    r1, r2 = 60, Rr - 20
    spoke = hull([(x0 + sx, y, z) for sx in (-14, 14)
                  for (y, z) in [(-20, r1), (20, r1), (-34, r2), (34, r2)]])
    spokes = [spoke.rotate((0, 0, 0), (1, 0, 0), 360.0 * i / SPOKES) for i in range(SPOKES)]
    rim = fuse([barrel, hub, cap] + spokes)
    if flip:
        tire = tire.rotate((0, 0, 0), (0, 0, 1), 180)
        rim = rim.rotate((0, 0, 0), (0, 0, 1), 180)
    return tire, rim, Rr
