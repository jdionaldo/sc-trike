"""Front shock (bought, 33 mm eye-to-eye class, 9 mm body, M3 eyes) between the front arm and the cage, as in the build videos: a clevis on the arm's inner
plate and a clevis block on a front cage tube. Everything is built in the chassis reference frame (world = ref + (0, CHASSIS_Y, CHASSIS_Z))."""
import cadquery as cq

SHOCK_LOW_XY = (66.2, -168.0)        # x, y of the lower clevis base on the arm's inner plate top
RAIL_REF = (45.0, -142.0, 100.3)      # the cage's lower side rail (x +-45, world z 85) at the shock's upper end (ref frame)
STANDOFF = 9.0                        # the clevis base stands this far outboard of the rail axis on a printed lug, so the shock clears the rail and the nodes
SHOCK_UP_REF = (RAIL_REF[0] + STANDOFF, RAIL_REF[1], RAIL_REF[2])
EYE_UP_OFF = 6.0                    # upper eye clears the cage tube (radius about 5) plus the eye ring
SHOCK_TOWER = 7.0                    # post under the lower clevis: lifts the shock axis over the arm's U1 node and bracing so the arm is not cut
EYE_L = 33.0                         # eye-to-eye length of the shock
GAP, PLATE_T, WIDTH, EMBED = 6.4, 3.0, 12.0, 4.0     # plates 3.0 x 12 (were 2.4 x 10): FEM root stress at the clevis
PIN_D, HOLE_D = 3.0, 3.2


def _loc(base, toward):
    b, t = cq.Vector(*base), cq.Vector(*toward)
    z = (t - b).normalized()
    x = z.cross(cq.Vector(0, 0, 1)).normalized()
    return cq.Location(cq.Plane(origin=b.toTuple(), xDir=x.toTuple(), normal=z.toTuple()))


def clevis(base, toward, eye_off):
    """Two plates (gap GAP) on a base block sunk EMBED mm into the structure; the pin hole is eye_off along the axis from the base."""
    h = eye_off + 5.0
    blk = cq.Solid.makeBox(GAP + 2 * PLATE_T, WIDTH, EMBED, cq.Vector(-(GAP / 2 + PLATE_T), -WIDTH / 2, -EMBED))
    c = blk
    for s in (1, -1):
        x0 = GAP / 2 if s > 0 else -(GAP / 2 + PLATE_T)
        c = c.fuse(cq.Solid.makeBox(PLATE_T, WIDTH, h, cq.Vector(x0, -WIDTH / 2, 0)))
    c = c.clean().cut(cq.Solid.makeCylinder(HOLE_D / 2, GAP + 2 * PLATE_T + 2, cq.Vector(-(GAP / 2 + PLATE_T) - 1, 0, eye_off), cq.Vector(1, 0, 0)))
    return c.moved(_loc(base, toward))


def geometry(base_low, base_up):
    D = (cq.Vector(*base_low) - cq.Vector(*base_up)).Length
    return D, D - EYE_L - EYE_UP_OFF, EYE_UP_OFF   # lower offset, upper offset


def shock_parts(base_low, base_up):
    """Return [(name, solid)] for the shock stand-in and its two pins, in the same frame as the bases."""
    D, off_low, off_up = geometry(base_low, base_up)
    parts = []
    for tag, b, t, eye_off in (('lower', base_low, base_up, off_low), ('upper', base_up, base_low, off_up)):
        fr = _loc(b, t)
        parts.append(('pin ' + tag, cq.Solid.makeCylinder(PIN_D / 2, GAP + 2 * PLATE_T - 0.2, cq.Vector(-(GAP / 2 + PLATE_T) + 0.1, 0, eye_off), cq.Vector(1, 0, 0)).moved(fr)))
    # shock along the line between the two eye centres, built in the lower clevis frame (z up the axis)
    fr = _loc(base_low, base_up)
    ring = lambda z: cq.Solid.makeCylinder(3.5, 6.0, cq.Vector(-3.0, 0, z), cq.Vector(1, 0, 0)).cut(cq.Solid.makeCylinder(HOLE_D / 2, 8, cq.Vector(-4.0, 0, z), cq.Vector(1, 0, 0)))
    z0, z1 = off_low, off_low + EYE_L
    sh = ring(z0).fuse(ring(z1))
    sh = sh.fuse(cq.Solid.makeCylinder(1.75, EYE_L - 7.2, cq.Vector(0, 0, z0 + 3.6), cq.Vector(0, 0, 1)))   # rod between the two rings, clear of the pins
    sh = sh.fuse(cq.Solid.makeCylinder(4.5, EYE_L - 20.0, cq.Vector(0, 0, z0 + 9.0), cq.Vector(0, 0, 1))).clean()
    parts.append(('shock', sh.moved(fr)))
    return parts


def rail_lug(sx, base_up, base_low):
    """Printed lug from the rail axis out to the clevis base, fused into the cage rail (ref frame, side sx). It is trimmed to the side of the clevis base plane
    that faces the rail, so the lug never reaches into the space of the shock's eye and body."""
    x0, x1 = sx * RAIL_REF[0], sx * (RAIL_REF[0] + STANDOFF + 4.0)
    lug = cq.Solid.makeBox(abs(x1 - x0), WIDTH, 10.0, cq.Vector(min(x0, x1), RAIL_REF[1] - WIDTH / 2, RAIL_REF[2] - 5.0))
    half = cq.Solid.makeBox(60.0, 60.0, 30.0, cq.Vector(-30.0, -30.0, -30.0)).moved(_loc(base_up, base_low))
    return lug.intersect(half)


def arm_post(base_low, base_up, chord_top_z):
    """Post on the arm's inner-plate chord under the lower clevis (ref frame): sunk 3 mm into the chord, trimmed to the clevis base plane so it never reaches into the shock's space."""
    w = GAP + 2 * PLATE_T
    post = cq.Solid.makeBox(w, WIDTH, base_low[2] - chord_top_z + 3.0 + 6.0, cq.Vector(base_low[0] - w / 2, base_low[1] - WIDTH / 2, chord_top_z - 3.0))
    half = cq.Solid.makeBox(60.0, 60.0, 30.0, cq.Vector(-30.0, -30.0, -30.0)).moved(_loc(base_low, base_up))
    return post.intersect(half)


WEB_T = 8.0                              # shear web thickness, x (inner truss plane at 66.2, belt starts at 70.5)
WEB_NODES = [(-168.0, 80.5), (-194.0, 67.6), (-194.0, 45.5), (-168.0, 47.0)]   # (y, z) ref: U1, U2, L2, L1 of parts/frontarm.py


def arm_web(sx):
    """Solid web filling the inner truss bay U1-U2-L2-L1 (ref frame, side sx): carries the shock post load from the upper chord down into the lower chord."""
    w = cq.Workplane('YZ').polyline(WEB_NODES).close().extrude(WEB_T).val()
    return w.translate(cq.Vector(sx * 66.2 - WEB_T / 2, 0, 0)) if sx > 0 else w.translate(cq.Vector(-66.2 - WEB_T / 2, 0, 0))


FOOT_Z_BOT = 71.3                        # ref z: belt top is 70.1 there, keep 1.2 mm


def arm_foot(base_low, base_up, chord_top_z):
    """Full-width foot (post width) from just above the belt up into the post, so the post never overhangs the chord and the web (8 mm) carries it straight down (ref frame)."""
    w = GAP + 2 * PLATE_T
    foot = cq.Solid.makeBox(w, WIDTH + 2.0, chord_top_z + 1.0 - FOOT_Z_BOT, cq.Vector(base_low[0] - w / 2, base_low[1] - WIDTH / 2 - 1.0, FOOT_Z_BOT))
    half = cq.Solid.makeBox(60.0, 60.0, 30.0, cq.Vector(-30.0, -30.0, -30.0)).moved(_loc(base_low, base_up))
    return foot.intersect(half)


BUTTRESS_L = 24.0                        # length of the wedge along the arm, forward of the clevis base
U1_REF, U2_REF = (-168.0, 80.5), (-194.0, 67.6)      # upper chord nodes of parts/frontarm.py (y, z), chord diameter 8


def arm_buttress(base_low):
    """Wedge behind the lower clevis (ref frame): since the lean beam the shock lies level and pushes the clevis forward along the arm. The wedge runs from the
    top of the post down the upper chord U1-U2 (sunk to the chord axis), full post width, so the push goes into the chord and the web as compression
    instead of bending the 6 mm post wall (FEM: 64 MPa without it)."""
    w = GAP + 2 * PLATE_T
    slope = (U2_REF[1] - U1_REF[1]) / (U2_REF[0] - U1_REF[0])
    zc = lambda y: U1_REF[1] + (y - U1_REF[0]) * slope
    y0, y1 = base_low[1], base_low[1] - BUTTRESS_L
    pts = [(y0, base_low[2] + 6.0), (y0, zc(y0)), (y1, zc(y1)), (y1, zc(y1) + 5.0)]
    b = cq.Workplane('YZ').polyline(pts).close().extrude(w).val()
    return b.translate(cq.Vector(base_low[0] - w / 2, 0, 0))


def arm_seat(base_low, base_up, eye_off):
    """Pad under the two clevis plates down into the chord (ref frame): closes the 0.5 mm notch between the plates' lower edge and the chord top,
    where the FEM peaked (33 MPa) once the wedge carried the push. Its top stays 1.3 mm under the shock's eye ring."""
    w = GAP + 2 * PLATE_T
    pad = cq.Solid.makeBox(w, 7.7, eye_off + 5.0, cq.Vector(-w / 2, 4.8, 0.0))      # clevis frame: z along the shock, y pointing down
    return pad.moved(_loc(base_low, base_up))
