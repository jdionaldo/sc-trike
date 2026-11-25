"""Part registry for the Fugu kit: one entry per printed DESIGN. Every printed STL stem must resolve through key_of().

Fields: id, sub (build-order group), name, stems (exported instance names, mirror pairs list both), material, function, mates, load,
walls, infill, support (auto|on|off), brim, note.  Hardware (bought parts) lives in HARDWARE below.
Sub-assemblies follow build order: CH chassis frame, SU suspension, ST steering, DT drivetrain, CG cage, SH shell, LT lights.
"""
SUBS = {"CH": "Chassis frame and decks", "SU": "Front suspension", "ST": "Steering", "DT": "Drivetrain housings and rear arm",
        "CG": "Cage", "SH": "Shell", "LT": "Lights"}
SUB_ORDER = ["CH", "SU", "ST", "DT", "CG", "SH", "LT"]

D = lambda **k: k
PARTS = [
    # --- chassis frame -------------------------------------------------------------------------------------------------------
    D(id="CH1", sub="CH", name="Front deck", stems=["w3_deck_front"], material="PETG", function="Flat front deck plate: carries the lean head, the steering servo cradle and the cage front feet", mates="CH2, CH3, cage feet (M3 inserts)", load="structural", walls=4, infill="35%", support="auto"),
    D(id="CH2", sub="CH", name="Rear deck", stems=["w3_deck_rear"], material="PETG", function="Centre deck: motor plate, cage rail feet", mates="CH1, CH3, CH4, cage feet", load="structural", walls=4, infill="35%", support="auto"),
    D(id="CH3", sub="CH", name="Tail deck", stems=["w3_deck_tail"], material="PETG", function="Rear deck: rear bearing carriers and swing-arm pivot", mates="CH2, DT rear carriers", load="structural", walls=4, infill="35%", support="auto"),
    D(id="CH4", sub="CH", name="Skid plate", stems=["w3_skid"], material="PETG", function="Nose guard, shell nose rests 1 mm ahead of it", mates="CH1", load="impact", walls=4, infill="30%", support="auto"),
    D(id="CH5", sub="CH", name="Motor plate", stems=["w3_motor_plate"], material="PETG", function="Holds the 540/550 motor (heat: PETG, not PLA)", mates="CH2, motor", load="structural+heat", walls=4, infill="40%", support="auto"),
    D(id="CH6", sub="CH", name="Battery tray", stems=["Battery_tray"], material="PETG", function="Raised tray for the 2S/3S pack over the steering servo, two hook-and-loop straps, front stop and rear lip; pack lifts out through the cockpit", mates="CH1 (4 x M3 from below into inserts)", load="light", walls=4, infill="30%", support="auto"),
    D(id="CH7", sub="CH", name="Receiver box", stems=["Receiver_box"], material="PETG", function="Receiver bay in the left front of the deck, lid on two M2.5 countersunk screws into inserts", mates="CH1 (2 x M3 from below into inserts), CH8", load="none", walls=3, infill="20%", support="auto"),
    D(id="CH8", sub="CH", name="Receiver lid", stems=["Receiver_lid"], material="PETG", function="Lid of the receiver box: slides under the outer ledge, 2 x M2.5 countersunk on the servo side", mates="CH7", load="none", walls=3, infill="20%", support="off"),
    # --- front suspension ----------------------------------------------------------------------------------------------------
    D(id="SU1", sub="SU", name="Lean head", stems=["Lean_head"], material="PETG", function="Tube frame on the front deck behind the skid: carries the four wishbone pivot rods (lean-steer head)", mates="CH1 (4 x M3 from below into inserts), SU2, SU3 (6 mm pivot rods)", load="structural", walls=6, infill="60%", support="auto"),
    D(id="SU2", sub="SU", name="Upper wishbone", stems=["Upper_arm_-1", "Upper_arm_1"], material="PETG", function="Upper A-arm in chamfered square tube with the truss post of the heave shock; carries the wheel load", mates="SU1 pivot rod, SU4 (6.8 mm ball cup), heave shock (M4 pin)", load="structural", walls=6, infill="70%", support="auto", mirrored=True),
    D(id="SU3", sub="SU", name="Lower wishbone", stems=["Lower_arm_-1", "Lower_arm_1"], material="PETG", function="Lower A-arm in chamfered square tube (push and pull only)", mates="SU1 pivot rod, SU4 (6.8 mm ball cup)", load="structural", walls=6, infill="60%", support="auto", mirrored=True),
    D(id="SU4", sub="SU", name="Knuckle", stems=["Knuckle_-1", "Knuckle_1"], material="PETG", function="Upright plate with both ball studs, axle boss inside the rim and the steering arm", mates="SU2, SU3 (ball studs M3), 6 mm axle pin, tie rod ball stud", load="structural", walls=6, infill="80%", support="auto", mirrored=True),
    D(id="SU5", sub="SU", name="Droop stop", stems=["Droop_stop_-1", "Droop_stop_1"], material="PETG", function="Droop stop base under the lower arm root (end of travel at 10 deg lean + 8 mm droop)", mates="CH1 (2 x M3 from below into inserts), SU6", load="impact", walls=4, infill="60%", support="auto", mirrored=True),
    D(id="SU6", sub="SU", name="Droop stop pad", stems=["Droop_stop_pad_-1", "Droop_stop_pad_1"], material="TPU 95A", function="Bumper pad bonded into the droop stop's pocket", mates="SU5 (glued)", load="impact", walls=3, infill="100%", support="off", mirrored=True),
    D(id="SU7", sub="SU", name="Heave bump stop", stems=["Heave_bump_stop"], material="TPU 95A", function="Sleeve on the heave shock shaft: meets the shock body at 12 mm heave + 10 deg lean (heave end of travel)", mates="heave shock shaft", load="impact", walls=3, infill="100%", support="off"),
    # --- steering -------------------------------------------------------------------------------------------------------------
    D(id="ST1", sub="ST", name="Steering horn", stems=["Steer_horn"], material="PETG", function="T horn on the servo shaft, one ball stud per tie rod", mates="steering servo, tie rod ball studs", load="structural", walls=6, infill="100%", support="off"),
    D(id="ST2", sub="ST", name="Steering servo mount", stems=["Steer_servo_mount"], material="PETG", function="Mount for the low-profile steering servo on top of the front deck: a pillar under each servo ear, joined by side rails", mates="CH1, steering servo", load="light", walls=4, infill="30%", support="auto"),
    D(id="ST3", sub="ST", name="Tie rod, printed (option)", optional=True, option=True, stems=["Tie_rod_printed_-1", "Tie_rod_printed_1"], material="PETG", function="Printed option to the steel M3 turnbuckle: 7 mm body, 9 mm end collars with M3 inserts, the same ball cups, 93 mm ball to ball", mates="2 x M3 insert, 2 x ball cup M3 6.8 mm", load="structural", walls=6, infill="100%", support="off", mirrored=True),
    # --- drivetrain ---------------------------------------------------------------------------------------------------------
    D(id="DT5", sub="DT", name="Pillow block lower", stems=["w3_pillow_lower"], material="PETG", function="Bearing block, lower half", mates="DT6", load="structural", walls=4, infill="60%", support="auto"),
    D(id="DT6", sub="DT", name="Pillow block upper", stems=["w3_pillow_upper"], material="PETG", function="Bearing block, upper half", mates="DT5", load="structural", walls=4, infill="60%", support="auto"),
    D(id="DT7", sub="DT", name="Rear bearing carrier lower", stems=["w3_rbc_lower"], material="PETG", function="Rear bearing carrier, lower half", mates="CH3, DT8", load="structural", walls=4, infill="50%", support="auto"),
    D(id="DT8", sub="DT", name="Rear bearing carrier upper", stems=["w3_rbc_upper"], material="PETG", function="Rear bearing carrier, upper half", mates="DT7", load="structural", walls=4, infill="50%", support="auto"),
    D(id="DT10", sub="DT", name="Rear ring hub", stems=["w3_rring_hub"], material="PETG", function="Hub carrying the rear ring gear", mates="DT7/DT8", load="structural", walls=4, infill="80%", support="auto"),
    D(id="DT11", sub="DT", name="Rear swing arm", stems=["w3_rear_arm"], material="PETG", function="Single-sided rear swing arm, shock bridge over the 140 mm tyre; pivots on three 5x11x4 bearings on the 5 mm cross shaft, the 8 mm axle turns in two 8x16x5 bearings", mates="5 mm cross shaft, rear shock (M6), 8 mm axle", load="structural", walls=6, infill="60%", support="auto"),
    D(id="DT14", sub="DT", name="Rear pivot pulley 26T GT2 (6 mm belt)", stems=["pulley_r_pivot"], material="PETG", function="26T GT2 pulley on the rear arm pivot shaft, D5 bore, M3 grub screw", mates="2GT-300 belt", load="drive", walls=6, infill="100%", support="off"),
    D(id="DT15", sub="DT", name="Rear axle pulley 30T GT2 (6 mm belt)", stems=["pulley_r_axle"], material="PETG", function="30T GT2 pulley on the 8 mm rear axle, M3 grub screw", mates="2GT-300 belt, 8 mm axle", load="drive", walls=6, infill="100%", support="off"),
    D(id="DT16", sub="DT", name="Front wheel 1.9 in, 6-spoke", stems=["wheel_f_-1", "wheel_f_1"], material="PETG", function="One-piece 6-spoke wheel, bead seat 48.3 mm, 34 mm wide, two 6x12x4 bearing seats (D12.1 x 4) in the hub, turns on the fixed 6 mm stub axle, takes a bought 1.9 in tyre (about 112 mm OD)", mates="2 x 6x12x4 bearings, 6 mm stub axle, front tyre", load="structural", walls=6, infill="60%", support="off", mirrored=True),
    D(id="DT17", sub="DT", name="Rear wheel 2.2 in, 6-spoke", stems=["wheel_r"], material="PETG", function="One-piece 6-spoke wheel, bead seat 55.9 mm, 40 mm wide, 12 mm hex drive pocket, takes a bought 2.2 in tyre (about 140 mm OD)", mates="12 mm hex hub, rear tyre", load="structural", walls=6, infill="60%", support="off"),
    # --- cage -------------------------------------------------------------------------------------------------------------------
    D(id="CG1", sub="CG", name="Cage", stems=["Cage"], material="PETG", function="Tubular roll cage that carries the shell, light contacts, tail housing and rear shock top", mates="CH1/CH2 (6 x M3 into inserts), SH1, SH2, SH3, rear shock pin", load="structural", walls=4, infill="30%", support="auto"),
    D(id="CG2", sub="CG", name="Front light contact block", stems=["Front_light_contact_block"], material="PETG", function="Magnet pad on the hood roof (2 x 6x3 magnets)", mates="CG1 front bridge", load="light", walls=3, infill="40%", support="auto"),
    D(id="CG3", sub="CG", name="Roof plate", stems=["Roof_plate"], material="PETG", function="Roof panel on the cage's roof frame (open cockpit)", mates="CG1 roof rails", load="none", walls=3, infill="15%", support="auto"),
    # --- shell ------------------------------------------------------------------------------------------------------------------
    D(id="SH1", sub="SH", name="Front shell", stems=["Front_shell"], material="PLA", function="Hood, nose, fenders, doors", mates="SH2 (lap flange), SH4, LT1, CG1 bosses", load="none", walls=3, infill="10%", support="auto"),
    D(id="SH2", sub="SH", name="Canopy", optional=True, stems=["Canopy"], material="PLA", function="Windscreen frame, roof, B-pillars, rear quarter covers", mates="SH1 lap flange, CG1", load="none", walls=3, infill="10%", support="auto"),
    D(id="SH3", sub="SH", name="Tail light housing", stems=["Tail_light_housing"], material="PLA", function="Compact rear housing for the tail light", mates="CG1 (2 x M3 countersunk), LT2", load="none", walls=3, infill="15%", support="auto"),
    D(id="SH4", sub="SH", name="Grille insert", stems=["Grille_insert"], material="PLA", function="Trapezoid hex grille", mates="SH1 nose", load="none", walls=3, infill="15%", support="off"),
    # --- lights -------------------------------------------------------------------------------------------------------------------
    D(id="LT1", sub="LT", name="Nose light strip", stems=["Nose_light_strip"], material="PLA-translucent", function="Red light bar: 1.75 mm plate in a blind groove on the nose face (1.2 mm shell backing behind it), two 5 mm pegs through the backing take the 3 mm LEDs", mates="SH1 groove, pegs through backing", load="none", walls=3, infill="100%", support="auto"),
    D(id="LT2", sub="LT", name="Tail light strip", stems=["Tail_light_strip"], material="PLA-translucent", function="Red tail light strip, 3 mm LEDs in pegs", mates="SH3 seat", load="none", walls=3, infill="100%", support="auto"),
]

# bought stand-ins in the model -> hardware (not printed)
HARDWARE_STEMS_PREFIX = ("b_", "mock_", "steer_horn", "diff_out", "tip_shaft", "M6_shock_pin", "Rear_shock", "Rear_tire", "lean_servo", "steer_servo",
                         "Front_shock", "Uplink_pin", "Lean_centring_spring", "Lean_beam_pivot_bolt",
                         "Heave_shock", "Pivot_rod", "Rod_end", "Ball_stud", "Axle_pin", "Axle_nut", "Axle_shim", "Wheel_bearing", "Wheel_hex_hub", "Tie_rod", "Steer_stud",   # Wheel_hex_hub: stale STLs of the removed hex hubs in old export folders
                         "Steer_servo")      # printed stems resolve through key_of() first (Steer_servo_mount is printed)


def key_of(stem):
    for p in PARTS:
        if stem in p["stems"]:
            return p["id"]
    return None


def is_hardware(stem):
    return stem.startswith(HARDWARE_STEMS_PREFIX)
