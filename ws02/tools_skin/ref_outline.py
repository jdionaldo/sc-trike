"""Reference silhouettes traced from the two drawings (54 top, 55 side) and scaled into the build frame (x fwd, front axle x 0, y left, z up).
x: 450 mm wheelbase = 913 px (top) / 842 px (side); z: 0.44 mm/px (front tyre r 56 mm = 127 px), floor at z -26 = the drawing's floor line."""
REF_HALF = [(55, 19), (3.5, 58), (-52, 85), (-105, 90), (-279, 91), (-327, 91), (-391, 62), (-401, 37)]          # (x, half width) plan
REF_TOP = [(40, 52), (-5, 74), (-72, 84), (-151, 124), (-290, 130), (-322, 128), (-397, 112), (-468, 100)]       # (x, z) centre-line roof
REF_FLOOR_Z = -26.0
import numpy as np
def half(x): p = sorted(REF_HALF); return float(np.interp(x, [a for a, _ in p], [b for _, b in p], left=np.nan, right=np.nan))
def top(x): p = sorted(REF_TOP); return float(np.interp(x, [a for a, _ in p], [b for _, b in p], left=np.nan, right=np.nan))
