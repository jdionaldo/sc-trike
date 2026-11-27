"""Battery tray and receiver box (printed PETG), with a battery stand-in. World coordinates (mm, Z up, front = -Y).

Design intent:
- Battery: a raised tray over the steering servo on the centre line, ahead of the motor. Two legs (x +-21..26, y -104..-74, behind the
  horn's sweep and ahead of the motor) stand on the front deck, M3 from below through the deck into heat-set inserts in their feet.
  The floor underside (FLOOR_Z) clears the horn's tie rod ball studs (top z 80.5) and the lean head (top z 82); the pack top stays under
  the cage cross tube (z 136 at y -131..-122). Fixed: the front stop at y TRAY_FRONT and the legs. The tray grows rearward with the
  pack length and sideways with the pack width.
- Hold-down without tools: two 20 mm hook-and-loop straps run in grooves across the floor, out through slots in the side walls and
  over the pack. Full-height front stop, low rear lip: open the straps, tip the rear end over the lip, slide back, lift out through the
  open cockpit (the shell stays on).
- Receiver: a box in the left front bay, beside the servo and ahead of the motor, seated parallel to the deck, 2 x M3 from below into
  inserts in its 6 mm floor. Closed by a lid plate: its outer edge slides under the overhang of a ledge rail (that side lies under the
  cage's lower rail), its servo side is held by 2 x M2.5 x 6 countersunk screws into heat-set inserts in two pillars, driven from above
  through the open cockpit. Space for a 15 x 24.6 x 10.7 receiver plus its plugs, which leave at the rear towards the servo and the
  motor/ESC. An FS-iA6B (about 47 x 26 x 15, ASSUMED) does not fit this bay with a lid.
- ESC: none of its own, it is inside the motor (Hobbywing Fusion SE 2-in-1).
- Material: all printed parts here are PETG (no PLA near the motor or ESC).
"""
import math
import cadquery as cq
from soma import param

V = cq.Vector
BATT_L = param(76.6, "Battery length", min=60.0, max=110.0, step=0.1, unit="mm", group="Electronics and power",
               help="Pack length along the car. The tray grows rearward, the front stop stays")
BATT_W = param(35.0, "Battery width", min=30.0, max=50.0, step=0.5, unit="mm", group="Electronics and power",
               help="Pack width across the car")
BATT_H = 30.0            # pack height (3S 1300 envelope); the straps take any height up to about 45 mm
FIT = 0.5                # clearance pack to walls, each side
FLOOR_Z, FLOOR_T = 84.5, 4.0     # floor underside 84.5: the tie rods (y -145) rise to z 83.4 at 12 mm bump + 10 deg lean, 1.1 mm below it
TRAY_FRONT = -152.0      # front face of the front stop (lean head top z 82 ends at y -153.3, under the floor)
STOP_T, STOP_H = 3.0, 12.0
LIP_T, LIP_H = 3.0, 5.0
SIDE_T, SIDE_H = 2.5, 8.0
STRAP_W, STRAP_T = 21.0, 2.5   # slot for a 20 mm strap
GROOVE_D = 1.5
LEG_X = (21.0, 26.0)     # leg wall, +x side (servo mount ends at x 13.6)
LEG_Y = (-104.0, -74.0)
PAD_X = (20.0, 28.0)     # foot pad around the inserts
PAD_H = 8.0              # pad height above the deck
BEAM_Y, BEAM_Z0 = (-80.0, -74.0), 60.0   # cross beam between the legs, above the servo (top z 54.7)
from parts.params import INSERT_M3_D
INSERT_R, INSERT_D = INSERT_M3_D / 2, 7.0   # M3 heat-set insert bore
HOLE_R = 1.7                             # M3 clearance through the deck

RX_IN = (15.6, 33.2)     # receiver space x, y between the side walls and the pillars (receiver 15 x 24.6 plus 8 mm for the plugs)
RX_WALL, RX_FLOOR, RX_H = 2.0, 6.0, 11.5   # side walls, floor (M3 inserts from below), floor to lid underside
RX_PIL = 8.0             # pillar block length along y, front and rear, on the servo side (x 2.2 .. 9.8 local)
RX_LEDGE = 2.2           # outer ledge rail: the lid's outer edge slides under its overhang (no screws under the cage rail)
LID_T, LID_GAP = 2.5, 0.6
RX_X = -40.7             # box centre x (local 0): servo-side face at x -30.9, ledge rail out to x -52.9
RX_FRONT = -119.0        # outer front y (cage foot collar ends at y -122)
RX_INSERT_D = 4.5        # M3 x 4 insert from below, 1.5 mm floor skin left over it
LID_INSERT_R, LID_INSERT_D = 1.7, 5.0    # M2.5 heat-set insert bore in the pillars (insert OD 3.5 ASSUMED)
CSK_R, CSK_HEAD_R, CSK_DEPTH = 1.4, 2.6, 1.2   # M2.5 countersunk clearance and 90 deg head seat in the lid

if BATT_W / 2 + FIT + SIDE_T > 36.0:
    raise ValueError("a battery wider than 66 mm does not fit between the cage's lower rails")


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _big(s):
    return max(s.Solids(), key=lambda q: q.Volume())


def deck_top(deck, x, y):
    """Top of the deck at (x, y), world."""
    return deck.intersect(box(x - 0.25, x + 0.25, y - 0.25, y + 0.25, -20, 80)).BoundingBox().zmax


def battery_tray(deck):
    """(tray, battery stand-in, deck hole points)."""
    inx = BATT_W / 2 + FIT
    hw = max(inx + SIDE_T, LEG_X[1])
    y_in = TRAY_FRONT + STOP_T
    y_lip = y_in + BATT_L + 2 * FIT
    y_end = max(y_lip + LIP_T, LEG_Y[1] + 2.0)
    zt = FLOOR_Z + FLOOR_T
    t = box(-hw, hw, TRAY_FRONT, y_end, FLOOR_Z, zt)
    t = t.fuse(box(-inx - SIDE_T, inx + SIDE_T, TRAY_FRONT, y_in, zt - 0.1, zt + STOP_H))
    t = t.fuse(box(-inx - SIDE_T, inx + SIDE_T, y_lip, y_lip + LIP_T, zt - 0.1, zt + LIP_H))
    for s in (1, -1):
        t = t.fuse(box(*sorted((s * inx, s * (inx + SIDE_T))), y_in - 0.1, y_lip + 0.1, zt - 0.1, zt + SIDE_H))
    legs, pts = None, []
    for s in (1, -1):
        leg = box(*sorted((s * LEG_X[0], s * LEG_X[1])), *LEG_Y, 0.0, FLOOR_Z + 0.5)
        ztop = max(deck_top(deck, s * sum(PAD_X) / 2, y) for y in LEG_Y)
        leg = leg.fuse(box(*sorted((s * PAD_X[0], s * PAD_X[1])), *LEG_Y, 0.0, ztop + PAD_H))
        legs = leg if legs is None else legs.fuse(leg)
    legs = legs.fuse(box(-LEG_X[1] + 0.5, LEG_X[1] - 0.5, *BEAM_Y, BEAM_Z0, FLOOR_Z + 0.5))
    v0 = legs.Volume()
    legs = _big(legs.cut(deck))
    assert v0 - legs.Volume() > 100.0, 'battery tray legs do not reach the deck'
    t = t.fuse(legs).clean()
    # straps: a groove across the floor and a slot through each side wall
    for yc in (y_in + FIT + BATT_L / 4, y_in + FIT + 3 * BATT_L / 4):
        t = t.cut(box(-hw - 1, hw + 1, yc - STRAP_W / 2, yc + STRAP_W / 2, zt - GROOVE_D, zt))
        t = t.cut(box(-inx - SIDE_T - 1, inx + SIDE_T + 1, yc - STRAP_W / 2, yc + STRAP_W / 2, zt - GROOVE_D, zt - GROOVE_D + STRAP_T))
    for s in (1, -1):
        for yh in (LEG_Y[0] + 5.0, LEG_Y[1] - 5.0):
            x = s * (PAD_X[0] + PAD_X[1]) / 2
            z0 = deck_top(deck, x, yh)
            t = t.cut(cq.Solid.makeCylinder(INSERT_R, z0 + INSERT_D, V(x, yh, 0.0), V(0, 0, 1)))
            pts.append((x, yh))
    assert t.isValid() and len(t.Solids()) == 1, 'battery tray is not one valid solid'
    batt = box(-BATT_W / 2, BATT_W / 2, y_in + FIT, y_in + FIT + BATT_L, zt + 0.05, zt + 0.05 + BATT_H)
    return t, batt, pts


def receiver_box(deck, rx):
    """(box, lid, receiver stand-in moved into it, deck hole points, lid screw points). `rx` is the receiver stand-in, world.
    Local frame: floor underside on z 0, front face on y 0, x 0 = RX_X, +x = servo side. Placed parallel to the deck."""
    hx = RX_IN[0] / 2 + RX_WALL                       # 9.8: outer face of the side walls
    oy = RX_IN[1] + 2 * RX_PIL
    zl = RX_FLOOR + RX_H                              # lid underside
    ztf, ztr = deck_top(deck, RX_X, RX_FRONT + 1.0), deck_top(deck, RX_X, RX_FRONT + oy - 1.0)
    ang = math.degrees(math.atan2(ztr - ztf, oy - 2.0))
    b = box(-hx - RX_LEDGE, hx, 0, oy, 0, RX_FLOOR)                                      # floor
    b = b.fuse(box(RX_IN[0] / 2, hx, 0, oy, 0, zl))                                      # servo-side wall
    b = b.fuse(box(-hx, -RX_IN[0] / 2, 0, oy, 0, zl))                                    # outer wall
    b = b.fuse(box(-hx - RX_LEDGE, -hx + 0.1, 0, oy, 0, zl + LID_T + LID_GAP + 1.6))     # ledge rail ...
    b = b.fuse(box(-hx - RX_LEDGE, -RX_IN[0] / 2, 0, oy, zl + LID_T + LID_GAP, zl + LID_T + LID_GAP + 1.6))   # ... and its overhang
    b = b.fuse(box(-RX_IN[0] / 2 - 0.1, 2.2, 0, RX_WALL, 0, zl))                         # front stop (servo side open for the plugs at the rear)
    pil = []
    for y0 in (0.0, oy - RX_PIL):
        b = b.fuse(box(2.2, hx, y0, y0 + RX_PIL, 0, zl))
        pil.append((6.0, y0 + RX_PIL / 2))
    hy = (14.0, oy - 14.0)
    for y in hy:
        b = b.cut(cq.Solid.makeCylinder(INSERT_R, RX_INSERT_D, V(0, y, -0.1), V(0, 0, 1)))
    lid = box(-hx + 0.2, hx, 0, oy, zl, zl + LID_T)
    for x, y in pil:
        b = b.cut(cq.Solid.makeCylinder(LID_INSERT_R, LID_INSERT_D, V(x, y, zl - LID_INSERT_D), V(0, 0, 1)))
        lid = lid.cut(cq.Solid.makeCylinder(CSK_R, LID_T + 1, V(x, y, zl - 0.5), V(0, 0, 1)))
        lid = lid.cut(cq.Solid.makeCone(CSK_R, CSK_HEAD_R, CSK_DEPTH + 0.01, V(x, y, zl + LID_T - CSK_DEPTH), V(0, 0, 1)))
    b = b.clean()
    for nm, s in (('receiver box', b), ('receiver lid', lid)):
        assert s.isValid() and len(s.Solids()) == 1, nm + ' is not one valid solid'
    p0 = V(RX_X, RX_FRONT, ztf + 0.02)
    place = lambda s: s.rotate(V(0, 0, 0), V(1, 0, 0), ang).translate(p0)
    rb = rx.BoundingBox()
    rx_l = rx.translate(V(-rb.center.x, RX_PIL + 0.3 - rb.ymin, RX_FLOOR + 0.05 - rb.zmin))   # flat on the floor, behind the front pillar
    assert RX_FLOOR + 0.05 + rb.zlen < zl - 0.3 and rb.xlen < RX_IN[0] - 0.4, 'receiver does not fit under the lid'
    wpt = lambda x, y, z=0.0: place(cq.Vertex.makeVertex(x, y, z)).Center()
    pts = [(wpt(0, y).x, wpt(0, y).y) for y in hy]
    screws = [wpt(x, y, zl + LID_T).toTuple() for x, y in pil]
    return place(b), place(lid), place(rx_l), pts, screws


def build(deck, rx):
    """deck: front deck, world. rx: receiver stand-in, world. Returns parts and the M3 hole points for the deck (world x, y)."""
    tray, batt, p1 = battery_tray(deck)
    rbox, rlid, rx2, p2, scr = receiver_box(deck, rx)
    return dict(tray=tray, battery=batt, rx_box=rbox, rx_lid=rlid, receiver=rx2, holes=p1 + p2, lid_screws=scr)


def deck_holes(deck_chassis, holes, off):
    """M3 clearance holes through the deck (chassis frame) at the world points `holes`."""
    for x, y in holes:
        deck_chassis = deck_chassis.cut(cq.Solid.makeCylinder(HOLE_R, 80.0, V(x, y, -30.0) - off, V(0, 0, 1)))
    return deck_chassis
