"""PETG cage, one part, built from solid round tubes with balled joints. All members are collected and fused in one go
(sequential booleans on dozens of tangent tubes were unreliable), the holes are cut at the end.

Frame facts (final frame, from tools/probe_xrow.py): front deck plate top z 16.6 (about 20 at the feet), half-width about 40 mm;
frame rail at x = +-52 for y = -180..20 with its top rising from z 20 to 34 and extra parts up to z 51 (hence the beams at z 59);
nothing stands at x >= 42 behind y = 20, the battery stack (x 12..36) reaches z 83.

Layout: front hoop leaning forward with crash bracing, side frames on the rails (lower beam, upper tube copying the shell belt line,
uprights and X bracing), rear legs rising back, A and B pillars, roof rails, supports under the rear shell hump, the rear shock
shock top mount (pin nodes tied to the rear supports and braced to the rear bridge, M6 pin) and the two magnetic light contact bridges.
"""
import cadquery as cq
from parts.params import *
from parts.light_contacts import make_connector, roof_underside

FRONT_LEG_X = param(45.5, 'Cage front legs, half distance (outside the left-side parts on the front deck)', min=30.0, max=46.0, step=0.5, unit='mm', group='Cage')
REAR_LEG_X = param(51.0, 'Cage rear bridge legs, half distance', min=40.0, max=52.0, step=1.0, unit='mm', group='Cage')
REAR_SUP_X = param(30.0, 'Tail tube ends, half distance', min=25.0, max=50.0, step=1.0, unit='mm', group='Cage')
CAGE_BEAM = param(10.0, 'Cage main tube diameter', min=6.0, max=14.0, step=0.5, unit='mm', group='Cage')
PILLAR_D = CAGE_BEAM     # every tube of the cage has the same diameter
PILLAR_IN = param(6.5, 'Pillar tube centre inboard of the shell frame node', min=5.0, max=14.0, step=0.5, unit='mm', group='Cage')
BELT_CLEAR = param(14.0, 'Cage upper tubes below the shell belt line', min=8.0, max=30.0, step=1.0, unit='mm', group='Cage')
CAGE_RAIL_X = 53.5       # mm: side frames over the frame rails
CAGE_Z = 59.0            # mm: lower beam centre height, above the extra parts on the rail (up to z 51)
FRONT_FOOT_Y = -180.0    # mm: front feet on the deck; the legs lean forward from here to the contact bridge (about 21 degrees)
FRONT_FOOT_Z = 20.2      # mm: deck top at the front feet (y -180), measured by tools/collide.py
RAIL_FEET = ((-150.0, 22.2), (-20.0, 31.3))    # (y, rail top z) where the beams drop to the rail on a post
RAIL_START_Y, RAIL_END_Y = -180.0, 20.0
CAGE_SCREW_D = 3.4       # mm: M3 clearance hole in each foot (assumed fastening)
BOSS_D, BOSS_HOLE = PILLAR_D + 2.0, 1.8   # mm: shell mounting bosses, M2 self-tapping pilot hole (assumed)

FOOT_POST_D=max(CAGE_SCREW_D+6*NOZZLE,CAGE_BEAM-0.6)

def _interp(pts, y):
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        if ya <= y <= yb: return za + (zb - za) * (y - ya) / (yb - ya)
    return pts[0][1] if y < pts[0][0] else pts[-1][1]

def _simplify(pts, tol):
    """Ramer-Douglas-Peucker on (y, z): keeps the kinks of the shell belt line, so the tubes copy its angles."""
    if len(pts) < 3: return pts
    (y0, z0), (y1, z1) = pts[0], pts[-1]
    d = [abs((z1 - z0) * (y - y0) - (y1 - y0) * (z - z0)) / max(1e-9, ((y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5) for y, z in pts]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= tol: return [pts[0], pts[-1]]
    return _simplify(pts[:i + 1], tol)[:-1] + _simplify(pts[i:], tol)

def belt_profile(shells, y0, y1, x=CAGE_RAIL_X):
    """Underside of the shell belt line at x (the rail of the shell above the sill) as simplified (y, z) vertices."""
    pts = []
    for y in range(int(y0), int(y1) + 1, 5):
        zs = [z for z in (roof_underside(sh, y, 90.0, x) for sh in shells) if z is not None and z < 170.0]
        if zs: pts.append((float(y), min(zs)))
    return _simplify(pts, 0.8)

class _Frame:
    """Collects solids to fuse and holes to cut."""
    def __init__(self): self.solids = []; self.holes = []; self.tags = {}
    def tube(self, a, b, d):
        v0, v1 = cq.Vector(*a), cq.Vector(*b); r = d / 2
        self.tags[len(self.solids)] = 'tube (%.1f,%.1f,%.1f)->(%.1f,%.1f,%.1f)' % (tuple(a) + tuple(b))
        cylinder=cq.Solid.makeCylinder(r,(v1-v0).Length,v0,v1-v0)
        ends=[cq.Solid.makeSphere(r,c,angleDegrees1=-90,angleDegrees2=90) for c in (v0,v1)]
        # Fuse each complete capsule first. Adding naked cylinders to a large
        # cage can leave tangent/edge-only joins before their balls are added.
        capsule=cylinder.fuse(*ends).clean()
        assert capsule.isValid() and len(capsule.Solids())==1, 'Invalid tube capsule'
        self.solids.append(capsule)
    def post(self, x, y, z0, z1, d): self.solids.append(cq.Solid.makeCylinder(d / 2, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))
    def boss(self, p, sx, reach):
        """Mounting boss on a pillar node: a short stub towards the shell with a pilot hole."""
        x, y, z = p
        self.solids.append(cq.Solid.makeCylinder(BOSS_D / 2, reach, cq.Vector(x, y, z), cq.Vector(sx, 0, 0)))
        self.holes.append(cq.Solid.makeCylinder(BOSS_HOLE / 2, reach + 1.0, cq.Vector(x, y, z), cq.Vector(sx, 0, 0)))
    def vhole(self, x, y, z0, ln, d=CAGE_SCREW_D): self.holes.append(cq.Solid.makeCylinder(d / 2, ln, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))
    def build(self):
        """Fuse one member at a time and check every step (valid, volume grows): OCC fails silently on some tangent tube joints,
        a failed step is retried with the member nudged by tiny amounts, and reported."""
        s = self.solids[0]; bad = 0
        for i, x in enumerate(self.solids[1:], 1):
            ok = False
            for dx, dy, dz in [(0, 0, 0), (0.013, 0.007, 0.011), (-0.017, 0.011, -0.013), (0.031, -0.023, 0.019), (-0.043, -0.037, 0.029)]:
                xm = x if (dx, dy, dz) == (0, 0, 0) else x.translate(cq.Vector(dx, dy, dz))
                t = s.fuse(xm)
                volume_tolerance=max(1e-6,s.Volume()*1e-8)
                if t.isValid() and t.Volume() >= s.Volume() - volume_tolerance and len(t.Solids()) <= len(s.Solids()) + 1:
                    s = t; ok = True; break
            if not ok:
                raise RuntimeError('Cage member failed to fuse: '+str(i)+' '+self.tags.get(i, self.tags.get(i-1,'joint')))
        if bad: print('cage: %d members could not be fused' % bad)
        t = s.clean()
        if t.isValid(): s = t
        for h in self.holes:
            t = s.cut(h)
            if t.isValid() and t.Volume() < s.Volume(): s = t
        t = s.clean()
        if t.isValid(): s = t
        return s

def make_cage(front_y, rear_y, belt=None, nodes=None, supports=None, tie=None, tower_foot_z=None, tail=None):
    F = _Frame()
    fb, _, zf = make_connector(front_y, 200.0, 'Front', FRONT_LEG_X, FRONT_FOOT_Z, legs=False)
    rb, _, zr = make_connector(rear_y, 200.0, 'Rear', REAR_LEG_X, CAGE_Z, legs=False)
    F.solids += [fb, rb]
    zft, zrt = zf - 2.0, zr - 2.0            # tube tops sit inside the contact plates
    fz0 = FRONT_FOOT_Z + CAGE_BEAM / 2       # ball centre: the foot rests on the deck
    y_bump = front_y - 14.0                  # crash bumper tube in front of the contact plate
    z_x = 66.0                               # cross tube above the left-side front parts (they reach z 55)
    y_x = FRONT_FOOT_Y + (front_y - FRONT_FOOT_Y) * (z_x - FRONT_FOOT_Z) / (zft - FRONT_FOOT_Z)
    upper = [(y, z - BELT_CLEAR) for y, z in belt] if belt else None
    for sx in (-1, 1):
        fx, rx, px = sx * FRONT_LEG_X, sx * REAR_LEG_X, sx * CAGE_RAIL_X
        # --- front hoop (leaning forward) and crash bracing
        for a, b in [((fx, FRONT_FOOT_Y, fz0), (fx, front_y, zft)),            # leaning front leg
                     ((fx, front_y, zft), (fx, y_bump, zft)),                  # leg top to bumper
                     ((fx, FRONT_FOOT_Y, fz0), (px, RAIL_START_Y, CAGE_Z)),    # foot to rail start (gusset)
                     ((fx, front_y, zft), (px, RAIL_START_Y, CAGE_Z)),         # crash diagonal
                     ((fx, y_x, z_x), (px, RAIL_START_Y, CAGE_Z))]:            # mid-height brace
            F.tube(a, b, CAGE_BEAM)
        # --- lower beam on the rail, rear leg rising back
        F.tube((px, RAIL_START_Y, CAGE_Z), (px, RAIL_END_Y, CAGE_Z), CAGE_BEAM)
        F.tube((px, RAIL_END_Y, CAGE_Z), (rx, rear_y, zrt), CAGE_BEAM)
        for y, zr_top in RAIL_FEET:
            F.post(px, y, zr_top + 1.0, CAGE_Z, FOOT_POST_D); F.vhole(px, y, zr_top - 1.0, CAGE_Z - zr_top + 1.0 + CAGE_BEAM / 2)
        F.vhole(fx, FRONT_FOOT_Y, FRONT_FOOT_Z - 1.0, 14.0)
        # --- upper tubes copy the shell belt line, uprights, X bracing of the side frame, diagonal to the rear bridge
        if upper:
            for a, b in zip([(fx, y_bump, zft)] + [(px, y, z) for y, z in upper], [(px, y, z) for y, z in upper] + [(rx, rear_y, zrt)]): F.tube(a, b, CAGE_BEAM)
            zs, ze = _interp(upper, RAIL_START_Y), _interp(upper, RAIL_END_Y)
            F.tube((px, RAIL_START_Y, CAGE_Z), (px, RAIL_START_Y + 0.01, zs), CAGE_BEAM)
            F.tube((px, RAIL_END_Y, CAGE_Z), (px, RAIL_END_Y + 0.01, ze), CAGE_BEAM)
            if not tail:
                F.tube((px, RAIL_START_Y, CAGE_Z), (px, RAIL_END_Y, ze), CAGE_BEAM)
            F.tube((px, RAIL_END_Y, CAGE_Z), (px, RAIL_START_Y, zs), CAGE_BEAM)
    if upper:   # cross tubes between the upper rails at the uprights: under the belt skin and above the componentry
        for y in (RAIL_START_Y, RAIL_END_Y): F.tube((-CAGE_RAIL_X, y, _interp(upper, y)), (CAGE_RAIL_X, y + 0.01, _interp(upper, y)), CAGE_BEAM)
    F.tube((-FRONT_LEG_X, y_x, z_x), (FRONT_LEG_X, y_x, z_x), CAGE_BEAM)                  # front cross tube between the legs
    F.tube((-FRONT_LEG_X, y_bump, zft), (FRONT_LEG_X, y_bump, zft), CAGE_BEAM)            # crash bumper tube
    if nodes and upper:
        n = nodes
        def inb(p): return (max(0.0, p[0] - PILLAR_IN), p[1], p[2] - PILLAR_D / 2)
        a0, b1, r_n = inb(n['roof0']), inb(n['roof2']), inb(n['roofN'])
        for sx in (-1, 1):
            f = lambda p: (sx * p[0], p[1], p[2])
            b_base = (CAGE_RAIL_X, n['belt930'][1], _interp(upper, n['belt930'][1]))
            b_in = (CAGE_RAIL_X - 6.0, b_base[1], b_base[2])     # step inboard first: the shell belt skin reaches x = 48 at z 143
            for a, b in [((FRONT_LEG_X, front_y, zft), a0),                       # A pillar
                         (b_base, b_in), (b_in, b1),                              # B pillar
                         (a0, inb(n['roof1'])), (inb(n['roof1']), b1),
                         (b1, (REAR_LEG_X, rear_y, zrt))]:
                F.tube(f(a), f(b), PILLAR_D)
            for p, reach in [(a0, PILLAR_IN - 2.0), (b1, PILLAR_IN - 2.0), (b_in, PILLAR_IN - 2.0)]: F.boss(f(p), sx, reach)
            if tail:
                end=tail
                start=(b1[0],n['belt930'][1],n['belt930'][2])
                F.tube(f(b_in),f(start),PILLAR_D)
                F.tube(f(start),f(end),PILLAR_D)
                F.tube(f(b1),f(end),PILLAR_D)
                def at_y(a,b,y):
                    t=(y-a[1])/(b[1]-a[1])
                    return tuple(a[i]+t*(b[i]-a[i]) for i in range(3))
                # Tapered side gusset, rooted into the lower chassis rail.
                gy=n['belt930'][1]+65.0
                top=at_y(start,end,gy)
                tip=end
                diagonal_start=(CAGE_RAIL_X,RAIL_START_Y,CAGE_Z)
                # One straight centreline in plan and elevation, through the
                # gusset foot and on to its rear tip: no legacy dogleg.
                lower=at_y(diagonal_start,tip,gy-25.0)
                F.tube(f(diagonal_start),f(tip),PILLAR_D)
                F.tube(f(lower),f(top),PILLAR_D)
                from parts.panels import panel_prisms
                web=panel_prisms([[f(top),f(lower),f(tip)]],(-sx,0,0),WALL_PRINT)
                from parts.util import hull
                a,b,c=[cq.Vector(*f(p)) for p in (top,lower,tip)]
                normal=(b-a).cross(c-a).normalized()
                if normal.x*sx>0: normal=normal*-1
                d=a+(b-a)*0.35; e=c+(b-c)*0.35
                # 6 mm attachment at the default wall, feathering back to the
                # 3 mm main web over roughly 16 mm: no block or abrupt ledge.
                root=hull([p.toTuple() for p in [a-normal*WALL_PRINT,c-normal*WALL_PRINT,d,e,
                                                a+normal*WALL_PRINT,c+normal*WALL_PRINT,
                                                d+normal*WALL_PRINT,e+normal*WALL_PRINT]])
                axis=c-a
                local=root.fuse(*web).clean()
                foot_thickness=max(2.5*WALL_PRINT,0.8*PILLAR_D)
                fade=3*foot_thickness
                ba=b+(a-b)*min(0.85,fade/(a-b).Length)
                bc=b+(c-b)*min(0.85,fade/(c-b).Length)
                foot=hull([p.toTuple() for p in [b-normal*(foot_thickness-WALL_PRINT),ba,bc,
                                                b+normal*WALL_PRINT,ba+normal*WALL_PRINT,bc+normal*WALL_PRINT]])
                collar=cq.Solid.makeSphere((PILLAR_D+WALL_PRINT)/2,b,angleDegrees1=-90,angleDegrees2=90)
                local=local.fuse(foot,collar).clean()
                edges=[]
                for edge in local.Edges():
                    adjacent=[face.geomType() for face in local.Faces()
                              if any(other.isSame(edge) for other in face.Edges())]
                    upper_root=edge.Length()>axis.Length/2 and 'CYLINDER' in adjacent and 'PLANE' in adjacent
                    lower_root='SPHERE' in adjacent and 'PLANE' in adjacent and (edge.Center()-b).Length<PILLAR_D
                    if upper_root or lower_root:
                        edges.append(edge)
                if edges:
                    for radius in (WALL_PRINT/2,WALL_PRINT/3):
                        try:
                            rounded=local.fillet(radius,edges)
                            if rounded.isValid():
                                local=rounded; break
                        except Exception:
                            pass
                assert local.isValid(), 'Invalid reinforced gusset'
                F.solids.append(local)
                if tie:
                    ty,tz=tie
                    pin=(9.5,ty,tz)
                    # Two braced pin nodes, leaving the central shock eye free.
                    F.tube(f(at_y(b1,end,ty)),f(pin),PILLAR_D)
                    F.tube(f(at_y(start,end,ty)),f(pin),PILLAR_D)
                    if sx==1:
                        F.holes.append(cq.Solid.makeCylinder(3.2,30,cq.Vector(-15,ty,tz),cq.Vector(1,0,0)))
            # supports under the rear shell hump, above the rear tire
            prev = (REAR_LEG_X, rear_y, zrt)
            for y, z in (supports or []):
                pt = (REAR_SUP_X, y, z); F.tube(f(prev), f(pt), PILLAR_D); prev = pt; F.boss(f(pt), sx, 3.0)
            if tie and supports:
                # shock top mount carried by the tube frame, no separate tower: the pin node is held by a tie to the first rear support
                # and by a brace down and forward to the rear bridge corner (the shock pushes the pin up and forward, the brace takes it in tension)
                y0, z0 = supports[0]; ty, tz = tie
                F.tube(f((REAR_SUP_X, y0, z0)), f((9.5, ty, tz)), PILLAR_D)
                F.tube(f((9.5, ty, tz)), f((REAR_LEG_X, rear_y, zrt)), CAGE_BEAM)
                if sx == 1: F.holes.append(cq.Solid.makeCylinder(3.2, 30.0, cq.Vector(-15.0, ty, tz), cq.Vector(1, 0, 0)))   # M6 pin through both pin nodes
        for k in ('roof0', 'roof2'):
            p = inb(n[k]); F.tube((-p[0], p[1], p[2]), (p[0], p[1], p[2]), PILLAR_D)
        if supports and len(supports) > 1:
            y, z = supports[1]; F.tube((-REAR_SUP_X, y, z), (REAR_SUP_X, y, z), PILLAR_D)
        if tail:
            x,y,z=tail
            F.tube((-x,y,z),(x,y,z),PILLAR_D)
    return F.build(), zf, zr
