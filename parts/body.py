"""Body skin: curved lofted shells printed with supports, plus two flat plates (bumper cage and rear bumper).

Each shell is a SolidCraft loft through closed thin-band sections (an outer curve and its 1.6 mm inner offset), so the
loft itself is the hollow skin. A section is a cap: vertical sides from a rim up to a shoulder, a quarter-ellipse shoulder
curve, and a gently crowned roof. Shells are authored in the chassis frame (x forward, y left, z up), then turned
upside down (roof on the bed) for printing; `to_chassis` records the inverse. The lower side bands print lying on their
outer face. Yellow: hood, roof, pods. Black: glazing, lower bands, bumpers.

Chassis keys: the lower bands and the pods carry short pins that enter the sockets in pads on the chassis walls; the
hood has two screw bosses onto the front yoke. Shells butt against each other and are glued.
"""
import math

import numpy as np

from cad import Part

YELLOW, BLACK = "yellow", "black"


def _outer(w, rim, zs, zr, rw, crown, n=6):
    """Open outer curve from the left rim up and over the roof to the right rim, as (y, z) points."""
    left = [(-w, rim), (-w, zs)]
    for k in range(1, n):
        a = (math.pi / 2) * k / n
        left.append((-rw - (w - rw) * math.cos(a), zs + (zr - zs) * math.sin(a)))
    left += [(-rw, zr), (0.0, zr + crown)]
    right = [(-y, z) for y, z in reversed(left[:-1])]
    return left + right


def _band(outer, t):
    """Closed band: the outer curve and its inward offset by t, reversed."""
    pts = np.asarray(outer, float)
    inner = []
    last = len(pts) - 1
    for i, q in enumerate(pts):
        if i == 0:
            n = np.array([-1.0, 0.0])
        elif i == last:
            n = np.array([1.0, 0.0])
        else:
            d = pts[i + 1] - pts[i - 1]
            n = np.array([d[1], -d[0]]) / np.linalg.norm(d)
            if n[1] < 0:
                n = -n
        inner.append(q - n * t)
    return [tuple(map(float, q)) for q in pts] + [tuple(map(float, q)) for q in inner[::-1]]


def _roof_z(stations, x):
    """Outer roof height on the centreline at x, linearly between stations (crown included)."""
    xs = [-s[0] for s in stations]
    return float(np.interp(-x, xs, [s[4] + 1.5 for s in stations]))


def _shell(name, color, stations, p, pins=(), screw_holes=(), windows=(), cuts=(), t=None):
    part = Part(name, "roof down on the bed, open side up", "PETG", supports=True)
    t = t or p.body_t
    for x, w, rim, zs, zr, rw in stations:
        part.add("sketch.create", plane="YZ", offset=x)
        part.add("sketch.line", points=[list(q) for q in _band(_outer(w, rim, zs, zr, rw, 1.5), t)], closed=True)
        part.add("sketch.finish")
    part.add("solid.loft", sections=[{"sketch": i + 1} for i in range(len(stations))], **part._op("join"))
    for x, y, z, axis, length in pins:
        part.cyl((x, y, z), p.body_pin_dia, length, axis=axis)
    for x, y in screw_holes:
        part.cyl((x, y, p.yoke_top[1]), p.m2_clear, 30.0, axis="Z", op="cut")
    for pts in windows:
        part.prism_xz(pts)
    for kind, params in cuts:
        if kind == "cyl":
            part.cyl(params[0], params[1], params[2], axis="Y", op="cut")
        else:
            part.box(params[0], params[1], op="cut")
    part.orient(180.0, max(s[4] for s in stations) + 1.6)
    return part


def _band_part(p, side):
    """Lower side band: a thin curved wall printed lying on its outer face (pins grow up)."""
    t, w = p.body_t, p.body_band_w
    z0 = p.body_floor_z
    x0, x1 = p.body_band_x
    name = "body_side_lower_left" if side > 0 else "body_side_lower_right"
    part = Part(name, "outer face on the bed, pins up", "PETG")
    for x, z1 in zip((x0, (x0 + x1) / 2, x1), p.body_band_z):
        part.add("sketch.create", plane="YZ", offset=x)
        part.add("sketch.line", points=[[side * (w - t), z0], [side * w, z0], [side * w, z1], [side * (w - t), z1]],
                 closed=True)
        part.add("sketch.finish")
    part.add("solid.loft", sections=[{"sketch": i + 1} for i in range(3)], **part._op("join"))
    pin_len = (w - t) - (p.ch_in + p.ch_wall) + p.ch_key_socket_depth - 0.2
    for kx, kz in p.ch_body_keys_tub:
        part.cyl((kx, side * (w - t + 0.4), kz), p.body_pin_dia, pin_len + 0.4, axis=[0, -side, 0])
    part.orient(-90.0 * side, w)
    return part


def _shells(p):
    t = p.body_t
    s = dict(p.body_stations)
    hp = p.body_pod_w
    pod_pin = hp - t - (p.ch_in_rear + p.ch_wall) + p.ch_key_socket_depth - 0.2
    pins = [(kx, sd * (hp - t + 0.4), kz, [0, -sd, 0], pod_pin + 0.4) for kx, kz in p.ch_body_keys_rear for sd in (1, -1)]
    ax, az = p.axle_xz
    x0 = p.body_open_x
    cuts = [("box", ((p.body_x_tail - 4.0, -p.body_open_hw, -40.0), (x0 - p.body_x_tail + 4.0, 2 * p.body_open_hw, 120.0)))]
    screw_holes = [(0.0, sy * p.hood_screw_y) for sy in (1, -1)]
    return [(_shell("body_windscreen", BLACK, s["glass"], p), BLACK),
            (_shell("body_roof", YELLOW, s["roof"], p), YELLOW),
            (_shell("body_rear_window", BLACK, s["rear"], p), BLACK),
            (_shell("body_pods", YELLOW, s["pods"], p, pins=pins, cuts=cuts, windows=p.body_pod_windows), YELLOW)]


def _standoff(p, side):
    """Spacer between the front yoke top beam and the hood roof; the hood screw passes through it into the beam."""
    s = dict(p.body_stations)["hood"]
    inner = _roof_z(s, 0.0) - 1.5 * (p.hood_screw_y / s[2][5]) - p.body_t
    length = inner - p.yoke_top[1] - 0.4
    name = "hood_standoff_left" if side > 0 else "hood_standoff_right"
    part = Part(name, "standing", "PETG")
    part.cyl((0.0, 0.0, 0.0), p.body_boss_dia, length)
    part.cyl((0.0, 0.0, -1.0), p.m2_clear, length + 2.0, op="cut")
    m = np.eye(4)
    m[:3, 3] = (0.0, side * p.hood_screw_y, p.yoke_top[1] + 0.2)
    return part, m


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def _plate_frame(o, eu, ev, ew):
    eu, ev, ew = _unit(eu), _unit(ev), _unit(ew)
    assert abs(np.linalg.det(np.array([eu, ev, ew]).T) - 1.0) < 1e-9, "panel frame must be a proper rotation"
    return {"o": np.asarray(o, float), "eu": eu, "ev": ev, "ew": ew}


def _bumper_spec(p):
    t, hp = p.body_t, p.body_pod_w
    last = dict(p.body_stations)["pods"][-1]
    z_lo, z_hi = p.body_pod_floor_z, last[3]
    x = p.body_x_tail - t
    fr = _plate_frame((x, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0))
    return {"name": "body_rear_bumper", "color": BLACK, "frame": fr, "t": t,
            "outline": [(x, -(hp + t), z_lo), (x, hp + t, z_lo), (x, hp + t, z_hi), (x, -(hp + t), z_hi)]}


def _cage_spec(p):
    """Printed rear face down, front face up, so the light and emblem pockets open upward. Two bought steel dowels
    (BOM: DOWEL_2x18) press into the rear face and key into the front yoke leg."""
    x_rear = p.cage_x[0]
    t = p.cage_x[1] - p.cage_x[0]
    fr = _plate_frame((x_rear, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0))
    y, (z0, z1), bar = p.cage_y, p.cage_z, p.cage_bar
    top_bar = 11.0
    spec = {"name": "body_bumper_cage", "color": BLACK, "frame": fr, "t": t,
            "outline": [(x_rear, -y, z0), (x_rear, y, z0), (x_rear, y, z1), (x_rear, -y, z1)],
            "orientation": "rear face on the bed, front up", "openings": [], "pockets": [],
            "dowels": [(x_rear, s * p.cage_pins[0], p.cage_pins[1]) for s in (1, -1)]}
    for s in (1, -1):
        ya, yb = sorted((s * 2.5, s * (y - bar)))
        spec["openings"].append([(x_rear, ya, z0 + bar), (x_rear, yb, z0 + bar), (x_rear, yb, z1 - top_bar),
                                 (x_rear, ya, z1 - top_bar)])
        cy, cz = s * 20.0, z1 - top_bar / 2
        spec["pockets"].append([(x_rear, cy + dy, cz + dz) for dy, dz in
                                ((-1.2, -4), (1.2, -4), (1.2, -0.5), (4.7, 3.4), (3.0, 5.0), (0, 1.6), (-3.0, 5.0),
                                 (-4.7, 3.4), (-1.2, -0.5))])
    spec["emblem"] = ((x_rear, 0.0, z1 - top_bar / 2), 4.4)
    return spec


def _uv(spec, point):
    fr = spec["frame"]
    d = np.asarray(point, float) - fr["o"]
    return float(d @ fr["eu"]), float(d @ fr["ev"]), float(d @ fr["ew"])


def _poly_cut(part, spec, pts3d, w0, w1):
    part.prism("XY", w0, [_uv(spec, q)[:2] for q in pts3d], w1 - w0, op="cut")


def _plate_part(p, spec):
    part = Part(spec["name"], spec.get("orientation", "outer face on the bed"), "PETG")
    t = spec["t"]
    part.prism("XY", 0.0, [_uv(spec, q)[:2] for q in spec["outline"]], t)
    for opening in spec.get("openings", []):
        _poly_cut(part, spec, opening, -1.0, t + 1.0)
    for pocket in spec.get("pockets", []):
        _poly_cut(part, spec, pocket, t - 2.4, t + 1.0)
    if "emblem" in spec:
        center, r = spec["emblem"]
        u, v, _ = _uv(spec, center)
        part.cyl((u, v, t - 1.5), r * 2, 2.5, op="cut")
    for center in spec.get("dowels", []):
        u, v, _ = _uv(spec, center)
        part.cyl((u, v, -1.0), p.body_dowel_hole, 4.0, op="cut")
    return part


def _all(p):
    """(part, colour, print-to-chassis matrix) for every body part."""
    items = [(part, color, part.to_chassis) for part, color in _shells(p)]
    for side in (1, -1):
        part = _band_part(p, side)
        items.append((part, BLACK, part.to_chassis))
    for spec in (_bumper_spec(p), _cage_spec(p)):
        fr = spec["frame"]
        m = np.eye(4)
        m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = fr["eu"], fr["ev"], fr["ew"], fr["o"]
        items.append((_plate_part(p, spec), spec["color"], m))
    return items


def build(p):
    return [part for part, _, _ in _all(p)]


def placements(p):
    return {part.name: m for part, _, m in _all(p)}


def colors(p):
    return {part.name: c for part, c, _ in _all(p)}
