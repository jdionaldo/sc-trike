"""Printable rear swingarm (PETG): high-strength Vierendeel / ladder-truss single-sided arm (modeled after NLC ST-30102 sample).

Built in the rear swingarm frame (parts/rear_ref.step, before model.py rotates the group about the pivot):
X lateral, Y toward the tail, Z up. Hard points match the stand-in arm: pivot (y 105.64, z 79.02), axle (y 225.55, z 55.86),
and shock lower eye on the wheel centre plane at (x 0, y 150, z 114). The belt runs between the inner and outer ladder frames (x 54..57).
For maximum bending and torsional strength, each side uses thick top and bottom main chord tubes with a solid pivot web plate,
three angled ladder struts, a concentric eccentric-style axle flange, and a heavy triangulated arch to the twin shock ears.
"""
import cadquery as cq

PIVOT_YZ = (105.64, 79.02)
AXLE_YZ = (225.55, 55.86)
PLATE_X = (47.0, 72.0)            # inner and outer ladder centerplanes straddling the belt (x 54..57)
INNER_PIVOT_X = -4.0              # second pivot plate centreplane, inboard of the rear drive block (face at x = 6)
CHORD_D = 12.0                   # thick main upper/lower chord tubes
BELT_LIFT = (0.0, 2.5, 3.5, 2.5, 0.0)   # mm, lift of the upper Warren nodes over the belt
STRUT_D = 10.0                     # Warren diagonals
LOW_TIE_Z = 40.0                  # centre line of the lower tie plane
LOW_X = True                      # X-brace the lower cross plane
CROSS_D = 12.0                     # cross tubes between the plates (they carry the wheel's roll torque)
BOSS_W = 10.0                     # boss width along x
PIVOT_OD, PIVOT_BORE = 22.0, 5.6  # pivot boss on the 5 mm cross shaft (pivot pulley bore 5.2, carrier bearings 5x11x4): the arm rides on one 5x11x4
                                  # bearing per pivot plate (PIVOT_SEATS), the bore beside the seat clears the turning shaft
AXLE_OD, AXLE_BORE = 30.0, 8.2    # large flange hub around 8 mm axle (with 6-bolt pattern like reference); the axle turns in two 8x16x5 bearings (AXLE_SEATS)
BRG_FIT = 0.1                     # bearing seat diameter over the bearing OD (as the printed bearing blocks: D11.1)
PIVOT_BRG = (11.0, 4.0)           # 5x11x4 (MR115ZZ)
AXLE_BRG = (16.0, 5.0)            # 8x16x5 (688ZZ)
PIVOT_SEATS = ((-3.0, 1.0), (42.0, 46.0), (67.0, 71.0))   # x ranges of the pivot bearing seats: the face of each plate toward the drive block / pulley
AXLE_SEATS = ((47.0, 52.0), (67.0, 72.0))                # x ranges of the axle bearing seats: the faces toward the axle pulley
APEX_YZ = (134.0, 114.0)          # front arch cross-tube axis ahead of the shock eye
ARCH_D = 12.0                     # twin over-tire arch tube diameter
SHOCK_EYE_YZ = (150.0, 114.0)     # shock lower eye pin axis (arm frame)
EYE_W = 8.0                       # shock eye width
EAR_GAP = EYE_W + 0.8             # 8.8 mm clear slot between the ears (0.4 mm clearance per side)
EAR_T = 8.4                       # ear thickness (x = ±4.4..12.8 mm; was 6.0: FEM at the 237 N shock force, safety 1.53 on the ear's outer face)
EAR_R = 8.5                       # ear end radius around the pin
KNEE_LIFT = 34.0                  # front knee node above the pin axis (keeps the pin axis free for the bolt head and nut)
KNEE_LIFT_R = 24.0                # rear knee node: lower, so the arm clears the cage tail rail at full bump (35 mm travel at 34 mm lift)
PIN_BORE = 6.4                    # M6 pin
PIN_CORRIDOR_D = 15.0             # free corridor along the pin axis for the M6 head, the nut and their tools
PIN_CORRIDOR_FLAT = 6.5           # half width of the corridor's flat sides where it runs out of the bridge tubes' top and bottom faces
KEEL_DROP_F = 6.0                 # front keel: shallower, it passes over the rear bearing carrier (w3 rbc upper) at full droop (1.4 mm clear at -15)
KEEL_DROP = 10.0                  # keel under each shock bridge tube, depth under the tube at the inner plate (tapers to the ear lug's bottom)
PIN_SLOT_L = 25.2                 # length of the corridor's flat-sided slot from the ear face (ends at x 38.0, 3.7 mm short of the root rail)
CORR_CH = 1.0                     # 45 deg chamfer of material in the corner where the pin corridor leaves the ear face
WEB_X = 22.0                      # the web behind the pin corridor runs from the +x ear out along the rear bridge tube to here
AXLE_CAP_X = 78.8                 # end of the axle bore in the outer plate: a 1.2 mm cap closes it (the axle ends at x 76)


def _v(x, y, z): return cq.Vector(x, y, z)


def _boss(x0, x1, yz, od):
    return cq.Solid.makeCylinder(od / 2, x1 - x0, _v(x0, yz[0], yz[1]), _v(1, 0, 0))


def _lerp(p, q, t): return (round(p[0] + (q[0] - p[0]) * t, 2), round(p[1] + (q[1] - p[1]) * t, 2))


def make_rear_arm():
    """Single-sided rear swingarm in the same language as the front arms: two slim triangulated (Warren) tube trusses either side of the belt,
    solid cast-style necks at the pivot and the axle hub, cross tubes at the nodes, and a short triangulated bridge out to the shock clevis.
    Second pivot plate on the far side of the rear drive block (A-frame)."""
    import math
    from parts.cage import _Frame
    from parts.stealth_shell import beveled_hull as hull
    F = _Frame()
    P, A, AF, AR = PIVOT_YZ, AXLE_YZ, APEX_YZ, SHOCK_EYE_YZ
    xi, xo = PLATE_X
    U0, U2 = (122.0, 95.0), (218.0, 64.0)          # upper chord root and hub end
    L0, L2 = (122.0, 55.0), (218.0, 41.0)          # lower chord, 8 mm lower than before so the lower lattice sits at chord level, under the belt
    # Warren nodes: bottoms at 0, 1/3, 2/3, 1; tops at the root post, then midway between bottoms (diagonals alternate up and down)
    B = [L0, _lerp(L0, L2, 1 / 3), _lerp(L0, L2, 2 / 3), L2]
    Tn = [U0, _lerp(U0, U2, 1 / 6), _lerp(U0, U2, 1 / 2), _lerp(U0, U2, 5 / 6), U2]
    # the 6 mm GT2 belt (pulleys 26T / 30T) runs 2 to 3 mm higher than the old 3 mm belt: the upper chord nodes over it are lifted
    Tn = [(q[0], q[1] + dz) for q, dz in zip(Tn, BELT_LIFT)]
    zig = [(B[0], Tn[1]), (Tn[1], B[1]), (B[1], Tn[2]), (Tn[2], B[2]), (B[2], Tn[3]), (Tn[3], B[3])]

    for x in PLATE_X:
        T = lambda p: (x, round(p[0], 2), round(p[1], 2))
        u_pts = [U0, Tn[1], Tn[2], Tn[3], U2]
        l_pts = B
        for a, b in zip(u_pts, u_pts[1:]): F.tube(T(a), T(b), CHORD_D)
        for a, b in zip(l_pts, l_pts[1:]): F.tube(T(a), T(b), CHORD_D)
        F.tube(T(L0), T(U0), CHORD_D)                                  # root post
        for a, b in zig: F.tube(T(a), T(b), STRUT_D)
        # cast-style neck: pivot boss to the chord roots
        NW = BOSS_W / 2; NWI = 4.2 if x == xi else NW   # inner face of the inner plate stays 0.2 mm off the tail deck wall (x 42.6)
        # neck as wide as the pivot boss (10 mm; was 7 mm): the junction near L0 was the sharp-corner stress spot in the FEM
        F.solids.append(hull([
            (x - NWI, P[0], P[1] + 9.0), (x + NW, P[0], P[1] + 9.0),
            (x - NWI, P[0], P[1] - 10.0), (x + NW, P[0], P[1] - 10.0),
            (x - NWI, U0[0], U0[1] + 3.0), (x + NW, U0[0], U0[1] + 3.0),
            (x - NWI, L0[0], L0[1] - 4.0), (x + NW, L0[0], L0[1] - 4.0)]))
        # cast-style neck: chord ends to the axle hub
        F.solids.append(hull([
            (x - 3.5, U2[0], U2[1] + 3.0), (x + 3.5, U2[0], U2[1] + 3.0),
            (x - 3.5, L2[0], L2[1] - 3.0), (x + 3.5, L2[0], L2[1] - 3.0),
            (x - 3.5, A[0], A[1] + 11.0), (x + 3.5, A[0], A[1] + 11.0),
            (x - 3.5, A[0], A[1] - 11.0), (x + 3.5, A[0], A[1] - 11.0)]))
        F.solids.append(_boss(x - BOSS_W / 2, x + BOSS_W / 2, P, PIVOT_OD))
        F.holes.append(_boss(x - 7, x + 7, P, PIVOT_BORE))
        F.solids.append(_boss(x - BOSS_W / 2, x + BOSS_W / 2, A, AXLE_OD))
        F.holes.append(_boss(x - 7, x + (7 if x == xi else AXLE_CAP_X - xo), A, AXLE_BORE))

    # Lower lattice under the belt: the lattice of the plates continues across the arm in plan view, at chord level (no posts). The lower chords sit
    # 8 mm lower than the plate trusses' original line, so cross tubes and X diagonals pass under the belt's lower strand.
    LB = B[:3]                                          # nothing at the hub end: the axle pulley (y >= 219.5) sits there
    for q in LB:
        F.tube((xi, q[0], q[1]), (xo, q[0], q[1]), CROSS_D)
    for q0, q1 in zip(LB, LB[1:]):
        F.tube((xi, q0[0], q0[1]), (xo, q1[0], q1[1]), STRUT_D - 1.0)
        if LOW_X: F.tube((xo, q0[0], q0[1]), (xi, q1[0], q1[1]), STRUT_D - 1.0)
    # Cross tubes at the root and mid top nodes (above the belt) and one diagonal
    for q, d_ in ((U0, CROSS_D), (Tn[1], CROSS_D), (Tn[2], CROSS_D)):   # mid node at 12 mm like the others (it was 8: its section met the 12 mm chord faces with 0.005 mm edges)
        F.tube((xi, q[0], q[1]), (xo, q[0], q[1]), d_)
    F.tube((xi, U0[0], U0[1]), (xo, Tn[1][0], Tn[1][1]), STRUT_D - 1.0)
    F.tube((xo, Tn[1][0], Tn[1][1]), (xi, Tn[2][0], Tn[2][1]), STRUT_D - 1.0)

    # Outer flange ring with 6 pinch-bolt holes
    F.solids.append(_boss(xo + 1.0, xo + 6.5, A, AXLE_OD + 4.0))
    F.solids.append(_boss(xo + 5.0, xo + 8.0, A, 18.0))
    for k in range(6):
        ang = math.radians(k * 60.0 + 30.0)
        F.holes.append(_boss(xo - 6.0, xo + 10.0, (A[0] + 11.5 * math.cos(ang), A[1] + 11.5 * math.sin(ang)), 2.8))

    # Shock bridge: a frame in the plane z = 114 from the inner plate to the +x clevis ear, passing front and rear of the pin axis (no diagonal: the
    # pin's tool corridor crosses the bay and cut the old one down to a dead stub with feather edges; the
    # M6 head sits on the axis at y 150, so the tubes run at y 126 and y 164), tied down to the inner plate by two risers.
    xc = round(EAR_GAP / 2 + EAR_T / 2, 2)
    ZB = AF[1]
    YF, YR = AF[0] - 8.0, AR[0] + 14.0                 # front and rear bridge tubes
    for y_, y_e in ((YF, AF[0] - 4.0), (YR, AR[0] + 6.0)):
        F.tube((xi, y_, ZB), (xc, y_e, ZB), CHORD_D)
    F.tube((xi, YF, ZB), (xi, YR, ZB), CHORD_D)         # root rail on the inner plate
    # Keels under the two bridge tubes (chord pass 1, November 26): the bridge is a frame in the plane z = 114 and the 273 N shock force is
    # vertical, so its tubes bend out of that plane as a cantilever from the inner plate (FEM: safety 1.09 to 1.30 at the root on the inner plate).
    # A 6 mm blade under each tube makes it a T, KEEL_DROP deeper at the plate and down to the ear lug's bottom at the ear (the tire stays 12 mm clear).
    # (the front keel's root sits 2 mm forward so it ends inside the riser from the upper chord root, which leans forward there)
    for y_, y_e, y0, kd in ((YF, AF[0] - 4.0, -2.0, KEEL_DROP_F), (YR, AR[0] + 6.0, 0.0, KEEL_DROP)):
        F.solids.append(hull([(x_, yy + dy, z_) for x_, yy, zb in ((xi, y_ + y0, ZB - CHORD_D * 0.44 - kd), (xc, y_e, ZB - EAR_R + 1.0))
                               for dy in (-3.0, 3.0) for z_ in (ZB, zb)]))
    F.tube((xi, U0[0], U0[1]), (xi, YF, ZB), CHORD_D)             # risers from the inner upper chord
    F.tube((xi, Tn[1][0], Tn[1][1]), (xi, YR, ZB), CHORD_D)
    F.tube((xi, Tn[1][0], Tn[1][1]), (xi, YF, ZB), STRUT_D)
    # Front barrel and double-shear clevis ears straddling the shock eye (x = +-(4.4..10.4))
    arch_end = -(EAR_GAP / 2 + EAR_T)
    F.solids.append(_boss(arch_end, -arch_end, AF, ARCH_D + 2.0))
    for sx in (-1, 1):
        x0 = sx * EAR_GAP / 2; x1 = sx * (EAR_GAP / 2 + EAR_T)
        lo, hi = min(x0, x1), max(x0, x1)
        lug = _boss(lo, hi, AF, 2 * EAR_R).fuse(_boss(lo, hi, AR, 2 * EAR_R))
        lug = lug.fuse(cq.Solid.makeBox(hi - lo, AR[0] - AF[0], 2 * EAR_R, _v(lo, AF[0], AF[1] - EAR_R)))
        F.solids.append(lug)
    F.holes.append(_boss(-EAR_GAP / 2 - EAR_T - 1, EAR_GAP / 2 + EAR_T + 1, AR, PIN_BORE))
    arch_out = EAR_GAP / 2 + EAR_T
    F.holes.append(_boss(-EAR_GAP / 2, EAR_GAP / 2, AR, 21.0))
    # Tool corridor for the M6 head and nut, D15 on the pin axis. Above and below it has flat sides (a slot through z): the round corridor left the
    # rear bridge tube's top and bottom faces at 45 degrees, a feather edge 17 mm long.
    # Where the corridor and its slot leave the ear face, the inside corner keeps a CORR_CH x 45 deg chamfer of material (chord pass 2): the sharp
    # corner was the low spot of the arm (FEM 1.71 / 1.47 / 1.34 at meshes 2.0 / 1.8 / 1.5, not settling). The face keeps r 6.5 free (M6 head and nut r 5.8).
    c_ = CORR_CH
    for sg in (1, -1):
        xf = sg * arch_out                                  # ear face
        x0 = xf + sg * c_
        F.holes.append(_boss(min(x0, x0 + sg * (24.0 - c_)), max(x0, x0 + sg * (24.0 - c_)), AR, PIN_CORRIDOR_D))
        F.holes.append(cq.Solid.makeCone(PIN_CORRIDOR_D / 2 - c_, PIN_CORRIDOR_D / 2, c_, _v(xf, AR[0], AR[1]), _v(sg, 0, 0)))
        # the flat sides run to where they leave the rear bridge tube's front face (x 36.9) plus 1.1 mm, no further: at 30 mm (to x 42.8) they
        # notched the root rail's inboard face (x 41.7) 1.1 mm deep next to the bridge crotch, the arm's low spot (chord pass 3)
        xb0, xb1 = sorted((x0, x0 + sg * (PIN_SLOT_L - c_)))
        F.holes.append(cq.Solid.makeBox(xb1 - xb0, 2 * PIN_CORRIDOR_FLAT, 2 * CHORD_D, _v(xb0, AR[0] - PIN_CORRIDOR_FLAT, AR[1] - CHORD_D)))
        w_ = PIN_CORRIDOR_FLAT
        F.holes.append(cq.Workplane('XY').polyline([(xf, AR[0] - w_ + c_), (x0, AR[0] - w_), (x0, AR[0] + w_), (xf, AR[0] + w_ - c_)]).close()
                       .extrude(2 * CHORD_D).translate((0, 0, AR[1] - CHORD_D)).val())

    # Web behind the corridor where the rear bridge tube meets the +x ear: the corridor leaves only a 5 mm band of the tube against the ear face, and
    # the shock force turns from the ear into the bridge through it (FEM: 12.0 MPa, safety 1.66 at the corridor's edge on the ear face). The web
    # widens the band rearward and up to the ear's top; the corridor and its slot are cut after it, so the tool path stays as it was.
    yb = lambda x_: YR + (AR[0] + 6.0 - YR) * (xi - x_) / (xi - xc)    # rear bridge tube centre line at x_
    from parts.cage import TUBE_K
    hb = CHORD_D * TUBE_K / 2.0
    hi_ = hb - 2.0   # the web's far end lies inside the tube's octagon at the top and sides and 1 mm under it at the bottom, inside the keel: its square corners on the
                     # chamfers left 0.007 mm edges (mesh failure)
    F.solids.append(hull([(xc, AR[0] + 4.0, ZB - EAR_R + 2.0), (xc, AR[0] + 4.0, ZB + EAR_R - 0.5), (xc, yb(xc) + hb + 3.0, ZB - hb), (xc, yb(xc) + hb + 3.0, ZB + EAR_R - 1.5),
                          (WEB_X, yb(WEB_X) - 2.0, ZB - hb - 1.0), (WEB_X, yb(WEB_X) - hi_, ZB + hi_), (WEB_X, yb(WEB_X) + 2.0, ZB - hb - 1.0), (WEB_X, yb(WEB_X) + hi_, ZB + hi_)]))

    # Second pivot plate on the far side of the rear drive block, webbed to the front barrel
    XP = INNER_PIVOT_X
    F.solids.append(_boss(XP - BOSS_W / 2, XP + BOSS_W / 2, P, PIVOT_OD))
    F.holes.append(_boss(XP - 7, XP + 7, P, PIVOT_BORE))
    F.solids.append(hull([
        (XP - 3.5, P[0], P[1] + 9.0), (XP + 3.5, P[0], P[1] + 9.0),
        (XP - 3.5, P[0] + 6.0, P[1] - 9.0), (XP + 3.5, P[0] + 6.0, P[1] - 9.0),
        (XP - 3.5, AF[0] - 4.0, AF[1] + 5.0), (XP + 3.5, AF[0] - 4.0, AF[1] + 5.0),
        (XP - 3.5, AF[0] - 4.0, AF[1] - 5.0), (XP + 3.5, AF[0] - 4.0, AF[1] - 5.0)]))   # web ends 6.4 mm from the barrel axis, inside its r 7 (at 6.0 it stood 0.2 mm out: a 0.013 mm2 sliver face that broke the FEM mesh)
    F.tube((XP, P[0], P[1] + 4.0), (XP, AF[0], AF[1] - 2.0), CHORD_D)
    arm = F.build()
    # The square chords (CHORD_D x TUBE_K = 10.56 mm) were 0.28 mm wider than the 10 mm bosses: clip them flush with the boss faces near the
    # axle hubs (both plates; the outer face of the outer hub is under the flange ring) and the inner pivot boss.
    for x, yz, r, sides in ((xi, A, AXLE_OD / 2, (-1, 1)), (xo, A, AXLE_OD / 2, (-1,)), (XP, P, PIVOT_OD / 2, (-1, 1))):
        for sd in sides:
            x0 = x + sd * BOSS_W / 2
            arm = arm.cut(_boss(x0, x0 + 3.0, yz, 2 * r + 5.0) if sd > 0 else _boss(x0 - 3.0, x0, yz, 2 * r + 5.0))
    for (x0, x1) in PIVOT_SEATS:
        arm = arm.cut(_boss(x0 - (0.5 if x0 > 0 else 0.0), x1 + (0.5 if x0 < 0 else 0.0), P, PIVOT_BRG[0] + BRG_FIT))
    for (x0, x1) in AXLE_SEATS:
        arm = arm.cut(_boss(x0 - (0.5 if x0 == 67.0 else 0.0), x1 + (0.5 if x0 == 47.0 else 0.0), A, AXLE_BRG[0] + BRG_FIT))
    arm = arm.clean()
    assert arm.isValid() and len(arm.Solids()) == 1, 'rear arm must be one valid solid, got %d' % len(arm.Solids())
    return arm
