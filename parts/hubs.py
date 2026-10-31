"""Front hubs: steering knuckle with integrated stub axle and kingpin bore.

Chassis frame (x fwd, y left, z up, origin at lower lean-bar pivot on the centreline).
Print frame: u = x, v = s*z, w = side*y - y0, with s = -1 left / +1 right so both are proper rotations
(a mirror would print the wrong hand). w = 0 is the inboard lug face on the bed, the stub axle grows upward.
"""
import math

from cad import Part, OVERLAP


def hub(p, side):
    s = -1.0 if side > 0 else 1.0
    name = "hub_left" if side > 0 else "hub_right"
    y_in = p.front_track / 2 - p.front_tire_w / 2 - p.hub_thick       # hub inboard face (abs y)
    y0 = y_in - p.hub_lug_len
    c = math.radians(p.caster_deg)
    k_ax = (-math.sin(c), s * math.cos(c))                              # kingpin axis in (u, v)
    wk = p.bar_half - y0                                                # kingpin plane in w
    part = Part(name, "stub axle up, inboard face on bed, kingpin bore horizontal", "PETG")

    x0, x1 = p.hub_x
    z0, z1 = p.hub_z
    v_lo, v_hi = sorted((s * z0, s * z1))
    w_body = p.hub_lug_len
    part.box((x0, v_lo, 0.0), (x1 - x0, v_hi - v_lo, w_body + p.hub_thick))

    ax, az = 0.0, -p.axle_drop
    part.cyl((ax, s * az, w_body + p.hub_thick - OVERLAP), p.hub_stub_dia, p.hub_stub_len + OVERLAP)

    arm_x, _, arm_z = p.steer_arm_xyz
    part.cyl((arm_x, s * arm_z, 0.0), p.hub_lug_dia, w_body + OVERLAP)
    lug_lo = min(s * arm_z, s * az) - p.hub_lug_dia / 2
    lug_hi = max(s * arm_z, s * az) + p.hub_lug_dia / 2
    part.box((min(arm_x, ax) - p.hub_lug_dia / 2, lug_lo, 0.0),
             (abs(arm_x - ax) + p.hub_lug_dia, lug_hi - lug_lo, w_body + OVERLAP))

    part.cyl((ax, s * az, -1.0), p.axle_dia + p.clr_slide, w_body + p.hub_thick + p.hub_stub_len + 2.0, op="cut")
    part.cyl((arm_x, s * arm_z, -1.0), p.ball_stud_dia + p.clr_press * 2, w_body + 2.0, op="cut")

    length = 3 * p.kingpin_len
    part.add("solid.cylinder", diameter=p.pin_dia + p.clr_slide, height=length,
             base=[-k_ax[0] * length / 2, -k_ax[1] * length / 2, wk], axis=[k_ax[0], k_ax[1], 0.0],
             operation="cut", targets=[name])
    return part


def build(p):
    return [hub(p, +1), hub(p, -1)]
