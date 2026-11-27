"""Trim the scaled shell around the 1:1 chassis, including suspension and steering travel.

Tool data comes from tools/make_relief.py (parts/relief.json): hull vertices of every chassis part that reaches
into the shell, tire cylinders and the rear swingarm pivot. Frame = shell frame at 1:1 (X lateral, Y = -forward,
Z up, ground z = 0); the tools are moved by CHASSIS_Y / CHASSIS_Z.
"""
import json, math, os
import cadquery as cq
from parts.util import hull
from parts.params import *

_DATA = json.load(open(os.path.join(os.path.dirname(__file__), 'relief.json')))
PIVOT = (_DATA['pivot'][1], _DATA['pivot'][2])            # rear swingarm pivot (y, z)
REAR_AXLE = (_DATA['rear_axle'][1], _DATA['rear_axle'][2])  # rear axle at the original 112 mm tire
SHOCK_TOP0 = (0.0, 136.3, 129.5)     # upper eye on the frame (x, y, z), on the wheel centre plane, raised by REAR_SHOCK_RISE
SHOCK_BOT0 = (0.0, 150.0, 114.0)   # lower eye (arm frame): the pin of the shock bridge over the tire, final (215, 139) at ride
BRIDGE_ARM = [(77.0, 133.0, 114.0), (30.0, 133.0, 114.0), (-9.3, 133.0, 114.0), (-9.3, 157.5, 114.0), (9.3, 157.5, 114.0)]   # outer plate apex, arch, ears around the shock eye pin (new rear arm)   # shock bridge path in the arm frame (x, y, z): apex node, up, across
FRONT_X, FRONT_Y = 144.0, -225.55                         # front axle centres (|x|, y)


def rear_lift_angle():
    """Swingarm rotation (rad) that lifts the rear axle to the new tire radius."""
    dy, dz = REAR_AXLE[0]-PIVOT[0], REAR_AXLE[1]-PIVOT[1]
    L = math.hypot(dy, dz)
    return math.asin((REAR_TIRE_OD/2 - PIVOT[1])/L) - math.atan2(dz, dy)

def rot_yz(p, ang, c=PIVOT):
    """Rotate point p=(x,y,z) about the lateral axis through c=(y,z); positive raises the tail."""
    x, y, z = p; dy, dz = y-c[0], z-c[1]
    return (x, c[0] + dy*math.cos(ang) - dz*math.sin(ang), c[1] + dy*math.sin(ang) + dz*math.cos(ang))

def rot_xy(p, ang, c):
    """Rotate point about a vertical axis through c=(x,y) (steering)."""
    x, y, z = p; dx, dy = x-c[0], y-c[1]
    return (c[0] + dx*math.cos(ang) - dy*math.sin(ang), c[1] + dx*math.sin(ang) + dy*math.cos(ang), z)

def _grown(pts, g):
    out = []
    for x, y, z in pts:
        out += [(x+g, y, z), (x-g, y, z), (x, y+g, z), (x, y-g, z), (x, y, z+g), (x, y, z-g)]
    return out

def _circle(cx, cy, cz, r, hw, n=28):
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        for sx in (-hw, hw):
            pts.append((cx+sx, cy + r*math.cos(a), cz + r*math.sin(a)))
    return pts

def _circle2(c, r, n=12):
    return [(c[0]+r*math.cos(2*math.pi*i/n), c[1]+r*math.sin(2*math.pi*i/n), c[2]+s*r) for i in range(n) for s in (-1, 1)]

FRONT_CLEAR = 3.0        # mm: clearance of the shell around the moving wishbone parts (their geometry is exact, unlike the old stand-in hulls)
FRONT_UP_DEG = 26.0      # arm angle upward the shell has to clear: 10 deg lean (15.6 deg at the arm) plus 12 mm bump (7.3 deg)
FRONT_STEER_DEG = 22.5   # knuckle steering angle each way: the inner wheel steers 22.5 deg at full horn throw (parts/wishbone.py, November 24)
FRONT_TYRE_LIFT = 40.0   # mm: front wheel travel upward relative to the body: 25.4 at 10 deg lean, 12 bump, margin
FRONT_ARM_L = 91.0       # wishbone length (parts/wishbone.py ARM_L)


def wishbone_relief_tools(extra=0.0, kinds=('arm', 'knuckle', 'tyre'), sides=(1, -1), sweep_x=0.0):
    """Cut-out tools (world coordinates) for the travel of the new front end (parts/wishbone.py): each upper arm with its shock post swept upward
    about its pivot rod, each knuckle carried along and steered. Only what rises toward the shell matters; the lower arm stays under it.
    extra grows every volume by that much more (the wheel-well liner is the grown volume minus the plain one); kinds and sides pick a subset."""
    from parts import wishbone as wb
    V = cq.Vector
    arm, kn = wb.a_arm(wb.ZU, True), wb.knuckle()
    A = [v.toTuple() for v in arm.Vertices()]
    K = [v.toTuple() for v in kn.Vertices()]
    tools = []
    for s in sides:
        pa, pk = [], []
        for k in range(5):
            psi = -s * FRONT_UP_DEG * k / 4.0                      # wheel up on side s
            loc = wb._loc_axis((s * wb.XI, 0, wb.ZU), (0, 1, 0), psi)
            T = loc.wrapped.Transformation()
            for x, y, z in A:
                q = V(s * x, y, z).toPnt().Transformed(T); pa.append((q.X(), q.Y(), q.Z()))
            dx, dz = wb.arm_ball(s, psi)
            for d in (-FRONT_STEER_DEG, 0.0, FRONT_STEER_DEG):
                c, sn = math.cos(math.radians(d)), math.sin(math.radians(d))
                for x, y, z in K:
                    rx, ry = s * x - s * wb.KX, y - wb.KY
                    pk.append((s * wb.KX + c * rx - sn * ry + dx, wb.KY + sn * rx + c * ry, z + dz))
        if 'arm' in kinds:
            if sweep_x:      # the arm's volume extended inboard: a slot cut with it goes straight through a wall that faces x. Only inboard: an
                # outboard extension ran past the arm's own cut beside the knuckle and the tyre and left 0.7 to 2 mm slabs of liner there
                pa = pa + [(x - s * sweep_x, y, z) for x, y, z in pa]
            tools.append(hull(_grown(pa, FRONT_CLEAR + extra * 1.5)))
        if 'knuckle' in kinds: tools.append(hull(_grown(pk, FRONT_CLEAR + extra * 1.5)))
    # front tyres over the wishbone travel (lean plus bump lifts the wheel up to FRONT_TYRE_LIFT relative to the body and carries it inboard on the
    # arm's arc), steered FRONT_STEER_DEG each way about the kingpin: one hull per travel step, so the cut hugs the swept tyre
    L = math.radians(FRONT_STEER_DEG)
    for t in _DATA['tires']:
        if t['name'] == 'mock_rear_tire_ring' or 'tyre' not in kinds: continue
        cx, cy, cz = t['center']; s = 1 if cx > 0 else -1
        if s not in sides: continue
        lifts = [0.0, FRONT_TYRE_LIFT / 2, FRONT_TYRE_LIFT]
        ring = {}
        for lift in lifts:
            dx = -s * (FRONT_ARM_L - math.sqrt(FRONT_ARM_L ** 2 - lift ** 2))
            kx = s * wb.KX + dx
            ring[lift] = [rot_xy((p[0] + dx, p[1], p[2]), a, (kx, cy)) for a in (-L, 0, L)
                          for p in _circle(cx, cy, cz + lift, t['r'] + TIRE_GAP + extra, t['hw'] + TIRE_GAP + extra)]
        for l0, l1 in zip(lifts, lifts[1:]):
            tools.append(hull(ring[l0] + ring[l1]).translate(cq.Vector(0, CHASSIS_Y, CHASSIS_Z)))
    return tools


LINER_WALL = WALL_PRINT   # wheel-well liner wall: the printed shell wall (the liner is built at 1:1; WALL is the pre-scale generation wall, 1.38 mm)


def wheel_well_liners():
    """Raw wheel-well liners {side: solid}, world coordinates: a wall of LINER_WALL around the swept space of the front tyre and the knuckle
    (lean, bump and steering), with every swept volume cut out of it, so the upper arm and its shock post pass through their own opening.
    model.py clips it to the inside of the body skin, to the arch and trim lines and to the cage, and fuses it into the front shell."""
    out = {}
    cuts = wishbone_relief_tools() + [c for c, _ in arm_tunnels().values()]      # the arm passes through the liner in its tunnel (arm_tunnels)
    for s in (1, -1):
        grown = wishbone_relief_tools(extra=LINER_WALL, kinds=('knuckle', 'tyre'), sides=(s,))
        w = grown[0]
        for t in grown[1:]:
            w = w.fuse(t)
        for t in cuts:
            w = w.cut(t)
        out[s] = w.clean()
    return out


# Upper arm tunnel (owner, November 24: "clean it up into one framed opening"). The skin notch and the liner slot for the upper arm's travel were
# cut by different tools (the skin's notch squared along each skin facet, the liner's slot along x), so their edges did not line up and stepped
# wedge faces showed. Now one prism along x makes the opening through skin and liner: its section is the octagon (support lines at 0, 45, 90 and
# 135 deg in the y-z plane) around the upper arm's travel envelope outboard of ARM_TUNNEL_X0, and a frame of LINER_WALL around it joins liner and
# skin, so the opening reads as one framed aperture with straight facets.
TUNNEL_FRAME_FLUSH = True  # arm tunnel frame clipped flush with the skin's bevelled outer boundary (False: 1 mm inside the outer face)
ARM_TUNNEL_X0 = 64.0       # inner face of the wheel-well liner at the arm (the raw liner starts at x 64.9 there)


def arm_tunnels():
    """{side: (cutter, raw frame)} in world coordinates. The frame is clipped to the body (1 mm inside the outer face), to the liner's inner face,
    to the arch and to the knuckle and tyre travel; model.py keeps it off the cage and fuses it into the front shell."""
    import parts.stealth_shell as ss
    V = cq.Vector
    dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(0, 360, 45)]
    out = {}
    for s in (1, -1):
        t = wishbone_relief_tools(kinds=('arm',), sides=(s,))[0]
        x0 = ARM_TUNNEL_X0 - 2.0
        t = t.intersect(cq.Solid.makeBox(200.0, 400.0, 300.0, V(x0 if s > 0 else -x0 - 200.0, -400.0, -50.0)))
        yz = [(v.Y, v.Z) for v in t.Vertices()]
        sup = [max(p[0] * c + p[1] * q for p in yz) for c, q in dirs]

        def prism(grow, x_in):
            poly = []
            for i in range(8):
                (c1, s1), (c2, s2) = dirs[i], dirs[(i + 1) % 8]
                h1, h2 = sup[i] + grow, sup[(i + 1) % 8] + grow
                det = c1 * s2 - s1 * c2
                poly.append(((h1 * s2 - h2 * s1) / det, (c1 * h2 - c2 * h1) / det))
            p = cq.Workplane('YZ', origin=(x_in, 0, 0)).polyline(poly).close().extrude(140.0 - x_in).val()
            return p if s > 0 else p.mirror('YZ')

        cutter = prism(0.0, x0)
        # clipped by the skin's own bevelled boundary (as the wheel-well liners, November 27): clipped 1 mm inside the outer face, its inset plane met the
        # cheek's lower facet and the arch top in a 0.13 mm2 sliver at (77, -227, 102)
        frame = prism(LINER_WALL, ARM_TUNNEL_X0).cut(cutter).intersect(ss.outer_solid(bevel=True) if TUNNEL_FRAME_FLUSH else ss._skin_inset(1.0))
        for k in ss.arch_cut() + wishbone_relief_tools(kinds=('knuckle', 'tyre'), sides=(s,)):
            frame = frame.cut(k)
        out[s] = (cutter, frame.clean())
    return out


# Side panels in the lower front arch (owner, November 23: "liners for the bigger cutout"). Below the fender line the arch is open from the nose to
# y -77; the wishbones, the knuckle and the tie rods need everything ahead of the tie rods. Behind them a panel closes the arch: a wall of LINER_WALL
# just outboard of the cage and the deck edge, with a return of the same wall along the arch outline into the skin.
ARCH_PANEL_X = 55.5        # inner face of the panel: 2 mm outboard of the cage foot post and the lower rail (x 53.5), 1 mm off the deck edge (54.5)
ARCH_PANEL_RELIEF = 0.3    # the return wall stands this far back from the skin's arch rim: faces that coincide with the rim made the fused shell export as an open shell
ARCH_PANEL_Y0 = -133.0     # front edge: the tie rods and the knuckle's steering arm reach y -136.1 outboard of x 50 (lean +-10, horn +-30, bump +12 / -8)


def arch_side_panels():
    """Raw lower-arch side panels {side: solid}, world coordinates, inside the skin (1 mm in from the outer face, so the arch rim keeps its
    chamfer) and clear of the wishbone travel cuts. model.py keeps them off the cage and fuses them into the front shell."""
    import parts.stealth_shell as ss
    V = cq.Vector

    # the arch outline (y, z) sampled about every mm along its lines and curves, then moved out as a polygon: an offset2D of the spline wire gave
    # a solid that came back from STEP as an open shell
    sol = ss._arch_solid(0.0)
    f = [f for f in sol.Faces() if f.geomType() == 'PLANE' and abs(f.Center().x) < 1e-6][0]
    outline = []
    for e in f.outerWire().Edges():
        n = max(2, int(e.Length()))
        outline += [(p.y, p.z) for p in (e.positionAt(i / n) for i in range(n))]
    if sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(outline, outline[1:] + outline[:1])) < 0:
        outline = outline[::-1]

    def prism(x0, grow):
        poly = ss._grow(outline, grow) if grow else outline
        return cq.Workplane('YZ', origin=(x0, 0, 0)).polyline([tuple(p) for p in poly]).close().extrude(200.0 - x0).val()

    w = prism(ARCH_PANEL_X, LINER_WALL + ARCH_PANEL_RELIEF).cut(prism(ARCH_PANEL_X + LINER_WALL, ARCH_PANEL_RELIEF))
    w = w.intersect(cq.Solid.makeBox(200.0, -60.0 - ARCH_PANEL_Y0, 140.0, V(0, ARCH_PANEL_Y0, 0))).intersect(ss._skin_inset(1.0))
    # square bottom: the skin's rocker plane cuts the panel at about 54 deg to its faces (a 0.42 mm feather edge). The same plane turned about its
    # trace on the panel's outer face, so it stands square to the panel, cuts the bottom instead (only across the panel itself, x up to its outer face)
    xo = ARCH_PANEL_X + LINER_WALL
    for f in w.Faces():
        c = f.Center(); n = f.normalAt(c)
        if f.geomType() != 'PLANE' or n.z > -0.3 or abs(n.x) < 0.2 or c.x > xo + 0.5:
            continue
        m = V(0, n.y, n.z).normalized()
        q = V(xo, c.y, c.z - n.x * (xo - c.x) / n.z)          # on the face plane at the outer face, same y
        pl = cq.Plane(origin=(xo, q.y, q.z), xDir=(0, m.z, -m.y), normal=m.toTuple())       # its y direction is world -x
        assert pl.yDir.x < -0.99
        w = w.cut(cq.Workplane(pl).rect(400.0, LINER_WALL + 1.0, centered=(True, False)).extrude(60.0).val())
    for t in wishbone_relief_tools():
        w = w.cut(t)
    w = w.clean()
    assert w.isValid() and len(w.Solids()) == 1, 'arch side panel: expected one solid, got %d' % len(w.Solids())
    return {1: w, -1: w.mirror('YZ')}


def relief_tools():
    """Cut-out tools in final (scaled) shell coordinates: tire arches and suspension travel."""
    off = cq.Vector(0, CHASSIS_Y, CHASSIS_Z)
    T = BUMP_TRAVEL; L = math.radians(STEER_LOCK)
    th0 = rear_lift_angle(); thb = math.asin(min(1.0, T/math.hypot(REAR_AXLE[0]-PIVOT[0], REAR_AXLE[1]-PIVOT[1])))
    tools = []
    # --- tires
    for t in _DATA['tires']:
        cx, cy, cz = t['center']
        if t['name'] == 'mock_rear_tire_ring':
            R = REAR_TIRE_OD/2
            pts = []
            for k in (0, 0.5, 1.0):                      # axle path along the swingarm arc
                c = rot_yz((cx, cy, cz), th0 + k*thb)
                pts += _circle(0, c[1], c[2], R + RELIEF, t['hw'] + RELIEF)
        else:
            pts = []
            for a in (-L, 0, L):                         # steering lock sweep about the wheel centre
                for lift in (0, T):                      # bump travel
                    pts += [rot_xy(p, a, (cx, cy)) for p in _circle(cx, cy, cz+lift, t['r'] + TIRE_GAP, t['hw'] + TIRE_GAP)]
        tools.append(hull(pts).translate(off))
    # --- suspension, steering and swingarm parts
    for h in _DATA['hulls']:
        P = [tuple(p) for p in h['pts']]; kind = h['kind']
        if kind != 'rear': continue      # the front hulls belong to the old front end (swingarms, uplinks, belts, lean servo): wishbone_relief_tools() replaces them
        if kind == 'susp':
            pts = P + [(x, y, z + T*min(1.0, max(0.0, (abs(x)-30)/114.0))) for x, y, z in P]
        elif kind == 'steer':
            cx = math.copysign(FRONT_X, P[0][0])
            pts = []
            for a in (-L, 0, L):
                for lift in (0, T):
                    pts += [rot_xy((x, y, z+lift), a, (cx, FRONT_Y)) for x, y, z in P]
        elif kind == 'rear':
            pts = [rot_yz(p, th0) for p in P] + [rot_yz(p, th0 + thb) for p in P]
        else:
            pts = P
        tools.append(hull(_grown(pts, RELIEF)).translate(off))
    # the wishbone travel (wishbone_relief_tools) is cut from the finished front shell in model.py
    # --- rear shock strut: top mount fixed on the frame (raised), bottom eye rides on the swingarm
    top = (SHOCK_TOP0[0], SHOCK_TOP0[1], SHOCK_TOP0[2] + REAR_SHOCK_RISE)
    pts = []
    for k in (0, thb):
        b = rot_yz(SHOCK_BOT0, th0 + k)
        for f in (0.0, 0.5, 1.0):
            pts += _circle2(tuple(top[i] + f*(b[i]-top[i]) for i in range(3)), 12.0 + RELIEF)
    tools.append(hull(pts).translate(off))
    # --- shock bridge over the rear tire swings with the arm
    bp = []
    for k in (0, thb):
        bp += [rot_yz(p, th0 + k) for p in BRIDGE_ARM]
    tools.append(hull(_grown(bp, RELIEF + 8.0)).translate(off))
    return tools
