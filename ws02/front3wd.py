"""WS-03 front kinematics: swing arms (x-z plane), lean-servo horn solve. Frame: z = 0 at axle height at zero lean."""
import math, numpy as np
from scipy.optimize import brentq

R, W, T, LA = 56.0, 62.0, 144.0, 100.0          # tire radius, width, wheel centre half-track, arm length
P = np.array([-LA, 0.0])                          # arm pivot (x, z); front diff axis


def arm_angles(phi):
    """Arm angle (rad, up positive) for the left and right wheel at body lean phi (rad, left up)."""
    h = R * math.cos(phi) + W / 2 * abs(math.sin(phi)) - R
    zl = (h - T * math.sin(phi)) / math.cos(phi)
    zr = (h + T * math.sin(phi)) / math.cos(phi)
    return math.asin(zl / LA), math.asin(zr / LA)


def lean_horn(theta, lug, shaft, r, lr, rest):
    """Horn angle (rad from +z, toward -x) for arm angle theta; None if unreachable."""
    a = math.atan2(lug[1], lug[0]); rho = math.hypot(*lug)
    l = P + rho * np.array([math.cos(a + theta), math.sin(a + theta)])
    def f(psi):
        t = shaft + r * np.array([-math.sin(psi + rest), math.cos(psi + rest)])
        return np.linalg.norm(t - l) - lr
    return brentq(f, -1.6, 1.6) if f(-1.6) * f(1.6) < 0 else None


if __name__ == "__main__":
    ph = np.radians(np.linspace(-30, 30, 13))
    th = np.array([arm_angles(p) for p in ph])
    print("arm angle max deg", round(math.degrees(np.abs(th).max()), 1),
          "wheel x shift max mm", round(LA * (1 - math.cos(np.abs(th).max())), 1))
    best = []
    for rho_a in (12.0, 16.0, 20.0, 24.0):
        for ang in (20, 32, 45, 60):
            lug = rho_a * np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
            for r in (20.0, 24.0, 28.0):
                for rest in (-40, -20, 0, 20, 40):
                    shaft = P + lug + np.array([0.0, -r * 0.9])
                    for lr in (16.0, 24.0, 32.0):
                        rs = [lean_horn(t, lug, shaft, r, lr, math.radians(rest)) for t in th.ravel()]
                        if None in rs:
                            continue
                        worst = max(abs(math.degrees(x)) for x in rs)
                        best.append((worst, rho_a, ang, r, rest, lr, shaft.round(1).tolist()))
    best.sort()
    for b in best[:5]:
        print(b)
