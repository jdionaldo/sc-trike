"""WS-03 single lean servo: an Injora INJS15 on the centreline, shaft along x pointing aft, driving a V-shaped printed rocker whose two tips
push two ball-link rods to the arm lugs (one arm up, the other down).  Printed here: the rocker and the servo tower.

Geometry (x, zc, R, beta, L) was fitted in the lean range +-20 deg so both rods keep one length to 0.6 mm (see WS03_LEAN.md); the servo turns
+-22.3 deg for +-20 deg of lean, almost linearly.  Servo envelope and mount: INJS15 body 23 x 12 x 27.5 (32 over the ears); the shaft offset
(4.5 mm from the body centre), flange height (5 mm below the top face) and ear hole pitch (28 mm) are read off the drawing, UNVERIFIED."""
import math

from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart, _clean

XR, ZC = -82.0, 34.5                  # rocker axis (x, z): along x, on the centreline
R, BETA = 17.29, 1.2548                 # tip radius, V half angle at rest (rad above horizontal)
K_SERVO = 1.0132                       # servo angle per degree of lean (the servo sets the lean: psi = -K_SERVO * phi)
SHOCK = dict(lmin=51.5, lmax=75.5, stroke=24.0, rest=68.3, eye=3.0, mass_g=25.0)   # coilover link: eye to eye compressed / extended, 70 % extended at rest
ROD_L = SHOCK['rest']
PLATE = 6.0                            # rocker thickness (grows aft: the +x face stays against the servo horn)
TOP_X = XR + 2.0 + 4.5                 # servo top face (horn plate, then the 4.5 mm of spline)
SV_L, SV_W, SV_H, SV_EAR, SV_OFF = 23.0, 12.0, 27.5, 32.0, 4.5   # body along y, along z, along x; ears; shaft offset (body centre at y = -SV_OFF)
FLANGE_DX = 5.0                        # ear plane below the top face
TWR_X = (TOP_X + FLANGE_DX - 5.0, TOP_X + FLANGE_DX)       # tower plate 5 mm (was 2.5), ears sit on its forward face
TWR_Y = (-21.5, 12.5)
LEG_Y0 = 0.3                          # the plate hangs from one leg on the +y side; below z 12.5 it is open to the battery
TWR_Z0, TWR_Z1 = -23.0, ZC + 10.0
FOOT_X = (TWR_X[0], TWR_X[0] + 9.0)
FEET = [(TWR_X[0] + 5.8, 4.5), (TWR_X[0] + 5.8, 10.0)]   # M2 screws into the base plate (portal legs straddle the battery)
EAR_Y = (-SV_OFF - 14.0, -SV_OFF + 14.0)


def tips(psi=0.0):
    """Rocker tip positions (y, z) for the left (+y) and right (-y) rod at servo angle psi (rad)."""
    return ((R * math.cos(BETA + psi), ZC + R * math.sin(BETA + psi)), (-R * math.cos(BETA - psi), ZC + R * math.sin(BETA - psi)))


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def rocker(p):
    """V rocker, plate thickness along x; print frame: X' = y, Y' = z - ZC, Z' = x - (XR - 2), flat on the bed."""
    def fn():
        hub = Manifold.cylinder(PLATE, 6.5, 6.5, 40)
        (yl, zl), (yr, zr) = tips()
        arms = None
        for y, z in ((yl, zl - ZC), (yr, zr - ZC)):
            eye = Manifold.cylinder(PLATE, 4.5, 4.5, 36).translate((y, z, 0.0))
            a = Manifold.batch_hull([hub, eye])
            arms = a if arms is None else arms + a
        body = arms + hub
        for y, z in ((yl, zl - ZC), (yr, zr - ZC)):
            body = body - Manifold.cylinder(PLATE + 2.0, 1.6, 1.6, 24).translate((y, z, -1.0))                  # shock eye bolt, M3
        body = body - Manifold.cylinder(PLATE + 2.0, 1.7, 1.7, 24).translate((0.0, 0.0, -1.0))                  # horn screw
        for k in range(4):
            a = math.radians(45.0 + 90.0 * k)
            body = body - Manifold.cylinder(PLATE + 2.0, 1.1, 1.1, 20).translate((5.5 * math.cos(a), 5.5 * math.sin(a), -1.0))   # to the servo horn
        return _clean(MB.to_trimesh(body))
    return MeshPart("w3_lean_rocker", fn, walls=False, supports=False)


def tower(p):
    """Servo tower, assembly frame shifted down by TWR_Z0 so the feet sit on the bed: a plate with the servo window, two gussets and a foot plate."""
    def fn():
        plate = _box(TWR_X[0], TWR_X[1], TWR_Y[0], TWR_Y[1], 0.0, TWR_Z1 - TWR_Z0)
        foot = _box(FOOT_X[0], FOOT_X[1], LEG_Y0, TWR_Y[1], 0.0, 4.0)
        body = plate + foot
        for y0, y1 in ((LEG_Y0, LEG_Y0 + 3.0), (TWR_Y[1] - 3.0, TWR_Y[1])):
            tri = MB.prism_xz([(TWR_X[0], 4.0), (TWR_X[0] + 18.0, 4.0), (TWR_X[0], 26.0)], y0, y1).translate((0.0, 0.0, 0.0))
            body = body + tri
        zc = ZC - TWR_Z0
        win = _box(TWR_X[0] - 1.0, TWR_X[1] + 1.0, -SV_OFF - SV_L / 2 - 0.3, -SV_OFF + SV_L / 2 + 0.3, zc - SV_W / 2 - 0.3, zc + SV_W / 2 + 0.3)
        body = body - win
        import layout3wd as LY                                                                           # the plate is open under the servo so the battery (y -37.5..-2.5, up to z 11) slides in
        (_, _), (by0, by1), (_, bz1) = LY.BATT_BOX
        body = body - _box(TWR_X[0] - 1.0, TWR_X[1] + 1.0, by0 - 2.8, by1 + 2.8, -1.0, bz1 + 1.5 - TWR_Z0)
        for y in EAR_Y:                                                           # ear screws (M2 self-tapping, from the front)
            body = body - Manifold.cylinder(TWR_X[1] - TWR_X[0] + 2.0, 0.95, 0.95, 20).rotate((0.0, 90.0, 0.0)).translate((TWR_X[0] - 1.0, y, zc))
        for fx, fy in FEET:
            body = body - Manifold.cylinder(6.0, 1.3, 1.3, 24).translate((fx, fy, -1.0))                  # M2 clear, screw into the base plate pilots
        return _clean(MB.to_trimesh(body))
    return MeshPart("w3_lean_tower", fn, walls=True, supports=True)


def build(p):
    return [rocker(p), tower(p)]
