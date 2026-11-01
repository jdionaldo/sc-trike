"""WS-03 body: a faceted wedge built from clean plan, side and section shapes taken from the base.stl silhouettes (old chassis
frame numbers), mapped to the 3WD frame, hollowed to a 2.4 mm wall with an open belly, windows cut where the front arms
swing. Output: out/mono3/body3.stl (and halves/pieces via split_body3)."""
import sys
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold
from shapely.geometry import MultiPoint, Polygon

import mono_build as MB

OUT = Path("out/mono3")
KX, KY, DZ, XOFF = 1.19, 1.17, 20.7, -14.4        # old frame -> new frame: x' = KX x + XOFF, y' = KY y, z' = z + DZ
WALL = 2.4

# base.stl silhouettes, cleaned (old chassis frame, mm)
SIDE = [(-240, -30), (-210, -25), (-165, -36.5), (-72, -40), (0, -41), (8, -38), (27, -28), (27, -20), (17, 5), (-35, 19.5),
        (-55, 22.5), (-108, 45.5), (-145, 49.2), (-165, 48.7), (-200, 33), (-240, 33)]
HALF = [(-240, 36), (-218, 37), (-215, 44), (-200, 44), (-195, 42), (-165, 57.5), (-100, 57), (-80, 55), (-47, 52), (-25, 47),
        (0, 36), (27, 18)]
SECTION = [(-58, -60), (58, -60), (58, -30), (38, 55), (-38, 55), (-58, -30)]           # (y, z): flanks lean in 11 deg toward the roof


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
        for k in range(1, 14):
            acc = acc + s.translate((0, 0, -5.0 * k))
        s = acc
    return s


def front_window():
    """Hull of the front mechanism over the lean range, projected to (x, z), grown by 4 mm: a clean polygon cut through the flanks."""
    import w3_scene as S
    pts = []
    for ph in range(-30, 31, 6):
        for n, m, k in S.scene(float(ph)):
            if n.startswith(("arm_", "cover_", "uplink_", "carrier_", "knuckle_", "tie_rod", "lean_rod")):
                pts += [(float(x), float(z)) for x, y, z in m.vertices[::7]]
    hull = MultiPoint(pts).convex_hull.buffer(5.5, join_style=2).simplify(2.0)
    return hull


# styling in the new frame (x, z): recessed painted panels (0.8 mm) and through vents on both flanks, as in the references
PANELS = [  # recessed
    [(-292, -8), (-212, -8), (-176, 14), (-292, 14)],                          # low rear sill panel
    [(-205, 4), (-150, 4), (-122, 24), (-150, 52), (-205, 38)],               # big diagonal panel behind the arm window
]
VENTS = [  # through the skin
    [(-282, 40), (-252, 40), (-257, 47), (-282, 47)], [(-282, 49), (-252, 49), (-257, 56), (-282, 56)],      # louvre slots
    [(-238, 22), (-206, 22), (-222, 44)],                                       # triangular vent
]
HATCH = (-176.0, -112.0, 34.0)      # roof access hatch over the ESC bay: x0, x1, half width


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
    for s in (1, -1):
        y0, y1 = (46.0, 100.0) if s > 0 else (-100.0, -46.0)
        body = body - MB.prism_xz(wpts, y0, y1)
    body = body - Manifold.cube((40.0, 46.0, 90.0), center=True).translate((-281.0, 59.0, 0.0))    # rear arm leaves the body, left
    body = body - Manifold.cube((40.0, 46.0, 90.0), center=True).translate((-281.0, -59.0, 0.0))   # mirrored
    for poly in PANELS:
        body = body - flank_cut(poly, 0.8)
    for poly in VENTS:
        body = body - flank_cut(poly)
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
