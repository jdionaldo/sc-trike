"""Single source of truth. Every dimension in mm, grams, degrees, volts unless the name says otherwise.

VERIFIED  = read from Hobbywing's manual HW-SMC337DUL02 (2024-11-08) / product page.
UNVERIFIED = assumption pending Phase 0 listing check; verify with calipers on arrival.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Params:
    # ---- scale and layout (ratios from ref1, absolutes locked to 1/18) ----
    scale: float = 1 / 18
    length: float = 250.0
    front_track: float = 250.0 * 0.63
    body_width: float = 250.0 * 0.63 * 0.55

    # ---- printer ----
    bed_x: float = 220.0
    bed_y: float = 220.0
    bed_z: float = 250.0
    overhang_max_deg: float = 45.0
    overhang_fail_fraction: float = 0.02
    bridge_max: float = 10.0
    wall_min: float = 1.2
    wall_panel: float = 1.2

    # ---- fit clearances ----
    clr_slide: float = 0.2
    clr_press: float = 0.1
    clr_gear: float = 0.3
    clr_bought_min: float = 1.0
    interference_max_mm3: float = 0.5
    body_margin: float = 3.0

    # ---- power unit: Hobbywing QuicRun Fusion Mini16 3000KV (VERIFIED, manual) ----
    pu_dia: float = 28.0
    pu_len: float = 30.0
    pu_mass_g: float = 60.0
    pu_shaft_dia: float = 3.17
    pu_shaft_len: float = 12.0
    pu_kv: float = 1400.0
    pu_poles: int = 4
    pu_i_cont: float = 60.0
    pu_i_peak: float = 120.0
    pu_vin_min_s: int = 2
    pu_vin_max_s: int = 3
    pu_bec_v: float = 6.0            # selectable 6.0 / 7.4, 4 A continuous
    pu_bec_a: float = 3.0
    pu_lead_batt_len: float = 150.0  # 18AWG, EC2 connector
    pu_lead_bend_radius: float = 6.0
    pu_lead_dia: float = 3.2         # UNVERIFIED 18AWG silicone
    pu_mount_m25_pcd: float = 16.0   # 4x M2.5 on 16 mm, 2x M3 on 17 mm (drawing)
    pu_mount_m3_pcd: float = 17.0
    pu_mount_screw_depth: float = 4.0
    pu_case_temp_limit_c: float = 90.0     # manual: external system temp must not exceed
    pu_thermal_cutoff_c: float = 105.0     # default ESC thermal protection
    pu_program_method: str = "yellow signal wire + Hobbywing LED/LCD program box (no SET-button programming of parameters)"

    # ---- tires / wheels (UNVERIFIED, see bom.md) ----
    rear_tire_od: float = 62.0
    rear_tire_w: float = 40.0
    rear_hex: float = 12.0
    front_tire_od: float = 52.0
    front_tire_w: float = 16.0
    front_axle_dia: float = 3.0

    # ---- servo: 9 g metal gear (UNVERIFIED, MG90S-class) ----
    servo_l: float = 40.0
    servo_w: float = 20.0
    servo_h: float = 19.3
    servo_ear_span: float = 49.0
    servo_stall_torque_nmm: float = 12.0 * 9.81 * 10.0   # purchase requirement: >= 3.0 kg.cm at 6 V (a 2.2 kg.cm MG90S gives only 15 % margin)
    servo_usable_fraction: float = 0.5
    mass_front_fraction: float = 0.5
    cg_height: float = 44.0              # above ground, measured from the model by report.py
    load_friction_factor: float = 1.25
    servo_travel_deg: float = 90.0

    # ---- electronics (UNVERIFIED) ----
    rx_l: float = 22.0
    rx_w: float = 13.0
    rx_h: float = 6.0
    lipo_l: float = 62.0
    lipo_w: float = 20.0
    lipo_h: float = 14.0
    lipo_mass_g: float = 33.0
    lipo_cells: int = 2

    # ---- drivetrain targets ----
    top_speed_mps: float = 7.5
    loaded_rpm_fraction: float = 0.85   # FOC under load vs KV*V
    gear_pinion_1: int = 15
    gear_gear_1: int = 60
    gear_pinion_2: int = 15
    gear_gear_2: int = 30
    gear_module: float = 0.8            # stage 1 spur, 15T pinion to 60T
    belt_pitch: float = 2.0             # stage 2 GT2 belt, 15T to 30T pulleys
    belt_center: float = 44.0           # stage 2 pulley centre distance
    mass_total_g: float = 620.0              # measured from the model by report.py
    crr: float = 0.04
    accel_target_mps2: float = 3.0
    drivetrain_eff: float = 0.80

    # ---- suspension / lean targets ----
    lean_target_deg: float = 30.0
    lean_min_deg: float = 25.0
    lean_max_deg: float = 35.0
    steer_at_full_lean_min_deg: float = 15.0
    rear_travel: float = 9.0

    # ---- solved by kinematics.py (Phase 1); tests/test_kinematics.py re-solves and compares ----
    bar_half: float = 64.75              # lean bar: chassis pivot to upright pivot
    upright_len: float = 22.0            # upper to lower lean bar spacing (lowers the servo, ears and roof beam)
    hub_out: float = 14.0                # axle outward of upright pivot
    axle_drop: float = 14.0              # axle below lower bar
    caster_deg: float = 12.0
    trail: float = 8.5
    steer_arm_xyz: tuple = (-5.0, -12.75, -22.0)          # left wheel, from the kingpin point; the right wheel mirrors it
    link_anchor_bar_xyz: tuple = (-34.0, 58.895, 6.422)  # bracket on the lower lean bar, in the bar frame
    coupling_link_len: float = 41.19
    steer_at_target_lean_deg: float = 16.63
    servo_horn_r: float = 8.0
    servo_rod_len: float = 10.0
    lug_drop: float = 6.0
    servo_deg_at_max_lean: float = 27.03
    swingarm_len: float = 47.5
    swing_arm_angle_deg: float = 8.0      # axle below pivot axis
    swing_lug_r: float = 36.0
    swing_lug_deg: float = 100.0
    shock_mount_dx: float = 34.0
    shock_stroke: float = 6.71
    shock_motion_ratio: float = 0.746
    shock_len_ride: float = 34.0
    spring_rate_n_per_mm: float = 1.094

    # ---- hardware sizes used by printed parts ----
    pin_dia: float = 3.0                 # steel pivot pins and kingpin
    axle_dia: float = 3.0
    ball_stud_dia: float = 2.0           # M2 ball link studs
    rod_end_dia: float = 6.0
    kingpin_len: float = 26.0
    m2_clear: float = 2.4
    m2_insert_hole: float = 3.2          # heat-set insert pilot for M2
    m3_clear: float = 3.4
    m3_insert_hole: float = 4.2

    # ---- front hub (Phase 2) ----
    hub_x: tuple = (-8.0, 10.0)
    hub_z: tuple = (-26.0, -10.6)
    hub_thick: float = 10.0              # along y, inboard face to wheel face
    hub_stub_dia: float = 8.0
    hub_stub_len: float = 17.0
    hub_lug_len: float = 4.75            # steering arm lug inboard of hub
    hub_lug_dia: float = 6.0

    # ---- upright ----
    up_x: float = 7.9                    # lap hinge: the post sits in front of the bar tongues
    up_x0: float = -2.4
    up_y: float = 6.0
    up_z: tuple = (-8.0, 30.0)

    # ---- lean bars and rods ----
    bar_w: float = 10.0                  # along x
    bar_h: float = 6.0                   # along z
    bar_pad: float = 2.8                 # bar end beyond pivot bore centre
    bar_end_len: float = 8.0             # length of the thin hinge tongue at each bar end
    bar_tongue_t: float = 2.4            # tongue thickness along x, on the rear face
    kingpin_gap: float = 1.3             # kingpin socket top to pivot bore edge
    rod_w: float = 4.5
    rod_t: float = 3.5
    rod_boss: float = 7.0
    rod_drive_boss: float = 5.4          # small enough to stay inside the ear window at full lean
    lug_w: float = 8.0
    lug_t: float = 3.5                   # drive lug tongue on the rear face of the upper bar
    drive_rod_x: tuple = (-8.5, -5.0)    # rod plane: horn on its rear face, lug tongue on its front face

    # ---- swingarm (swingarm frame: origin on the motor axis, x fwd, y along the axle, z up) ----
    sw_wall: float = 1.8
    sw_block_half: float = 14.2          # block half-width in x and z around the motor pocket
    sw_motor_clr: float = 0.4
    sw_y_out_a: float = 36.5             # outer face of the left arm
    sw_y_out_b: float = 38.0             # outer face of the right arm (thicker wall for the pivot cup)
    sw_y_tire_face: float = 22.5         # inner arm faces, tire side
    sw_y_cavity_out: float = 34.7
    sw_rim: float = 2.4                  # gearbox rim around the gear cavity
    sw_gear_clr: float = 0.8
    sw_hatch_open: float = 29.0
    sw_hatch_depth: float = 5.5
    sw_hatch_flange: float = 39.6
    sw_hatch_flange_t: float = 7.5
    sw_hatch_cone_h: float = 5.8         # at least the flange overhang so the underside is 45 degrees or steeper
    sw_tube_od: float = 17.0             # chassis-side pivot tube that enters the hatch counterbore
    sw_cbore_depth: float = 3.0
    sw_vent_slots: int = 4
    sw_vent_dia: float = 2.6
    sw_vent_r: float = 11.7
    sw_shim_w: float = 11.0
    sw_shim_slot_t: float = 1.0
    sw_shim_y: float = 11.0
    sw_plate_r_pivot: float = 23.0
    sw_plate_r_axle: float = 12.0
    sw_screw_r: float = 17.4             # hatch screw circle
    sw_cup_dia: float = 9.0              # right pivot cup in the outer wall
    sw_cup_depth: float = 1.5
    sw_split_screw: float = 11.0         # split-face screw offset from the motor axis (x and z)
    bearing_od: float = 6.0              # MR63ZZ 3x6x2.5
    bearing_w: float = 2.5

    # ---- chassis: narrow front tub and wide rear cradle, each in left/right halves split on y = 0 ----
    # Left is +y. Each half is authored with |y|; the halves are proper-rotation mirrors of each other.
    ch_in: float = 35.0                  # tub inner wall face (the lean sweep must clear it)
    ch_in_rear: float = 44.5             # cradle inner wall face (clears the swingarm and hatch)
    ch_wall: float = 2.0
    rib_t: float = 2.0
    bulk_t: float = 5.6                  # thick enough that an M2 insert pilot keeps 1.2 mm of wall
    ch_floor_z: tuple = (-20.0, -18.0)
    ch_floor_x: tuple = (-113.6, -46.5)   # no floor forward of the battery: the lean bars sweep through it
    ch_profile: tuple = ((-11.1, -20.0), (-11.1, 46.0), (-14.0, 46.0), (-14.0, 26.0), (-113.6, 26.0), (-113.6, -20.0))
    ch_rear_profile: tuple = ((-119.2, -30.0), (-119.2, 34.0), (-176.0, 34.0), (-176.0, 35.0), (-190.0, 35.0), (-190.0, 28.0),
                              (-176.0, 28.0), (-176.0, -30.0))
    ch_bulkheads: tuple = ((-11.1, -5.5, 46.0), (-113.6, -108.0, 30.0))     # rear lean ear, end bulkhead
    ch_screws: tuple = ((-10.0, 16.0), (-10.0, 20.0))
    ch_pins: tuple = (28.0, 10.0)
    ch_rear_bulkhead: tuple = (-119.2, -113.6, 30.0)
    ch_join_bolts: tuple = ((12.0, 10.0), (26.0, 10.0), (12.0, 24.0), (26.0, 24.0))   # (|y|, z) tub-to-cradle bolts along x
    ch_ear_bottom: float = -24.0         # the rear ear hangs below the floor to carry the servo tabs
    # front yoke: carries the front lean pivots, bolts to the rear ear, narrow so the lean arms sweep outside it
    yoke_hw: float = 24.0
    yoke_leg: tuple = (5.5, 11.1)        # x range of the front leg
    yoke_top: tuple = (40.0, 45.6)       # top beam z range
    yoke_bottom: tuple = (-24.0, -18.2)  # bottom beam z range
    ch_yoke_bolts: tuple = ((1, 8.0, 42.8), (-1, 8.0, 42.8), (1, 12.0, -21.1), (-1, 19.5, -21.1))   # (side, |y|, z) along x
    ch_lead_window: tuple = (0.0, 34.6, -12.5, 5.0)    # tub end and cradle front bulkheads, right half only, open to the split
    ch_lead_window_left: float = 4.0     # left half notch so the lead can reach the centreline
    ch_tie_slots: tuple = (14.0, 17.4, 20.6, 24.0)      # strain-relief tie slots through the floor (ya ranges)
    ch_tie_x: tuple = (-106.0, -104.2)
    ch_boss_dia: float = 8.8             # left pivot boss entering the swingarm cup
    ch_access_dia: float = 42.0          # right wall access to the hatch and motor
    ch_ring_od: float = 54.0
    ch_ring_t: float = 4.5
    ch_ring_screw_r: float = 25.0
    ch_pin_dia: float = 2.0
    ch_servo_windows: tuple = ((-17.0, 0.0, -30.0, -2.0), (0.0, 8.5, -30.0, -2.0))   # rod and horn windows, open to the split and the bottom
    servo_tab_pilot: float = 2.0         # self-tapping M2 pilot
    horn_t: float = 2.5
    servo_shaft_offset: float = 11.4     # output shaft from the body centre along its long axis (UNVERIFIED)
    servo_ear_insert_depth: float = 4.0

    # ---- steering link bracket (bolts to the lower bar top face) ----
    br_t: float = 3.0
    br_standoff: float = 8.4
    br_base: tuple = (-5.2, 5.2, 44.5, 51.0)      # x0, x1, y0, y1 over the bar
    br_arm: tuple = (-37.6, -4.0, 53.0, 61.3)     # x0, x1, y0, y1 toward the link eye
    br_strip: tuple = (-5.4, -2.6, 50.0, 61.3)    # joins base and arm, clear of the rear ear and the upright
    br_screws: tuple = ((-2.0, 47.5), (2.0, 47.5))  # x, y of the two M2 screws into the bar
    br_boss_dia: float = 5.6
    br_pilot_depth: float = 6.0

    # ---- pivot plate, mounts, rear hub ----
    pp_t: float = 2.5
    sw_lead_slot_w: float = 8.0          # radial lead exit through the pocket wall, forward (+x)
    sw_lead_slot_reach: float = 30.0
    mount_wall: float = 1.2
    mount_floor: float = 1.6
    mount_fit: float = 0.5               # tray clearance around bought parts
    rx_tray_h: float = 6.0
    rx_beside_y: float = 21.0            # receiver tray beside the battery, clear of the crossing links
    batt_tray_h: float = 8.0
    batt_bay: tuple = (-108.0, -42.0)    # tray centring, kept clear of the link anchors
    hex_af: float = 12.0                 # wheel hex drive across flats (UNVERIFIED)
    hub_len: float = 12.0
    set_screw_pilot: float = 1.6         # M2 tap pilot

    # ---- body panels (chassis frame; flat plates, yellow upper, black lower) ----
    body_t: float = 1.9
    body_t_steep: float = 4.0            # hood and rear window: raked surfaces are thinner along their normal
    # Shell stations (x, half-width, rim z, shoulder start z, roof z, roof half-width), front to back by segment.
    body_stations: tuple = (
        ("glass", ((-14.0, 38.0, 26.5, 27.0, 29.0, 26.0), (-30.0, 39.0, 26.5, 27.5, 31.0, 24.0),
                   (-45.0, 40.0, 26.5, 28.0, 33.0, 22.0))),
        ("roof", ((-45.0, 40.0, -3.7, 24.0, 33.0, 20.0), (-70.0, 40.0, 0.8, 24.0, 34.0, 18.0),
                  (-96.0, 40.0, 5.5, 24.0, 33.0, 18.0))),
        ("rear", ((-96.0, 40.0, 5.5, 30.0, 34.0, 26.0), (-104.0, 40.0, 6.9, 30.0, 34.0, 26.0),
                  (-112.0, 40.0, 8.3, 30.0, 34.0, 26.0))),
        ("pods", ((-113.4, 58.0, -24.0, 35.0, 40.0, 34.0), (-150.0, 58.0, -24.0, 34.0, 40.0, 34.0),
                  (-190.0, 58.0, -24.0, 32.0, 40.0, 34.0), (-228.0, 52.0, -24.0, 20.0, 26.0, 26.0))))
    body_pod_w: float = 58.0             # rear pod half-width
    body_band_w: float = 40.0            # lower side band outer half-width
    body_band_x: tuple = (-45.0, -112.0)
    body_band_z: tuple = (-4.0, 2.0, 8.0)             # top of the black lower band
    body_floor_z: float = -18.0
    body_pod_floor_z: float = -24.0
    body_x_tail: float = -228.0
    body_open_hw: float = 41.0           # rear deck opening: the tire and swingarm stand free between the pod blades
    body_open_x: float = -124.0
    body_arch_r: float = 40.0            # rear wheel arch hole in the pod side
    body_boss_dia: float = 6.0           # hood standoff diameter
    hood_screw_y: float = 10.0           # hood screws at y = plus and minus this, x = 0, into the yoke top beam
    body_shock_window: tuple = (-186.0, -150.0, 8.0)   # x0, x1, half-width: shows the coil-over spring through the deck
    body_pod_windows: tuple = (((-120.0, -12.0), (-120.0, 22.0), (-146.0, -12.0)),)   # angular cut-outs in the pod sides (x, z)
    ch_body_keys_tub: tuple = ((-58.0, 0.0), (-80.0, 4.0), (-100.0, 0.0))
    ch_body_keys_rear: tuple = ((-128.0, 20.0), (-165.0, 17.0), (-177.0, 15.0))
    ch_key_pad_dia: float = 6.0
    ch_key_pad_len: float = 5.0
    ch_key_socket: float = 2.3
    ch_key_socket_depth: float = 5.5
    body_pin_dia: float = 2.0
    body_dowel_hole: float = 1.95        # press fit for a 2 mm steel dowel
    cage_x: tuple = (22.0, 26.0)
    cage_y: float = 38.0
    cage_z: tuple = (-20.0, 16.0)
    cage_bar: float = 5.0
    cage_pins: tuple = (18.0, -17.5)       # |y|, z; pins enter sockets in the front ear
    ch_ear_socket_depth: float = 4.0

    # ---- masses of bought parts (g, UNVERIFIED: weigh on arrival) and print settings ----
    rear_tire_mass_g: float = 38.0
    front_tire_mass_g: float = 16.0
    servo_mass_g: float = 13.4
    horn_mass_g: float = 1.0
    rx_mass_g: float = 5.0
    gears_mass_g: tuple = (("GEAR_PINION_1", 1.0), ("GEAR_1", 3.5), ("GEAR_PINION_2", 1.0), ("GEAR_2", 2.0))
    steel_density_g_cc: float = 7.85
    dowel_mass_g: float = 0.4
    hardware_mass_g: float = 28.0         # screws, inserts, pins and bearings, placed at the chassis centroid
    shock_mass_g: float = 6.0
    shock_xz: tuple = (-170.0, 33.0)
    density_g_cc: tuple = (("PETG", 1.27), ("PETG-CF", 1.30))
    nozzle: float = 0.4
    layer: float = 0.2
    perimeters: int = 3
    infill_structural: float = 0.30
    infill_cosmetic: float = 0.15
    flow_mm3_s: float = 9.0
    time_overhead: float = 1.35
    part_qty: tuple = (("upright", 2), ("link_steer", 2))

    # ---- derived ----
    @property
    def axle_xz(self) -> tuple:
        return (self.front_tire_od / 2 - self.length + self.rear_tire_od / 2,
                -(self.axle_drop + self.front_tire_od / 2) + self.rear_tire_od / 2)

    @property
    def pivot_xz(self) -> tuple:
        a = math.radians(self.swing_arm_angle_deg)
        ax, az = self.axle_xz
        return (ax + self.swingarm_len * math.cos(a), az + self.swingarm_len * math.sin(a))

    @property
    def pivot_tube_len(self) -> float:
        hatch_top = self.sw_y_out_a + self.sw_hatch_flange_t
        floor = hatch_top - self.sw_cbore_depth
        return self.ch_in_rear + self.ch_wall - (floor + 0.4)

    @property
    def servo_shaft_z(self) -> float:
        return -(self.lug_drop + self.servo_horn_r)

    @property
    def servo_axis_y(self) -> float:
        return self.servo_rod_len

    @property
    def servo_center_y(self) -> float:
        return self.servo_shaft_offset - self.servo_rod_len

    @property
    def v_nom(self) -> float:
        return 3.7 * self.lipo_cells

    @property
    def ratio(self) -> float:
        return (self.gear_gear_1 / self.gear_pinion_1) * (self.gear_gear_2 / self.gear_pinion_2)

    @property
    def top_speed_ratio_required(self) -> float:
        wheel_rpm = self.top_speed_mps / (math.pi * self.rear_tire_od / 1000.0) * 60.0
        motor_rpm = self.pu_kv * self.v_nom * self.loaded_rpm_fraction
        return motor_rpm / wheel_rpm

    @property
    def top_speed_actual_mps(self) -> float:
        motor_rpm = self.pu_kv * self.v_nom * self.loaded_rpm_fraction
        return motor_rpm / self.ratio / 60.0 * math.pi * self.rear_tire_od / 1000.0

    @property
    def motor_current_a(self) -> float:
        m = self.mass_total_g / 1000.0
        f = m * (9.81 * self.crr + self.accel_target_mps2)
        v_wheel = self.top_speed_mps
        p_mech = f * v_wheel / self.drivetrain_eff
        return p_mech / self.v_nom



# ---- WS-02 baseline: the validated 1/18 layout scaled to 370 mm; bought parts and fasteners keep their real sizes ----
import dataclasses

K = 370.0 / 250.0
_KEEP = {"scale", "bed_x", "bed_y", "bed_z", "overhang_max_deg", "overhang_fail_fraction", "bridge_max", "wall_min",
         "wall_panel", "clr_slide", "clr_press", "clr_gear", "clr_bought_min", "interference_max_mm3", "body_margin",
         "rx_l", "rx_w", "rx_h", "lipo_l", "lipo_w", "lipo_h", "pin_dia", "axle_dia", "ball_stud_dia", "rod_end_dia",
         "m2_clear", "m2_insert_hole", "m3_clear", "m3_insert_hole", "sw_wall", "sw_rim", "horn_t", "bearing_od",
         "bearing_w", "ch_wall", "rib_t", "bulk_t", "pp_t", "mount_wall", "mount_floor", "mount_fit", "set_screw_pilot",
         "body_t", "body_t_steep", "body_pin_dia", "body_dowel_hole", "ch_key_pad_dia", "ch_key_pad_len",
         "ch_key_socket", "ch_key_socket_depth", "ch_pin_dia", "servo_tab_pilot", "servo_ear_insert_depth",
         "sw_cup_depth", "sw_cbore_depth", "sw_vent_dia", "sw_shim_slot_t", "sw_gear_clr", "sw_motor_clr",
         "gear_module", "front_axle_dia", "ch_ear_socket_depth", "pu_dia", "pu_len", "pu_shaft_dia", "pu_shaft_len",
         "servo_l", "servo_w", "servo_h", "servo_ear_span", "servo_shaft_offset", "br_pilot_depth"}


def _k(v):
    if isinstance(v, bool) or isinstance(v, int):
        return v
    if isinstance(v, float):
        return v * K
    if isinstance(v, tuple):
        return tuple(_k(x) for x in v)
    return v


_LEN = [f.name for f in dataclasses.fields(Params) if f.type in (float, tuple) and f.name not in _KEEP
        and not any(t in f.name for t in ("deg", "_g", "kv", "fraction", "factor", "rate", "crr", "eff", "mps", "rpm",
                                          "density", "torque", "cells", "ratio", "time", "flow", "infill", "layer",
                                          "nozzle", "interference", "stroke_n", "_v", "_a", "_c", "poles", "qty",
                                          "perimeters", "travel_deg", "motion"))]
_FORCE = ["kingpin_gap", "sw_y_out_a", "sw_y_cavity_out", "sw_hatch_cone_h", "sw_vent_r", "sw_plate_r_axle", "sw_cup_dia",
          "ch_access_dia", "br_arm", "body_arch_r", "steer_arm_xyz", "link_anchor_bar_xyz"]
_over = {n: _k(getattr(Params(), n)) for n in _LEN + _FORCE}
_over.update(mass_total_g=1123.5, cg_height=61.1, sw_hatch_open=33.0, sw_hatch_cone_h=9.0, sw_hatch_flange=48.6, sw_screw_r=20.3, sw_hatch_flange_t=13.4, sw_hatch_depth=6.0, sw_vent_r=9.0, sw_shim_y=4.0, rear_tire_od=92.0, rear_tire_w=59.0, front_tire_od=77.0, front_tire_w=24.0, rear_hex=12.0)
_over.update(steer_arm_xyz=(-7.4, -19.79, -32.56), link_anchor_bar_xyz=(-50.11, 86.982, 9.844),
             coupling_link_len=61.172, shock_stroke=9.932,
             spring_rate_n_per_mm=1.339, shock_motion_ratio=0.7456,
             shock_len_ride=50.32)
_over.update(
    body_stations=(
        ("hood", ((-20.7, 62.0, -8.0, 62.0, 12.0, 55.0, 24.0), (-57.0, 68.0, -7.4, 68.0, 16.0, 55.0, 28.0),
                  (-96.0, 70.0, -0.6, 70.0, 26.0, 55.0, 41.0))),
        ("glass", ((-96.0, 70.0, -0.6, 70.0, 26.0, 55.0, 41.0), (-128.0, 70.0, 4.9, 70.0, 30.0, 55.0, 45.0),
                   (-176.0, 71.0, 13.2, 71.0, 34.0, 70.0, 46.0))),
        ("pods", ((-176.0, 74.0, -44.0, 74.0, 36.0, 70.0, 45.0), (-229.0, 80.0, -44.0, 80.0, 34.0, 70.0, 44.0),
                  (-283.0, 86.0, -44.0, 86.0, 30.0, 70.0, 43.0), (-337.0, 78.0, -44.0, 78.0, 22.0, 66.0, 28.0)))),
    body_pod_w=86.0, body_band_w=70.0, body_band_x=(-57.0, -176.0), body_band_z=(-8.3, 2.0, 12.3), body_floor_z=-26.6,
    body_open_hw=62.0, body_open_x=-205.0, body_x_tail=-337.4, body_pod_windows=(),
    ch_body_keys_tub=((-80.0, -12.0), (-116.0, -6.0), (-150.0, 2.0)),
    ch_body_keys_rear=((-185.3, 33.0), (-254.0, 20.0), (-255.0, -30.0)),
    ch_profile=((-16.428, -29.6), (-16.428, 68.08), (-20.72, 68.08), (-20.72, 18.0), (-57.0, 24.0), (-96.0, 36.0),
                (-112.0, 38.48), (-168.128, 38.48), (-168.128, -29.6)),
    ch_rear_profile=((-176.416, -44.4), (-176.416, 38.5), (-260.48, 38.5), (-260.48, 40.0), (-281.2, 40.0),
                     (-281.2, 33.0), (-260.48, 33.0), (-260.48, -44.4)),
    ch_bulkheads=((-16.428, -8.14, 68.08), (-168.128, -159.84, 38.5)), ch_rear_bulkhead=(-176.416, -168.128, 38.5))
P = dataclasses.replace(Params(), **_over)
