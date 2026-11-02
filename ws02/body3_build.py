"""WS-03 body: a faceted wedge built from clean plan, side and section shapes taken from the base.stl silhouettes (old chassis
frame numbers), mapped to the 3WD frame, hollowed to a 2.4 mm wall with an open belly, windows cut where the front arms
swing. Output: out/mono3/body3.stl (and halves/pieces via split_body3)."""
import math
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
NOSE_LOW = (-1.0, -26.0)                              # where the nose underside meets the chassis floor
NOSE_TH = math.atan2(53.0, 35.0)                      # underside slope (56.6 deg)
TAIL = [(-299.0, 50.0), (-341.5, 66.4), (-348.1, 83.3)]                # new tail from the owner's markup: underside rising to the tail-light face, then the roof
SIDE = [(34, 40), (34, 27), NOSE_LOW, (-243, -26), (-243, 50)] + TAIL + [(-259, 97)]   # straight roofline, flat vertical nose face, short raked tail
HALF = [(30, 38), (20, 44), (-28, 44), (-73.5, 47), (-91.3, 60), (-120, 66), (-189, 74), (-229, 60), (-243, 52), (-300, 44), (-340, 40), (-348, 38.5)]
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
    for x in SEAM_X:                                                       # seam bosses straddling y = 0
        z = top_z(x, WALL) - 6.5
        body = body + cyl_m((x, 0.0, z), 4.0, 14.0, "y") + Manifold.cube((8.0, 14.0, 6.0), center=True).translate((x, 0.0, z + 3.0))
    body = body - flank_gills([(-241, 22), (-209, 22), (-225, 44)], 4)       # triangular vent: gill louvres, openings facing the rear
    for zc in (29.5, 33.0, 36.5):                                     # snub nose: cooling slots across the overhanging front face
        body = body - Manifold.cube((50.0, 28.0, 2.5), center=True).translate((20.0, 0.0, zc))
    th = NOSE_TH                                                          # the skid plate screws into the frame's nose pads through these holes
    for u_ in (10.0, 28.0):
        for sy in (1, -1):
            ox, oz = NOSE_LOW[0] + u_ * math.cos(th), NOSE_LOW[1] + u_ * math.sin(th)
            nx, nz = -math.sin(th), math.cos(th)
            hole = Manifold.cylinder(8.0, 1.35, 1.35, 24, True).rotate((0.0, -math.degrees(th), 0.0)).translate((ox + nx * 1.2, sy * 22.0, oz + nz * 1.2))
            body = body - hole
    # tail-light face: a 0.8 mm recess across the short vertical face at the end of the roof (painted red/black)
    (bx, bz), (cx_, cz_) = TAIL[2], TAIL[1]
    dvec = np.array([cx_ - bx, cz_ - bz]); dvec /= np.linalg.norm(dvec)
    nvec = np.array([-dvec[1], dvec[0]])
    if nvec[0] > 0:
        nvec = -nvec                                                      # outward = rearward
    p0, p1 = np.array([bx, bz]) + dvec * 3.0, np.array([cx_, cz_]) - dvec * 3.0
    quad = [tuple(p0 + nvec * 3.0), tuple(p1 + nvec * 3.0), tuple(p1 - nvec * 3.0), tuple(p0 - nvec * 3.0)]
    body = body - (MB.prism_xz(quad, -31.0, 31.0) - solid(0.8))
    canopy = [(-225, -24), (-205, -30), (-150, -30), (-128, -22), (-128, 22), (-150, 30), (-205, 30), (-225, 24)]   # glass canopy, recessed 0.8 for dark paint
    body = body - (MB.prism_xy(canopy, -100.0, 200.0) - solid(0.8))
    # roof spine: a 1.2 mm raised strip along the centre line from the nose to the tail
    spine = [(-258, -4.5), (-232, -6), (-120, -6), (-30, -4), (-8, -2), (-8, 2), (-30, 4), (-120, 6), (-232, 6), (-258, 4.5)]
    grown = solid(-1.2) - solid(0.0)
    if not os.environ.get("NO_SPINE"):
        body = body + ((MB.prism_xy(spine, -100.0, 200.0) ^ grown) ^ Manifold.cube((600.0, 100.0, 300.0), center=False).translate((-400.0, -50.0, 20.0)))
    # roof gills over the motor: slanted slats, openings facing the rear; the slats run across y so both sides are mirror images
    body = body - roof_gills(-233.0, -209.0, 8.0, 34.0)
    body = body - __import__('parts.w3_frame', fromlist=['relief']).relief()          # slots where frame tubes pass through the skin
    return body



def front_window():
    """Hull of the front mechanism over the lean range, projected to (x, z), grown by 4 mm: a clean polygon cut through the flanks."""
    import w3_scene as S
    pts = []
    for ph in range(-25, 26, 5):
        for n, m, k in S.scene(float(ph)):
            if n.startswith(("arm_", "pod_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod")):
                pts += [(float(x), float(z)) for x, y, z in m.vertices[::7]]
    hull = MultiPoint(pts).convex_hull.buffer(5.5, join_style=2).simplify(2.0)
    return hull


# styling in the new frame (x, z): recessed painted panels (0.8 mm) and through vents on both flanks, as in the references
PANELS = [  # recessed
    [(-232, -15), (-132, -18), (-124, -6), (-232, 2)],                          # low sill panel
    [(-205, 6), (-152, 6), (-130, 24), (-152, 46), (-205, 38)],               # big diagonal panel behind the arm window
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


TENT_K = 68.0, -9.3, 3.615           # flank tent: y = 68 - (z + 9.3) / 3.615 above z -9.3


def _flank_y(x, z):
    """Skin outer surface |y| at (x, z): the smaller of the plan half width and the tent."""
    tent = TENT_K[0] - (z - TENT_K[1]) / TENT_K[2]
    return min(hw_in(min(max(x, -299.0), 29.0), 0.0), min(68.0, tent))


def flank_gills(tri, n, pitch=5.4, slat=2.6, shift=7.0):
    """Louvred vent on both flanks, n horizontal slats inside a triangle (x, z); each slot is cut slanted so its opening faces the rear."""
    poly = Polygon(tri)
    z0 = poly.bounds[1] + 2.0
    out = None
    for k in range(n):
        zc = z0 + k * pitch
        seg = LineString([(-500, zc + slat / 2), (500, zc + slat / 2)]).intersection(poly.buffer(-1.0))
        if seg.is_empty:
            continue
        xa, xb = seg.bounds[0], seg.bounds[2]
        xm = 0.5 * (xa + xb)
        ys = _flank_y(xm, zc)
        for s in (1, -1):
            yo, yi = s * (ys + 4.0), s * (ys - 6.0)
            quad = [(xa, yo), (xb, yo), (xb + shift, yi), (xa + shift, yi)]             # outer edge rearward, inner edge forward
            cut = MB.prism_xy(quad, zc - slat / 2, zc + slat / 2)
            out = cut if out is None else out + cut
    return out


def roof_gills(x0, x1, y0, y1, n=4, slat=3.0, shift=8.0):
    """Roof vent over the motor: n slats across y, each slot slanted so the opening faces the rear (mirrored left/right)."""
    pitch = (x1 - x0 - slat) / (n - 1)
    out = None
    for k in range(n):
        xa = x0 + k * pitch
        zs = top_z(xa + slat / 2, 0.0)
        quad = [(xa, zs + 4.0), (xa + slat, zs + 4.0), (xa + slat + shift, zs - 6.0), (xa + shift, zs - 6.0)]    # top edge rearward of the bottom edge
        for s in (1, -1):
            ya, yb = (y0, y1) if s > 0 else (-y1, -y0)
            cut = MB.prism_xz(quad, ya, yb)
            out = cut if out is None else out + cut
    return out


def rocker_flare(m, bulge=3.5, z_lo=-22.0, max_edge=4.5):
    """Rocker panels: the lower flank swells outward by up to `bulge` mm (a smooth sin^2 profile from z_lo up to z = 0) and comes back in
    to meet the base plate.  The mesh is subdivided first so the displacement is smooth; inner and outer surfaces move together."""
    v, f = trimesh.remesh.subdivide_to_size(np.asarray(m.vertices), np.asarray(m.faces), max_edge=max_edge)
    v = v.copy()
    y, z = v[:, 1], v[:, 2]
    t = np.clip((z - z_lo) / (0.0 - z_lo), 0.0, 1.0)
    b = bulge * np.sin(np.pi * t) ** 2
    a = np.clip((np.abs(y) - 38.0) / 14.0, 0.0, 1.0)
    a = a * a * (3.0 - 2.0 * a)
    v[:, 1] = y + np.sign(y) * b * a
    import fast_simplification
    out = trimesh.Trimesh(v, f, process=True)
    out.merge_vertices()
    for red in (0.8, 0.65, 0.5):                                                              # flat areas collapse again; keep the first watertight result
        v2, f2 = fast_simplification.simplify(v, np.asarray(f), target_reduction=red, agg=3)
        t = trimesh.Trimesh(v2, f2, process=True)
        t.merge_vertices()
        if t.is_watertight and len(t.split(only_watertight=False)) == 1:
            return t
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
    m = rocker_flare(m)
    rel = __import__('parts.w3_frame', fromlist=['relief']).relief()                 # the flare moved the skin: cut the tube slots again
    m = MB.to_trimesh(MB.man(m) - rel)
    m.merge_vertices()
    m.export(OUT / "body3.stl")
    print("lid3", len(ml.faces), ml.is_watertight, np.round(ml.extents, 1).tolist())
    print("body3", len(m.faces), m.is_watertight, round(m.volume), np.round(m.bounds, 1).tolist())


if __name__ == "__main__":
    main()
