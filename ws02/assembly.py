"""Places printed parts and bought-part placeholders in the chassis frame for a given pose.

Chassis frame: x forward, y left, z up, origin on the lower lean-bar pivot on the centreline.
Printed parts are exported in their print frames; the matrices below are the inverse of each part's frame.
Joints are rigid transforms driven by kinematics.py (SolidCraft joints were not needed: the transforms are exact).
"""
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import brentq

import kinematics as K
from params import P
from parts import body as body_parts
from parts.swingarm import layout, gear_planes

STL = Path("out/stl")
D2R = math.pi / 180.0


@dataclass
class Item:
    name: str
    mesh: trimesh.Trimesh
    kind: str                        # printed | bought
    group: str = "chassis"           # chassis | swingarm | front


def M4(rows, t=(0.0, 0.0, 0.0)):
    m = np.eye(4)
    m[:3, :3] = np.array(rows, dtype=float)
    m[:3, 3] = t
    return m


def T(x, y, z):
    return M4(np.eye(3), (x, y, z))


def R_axis(axis, ang, point=(0.0, 0.0, 0.0)):
    r = trimesh.transformations.rotation_matrix(ang, axis, point)
    return r


@lru_cache(maxsize=None)
def stl(name):
    return trimesh.load(STL / f"{name}.stl", force="mesh")


def place(name, matrix):
    return stl(name).copy().apply_transform(matrix)


def cyl_y(center, r, y0, y1):
    """Cylinder along y between y0 and y1 about (x, z) of `center`."""
    c = trimesh.creation.cylinder(radius=r, height=abs(y1 - y0), sections=64)
    c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [0, 1, 0]))
    c.apply_translation((center[0], (y0 + y1) / 2, center[2]))
    return c


def box(center, size):
    b = trimesh.creation.box(extents=size)
    b.apply_translation(center)
    return b


def rod_matrix(p0, p1, thickness_hint):
    """Print frame (u along the rod, v across, w thickness) with holes at u = 0 and u = |p1 - p0|."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    e1 = (p1 - p0) / np.linalg.norm(p1 - p0)
    e3 = np.asarray(thickness_hint, float)
    e3 = e3 - e1 * (e3 @ e1)
    e3 /= np.linalg.norm(e3)
    e2 = np.cross(e3, e1)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = e1, e2, e3
    m[:3, 3] = p0 - e3 * P.rod_t / 2
    return m


# ---- print frame to chassis-frame matrices, one per part ----
def print_to_local(name):
    y_tub = P.ch_in + P.ch_wall
    y_cra = P.ch_in_rear + P.ch_wall
    y0 = P.front_track / 2 - P.front_tire_w / 2 - P.hub_thick - P.hub_lug_len
    left = lambda y_out: M4([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, y_out, 0))
    right = lambda y_out: M4([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, -y_out, 0))
    bar = M4([[0, 0, 1], [1, 0, 0], [0, 1, 0]], (-P.bar_w / 2, 0, 0))
    table = {
        "hub_left": M4([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (0, y0, 0)),
        "hub_right": M4([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, -y0, 0)),
        "upright": M4([[0, 0, 1], [1, 0, 0], [0, 1, 0]], (P.up_x0, 0, 0)),
        "lean_bar_upper": bar,
        "lean_bar_lower": bar,
        "link_bracket_left": M4([[1, 0, 0], [0, -1, 0], [0, 0, -1]], (0, 0, P.br_t + P.br_standoff + P.bar_h / 2)),
        "link_bracket_right": M4([[1, 0, 0], [0, -1, 0], [0, 0, -1]], (0, 0, P.br_t + P.br_standoff + P.bar_h / 2)),
        "front_yoke": M4([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], (P.yoke_leg[1], 0, 0)),
        "chassis_tub_left": left(y_tub),
        "chassis_tub_right": right(y_tub),
        "chassis_cradle_left": left(y_cra),
        "chassis_cradle_right": right(y_cra),
        "motor_flange": M4([[1, 0, 0], [0, 0, 1], [0, -1, 0]], (P.pivot_xz[0], y_cra, P.pivot_xz[1])),
        "swingarm_cover": M4([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, P.sw_y_out_b + 8.0, 0)),
        "swingarm_arm": M4([[1, 0, 0], [0, 0, -1], [0, 1, 0]], (0, P.sw_y_out_b, 0)),
        "rear_hub": M4([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], (0, -P.hub_len / 2, 0)),
    }
    return table[name]


def front_end(phi):
    """Per side: bar end, steer angle, hub transform, and the two end points of the steering link."""
    out = {}
    arm = np.array(P.steer_arm_xyz)
    for side in (1, -1):
        d = K.steer_angle(phi, arm, P.link_anchor_bar_xyz, P.coupling_link_len, 0.0, side)
        if math.isnan(d):
            d = K.steer_angle(phi, arm, P.link_anchor_bar_xyz, P.coupling_link_len, math.copysign(0.3, phi), side)
        k0 = K.bar_end(0.0, side)
        k = K.bar_end(phi, side)
        hub = T(*(k - k0)) @ R_axis(K.KP_AXIS, d, k0)
        out[side] = {"k": k, "k0": k0, "delta": d, "hub": hub,
                     "s_end": k + K.rot_axis(K.KP_AXIS, d) @ (arm * np.array([1, side, 1])),
                     "a_end": K.anchor_pos(phi, P.link_anchor_bar_xyz, side)}
    return out


def horn_angle(phi):
    """Horn angle (rad from straight up, toward +y) that holds the drive rod at its length for bar angle phi."""
    lug = np.array([P.lug_drop * math.sin(phi), -P.lug_drop * math.cos(phi)])
    sv = np.array([-P.servo_axis_y, P.servo_shaft_z])

    def f(a):
        tip = sv + P.servo_horn_r * np.array([math.sin(a), math.cos(a)])
        return np.linalg.norm(tip - lug) - P.servo_rod_len

    return brentq(f, -1.3, 1.3), sv, lug


def swing_angle(travel):
    ax, az = P.axle_xz
    mx, mz = P.pivot_xz
    rel = np.array([ax - mx, az - mz])

    def dz(b):
        return -rel[0] * math.sin(b) + rel[1] * math.cos(b) - rel[1] - travel

    return brentq(dz, -0.4, 0.4)


def scene(lean_deg=0.0, travel=0.0, lead=True, body=False):
    phi = lean_deg * D2R
    items = []

    def add(name, mesh, kind="printed", group="chassis"):
        items.append(Item(name, mesh, kind, group))

    add("front_yoke", place("front_yoke", print_to_local("front_yoke")))
    for n in ("mono_left", "mono_right"):               # body shell fused with the tub and cradle (mono_build.py)
        add(n, trimesh.load(Path("out/mono") / f"{n}.stl"))
    add("canopy_lid", trimesh.load(Path("out/mono") / "canopy_lid.stl"), "printed", "body")

    fe = front_end(phi)
    add("lean_bar_lower", place("lean_bar_lower", R_axis([1, 0, 0], phi) @ print_to_local("lean_bar_lower")), group="front")
    add("lean_bar_upper", place("lean_bar_upper", T(0, 0, P.upright_len) @ R_axis([1, 0, 0], phi, (0, 0, 0))
                                @ print_to_local("lean_bar_upper")), group="front")
    for side, tag in ((1, "left"), (-1, "right")):
        e = fe[side]
        add(f"upright_{tag}", place("upright", T(*e["k"]) @ print_to_local("upright")), group="front")
        add(f"hub_{tag}", place(f"hub_{tag}", e["hub"] @ print_to_local(f"hub_{tag}")), group="front")
        wheel = cyl_y((0, side * (P.front_track / 2), -P.axle_drop), P.front_tire_od / 2,
                      side * (P.front_track / 2) - P.front_tire_w / 2, side * (P.front_track / 2) + P.front_tire_w / 2)
        add(f"FRONT_TIRE_WHEEL_{tag.upper()}", wheel.apply_transform(e["hub"]), "bought", "front")
        add(f"link_steer_{tag}", place("link_steer", rod_matrix(e["a_end"], e["s_end"], R_axis([1, 0, 0], phi)[:3, :3] @ np.array([0.0, 0.0, 1.0]))), group="front")
        add(f"link_bracket_{tag}", place(f"link_bracket_{tag}", R_axis([1, 0, 0], phi) @ print_to_local(f"link_bracket_{tag}")),
            group="front")

    a, sv, lug = horn_angle(phi)
    rod_x = sum(P.drive_rod_x) / 2
    tip = sv + P.servo_horn_r * np.array([math.sin(a), math.cos(a)])
    add("rod_drive", place("rod_drive", rod_matrix((rod_x, *tip), (rod_x, *lug), (1, 0, 0))), group="front")
    x_ear = P.ch_bulkheads[0][0]
    horn_len = P.servo_horn_r
    horn = box((x_ear + P.horn_t / 2, 0.0, 0.0), (P.horn_t, 5.0, horn_len))
    horn.apply_translation((0, 0, horn_len / 2))
    horn.apply_transform(R_axis([1, 0, 0], -a))
    horn.apply_translation((0, sv[0], sv[1]))
    add("SERVO_HORN", horn, "bought", "front")
    add("SERVO_9G", box((x_ear - P.servo_h / 2, P.servo_center_y, P.servo_shaft_z), (P.servo_h, P.servo_l, P.servo_w)),
        "bought")

    bay_mid = sum(P.batt_bay) / 2
    floor_top = P.ch_floor_z[1]
    bm = stl("battery_mount")
    add("battery_mount", place("battery_mount", T(bay_mid - bm.bounds[1][0] / 2, -bm.bounds[1][1] / 2, floor_top)))
    add("LIPO_2S", box((bay_mid, 0, floor_top + P.mount_floor + P.lipo_h / 2 + 0.01), (P.lipo_l, P.lipo_w, P.lipo_h)), "bought")
    rx = stl("rx_mount")
    rx_x, rx_y = bay_mid, P.rx_beside_y
    add("rx_mount", place("rx_mount", T(rx_x - rx.bounds[1][0] / 2, rx_y - rx.bounds[1][1] / 2, floor_top)))
    add("RECEIVER", box((rx_x, rx_y, floor_top + P.mount_floor + P.rx_h / 2 + 0.01), (P.rx_l, P.rx_w, P.rx_h)), "bought")

    mx, mz = P.pivot_xz
    beta = swing_angle(travel)
    g = R_axis([0, 1, 0], beta, (mx, 0, mz)) @ T(mx, 0, mz)
    L = layout(P)
    ax, az = P.axle_xz

    def sw(name, mesh, kind="printed"):
        add(name, mesh.apply_transform(g), kind, "swingarm")

    sw("swingarm_arm", place("swingarm_arm", print_to_local("swingarm_arm")))
    sw("swingarm_cover", place("swingarm_cover", print_to_local("swingarm_cover")))
    add("motor_flange", place("motor_flange", print_to_local("motor_flange")), "printed", "chassis")
    y_face = P.ch_in_rear
    add("POWER_UNIT", cyl_y((mx, 0, mz), P.pu_dia / 2, y_face - P.pu_len, y_face), "bought", "chassis")
    add("POWER_UNIT_SHAFT", cyl_y((mx, 0, mz), P.pu_shaft_dia / 2, y_face, y_face + P.pu_shaft_len), "bought", "chassis")
    (s0, s1), (b0, b1) = gear_planes(P)
    sw("GEAR_PINION_1", cyl_y((0, 0, 0), L["r_pin1"], s0, s1), "bought")
    sw("GEAR_1", cyl_y((L["I"][0], 0, L["I"][1]), L["r_gear1"], s0, s1), "bought")
    sw("GEAR_PINION_2", cyl_y((L["I"][0], 0, L["I"][1]), L["r_pin2"], b0, b1), "bought")
    sw("GEAR_2", cyl_y((L["A"][0], 0, L["A"][1]), L["r_gear2"], b0, b1), "bought")
    sw("AXLE_REAR", cyl_y((L["A"][0], 0, L["A"][1]), P.rear_axle_dia / 2, -P.rear_tire_w / 2 - 3.0, P.sw_y_out_b + 1.0), "bought")
    sw("SHAFT_INTERMEDIATE", cyl_y((L["I"][0], 0, L["I"][1]), P.pin_dia / 2, P.sw_y_tire_face, P.sw_y_cavity_out + 1.0), "bought")
    sw("REAR_TIRE_WHEEL", cyl_y((L["A"][0], 0, L["A"][1]), P.rear_tire_od / 2, -P.rear_tire_w / 2, P.rear_tire_w / 2), "bought")
    sw("rear_hub", place("rear_hub", T(L["A"][0], 0, L["A"][1]) @ print_to_local("rear_hub")))
    esc_x = P.esc_x
    add("ESC", box((esc_x, 0, P.esc_z), (P.esc_l, P.esc_w, P.esc_h)), "bought", "chassis")
    if body:
        items.extend(body_items())
    return items


def body_items():
    return []                                           # the body is part of the monocoque halves now


def lead_points():
    """Lead centreline: tail, arc (bend radius), straight through the slot, free span, strain relief, battery."""
    mx, mz = P.pivot_xz
    r = P.pu_lead_bend_radius
    y_tail = -P.pu_len / 2
    arc = [(r - r * math.cos(t), y_tail - r * math.sin(t), 0.0) for t in np.linspace(0, math.pi / 2, 7)]
    inner = [(p[0], p[1], p[2]) for p in arc]
    slot_end = (P.sw_lead_slot_reach, inner[-1][1], 0.0)
    return inner, slot_end


def lead_polyline(g):
    """Lead centreline: the arc and slot rotate with the swingarm, the strain-relief anchor and battery end are fixed."""
    mx, mz = P.pivot_xz
    inner, slot_end = lead_points()
    rotating = [(g @ np.array([p[0], p[1], p[2], 1.0]))[:3] for p in inner + [slot_end]]
    tray_x0 = sum(P.batt_bay) / 2 - (P.lipo_l + 2 * P.mount_fit + 2 * P.mount_wall) / 2
    anchor = np.array([P.ch_floor_x[0] + 4.0, rotating[-1][1] - 3.0, mz - 3.0])
    batt = np.array([tray_x0 + 1.0, 0.0, P.ch_floor_z[1] + P.mount_floor + P.lipo_h / 2])
    return rotating, anchor, batt, len(inner)


def lead_length(travel):
    """Centreline length of the lead from the motor tail to the battery connector at a swingarm travel."""
    mx, mz = P.pivot_xz
    g = R_axis([0, 1, 0], swing_angle(travel), (mx, 0, mz)) @ T(mx, 0, mz)
    rotating, anchor, batt, _ = lead_polyline(g)
    pts = rotating + [anchor, batt]
    return float(sum(np.linalg.norm(b - a) for a, b in zip(pts[:-1], pts[1:])))


def lead_segments(g):
    rotating, anchor, batt, n = lead_polyline(g)
    exit_pt = rotating[-1]
    return [("LEAD_ARC", chain(rotating[:n])), ("LEAD_SLOT", chain([rotating[n - 1], exit_pt])),
            ("LEAD_SPAN", chain([exit_pt, anchor])), ("LEAD_RUN", chain([anchor, batt]))]


def chain(points):
    parts = []
    for a, b in zip(points[:-1], points[1:]):
        v = np.asarray(b) - np.asarray(a)
        n = np.linalg.norm(v)
        if n < 1e-6:
            continue
        c = trimesh.creation.cylinder(radius=P.pu_lead_dia / 2, height=n, sections=16)
        c.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], v / n))
        c.apply_translation((np.asarray(a) + np.asarray(b)) / 2)
        parts.append(c)
    return trimesh.util.concatenate(parts)


POSES = {
    "default": (0.0, 0.0),
    "lean_left_half": (P.lean_target_deg / 2, 0.0),
    "lean_right_half": (-P.lean_target_deg / 2, 0.0),
    "lean_left": (P.lean_target_deg, 0.0),
    "lean_right": (-P.lean_target_deg, 0.0),
    "travel_up": (0.0, P.rear_travel / 2),
    "travel_down": (0.0, -P.rear_travel / 2),
    "combined_left_up": (P.lean_target_deg, P.rear_travel / 2),
    "combined_right_down": (-P.lean_target_deg, -P.rear_travel / 2),
}

if __name__ == "__main__":
    for pose, (lean, travel) in POSES.items():
        sc = scene(lean, travel)
        print(pose, len(sc), "items")
