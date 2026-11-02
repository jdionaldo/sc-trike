"""WS-03 whale tail: a duck-tail wing as wide as the front track (269 mm) over the rear deck, parallel to the hood's top line (the lead edge
is higher than the tail edge: downforce), with a raised rim, a kicked-up rear lip and underside ribs.  Three printed pieces (centre and two
outer wings, split at y = +-66); two struts per side from the rear frame node up through the hood skin screw into bosses under the plate.

Local print frame: u = chord (0 at the front root, negative rearward), v = span (y), plate lower surface at z = 0; the STL is lifted by TZ so the
underside ribs and bosses stand on the bed.  Placement: translate to the root point and tilt by the hood slope.
"""
import math

import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart, _clean

SPAN = 134.5                       # half span = half the front track (269 / 2)
CHORD = 110.0                      # root at u = 0, trailing edge at u = -CHORD
X_ROOT = -262.0                    # assembly x of the root
GAP = 9.7                          # plate lower surface above the hood top line
TZ = 6.5                           # STL lift (rib / boss depth)
PLATE_T, RIM_T, RIM_H, LIP_H = 3.0, 2.4, 7.0, 14.0
STRUT_X, STRUT_Y = -290.0, 38.0    # strut tops (assembly x, |y|)
SPLIT = 66.0


def hood_top(x):
    return 97.0 + (97.0 - 83.3) / 89.1 * (x + 259.0)               # hood top line from (-259, 97) to (-348.1, 83.3), extended


SLOPE = (97.0 - 83.3) / 89.1                                        # rise toward the front (0.154)
ALPHA = math.atan(SLOPE)


def place_matrix():
    """Local print frame -> assembly (before the TZ lift)."""
    z0 = hood_top(X_ROOT) + GAP
    R = trimesh.transformations.rotation_matrix(-ALPHA, [0, 1, 0])
    T = np.eye(4); T[:3, 3] = (X_ROOT, 0.0, z0)
    return T @ R


def strut_node():
    """Assembly point under the plate where the strut pad meets the boss (pad top = boss bottom - 0.2)."""
    u = (STRUT_X - X_ROOT) / math.cos(ALPHA)
    p = place_matrix() @ np.array([u, 0.0, -6.0, 1.0])
    return np.array([STRUT_X, STRUT_Y, p[2]])                       # z of the boss bottom at the strut


def _planform():
    from shapely.geometry import Polygon
    pts = [(0, 42), (-18, 70), (-34, SPAN), (-CHORD, SPAN), (-CHORD, -SPAN), (-34, -SPAN), (-18, -70), (0, -42)]
    return Polygon(pts).buffer(-8.0).buffer(8.0)                    # rounded corners


def _prism(poly, z0, z1):
    return MB.prism_xy(list(poly.exterior.coords)[:-1], z0, z1)


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def _whole(p):
    pl = _planform()
    inner = pl.buffer(-RIM_T)
    body = _prism(pl, 0.0, PLATE_T)
    rim = _prism(pl, PLATE_T - 0.1, PLATE_T + RIM_H) - _prism(inner, PLATE_T - 0.2, PLATE_T + RIM_H + 1.0)
    body = body + rim
    body = body + (_prism(pl, PLATE_T - 0.1, PLATE_T + LIP_H) ^ _box(-CHORD - 1.0, -CHORD + 7.0, -200.0, 200.0, 0.0, 40.0)) - _prism(inner, PLATE_T - 0.2, PLATE_T + LIP_H + 1.0)   # rear lip
    for y in (-100.0, -66.0, -34.0, 34.0, 66.0, 100.0):                 # chordwise ribs under the plate
        body = body + (_box(-CHORD, 0.0, y - 1.5, y + 1.5, -5.0, PLATE_T + 0.1) ^ _prism(pl.buffer(-0.2), -6.0, PLATE_T + 1.0))
    ux = (STRUT_X - X_ROOT) / math.cos(ALPHA)
    for sg in (1, -1):                                                   # strut bosses
        body = body + Manifold.cylinder(6.0 + 0.1, 6.0, 6.0, 36).translate((ux, sg * STRUT_Y, -6.0))
        body = body - Manifold.cylinder(PLATE_T + RIM_H + 14.0, 1.35, 1.35, 24).translate((ux, sg * STRUT_Y, -6.1))        # clearance through the plate
        body = body - Manifold.cylinder(2.8, 2.6, 2.6, 28).translate((ux, sg * STRUT_Y, PLATE_T - 2.7))                    # counterbore for the head
    return body


def _piece(which):
    body = _whole(None)
    if which == "center":
        keep = _box(-CHORD - 2.0, 2.0, -SPLIT + 0.025, SPLIT - 0.025, -10.0, 40.0)
    elif which == "left":
        keep = _box(-CHORD - 2.0, 2.0, SPLIT + 0.025, 200.0, -10.0, 40.0)
    else:
        keep = _box(-CHORD - 2.0, 2.0, -200.0, -SPLIT - 0.025, -10.0, 40.0)
    m = MB.to_trimesh(body ^ keep)
    m.merge_vertices()
    m = max(m.split(only_watertight=False), key=lambda c: abs(c.volume))
    m.apply_translation((0.0, 0.0, TZ))
    return _clean(m)


def build(p):
    return [MeshPart("w3_tail_center", lambda: _piece("center"), walls=False, supports=True),
            MeshPart("w3_tail_left", lambda: _piece("left"), walls=False, supports=True),
            MeshPart("w3_tail_right", lambda: _piece("right"), walls=False, supports=True)]


def placed():
    out = []
    M = place_matrix()
    for n in ("w3_tail_center", "w3_tail_left", "w3_tail_right"):
        m = trimesh.load(f"out/stl/{n}.stl")
        m.apply_translation((0.0, 0.0, -TZ))
        m.apply_transform(M)
        out.append((n, m))
    return out
