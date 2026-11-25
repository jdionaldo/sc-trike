"""One-piece printed 6-spoke wheels in the style of a forged concave racing wheel (six flat-topped spokes, wide at the rim and narrow at the hub, deep
dish, no lettering). The rubber tyre is a bought part: it sits on the barrel (bead seat diameter) between the two flange lips.

Built on the x axis, centred on x = 0, outer face toward +x. Mirror for the other side. Print with the outer face down (axis vertical), PETG.
Sizes: 1.9 in crawler wheel = 48.3 mm bead seat, 2.2 in = 55.9 mm bead seat (nominal inch rim diameters).
"""
import math
import cadquery as cq

LIP_H = 2.5              # flange lip height above the bead seat
BARREL_T = 3.0           # barrel wall under the bead seat
SPOKES = 6
HEX_AF = 12.0 + 0.3      # 12 mm wheel hex plus clearance
HEX_DEPTH = 6.0
SPOKE_T = 7.0            # spoke thickness along x
DISH = 2.0               # outer face of the spokes sits this far inside the outer lip
BEARING_FIT = 0.1        # bearing seat diameter over the bearing OD (as the printed bearing blocks: D11.1 for 11 mm bearings)
BEARING_SHOULDER_D = 9.0 # bore between the two bearing seats: under the 6x12x4 outer race (ID about 10), over the 8 mm inner race spacer


def bead_seat(inch): return inch * 25.4


def make_wheel(seat_d, width, axle_bore=4.4, spoke_w_hub=5.0, spoke_w_rim=9.0, hub_od=20.0, hub_out=0.0, bearing=None, hub_in=0.0):
    """hub_out: the hub boss stands this far proud of the spoke faces (the floor over the hex pocket is 1 mm + hub_out, the wheel nut seats on it).
    bearing=(od, w): no hex pocket; the hub takes two ball bearings instead, one seat from each end of the hub (od + BEARING_FIT, w deep), with a
    shoulder bore BEARING_SHOULDER_D between them (smaller than the outer race, larger than the inner race spacer): the wheel turns on a fixed axle."""
    ax = cq.Vector(1, 0, 0)
    r_seat = seat_d / 2
    r_in = r_seat - BARREL_T
    r_lip = r_seat + LIP_H
    x_out = width / 2
    # barrel: seat tube plus two lips
    barrel = cq.Solid.makeCylinder(r_lip, width, cq.Vector(-width / 2, 0, 0), ax).cut(
        cq.Solid.makeCylinder(r_in, width, cq.Vector(-width / 2, 0, 0), ax))
    groove = cq.Solid.makeCylinder(r_lip + 1, width - 2 * 2.0, cq.Vector(-width / 2 + 2.0, 0, 0), ax).cut(
        cq.Solid.makeCylinder(r_seat, width - 2 * 2.0, cq.Vector(-width / 2 + 2.0, 0, 0), ax))
    barrel = barrel.cut(groove)                                   # lips are 2 mm wide, the bead seat runs between them
    # spokes in the plane just inside the outer lip
    x1 = x_out - DISH
    x0 = x1 - SPOKE_T
    body = barrel
    hub = cq.Solid.makeCylinder(hub_od / 2, SPOKE_T + 4.0 + hub_out + hub_in, cq.Vector(x0 - 4.0 - hub_in, 0, 0), ax)   # hub_in: hub runs on inboard
    body = body.fuse(hub)
    r_h = hub_od / 2 - 1.0
    r_r = r_in + 1.0
    for k in range(SPOKES):
        a = 2 * math.pi * k / SPOKES + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        pts = [(r_h * ca + nx * spoke_w_hub / 2, r_h * sa + ny * spoke_w_hub / 2),
               (r_r * ca + nx * spoke_w_rim / 2, r_r * sa + ny * spoke_w_rim / 2),
               (r_r * ca - nx * spoke_w_rim / 2, r_r * sa - ny * spoke_w_rim / 2),
               (r_h * ca - nx * spoke_w_hub / 2, r_h * sa - ny * spoke_w_hub / 2)]
        sp = cq.Workplane('YZ', origin=(x0, 0, 0)).polyline(pts).close().extrude(SPOKE_T).val()
        body = body.fuse(sp)
    # hex drive pocket from the inner side of the hub boss and the retaining screw / axle bore
    if bearing is None:
        hexp = cq.Workplane('YZ', origin=(x0 - 4.0 - 0.1, 0, 0)).polygon(6, HEX_AF / math.cos(math.pi / 6)).extrude(HEX_DEPTH + 4.0 + 0.1).val()
        body = body.cut(hexp)
        body = body.cut(cq.Solid.makeCylinder(axle_bore / 2, width + 2, cq.Vector(-width / 2 - 1, 0, 0), ax))
    else:
        bod, bw = bearing
        h0, h1 = x0 - 4.0 - hub_in, x1 + hub_out                           # hub ends
        body = body.cut(cq.Solid.makeCylinder(BEARING_SHOULDER_D / 2, width + 2, cq.Vector(-width / 2 - 1, 0, 0), ax))
        for xa in (h0 - 1.0, h1 - bw):                                    # seat from the inner end (1 mm extra out of the hub) and from the outer end
            body = body.cut(cq.Solid.makeCylinder((bod + BEARING_FIT) / 2, bw + 1.0, cq.Vector(xa, 0, 0), ax))
    body = body.clean()
    assert body.isValid() and len(body.Solids()) == 1, 'wheel is not one valid solid'
    return body


def tyre_seat_radius(seat_d): return seat_d / 2 + LIP_H
