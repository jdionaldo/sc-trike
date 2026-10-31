"""Lean parallelogram members and modular rods. Pivot bores are printed vertical (axis along print Z).

Bars: print frame u = y, v = z, w = x + bar_w / 2. Upright: w = x - up_x0. Both are proper rotations of chassis axes.
The bar ends are thin tongues on the rear face that lap against the upright post (lap hinge).
"""
import math

from cad import Part


def _bore(p):
    return p.pin_dia + p.clr_slide


def bar(p, name, drive_lug, bracket_pilots=False):
    half = p.bar_half
    part = Part(name, "flat on its side, pivot bores vertical", "PETG")
    body = half - p.bar_end_len
    part.box((-body, -p.bar_h / 2, 0.0), (2 * body, p.bar_h, p.bar_w))
    for sign in (-1, 1):
        u0, u1 = sorted((sign * (body - 0.4), sign * (half + p.bar_pad)))
        part.box((u0, -p.bar_h / 2, 0.0), (u1 - u0, p.bar_h, p.bar_tongue_t))
    if drive_lug:
        part.box((-p.lug_w / 2, -(p.bar_h / 2 + p.lug_drop + p.lug_w / 2), 0.0),
                 (p.lug_w, p.bar_h / 2 + p.lug_drop + p.lug_w / 2, p.lug_t))
    for u in (-half, 0.0, half):
        part.cyl((u, 0.0, -1.0), _bore(p), p.bar_w + 2.0, op="cut")
    if drive_lug:
        part.cyl((0.0, -p.lug_drop, -1.0), p.m2_clear, p.lug_t + 2.0, op="cut")
    if bracket_pilots:
        for sign in (-1, 1):
            for x, y in p.br_screws:
                part.cyl((sign * y, p.bar_h / 2 - p.br_pilot_depth, x + p.bar_w / 2), p.m2_insert_hole,
                         p.br_pilot_depth + 1.0, axis="Y", op="cut")
    return part


def bracket(p, side):
    """Carries the steering link eye below its plate; bolts to the top face of the lower bar. Flat on the bed, plate
    face up. Print frame: x = u, y = -v, z = br_t + br_standoff + 4 - w (a proper rotation)."""
    name = "link_bracket_left" if side > 0 else "link_bracket_right"
    part = Part(name, "plate on bed, standoffs up", "PETG")
    bx0, bx1, by0, by1 = p.br_base
    ax0, ax1, ay0, ay1 = p.br_arm
    sx0, sx1, sy0, sy1 = p.br_strip
    part.box((bx0, min(-side * by0, -side * by1), 0.0), (bx1 - bx0, by1 - by0, p.br_t))
    part.box((ax0, min(-side * ay0, -side * ay1), 0.0), (ax1 - ax0, ay1 - ay0, p.br_t))
    part.box((sx0, min(-side * sy0, -side * sy1), 0.0), (sx1 - sx0, sy1 - sy0, p.br_t))
    for x, y in p.br_screws:
        part.cyl((x, -side * y, p.br_t - 0.4), p.br_boss_dia, p.br_standoff + 0.4)
    for x, y in p.br_screws:
        part.cyl((x, -side * y, -1.0), p.m2_clear, p.br_t + p.br_standoff + 2.0, op="cut")
    ex, ey, _ = p.link_anchor_bar_xyz
    part.cyl((ex, -side * ey, -1.0), p.m2_clear, p.br_t + 2.0, op="cut")
    return part


def upright(p):
    part = Part("upright", "on its side, pivot bores vertical, kingpin socket near-horizontal", "PETG")
    zlo, zhi = p.up_z
    part.box((-p.up_y / 2, zlo, 0.0), (p.up_y, zhi - zlo, p.up_x))
    for z in (0.0, p.upright_len):
        part.cyl((0.0, z, -1.0), _bore(p), p.up_x + 2.0, op="cut")
    c = math.radians(p.caster_deg)
    pivot_edge = _bore(p) / 2 + p.kingpin_gap
    t0, t1 = zlo / math.cos(c), -pivot_edge / math.cos(c)
    base = (0.0, zlo, -p.up_x0 - math.sin(c) * t0)
    part.add("solid.cylinder", diameter=p.pin_dia - p.clr_press, height=(t1 - t0), base=list(base),
             axis=[0.0, math.cos(c), -math.sin(c)], operation="cut", targets=[part.name])
    return part


def rod(p, name, length, boss):
    part = Part(name, "flat, bores vertical", "PETG")
    part.box((0.0, -p.rod_w / 2, 0.0), (length, p.rod_w, p.rod_t))
    for u in (0.0, length):
        part.cyl((u, 0.0, 0.0), boss, p.rod_t)
    for u in (0.0, length):
        part.cyl((u, 0.0, -1.0), p.m2_clear, p.rod_t + 2.0, op="cut")
    return part


def build(p):
    return [bar(p, "lean_bar_upper", False), bar(p, "lean_bar_lower", True, True), upright(p),
            rod(p, "rod_drive", p.servo_rod_len, p.rod_drive_boss), rod(p, "link_steer", p.coupling_link_len, p.rod_boss),
            bracket(p, +1), bracket(p, -1)]
