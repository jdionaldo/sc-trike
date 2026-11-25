"""Active shell parameters, units mm; Z up and front -Y."""
from soma import param

# Outer shell dimensions follow the 1:10 reference. Ground is the shell's lower edge.
LENGTH = param(278.0, 'Shell length', min=260.0, max=290.0, unit='mm', group='Shell')
# The shell is generated at its 1:10-blueprint size (278 mm) and scaled up as the last step to fit the 1:1 chassis.
# WALL is the wall thickness while generating; WALL_PRINT is the real printed thickness after scaling.
SHELL_SCALE = param(2.17, 'Shell scale (fits the 1:1 chassis)', min=1.0, max=2.4, step=0.01, group='Shell')
WALL_PRINT = param(3.0, 'Printed panel thickness', min=2.4, max=5.0, step=0.1, unit='mm', group='Shell')
SHELL_Z = param(0.9, 'Shell height factor (lower = more aggressive stance)', min=0.75, max=1.0, step=0.01, group='Shell')
WALL = WALL_PRINT / SHELL_SCALE
SILL_PLANE_END_PX = 815   # canopy sill fascia: stations up to here share one plane (trace px along the belt)
SILL_PLANE_NUDGE = 0.5    # largest sideways move of a fascia lower-edge point onto that plane, model mm (1.1 mm printed, at a part joint)
NOZZLE=0.4; CLEARANCE=0.3; MAX_OVERHANG=45; BED=(220,220,250)
BODY=(0.25,0.28,0.32); ROOF=(0.19,0.22,0.26)
Y_SCALE=LENGTH/278.0
# Reference plan outline: narrow blunt nose, broad cockpit, steadily tapered tail.
# Only transverse coordinates change aft of the nose; station heights stay put.
CABIN_WIDTH = param(0.80, 'Cabin width factor (1.0 = blueprint)', min=0.6, max=1.0, step=0.01, group='Shell')
# Width factor along the length (blueprint mm): full width at the nose, over the front tires and at the tail,
# slimmed through the cabin so the sides come in toward the chassis frame.
PLAN_STATIONS = [(-139, 1.0), (-80, 1.0), (-45, CABIN_WIDTH), (20, CABIN_WIDTH), (68, 1.0), (139, 1.0)]
NOSE_SWEEP = 0.0
SEAM_CHIP_LIMIT = 100.0*(WALL/2.5)**3  # mm3: detached offset-skin chips at the crease split
GLUE_GAP = 0.15
PANEL_GAP = param(0.3, 'Panel seam gap (canopy, grille, shell seams)', min=0.15, max=0.6, step=0.05, unit='mm', group='Shell')
FRAME_WIDTH = 4.5
WINDOW_RAIL_WIDTH = 4.0
SEAT_WIDTH = 8.0
SEAT_DROP = 3.5
# Sill rail top is level with the shell seat-beam top: (RAIL/2) - (SEAT/2 - SEAT_DROP).
RAIL_DROP = WINDOW_RAIL_WIDTH/2 - (SEAT_WIDTH/2 - SEAT_DROP)


# Nose upper edge stays put; the lower edge pitches back by 10 mm over 32 mm.
NOSE_RAKE = 22.0   # mm in blueprint units: nose face leans 37 degrees, the same plane as the chassis front guard
NOSE_TOP = 57.0
NOSE_HEIGHT = 32.0
NOSE_BLEND_END = -100.0

# Faceted frame-to-body transitions. Fascia thickness follows the panel thickness.
SILL_BLEND_DEPTH = 10.0
WING_DETAIL_AREA = 4.0  # mm2: tiny raised skin overlaps, never the designed intakes

WHEEL_NOTCH_HALF_WIDTH = 59.0  # mm: clean termination at the front wheel-opening shoulder
SILL_END_PX = 1020  # trace station: terminate the canopy skirt at the existing body junction
PANEL_JOIN_OVERLAP = 0.3  # mm: finite overlap where the channel web meets the adjacent skins

WING_LEAD_IN_PX = 760  # trace station: body-root start of the swept leading deflector

# Supplied chassis (inputs/WS03_chassis_only.glb, 1:1 size) as a reference under the shell.
CHASSIS_Y = param(9.0, 'Chassis shift along Y (shell forward of the guard)', min=-120.0, max=120.0, step=1.0, unit='mm', group='Chassis fit')
CHASSIS_Z = param(-15.3, 'Ground below shell rocker', min=-160.0, max=-5.0, step=1.0, unit='mm', group='Chassis fit')

RELIEF = param(8.0, 'Clearance around tires and suspension', min=4.0, max=20.0, step=1.0, unit='mm', group='Chassis fit')
TIRE_GAP = param(2.0, 'Gap between front fenders and tires', min=0.0, max=10.0, step=0.5, unit='mm', group='Chassis fit')

SHELL_PITCH = param(3.0, 'Shell rake (tail up, about the front axle)', min=0.0, max=6.0, step=0.1, unit='deg', group='Chassis fit')
REAR_TIRE_OD = param(140.0, 'Rear tire diameter', min=112.0, max=165.0, step=1.0, unit='mm', group='Rear wheel')
BUMP_TRAVEL = param(20.0, 'Suspension bump travel allowed under the shell', min=0.0, max=40.0, step=1.0, unit='mm', group='Chassis fit')
STEER_LOCK = param(30.0, 'Front steering lock each way', min=0.0, max=40.0, step=1.0, unit='deg', group='Chassis fit')
REAR_SHOCK_RISE = param(66.0, 'Rear shock top mount raised above the original', min=0.0, max=70.0, step=1.0, unit='mm', group='Rear wheel')
DECK_TRIM = param(-6.06, 'Shell bottom edge relative to the deck top plane (-6.06 = level with the deck underside)', min=-10.0, max=30.0, step=0.01, unit='mm', group='Chassis fit')
# Deck plate stand-ins (w3 deck front / rear), measured in the chassis_ref frame: top z at ref y -189, slope along y, plate thickness.
DECK_REF_Z0, DECK_SLOPE, DECK_THICKNESS = 35.4, 0.0698, 6.06
DECK_FRONT_RAISE = 0.0   # mm: was 0.9 (the front deck was lifted against the base of the front diff housing, which is gone): 0 lines the front deck up with the rear deck at their seam
_DECK_FRONT_RAISE_OLD = 0.9   # mm: the front deck plate is lifted so its top face sits flush against the base of the front diff housing (was 0.9-1.0 mm below it)
SHELL_HALF_WIDTH = param(93.5, 'Widest shell half-width (93.5 = outer edge of the swingarm arms)', min=80.0, max=175.0, step=0.5, unit='mm', group='Chassis fit')
BASE_HALF_WIDTH = 122.4  # widest half-width of the shell at SHELL_SCALE before the width match
# The shell is built at model scale and stretched by SHELL_SCALE afterwards (x: width match, y: scale, z: scale*height factor).
# Gaps built into the model are stretched with it, so PANEL_GAP is converted to model units here (y/z average) and x gets a
# correction factor, giving a true PANEL_GAP in the final frame.
PANEL_GAP_M = PANEL_GAP*2.0/(SHELL_SCALE*(1.0+SHELL_Z))
PANEL_KX = SHELL_SCALE*(1.0+SHELL_Z)/2.0/(SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH)
NOSE_HALF_WIDTH = param(40.0, 'Nose half-width (40 = front guard / skid plate)', min=25.0, max=70.0, step=0.5, unit='mm', group='Chassis fit')
NOSE_END_Y = -252.0   # nose section ends here, behind it the fenders
NOSE_BASE_HALF=NOSE_HALF_WIDTH*BASE_HALF_WIDTH/(SHELL_SCALE*SHELL_HALF_WIDTH)
REAR_SHOULDER_WIDTH=29.0  # maintains approximately 3 mm clearance to the tapered rear tube
REAR_SHOULDER_PY=215.0  # halfway from the original peak (144) toward the lower crease (286)

SERVO_BACK = 20.0   # mm: front steering servos, horns and tie-rod horn ends moved back (+y); the deck under them is a flat seat
SERVO_TILT_DEG = 4.289   # servo and horn tilt about x: parallel to the deck slope (0.9 mm rise per 12 mm toward the rear)
STEER_OUT = 6.0   # mm: steering servos, horns and tie-rod horn ends moved outboard so a 26.5 mm low-profile servo (AGFRC B44BLS class) clears the front diff housing
