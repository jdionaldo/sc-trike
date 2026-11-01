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
    if bracket_pilots:                       # steer-servo mount screws into the front face of the lower bar
        for sign in (-1, 1):
            for y in (53.0, 64.0):
                part.cyl((sign * y, 0.0, p.bar_w - p.br_pilot_depth), p.m2_insert_hole, p.br_pilot_depth + 1.0, op="cut")
    return part


def servo_mount(p, side):
    """Steer-servo mount: a wall that screws to the front face of the lower bar and a plate that clamps the servo ears.
    Print frame: u = side * y, v = side * z, w = x - ssv_mount_x0 (a proper rotation); the wall lies on the bed."""
    name = "servo_mount_left" if side > 0 else "servo_mount_right"
    part = Part(name, "wall flat on the bed, plate standing up", "PETG")
    part.supports = True                    # the relief notches in the plate leave short overhangs
    t = p.ssv_mount_t
    ztop = p.ssv_z_bottom + p.servo_h
    xc = p.ssv_x - p.ssv_mount_x0
    yc = p.ssv_center_y
    w_end = xc + p.servo_w / 2 + 1.0
    u0, u1 = p.ssv_mount_y
    part.box((u0, ztop, 0.0), (u1 - u0, t, w_end))                           # plate over the servo top
    v0 = -p.bar_h / 2 - 8.0 - 0.0
    wu0, wu1 = p.ssv_wall_y
    part.box((wu0, v0, 0.0), (wu1 - wu0, ztop + t - v0, t))                  # wall against the bar
    for u in (53.0, 64.0):
        part.cyl((u, -p.bar_h / 2 + 2.0, -1.0), p.m2_clear, t + 2.0, op="cut")
    for du in (-p.ssv_hole_dy, p.ssv_hole_dy):
        for dw in (-5.0, 5.0):
            part.cyl((yc + du, ztop - 1.0, xc + dw), p.m2_clear, t + 2.0, axis="Y", op="cut")
    part.box((u0 - 1.0, ztop - 1.0, -1.0), (wu0 - u0 + 1.0, t + 2.0, 18.0 - p.ssv_mount_x0), op="cut")                    # clear the yoke leg
    part.box((wu1, ztop - 1.0, -1.0), (u1 - wu1 + 1.0, t + 2.0, 18.5 - p.ssv_mount_x0 + 1.0), op="cut")   # clear the upright post
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
            rod(p, "rod_drive", p.servo_rod_len, p.rod_drive_boss), rod(p, "tie_rod", p.ssv_rod_len, p.rod_boss),
            servo_mount(p, +1), servo_mount(p, -1)]
