"""WS-03 rear coilover (left side, outside the skin): mounting points, kinematics over the arm's travel, and the purchased shock's envelope mesh.

Stock 1/10 aluminium coilover, 55 mm closed to 80 mm open eye to eye (25 mm stroke), 3 mm eyes, adjustable spring.  The lower eye bolts to a printed lug on
the swing arm's outer plane, the upper eye to a printed tab on the cage node R2 that reaches out through the skin.  Both bolt axes are along y.
"""
import math
import numpy as np
from manifold3d import Manifold

LMIN, LMAX = 55.0, 80.0           # purchased shock, eye to eye
LUG_UV = (50.0, 22.0)             # lower eye in the arm frame: u along the arm from the pivot, v across it (up at rest)
L_DROOP, L_BUMP = 79.5, 60.5      # eye to eye at 20 mm droop / 25 mm bump: 0.5 mm spare at full extension, 5.5 mm before bottoming
PLATE_Y = (72.5, 77.0)            # lug / tab plate |y| range
BOSS_Y1 = 81.4                    # bolt boss end face
EYE_Y = (81.8, 87.3)              # shock eye (0.4 mm off the boss: a washer)
SHOCK_Y = 0.5 * sum(EYE_Y)        # shock axis plane
LUG_R, BOSS_R, PIN_D = 5.5, 4.6, 3.2
TAB_TUBE_R = 6.5


def _geom():
    from parts import w3_drive as D
    px, pz = D.XR, 0.0
    ax, az = D.RAXLE
    L = math.hypot(ax - px, az - pz)
    d = np.array([(ax - px) / L, (az - pz) / L])
    n = np.array([d[1], -d[0]])
    return np.array([px, pz]), d, n, L


def travel_angles(up_mm=25.0, down_mm=20.0):
    """Arm angle (deg, positive = wheel up) for `down_mm` of droop and `up_mm` of bump at the axle."""
    L = _geom()[3]
    return -math.degrees(math.asin(down_mm / L)), math.degrees(math.asin(up_mm / L))


def lug_point(deg=0.0):
    """Lower eye (x, z) with the arm swung `deg` about the pivot."""
    P, d, n, _ = _geom()
    q = LUG_UV[0] * d + LUG_UV[1] * n
    a = math.radians(deg)
    return P + np.array([math.cos(a) * q[0] + math.sin(a) * q[1], -math.sin(a) * q[0] + math.cos(a) * q[1]])


def _tab():
    """Upper eye: the point 79.5 mm from the lower eye at full droop and 60.5 mm at full bump (the intersection ahead of the pivot).
    Derived from the arm geometry so it follows the wheelbase and rake."""
    dn, up = travel_angles()
    a, b = lug_point(dn), lug_point(up)
    c = b - a
    D = float(np.linalg.norm(c))
    x = (L_DROOP ** 2 - L_BUMP ** 2 + D ** 2) / (2 * D)
    h = math.sqrt(L_DROOP ** 2 - x ** 2)
    e = c / D
    pts = [a + x * e + h * np.array([-e[1], e[0]]), a + x * e - h * np.array([-e[1], e[0]])]
    return tuple(float(v) for v in max(pts, key=lambda p: p[0]))


def tab_xz():
    return _tab()


def eye_to_eye(deg=0.0):
    return float(np.linalg.norm(np.array(tab_xz()) - lug_point(deg)))


def mount_lever(deg=0.0, h=0.05):
    """Wheel travel per unit of shock length change (mm/mm) at arm angle `deg`."""
    L = _geom()[3]
    return float(L * math.radians(h) / abs(eye_to_eye(deg + 0.5 * h) - eye_to_eye(deg - 0.5 * h)))


def _cyl_x(s0, s1, r, y=SHOCK_Y, k=40):
    return Manifold.cylinder(s1 - s0, r, r, k).rotate((0.0, 90.0, 0.0)).translate((s0, y, 0.0))


def _eye(s, r, y0, y1):
    return Manifold.cylinder(y1 - y0, r, r, 40).rotate((-90.0, 0.0, 0.0)).translate((s, y0, 0.0))


def shock_manifold(deg=0.0, tab=None):
    """Envelope of the coilover with the arm at `deg`: eyes, mount stems, body, rod, adjuster collar and the spring (a solid cylinder, conservative)."""
    a, b = lug_point(deg), np.array(tab if tab is not None else tab_xz(), float)
    L = float(np.linalg.norm(b - a))
    c, s = (b - a) / L
    parts = [_eye(0.0, 4.6, EYE_Y[0], EYE_Y[1]), _cyl_x(0.0, 12.0, 2.6), _cyl_x(10.0, 46.0, 8.0), _cyl_x(17.0, L - 17.0, 11.0, k=48), _cyl_x(40.0, L - 6.0, 1.9),
             _cyl_x(L - 17.0, L - 13.0, 11.0, k=48), _cyl_x(L - 13.0, L - 3.0, 2.6), _eye(L, 4.6, EYE_Y[0], EYE_Y[1])]
    m = parts[0]
    for p in parts[1:]:
        m = m + p
    R = np.array([[c, 0.0, -s], [0.0, 1.0, 0.0], [s, 0.0, c]])
    return m.transform(np.hstack([R, np.array([[a[0]], [0.0], [a[1]]])]))
