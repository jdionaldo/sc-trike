"""WS-03 electronics and mechanical fit check: slides each candidate envelope through the assembly (with the old placeholders removed) and reports where it fits.
Envelopes: 3S LiPo stick 75 x 35 x 25 (1300 mAh class), 3S 2200 mAh 105 x 35 x 25, receiver 30 x 20 x 10, Fusion SE motor 36 x 58.1 (ESC built in), INJS15 servo 23 x 27.5 x 12 (32 mm over the ears)."""
import numpy as np
from manifold3d import Manifold
import mono_build as MB
import w3_assembly as A

SKIP = ("b_battery", "battery_tray", "b_esc", "b_motor", "b_motor_shaft", "lean_servo", "steer_servo", "mock_receiver", "lean_horn", "steer_horn")


def obstacles():
    acc = None
    for n, m, k in A.assembly(0.0, 0.0):
        if n.startswith(SKIP) or n.startswith("body3") or n.startswith("w3_tail"):
            continue
        t = MB.man(m)
        acc = t if acc is None else acc + t
    return acc


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def scan(O, make, xs, ys, zs):
    best = []
    for x in xs:
        for y in ys:
            for z in zs:
                v = (make(x, y, z) ^ O).volume()
                if v < 0.5:
                    best.append((x, y, z))
    return best


def run():
    O = obstacles()
    out = []
    # skin interior limits (simple): roof/hood height at x is far above everything here; the nose underside rises ahead of x -6
    def underside(x):                                   # nose underside z at x (skin floor): -26 behind x -1, rising 53/35 ahead of it
        return -26.0 if x < -1.0 else -26.0 + (x + 1.0) * 53.0 / 35.0
    cases = {
        "3S 1300 mAh 75x35x25": (lambda x, y, z: box(x, x + 75, y - 17.5, y + 17.5, z, z + 25), np.arange(-160, 10, 4.0), [-20.0, -10.0, 0.0], [-22.0, -14.0, -6.0]),
        "3S 2200 mAh 105x35x25": (lambda x, y, z: box(x, x + 105, y - 17.5, y + 17.5, z, z + 25), np.arange(-300, 10, 4.0), [-20.0, -10.0, 0.0], [-22.0, -14.0, -6.0]),
        "receiver 30x20x10": (lambda x, y, z: box(x, x + 30, y - 10, y + 10, z, z + 10), np.arange(-200, 20, 5.0), [0.0, 15.0, -15.0], [-22.0, -10.0, 5.0, 20.0]),
        "Fusion SE motor 36x58 (axis x)": (lambda x, y, z: Manifold.cylinder(58.1, 18, 18, 48).rotate((0, 90, 0)).translate((x, y, z)), np.arange(-340, -150, 4.0), [-21.0, 0.0, 21.0], [8.0, 16.0, 24.0, 32.0]),
        "INJS15 servo 23x27.5x12 (axis y)": (lambda x, y, z: box(x, x + 32, y, y + 27.5, z, z + 12), np.arange(-60, 20, 4.0), [-14.0, 0.0], [-22.0, -14.0, -6.0]),
    }
    for name, (mk, xs, ys, zs) in cases.items():
        ok = scan(O, mk, xs, ys, zs)
        if "battery" in name:
            ok = [p for p in ok if underside(p[0]) <= p[2] and underside(p[0] + 75) <= p[2]]
        out.append((name, len(ok), ok[:6]))
        print(name, len(ok), ok[:4], flush=True)
    lines = ["# WS-03 electronics and mechanical fit check", "", "Envelope slid through the assembly (placeholders removed); a position counts as a fit when it touches no printed part, gear, shaft, tube or tyre.", ""]
    for name, n, first in out:
        lines.append(f"- {name}: {n} fitting positions; first (x, y, z): {first[:4] if first else 'none'}")
    open("WS03_FIT.md", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    run()
