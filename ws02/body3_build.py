"""WS-03 body: a faceted wedge built from clean plan, side and section shapes taken from the base.stl silhouettes (old chassis
frame numbers), mapped to the 3WD frame, hollowed to a 2.4 mm wall with an open belly, windows cut where the front arms
swing. Output: out/mono3/body3.stl (and halves/pieces via split_body3)."""
import os
import sys
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import MultiPoint, Polygon

import mono_build as MB

OUT = Path("out/mono3")
KX, KY, DZ, XOFF = 1.0, 1.0, 0.0, 0.0           # the profile below is already in the assembly frame
WALL = 2.4

# profile from the owner's sketch over the RT-1 sheet (assembly frame, mm): truncated nose, roof rising toward the rear, high rear hood
# with a scoop, open tail underside above the gearbox; wide mid body, narrow tail
SIDE = [(17.7, 30), (17.7, -2), (-35, -26), (-243, -26), (-243, 50), (-300, 50), (-378, 105), (-259, 97), (-175, 80), (-98, 57), (-59, 44)]
HALF = [(17.7, 38), (10, 44), (-28, 44), (-73.5, 47), (-91.3, 60), (-120, 66), (-189, 74), (-229, 60), (-243, 52), (-300, 44), (-340, 40), (-378, 34)]
SECTION = [(-68, -40), (68, -40), (68, -9.3), (35, 110), (-35, 110), (-68, -9.3)]           # (y, z): flanks lean in toward the roof


def to_new(pts, kind):
    out = []
    for a, b in pts:
        if kind == "side":
            out.append((KX * a + XOFF, b + DZ))
        elif kind == "plan":
            out.append((KX * a + XOFF, KY * b))
        else:
            out.append((KY * a, b + DZ))
    return out


def prism_yz(pts, x0, x1):
    m = trimesh.creation.extrude_polygon(Polygon(pts), x1 - x0)           # polygon in (y, z), extruded along local z
    m.apply_transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1.0]]))
    m.apply_translation((x0, 0, 0))
    return MB.man(m)


def solid(inset=0.0, belly=False):
    side = Polygon(to_new(SIDE, "side")).buffer(-inset, join_style=2)
    hp = to_new(HALF, "plan")
    plan_pts = hp + [(x, -y) for x, y in reversed(hp)]
    plan = Polygon(plan_pts).buffer(-inset, join_style=2)
    sec = Polygon(to_new(SECTION, "sec")).buffer(-inset, join_style=2)
    s = MB.prism_xy(list(plan.exterior.coords)[:-1], -120.0, 140.0) ^ MB.prism_xz(list(side.exterior.coords)[:-1], -120.0, 120.0) ^ prism_yz(list(sec.exterior.coords)[:-1], -400.0, 100.0)
    if belly:                                        # open belly: sweep the cavity down in 5 mm steps so thin sections stay connected
        acc = s
        front = s ^ Manifold.cube((500.0, 400.0, 400.0), center=False).translate((-240.6, -200.0, -200.0))   # sweep only ahead of the rear bulkhead
        for k in range(1, 14):
            acc = acc + front.translate((0, 0, -5.0 * k))
        s = acc
    return s



from shapely.geometry import LineString


def _poly(kind, inset):
    if kind == "side":
        return Polygon(to_new(SIDE, "side")).buffer(-inset, join_style=2)
    hp = to_new(HALF, "plan")
    return Polygon(hp + [(x, -y) for x, y in reversed(hp)]).buffer(-inset, join_style=2)


def top_z(x, inset=0.0):
    g = LineString([(x, -500), (x, 500)]).intersection(_poly("side", inset))
    return g.bounds[3]


def hw_in(x, inset=WALL):
    g = LineString([(x, -500), (x, 500)]).intersection(_poly("plan", inset))
    return g.bounds[3]


def cyl_m(c, r, h, axis="z"):
    m = Manifold.cylinder(h, r, r, 32, True)
    if axis == "y":
        m = m.rotate((90.0, 0.0, 0.0))
    elif axis == "x":
        m = m.rotate((0.0, 90.0, 0.0))
    return m.translate(c)


PAD_X = (-228.0, -200.0, -168.0)            # rear deck screw stations (match parts/w3_chassis.py)
POST_XY = (-18.0, 16.0)                               # front body posts: deck to roof bosses
SEAM_X = (-270.0, -215.0, -100.0, -20.0)             # seam screws joining the left and right halves
HEX = lambda cx, cz, r: [(cx + r * np.cos(a), cz + r * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 7)[:-1]]


def honeycomb(tri, pitch=5.4, r=2.3):
    """Hex holes that fit inside a triangle (x, z)."""
    poly = Polygon(tri).buffer(-1.0)
    out = []
    minx, minz, maxx, maxz = poly.bounds
    row = 0
    z = minz
    while z < maxz:
        x = minx + (pitch / 2 if row % 2 else 0.0)
        while x < maxx:
            h = Polygon(HEX(x, z, r))
            if poly.contains(h):
                out.append(HEX(x, z, r))
            x += pitch
        z += pitch * 0.866
        row += 1
    return out


def details(body):
    """Pads, posts, seam bosses, antenna boss, base-style details. Returns the body with them added."""
    for x in PAD_X:                                                        # rear deck pads inside the skirt
        h = hw_in(x)
        for s in (1, -1):
            pad = Manifold.cube((10.0, 9.9, 3.6), center=False).translate((x - 5.0, (h - 9.5) if s > 0 else -(h + 0.4), -23.0))
            body = body + pad
            body = body - cyl_m((x, s * (h - 7.0), -21.0), 0.9, 6.0)
    zt = top_z(POST_XY[0], WALL)
    for s in (1, -1):                                                      # roof bosses for the front body posts
        body = body + cyl_m((POST_XY[0], s * POST_XY[1], 0.5 * (27.0 + zt + 0.4)), 4.5, zt + 0.4 - 27.0)
        body = body - cyl_m((POST_XY[0], s * POST_XY[1], 33.0), 1.1, 14.0)
    for x in SEAM_X:                                                       # seam bosses straddling y = 0
        z = top_z(x, WALL) - 6.5
        body = body + cyl_m((x, 0.0, z), 4.0, 14.0, "y") + Manifold.cube((8.0, 14.0, 6.0), center=True).translate((x, 0.0, z + 3.0))
    ztop = top_z(-255.0)                                                   # antenna post on the tail, standing proud of the roof
    body = body + cyl_m((-255.0, 0.0, ztop + 4.0), 4.0, 20.0) - cyl_m((-255.0, 0.0, ztop + 8.0), 1.6, 24.0)
    for tri in [[(-241, 22), (-209, 22), (-225, 44)]]:                     # honeycomb in the triangular vent, both flanks
        for hexp in honeycomb(tri):
            for s in (1, -1):
                y0, y1 = (20.0, 120.0) if s > 0 else (-120.0, -20.0)
                body = body - MB.prism_xz(hexp, y0, y1)
    heads = [(-230, 0), (-200, -10), (-150, -10), (-130, 10), (-205, 2), (-150, 2), (-292, 34), (-292, 58)]       # screw heads
    for hx, hz in heads:
        circ = [(hx + 2.2 * np.cos(a), hz + 2.2 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 13)[:-1]]
        body = body - flank_cut(circ, 0.6)
    for zc in (2.0, 9.0, 16.0, 23.0):                                      # flat snub nose: cooling slots across the vertical front face
        body = body - Manifold.cube((30.0, 28.0, 3.0), center=True).translate((8.0, 0.0, zc))
    # rocker panel armor: a 3 mm proud band along the lower flank between the rear bulkhead and the front window
    slab = Manifold.cube((118.0, 300.0, 12.0), center=False).translate((-240.0, -150.0, -24.0))
    sides = Manifold.cube((300.0, 110.0, 40.0), center=False).translate((-300.0, 40.0, -40.0)) + Manifold.cube((300.0, 110.0, 40.0), center=False).translate((-300.0, -150.0, -40.0))
    body = body + (((solid(-3.0) - solid(0.5)) ^ slab) ^ sides)
    canopy = [(-225, -24), (-205, -30), (-150, -30), (-128, -22), (-128, 22), (-150, 30), (-205, 30), (-225, 24)]   # glass canopy, recessed 0.8 for dark paint
    body = body - (MB.prism_xy(canopy, -100.0, 200.0) - solid(0.8))
    # roof spine: a 1.2 mm raised strip along the centre line from the nose to the tail
    spine = [(-258, -4.5), (-232, -6), (-120, -6), (-30, -4), (-8, -2), (-8, 2), (-30, 4), (-120, 6), (-232, 6), (-258, 4.5)]
    grown = solid(-1.2) - solid(0.0)
    if not os.environ.get("NO_SPINE"):
        body = body + ((MB.prism_xy(spine, -100.0, 200.0) ^ grown) ^ Manifold.cube((600.0, 100.0, 300.0), center=False).translate((-400.0, -50.0, 20.0)))
    # roof grilles over the motor (honeycomb through the roof), mirrored left and right
    for s_ in (1, -1):
        rect = [(-232, s_ * 8), (-210, s_ * 8), (-210, s_ * 34), (-232, s_ * 34)]
        for hexp in honeycomb(rect):
            body = body - MB.prism_xy(hexp, -100.0, 200.0)
    return body



def front_window():
    """Hull of the front mechanism over the lean range, projected to (x, z), grown by 4 mm: a clean polygon cut through the flanks."""
    import w3_scene as S
    pts = []
    for ph in range(-25, 26, 5):
        for n, m, k in S.scene(float(ph)):
            if n.startswith(("arm_", "cover_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod")):
                pts += [(float(x), float(z)) for x, y, z in m.vertices[::7]]
    hull = MultiPoint(pts).convex_hull.buffer(5.5, join_style=2).simplify(2.0)
    return hull


# styling in the new frame (x, z): recessed painted panels (0.8 mm) and through vents on both flanks, as in the references
PANELS = [  # recessed
    [(-232, -15), (-132, -18), (-124, -6), (-232, 2)],                          # low sill panel
    [(-205, 6), (-152, 6), (-130, 24), (-152, 46), (-205, 38)],               # big diagonal panel behind the arm window
]
VENTS = [  # through the skin
    [(-296, 34), (-262, 34), (-266, 40), (-296, 40)], [(-296, 44), (-262, 44), (-266, 50), (-296, 50)],      # louvre slots on the hood
    [(-241, 22), (-209, 22), (-225, 44)],                                       # triangular vent
]
HATCH = (-96.0, -40.0, 24.0)        # roof access hatch over the battery and ESC: x0, x1, half width


def flank_cut(poly, depth=None):
    """Region of an (x, z) polygon extruded across the flank: recessed (outside the inset skin) or through."""
    out = None
    for s in (1, -1):
        y0, y1 = (20.0, 120.0) if s > 0 else (-120.0, -20.0)
        p = MB.prism_xz(poly, y0, y1)
        if depth is not None:
            p = p - solid(depth)
        out = p if out is None else out + p
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    outer = solid(0.0)
    inner = solid(WALL, belly=True)
    body = outer - inner
    win = front_window()
    wpts = list(win.exterior.coords)[:-1]
    from shapely.geometry import box as sbox
    low = win.intersection(sbox(-500.0, -500.0, 500.0, 25.0))                 # inboard of the arms only the servo level needs clearing
    lpts = list(low.exterior.coords)[:-1]
    for s in (1, -1):
        y0, y1 = (52.0, 100.0) if s > 0 else (-100.0, -52.0)                  # arm level: everything out
        body = body - MB.prism_xz(wpts, y0, y1)
        y0, y1 = (30.0, 52.0) if s > 0 else (-52.0, -30.0)                    # servo level: leave the upper shoulder as the frame's top beam
        body = body - MB.prism_xz(lpts, y0, y1)
    body = body - Manifold.cube((46.0, 46.0, 90.0), center=True).translate((-278.0, 59.0, 0.0))    # rear arm leaves the body, left
    body = body - Manifold.cube((46.0, 46.0, 90.0), center=True).translate((-278.0, -59.0, 0.0))   # mirrored
    for poly in PANELS:
        body = body - flank_cut(poly, 0.8)
    for poly in VENTS[:2]:
        body = body - flank_cut(poly)
    body = body - Manifold.cube((16.0, 30.0, 22.0), center=True).translate((-241.8, 21.0, 0.0))     # drive shaft tunnel through the rear bulkhead
    body = body - Manifold.cube((6.0, 300.0, 6.0), center=True).translate((-241.8, 0.0, -25.0))      # the rear deck passes under the bulkhead
    for y_ in (2.0, 35.0):
        body = body - cyl_m((-241.8, y_, 27.0), 1.35, 6.0, 'x')                                       # screws that hold the motor plate
    body = details(body)
    # roof hatch: a snug lid cut from the roof (0.25 mm gap all round)
    hx0, hx1, hy = HATCH
    cube = lambda g: Manifold.cube((hx1 - hx0 + 2 * g, 2 * (hy + g), 200.0), center=False).translate((hx0 - g, -(hy + g), 40.0 - g))
    lid = body ^ cube(-0.25)
    body = body - cube(0.25)
    ml = MB.to_trimesh(lid)
    ml.merge_vertices()
    ml.export(OUT / "lid3.stl")
    m = MB.to_trimesh(body)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    m.export(OUT / "body3.stl")
    print("lid3", len(ml.faces), ml.is_watertight, np.round(ml.extents, 1).tolist())
    print("body3", len(m.faces), m.is_watertight, round(m.volume), np.round(m.bounds, 1).tolist())


if __name__ == "__main__":
    main()
