"""Review renders of the fitted skin on the cage: python renders_fit.py OUTDIR
Four views of the assembly (front-left 3/4, rear-right 3/4, side, top) and close-ups of the mounts (nose hinge ears, tab pads and bosses, joint dowels, front arm slot)."""
import sys
from pathlib import Path
import numpy as np
import w3_assembly as A
import zrender as Z
import viewfit as V
import parts.w3_frame as FR

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out/renders_fit")
out.mkdir(parents=True, exist_ok=True)
items = V.groups(A.assembly(0.0, 0.0))
C = V.COL


def full(name, eye, target, h, size=(1500, 820), up=(0, 0, 1), title=None):
    Z.render([m for n, m, g in items], [C[g] for n, m, g in items], str(out / name), eye=eye, target=target, up=up, size=size, ortho_h=h, title=title or name)


def closeup(name, centre, h, clip_y=None, eye_dir=(0, 1, 0), size=(1100, 800), up=(0, 0, 1), clip_z=None, title=None):
    ms, cols = [], []
    for n, m, g in items:
        mm = m
        if clip_y is not None:
            mm = V.clip(mm, [0, clip_y, 0], [0, -1, 0])
        if clip_z is not None and mm is not None:
            mm = V.clip(mm, [0, 0, clip_z], [0, 0, -1])
        if mm is None:
            continue
        ms.append(mm)
        cols.append(C[g])
    c = np.array(centre, float)
    d = np.array(eye_dir, float)
    Z.render(ms, cols, str(out / name), eye=c + 800.0 * d / np.linalg.norm(d), target=c, up=up, size=size, ortho_h=h, title=title or name)


full("view1_front_left_34.png", (260, -700, 380), (-150, 0, 20), 520, title="front-left 3/4")
full("view2_rear_right_34.png", (-650, 700, 350), (-190, 0, 20), 560, title="rear-right 3/4")
full("view3_side_left.png", (-150, -900, 30), (-190, 0, 20), 330, title="left side (front is to the right)", up=(0, 0, 1))
full("view4_top.png", (-190, 0, 900), (-190, 0, 0), 520, size=(1500, 700), up=(1, 0, 0), title="top (front is up)")
hx, hz = FR.HINGE_PIN
closeup("mount1_nose_hinge_ears.png", (hx - 8, 0, hz + 5), 90, clip_y=0.5 * (FR.HINGE_EAR[0] + FR.HINGE_EAR[1]), title="nose hinge: skin ears on the pin, section through the ear plane")
tabs = FR.tab_stations()
for i, (tx, ty, tz, br) in enumerate(tabs):
    closeup(f"mount{2 + i}_tab_{['nose_roof', 'hoop_roof', 'cab_roof', 'rear_deck'][i]}.png", (tx, ty, tz + 10), 70, clip_y=ty, title=f"magnet tab {i + 1}: pad on the cage, boss on the skin (section y = {ty:.0f})")
import skin_user as U
closeup("mount6_joint_front_mid.png", (U.XOFF, 20, 40), 110, clip_y=38.0, title="front|cab joint: dowel bosses (section y = 38)")
closeup("mount7_joint_mid_rear.png", (U.XOFF - 57.5, 20, 40), 110, clip_y=38.0, title="cab|rear joint: dowel bosses (section y = 38)")
closeup("mount8_front_arm_slot.png", (-50, -120, 20), 160, eye_dir=(0, -1, 0), title="front wheel arch slot for the arms (left side)")
print("renders in", out)
