"""Steering linkage hardware placeholders (reference frame of parts/chassis_ref.step, +x side; the -x side is the mirror image).
Servo output spline + horn screw, two ball-joint rod ends (M3 studs, nuts) and the threaded rod between them. Hard points come from the
stand-ins they dress: horn pivot at the horn's lower end, knuckle pivot at the tie rod's outer end. Placeholders only: they show where the
real parts go, they are not printed (stems start with b_)."""
import math
import cadquery as cq
from parts.params import STEER_OUT as _S, SERVO_BACK as _B

SERVO_OUT_X = 54.5 + _S                    # servo output face (|x|)
HORN_X0, HORN_X1 = 61.2 + _S, 63.5 + _S         # horn plate
SHAFT_YZ = (-125.0 + _B, 51.9)             # servo output axis (along x)
P_HORN = (63.0 + _S, -125.1 + _B, 36.7)         # tie rod pivot on the horn
_SHAFT0, _PH0 = SHAFT_YZ, P_HORN
P_KNUCKLE = (106.5, -222.6, 29.9)     # tie rod pivot on the knuckle arm
ROD_D = 3.0                           # M3 threaded rod between the rod ends


def _cyl(p, d, r, h):
    d = cq.Vector(*d)
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p), d)


def _hex(p, d, af, h):
    wp = cq.Workplane(cq.Plane(origin=p, xDir=(0, 1, 0) if abs(d[0]) > .5 else (1, 0, 0), normal=d)).polygon(6, af / math.cos(math.pi / 6)).extrude(h)
    return wp.val()


def _rod_end(P, axis, rod_dir):
    """Ball joint: ball D6 on an M3 stud along `axis`, housing D8 x 9 along the rod, nut + washer on the far side of the stud."""
    ax = cq.Vector(*axis).normalized()
    c = cq.Vector(*P)
    out = []
    out.append(('ball', cq.Solid.makeSphere(3.0, c)))
    out.append(('stud', _cyl(c - ax * 8.0, ax.toTuple(), 1.5, 16.0)))
    rd = cq.Vector(*rod_dir).normalized()
    out.append(('housing', _cyl(c - rd * 4.5, rd.toTuple(), 4.0, 9.0)))
    out.append(('nut', _hex((c + ax * 5.0).toTuple(), ax.toTuple(), 5.5, 2.4)))
    out.append(('washer', _cyl((c + ax * 4.2).toTuple(), ax.toTuple(), 3.3, 0.8)))
    return out


def make_steer_hw():
    """Return [(name, solid)] for the +x side."""
    Ph, Pk = cq.Vector(*P_HORN), cq.Vector(*P_KNUCKLE)
    rd = (Pk - Ph).normalized()
    L = (Pk - Ph).Length
    parts = []
    # servo output: spline stub from the servo face through the horn, horn screw head on the outside
    parts.append(('spline', _cyl((SERVO_OUT_X, SHAFT_YZ[0], SHAFT_YZ[1]), (1, 0, 0), 3.0, HORN_X1 - SERVO_OUT_X + 0.5)))
    parts.append(('horn screw', _cyl((HORN_X1, SHAFT_YZ[0], SHAFT_YZ[1]), (1, 0, 0), 2.8, 1.8)))
    # horn end: stud along x
    for n, s in _rod_end(P_HORN, (1, 0, 0), rd.toTuple()): parts.append(('horn end ' + n, s))
    # knuckle end: stud vertical
    for n, s in _rod_end(P_KNUCKLE, (0, 0, 1), (-rd).toTuple()): parts.append(('knuckle end ' + n, s))
    # threaded rod between the housings
    parts.append(('rod', _cyl((Ph + rd * 4.5).toTuple(), rd.toTuple(), ROD_D / 2, L - 9.0)))
    return parts


def set_servo_pose(dz, tilt_deg, cy, cz):
    """Servo and horn tilted about the x axis through (cy, cz) and raised by dz: the output axis and the horn ball follow (model.py calls this before make_steer_hw)."""
    import math
    global SHAFT_YZ, P_HORN
    a = math.radians(tilt_deg)
    def mv(y, z):
        yy, zz = y - cy, z - cz
        return (cy + yy * math.cos(a) - zz * math.sin(a), cz + yy * math.sin(a) + zz * math.cos(a) + dz)
    SHAFT_YZ = mv(*_SHAFT0)
    yz = mv(_PH0[1], _PH0[2])
    P_HORN = (_PH0[0], yz[0], yz[1])
