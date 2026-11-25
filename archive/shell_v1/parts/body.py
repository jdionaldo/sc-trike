import cadquery as cq
from .params import *
from .util import hull, beam, ball, fuse, tubes, mx

NOSE_Y, NOSE_Z0, NOSE_Z1, NOSE_DY = -1500.0, 340.0, 640.0, 70.0   # nose face goes from (NOSE_Y,Z0) up and back


def sym(pts):
    """Add the mirrored copy of every point."""
    return list(pts) + [mx(p) for p in pts if p[0] != 0]


def hood_z(y):
    if y < -1000:
        return NOSE_Z1 + (y - (NOSE_Y + NOSE_DY)) * (770 - NOSE_Z1) / 430.0
    return 770 + (y + 1000) * (830 - 770) / 550.0


def make_tub():
    rings = [  # y, z bottom, z top, half width bottom, half width top
        (-1500, 340, None, 340, None),
        (-1000, 300, 770, 500, 440),
        (-450, 300, 830, 540, 460),
        (300, 300, 860, 540, 470),
        (720, 330, 800, 470, 420),
    ]
    pts = [(340, -1500, 340), (330, -1430, 640)]
    for y, z0, z1, h0, h1 in rings[1:]:
        pts += [(h0, y, z0), (h1, y, z1)]
    return hull(sym(pts))


def make_hood_ridge():
    pts = []
    for y in (-1385, -520):
        z = hood_z(y)
        pts += [(150, y, z - 8), (60, y, z + 38)]
    return hull(sym(pts))


def make_sills():
    s = []
    for sx in (1, -1):
        pts = [(sx * 525, -380, 300), (sx * 610, -330, 330), (sx * 610, -330, 450), (sx * 525, -380, 470),
               (sx * 470, 700, 300), (sx * 520, 640, 330), (sx * 520, 640, 440), (sx * 470, 700, 460)]
        s.append(hull(pts))
    return fuse(s)


def make_skid():
    return hull(sym([(300, -1450, 270), (480, -950, 255), (520, 250, 255), (440, 1000, 260),
                     (300, -1450, 330), (480, -950, 330), (520, 250, 330), (440, 1000, 330)]))


# ---- cockpit ---------------------------------------------------------------------------------
ROOF_Z = 1190.0
BASE_Z = 830.0
CAB = dict(  # key corners (|x|, y, z)
    base_f=(440, -420, BASE_Z), base_r=(400, 640, BASE_Z),
    roof_f=(330, -60, ROOF_Z), roof_r=(320, 470, ROOF_Z - 10),
)


def make_canopy():
    pts = []
    for k, (x, y, z) in CAB.items():
        pts += [(x, y, z), (-x, y, z)]
    return hull(pts)


def make_roof_panel():
    x, yf, yr = 345, -90, 500
    z = ROOF_Z - 10
    return hull(sym([(x, yf, z), (x - 15, yf - 10, z + 32), (x, yr, z - 10 + 0), (x - 15, yr + 5, z + 28)]))


def make_roof_frame():
    t = []
    for s in (1, -1):
        bf = (s * CAB["base_f"][0], CAB["base_f"][1], BASE_Z)
        br = (s * CAB["base_r"][0], CAB["base_r"][1], BASE_Z)
        rf = (s * CAB["roof_f"][0], CAB["roof_f"][1], ROOF_Z)
        rr = (s * CAB["roof_r"][0], CAB["roof_r"][1], CAB["roof_r"][2])
        t += [(bf, rf), (rf, rr), (rr, br), (bf, br)]
    rfL, rfR = (-CAB["roof_f"][0], CAB["roof_f"][1], ROOF_Z), (CAB["roof_f"][0], CAB["roof_f"][1], ROOF_Z)
    rrL, rrR = (-CAB["roof_r"][0], CAB["roof_r"][1], ROOF_Z - 10), (CAB["roof_r"][0], CAB["roof_r"][1], ROOF_Z - 10)
    t += [(rfL, rfR), (rrL, rrR)]
    # mid roof cross-bar and base windscreen bar
    t += [((-325, 200, ROOF_Z - 5), (325, 200, ROOF_Z - 5)),
          ((-CAB["base_f"][0], CAB["base_f"][1], BASE_Z), (CAB["base_f"][0], CAB["base_f"][1], BASE_Z))]
    return tubes(t, TUBE * 0.9)


def make_roof_pods():
    """Two small hexagonal light pods and their lenses on the front of the roof."""
    pods, lens = [], []
    for s in (1, -1):
        x = s * 210
        z = ROOF_Z + 70
        body = cq.Workplane("XZ").polygon(6, 120).extrude(95).val().translate((x, 20, z))      # XZ extrudes to -Y
        stalk = hull([(x - 30, 10, ROOF_Z - 15), (x + 30, 10, ROOF_Z - 15), (x - 30, -50, ROOF_Z - 15), (x + 30, -50, ROOF_Z - 15),
                      (x - 40, -10, z - 50), (x + 40, -10, z - 50), (x - 40, -60, z - 50), (x + 40, -60, z - 50)])
        pods += [body, stalk]
        lens.append(cq.Workplane("XZ").polygon(6, 96).extrude(8).val().translate((x, -74, z)))
    return fuse(pods), fuse(lens)


# ---- nose ------------------------------------------------------------------------------------
def face_y(z):
    return NOSE_Y + (z - NOSE_Z0) * NOSE_DY / (NOSE_Z1 - NOSE_Z0)


def make_grille():
    """Hexagonal black mesh plate (+ dark backing) lying on the sloped nose face."""
    import math
    W, H, T = 600.0, 200.0, 22.0
    plate = cq.Workplane("XY").box(W, T, H).translate((0, -T / 2, 0))        # outward = -Y
    pts, d, px, py = [], 44.0, 52.0, 45.0
    nx, nz = int(W // px), int(H // py)
    for j in range(-nz // 2 + 1, nz // 2 + 1):
        for i in range(-nx // 2, nx // 2 + 1):
            x = i * px + (px / 2 if j % 2 else 0)
            if abs(x) < W / 2 - d / 2 - 8 and abs(j * py) < H / 2 - d / 2 - 4:
                pts.append((x, j * py))
    holes = (cq.Workplane("XZ").pushPoints(pts).polygon(6, d).extrude(40, both=True))
    plate = plate.cut(holes).val()
    back = cq.Workplane("XY").box(W, 6, H).translate((0, -1, 0)).val()
    ang = -math.degrees(math.atan2(NOSE_DY, NOSE_Z1 - NOSE_Z0))
    zc = 462.0
    place = lambda s: s.rotate((0, 0, 0), (1, 0, 0), ang).translate((0, face_y(zc), zc))
    return place(plate), place(back)


def make_headlights():
    """Slim wraparound red LED strip: front band plus a wing on each side."""
    z0, z1 = 578.0, 614.0
    parts = [hull([(x, face_y(z) - 9, z) for x in (-338, 338) for z in (z0, z1)]
                  + [(x, face_y(z) + 4, z) for x in (-338, 338) for z in (z0, z1)])]
    for s in (1, -1):
        pts = []
        for z in (z0, z1):
            pts += [(s * 338, face_y(z) - 9, z), (s * 338, face_y(z) + 4, z),
                    (s * 424, -1280, z + 2), (s * 424, -1296, z + 2)]
        parts.append(hull(pts))
    return fuse(parts)


def make_bumper():
    low = 395
    P = lambda x, y, z: (x, y, z)
    t = [(P(-400, -1575, low), P(400, -1575, low)),                         # lower bar
         (P(-345, -1540, 620), P(345, -1540, 620)),                          # upper hoop bar
         (P(-400, -1575, low), P(-345, -1540, 620)), (P(400, -1575, low), P(345, -1540, 620)),
         (P(-400, -1575, low), P(-390, -1250, 390)), (P(400, -1575, low), P(390, -1250, 390)),
         (P(-345, -1540, 620), P(-330, -1300, 700)), (P(345, -1540, 620), P(330, -1300, 700)),
         (P(-200, -1575, low), P(-130, -1540, 620)), (P(200, -1575, low), P(130, -1540, 620))]
    return tubes(t, TUBE * 1.1)
