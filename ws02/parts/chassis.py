"""Chassis: a narrow front tub and a wide rear cradle, each in left and right halves split on y = 0.

Left is +y. Per section the left half carries the keyed pins, M2 insert pilots and (cradle) the pivot boss; the
right half carries sockets and bolt clearance holes, and (tub) the servo ear holes, (cradle) the access hole to the
swingarm hatch and motor. The tub is narrow so the lean bars, hubs and steering links sweep outside it; the cradle
is wide for the swingarm. Print frame: outer wall face on the bed, split face up, see cad.Frame.
"""
import math

from cad import Frame, Part

REAR_EAR, END_BULKHEAD = 0, 1


def _frame(p, side, y_in):
    return Frame(side, y_in + p.ch_wall, abs_y=True)


def _joins(p, f, part, side, bulkheads, y_out):
    """Split-face through-bolts (or insert pilots on the left), pins and sockets for each bulkhead."""
    for (x0, x1, _), zs, zp in bulkheads:
        xc = (x0 + x1) / 2
        for z in zs:
            if side > 0:
                f.cyl(part, xc, z, p.m2_insert_hole, (-1.0, 6.0), op="cut")
            else:
                f.cyl(part, xc, z, p.m2_clear, (-1.0, y_out + 1.0), op="cut")
        if side > 0:
            f.cyl(part, xc, zp, p.ch_pin_dia, (-3.0, 0.4))
        else:
            f.cyl(part, xc, zp, p.ch_pin_dia + 2 * p.clr_press, (-1.0, 3.5), op="cut")


def _body_keys(p, f, part, keys, y_in, y_out):
    """Pads on the inner wall face with blind sockets from the outer face: the body side panels' pins locate here."""
    for x, z in keys:
        f.cyl(part, x, z, p.ch_key_pad_dia, (y_in - p.ch_key_pad_len, y_in + 0.4))
    for x, z in keys:
        f.cyl(part, x, z, p.ch_key_socket, (y_out - p.ch_key_socket_depth, y_out + 1.0), op="cut")


def tub(p, side):
    y_in = p.ch_in
    y_out = y_in + p.ch_wall
    f = _frame(p, side, y_in)
    name = "chassis_tub_left" if side > 0 else "chassis_tub_right"
    part = Part(name, "outer wall on bed, split face up", "PETG")
    z_lo = p.ch_floor_z[0]
    ear0, ear1, ear_top = p.ch_bulkheads[REAR_EAR]
    ex0, ex1, end_top = p.ch_bulkheads[END_BULKHEAD]
    f.poly(part, p.ch_profile, (y_in, y_out))
    f.box(part, p.ch_floor_x, (0.0, y_out), p.ch_floor_z)
    f.box(part, (ear0, ear1), (0.0, y_out), (p.ch_ear_bottom, ear_top))
    f.box(part, (ex0, ex1), (0.0, y_out), (z_lo, end_top))
    for z in (0.0, p.upright_len):
        f.cyl_x(part, 0.0, z, p.pin_dia + p.clr_slide, (ear0 - 1.0, ear1 + 1.0), op="cut")
    _joins(p, f, part, side, zip(p.ch_bulkheads, p.ch_screws, p.ch_pins), y_out)
    for ya, z in p.ch_join_bolts:
        f.cyl_x(part, ya, z, p.m2_insert_hole, (ex0 - 1.0, ex0 + 4.0), op="cut")
    _body_keys(p, f, part, p.ch_body_keys_tub, y_in, y_out)
    for sd, ya, z in p.ch_yoke_bolts:
        if sd == side:
            f.cyl_x(part, ya, z, p.m2_clear, (ear0 - 1.0, ear1 + 1.0), op="cut")
    tab_ya = -(p.servo_center_y - p.servo_ear_span / 2) if side < 0 else p.servo_center_y + p.servo_ear_span / 2
    f.cyl_x(part, tab_ya, p.servo_shaft_z, p.servo_tab_pilot, (ear0 - 1.0, ear0 + p.servo_ear_insert_depth), op="cut")
    for y0, y1, z0, z1 in p.ch_servo_windows:
        lo, hi = (max(-y1, 0.0), -y0) if side < 0 else (max(y0, 0.0), y1)
        if hi > lo:
            f.box(part, (ear0 - 1.0, ear1 + 1.0), (lo - (1.0 if lo == 0.0 else 0.0), hi), (z0, z1), op="cut")
    if side < 0:
        ly0, ly1, lz0, lz1 = p.ch_lead_window
        f.box(part, (ex0 - 1.0, ex1 + 1.0), (ly0 - 1.0, ly1), (lz0, lz1), op="cut")
        for t0, t1 in ((p.ch_tie_slots[0], p.ch_tie_slots[1]), (p.ch_tie_slots[2], p.ch_tie_slots[3])):
            f.box(part, p.ch_tie_x, (t0, t1), (p.ch_floor_z[0] - 1.0, p.ch_floor_z[1] + 1.0), op="cut")
    else:
        _, _, lz0, lz1 = p.ch_lead_window
        f.box(part, (ex0 - 1.0, ex1 + 1.0), (-1.0, p.ch_lead_window_left), (lz0, lz1), op="cut")
    return part


def front_yoke(p):
    """Front lean pivots: a leg plate with two beams that bolt to the rear ear. Narrow, so the lean arms sweep outside it.
    Print frame: u = -y, v = z, w = leg front face - x (front face on the bed, beams grow up)."""
    part = Part("front_yoke", "front face on the bed, beams up", "PETG")
    lx0, lx1 = p.yoke_leg
    hw = p.yoke_hw
    t_leg = lx1 - lx0
    z_lo, z_hi = p.yoke_bottom[0], p.yoke_top[1]
    ear_front = p.ch_bulkheads[REAR_EAR][1]
    w_beam = lx1 - ear_front
    part.box((-hw, z_lo, 0.0), (2 * hw, z_hi - z_lo, t_leg))
    for z0, z1 in (p.yoke_top, p.yoke_bottom):
        part.box((-hw, z0, t_leg - 0.4), (2 * hw, z1 - z0, w_beam - t_leg + 0.4))
    for z in (0.0, p.upright_len):
        part.cyl((0.0, z, -1.0), p.pin_dia + p.clr_slide, t_leg + 2.0, op="cut")
    for s in (1, -1):
        part.cyl((s * p.cage_pins[0], p.cage_pins[1], -1.0), p.ch_key_socket, p.ch_ear_socket_depth + 1.0, op="cut")
    for sd, ya, z in p.ch_yoke_bolts:
        part.cyl((-sd * ya, z, w_beam - 6.0), p.m2_insert_hole, 7.0, op="cut")
    for s in (1, -1):
        part.cyl((s * p.hood_screw_y, p.yoke_top[1] - 6.0, lx1), p.m2_insert_hole, 7.0, axis="Y", op="cut")
    return part


def cradle(p, side):
    y_in = p.ch_in_rear
    y_out = y_in + p.ch_wall
    f = _frame(p, side, y_in)
    name = "chassis_cradle_left" if side > 0 else "chassis_cradle_right"
    part = Part(name, "outer wall on bed, split face up", "PETG")
    f.poly(part, p.ch_rear_profile, (y_in, y_out))
    bx0, bx1, bz = p.ch_rear_bulkhead
    f.box(part, (bx0, bx1), (0.0, y_out), (p.ch_rear_profile[0][1], bz))
    _joins(p, f, part, side, [((bx0, bx1, bz), p.ch_screws[END_BULKHEAD], p.ch_pins[END_BULKHEAD])], y_out)
    for ya, z in p.ch_join_bolts:
        f.cyl_x(part, ya, z, p.m2_clear, (bx0 - 1.0, bx1 + 1.0), op="cut")

    _body_keys(p, f, part, p.ch_body_keys_rear, y_in, y_out)
    mx, mz = p.pivot_xz
    if side > 0:
        # the 2830 motor sits against the inside of this wall; shaft and four M2.5 screws pass through to the flange
        f.cyl(part, mx, mz, p.motor_bore_dia + 2.0, (y_in - 1.0, y_out + 1.0), op="cut")
        for k in range(4):
            a = math.radians(45 + 90 * k)
            f.cyl(part, mx + p.pu_mount_m25_pcd / 2 * math.cos(a), mz + p.pu_mount_m25_pcd / 2 * math.sin(a),
                  p.m25_clear, (y_in - 1.0, y_out + 1.0), op="cut")
    return part


def motor_flange(p):
    """Outside the cradle's left wall: clamps the motor with its four screws and carries the swingarm's pivot boss."""
    part = Part("motor_flange", "flange down, boss up", "PETG")
    part.cyl((0.0, 0.0, 0.0), p.motor_pad_dia, p.motor_flange_t)
    part.cyl((0.0, 0.0, p.motor_flange_t - 0.4), p.ch_boss_dia, p.motor_boss_len + 0.4)
    part.cyl((0.0, 0.0, -1.0), p.motor_bore_dia, p.motor_flange_t + p.motor_boss_len + 2.0, op="cut")
    for k in range(4):
        a = math.radians(45 + 90 * k)
        x, y = p.pu_mount_m25_pcd / 2 * math.cos(a), p.pu_mount_m25_pcd / 2 * math.sin(a)
        part.cyl((x, y, -1.0), p.m25_clear, p.motor_flange_t + 2.0, op="cut")
        part.cyl((x, y, p.motor_flange_t - 1.2), p.m25_head, 2.0, op="cut")
    return part


def build(p):
    return [tub(p, +1), tub(p, -1), front_yoke(p), cradle(p, +1), cradle(p, -1), motor_flange(p)]
