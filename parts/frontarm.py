"""Printable front swingarm (PETG): high-strength S-bend / multi-triangulated tubular truss (modeled after sample H052aeaab2e854be2b013b8fdef09ac85U.jpg.png)
with integrated G-load suspension pod mount and cross-bracing (markup 12:26).

Built in the frame of parts/chassis_ref.step for the +x side (the -x arm is the mirror image). Hard points from the stand-in it replaces:
pivot = the diff output shaft axis (y -125.8, z 62.8, along x), tip = the tip shaft axis (y -225.55, z 55.9). The belt (x 70.5..73.5, z <= 70.1)
runs between the inner and outer truss planes; the lean pod (pod 1, x 85.5..93.5, y -214.3..-193.7, z 72.0..85.7) carries the front suspension G-load,
so the outer truss is built with a reinforced pod-seat cradle and direct vertical + diagonal compression struts down to the lower chord and across to the inner frame.
"""
import cadquery as cq

PIVOT_YZ = (-125.8, 62.8)
TIP_YZ = (-225.55, 55.9)
PLATE_X = (66.2, 89.5)            # inner and outer truss centerplanes (clears pivot pulley at x 70.2..73.8; pod sits on x 85.5..93.5)
CHORD_D = 8.0                     # thick main upper/lower chord tubes
U1_TIE_D = 8.0                    # U1 cross tube carries the highest stress (102 % at 7 mm)
U2_TIE_D = 4.5                    # rear-pod cross tube: slim so it clears the belt (top z 64.8) by >= 0.5 mm
DIAG_D = 6.0                      # Warren diagonals between the plates: they cross the belt corridor, so they stay thin
ROOT_TIE_D = 9.0                  # cross tubes between the plates at the root (pivot end) nodes U0 and L0: they carry the wheel's roll torque
ROOT_TIE_D_LOW = 8.6              # lower root cross tube: kept 1 mm clear of the belt (belt z >= 54.5 at y -139)
STRUT_D = 7.0                     # internal triangulation and cross-brace tubes
BOSS_OD, BOSS_W = 15.0, 7.5
TIP_BORE = 4.3                    # 4 mm tip shaft (D3.9 measured)
CROTCH_R = 3.0                    # radius between the root post and the upper chord's underside (FEM peak there)
PIVOT_OD, PIVOT_BORE = 18.0, 5.4  # heavy pivot boss around 5 mm diff output shaft (matching rear swingarm pivot style, markup 13:40)


def _boss(x0, x1, yz, od):
    return cq.Solid.makeCylinder(od / 2, x1 - x0, cq.Vector(x0, yz[0], yz[1]), cq.Vector(1, 0, 0))


def make_front_arm(sx=1):
    from parts.cage import _Frame
    from parts.stealth_shell import beveled_hull as hull
    F = _Frame()
    P, T = PIVOT_YZ, TIP_YZ
    # Cast-style tapered pivot neck from P (-125.8, 62.8) to vertical root post L0-U0 at y = -139.0 (matching rear swingarm pivot, markup 13:40),
    # rising to U1 at y = -168, then meeting the pod seat (y = -194..-214, z = 69.0) and tapering into the tip boss T.
    U0 = (-139.0, 75.5)   # upper chord root ahead of pivot boss; clears belt z<=69.0
    U1 = (-168.0, 80.5)
    U2 = (-194.0, 67.6)   # rear pod-mount node (directly under pod rear edge y=-193.7, z=72.0; clears belt z<=64.7)
    U3 = (-214.0, 67.6)   # front pod-mount node (directly under pod front edge y=-214.3, z=72.0; clears belt z<=63.1)
    L0 = (-139.0, 49.4)   # lower chord root ahead of pivot boss; clears belt z>=54.5
    L1 = (-168.0, 47.0)   # clears belt z>=53.0
    L2 = (-194.0, 45.5)   # directly below rear pod-mount node; clears belt z>=51.5
    L3 = (-214.0, 45.8)   # directly below front pod-mount node; clears belt z>=50.3

    pt = lambda x, q: (x, round(q[0], 2), round(q[1], 2))
    for x in PLATE_X:
        # Upper chord and lower chord starting from the vertical root post L0-U0 ahead of the pivot neck
        for a, b in ((U0, U1), (U1, U2), (U2, U3),
                     (L0, L1), (L1, L2), (L2, L3)):
            F.tube(pt(x, a), pt(x, b), CHORD_D)
        # Vertical root post L0-U0 behind pivot web + Warren/ladder triangulation under the pod and along the arm
        for a, b in ((L0, U0), (L0, U1), (L1, U1), (L2, U1), (L2, U2), (L3, U2), (L3, U3)):
            F.tube(pt(x, a), pt(x, b), STRUT_D)
        # Solid tapered pivot neck web connecting the cylindrical pivot boss P to the upper and lower chord roots U0, L0 (markup 13:40)
        NW = BOSS_W / 2   # neck as wide as the pivot boss (7.5 mm; was 6 mm): removes the step at the boss and the thin neck the FEM flagged
        F.solids.append(hull([
            (x - NW, P[0], P[1] + 8.0), (x + NW, P[0], P[1] + 8.0),
            (x - NW, P[0], P[1] - 8.0), (x + NW, P[0], P[1] - 8.0),
            (x - NW, U0[0], U0[1] + 3.0), (x + NW, U0[0], U0[1] + 3.0),
            (x - NW, L0[0], L0[1] - 3.0), (x + NW, L0[0], L0[1] - 3.0),
        ]))
        # Solid tapered tip neck web connecting U3, L3 into the front tip boss T (matching rear swingarm hub neck)
        F.solids.append(hull([
            (x - 3.0, U3[0], U3[1] + 2.0), (x + 3.0, U3[0], U3[1] + 2.0),
            (x - 3.0, L3[0], L3[1] - 2.0), (x + 3.0, L3[0], L3[1] - 2.0),
            (x - 3.0, T[0], T[1] + 6.0), (x + 3.0, T[0], T[1] + 6.0),
            (x - 3.0, T[0], T[1] - 6.0), (x + 3.0, T[0], T[1] - 6.0),
        ]))
        F.solids.append(_boss(x - BOSS_W / 2, x + BOSS_W / 2, T, BOSS_OD))

    xi, xo = PLATE_X
    # Low-profile pod-seat pad on the outer upper chord (x 85.5..93.5, y -214.5..-193.5, z 68.5..71.8 just under pod 1)
    # so the front tire G-load transfers directly into the triangulated outer truss nodes U2 and U3 (markup 12:26)
    pod_seat = hull([
        (85.5, U3[0] - 0.5, 68.5), (93.5, U3[0] - 0.5, 68.5),
        (85.5, U2[0] + 0.5, 68.5), (93.5, U2[0] + 0.5, 68.5),
        (85.5, U3[0] - 0.5, 71.8), (93.5, U3[0] - 0.5, 71.8),
        (85.5, U2[0] + 0.5, 71.8), (93.5, U2[0] + 0.5, 71.8),
    ])
    F.solids.append(pod_seat)

    # Heavy pivot barrel on inner plate + outer collar boss (clearing the belt pulley at x 70.2..73.8)
    F.solids.append(_boss(xi - BOSS_W / 2, xi + BOSS_W / 2, P, PIVOT_OD))
    F.holes.append(_boss(xi - 6, xo + 6, P, PIVOT_BORE))
    F.solids.append(_boss(xo - BOSS_W / 2, xo + BOSS_W / 2, P, PIVOT_OD))
    F.holes.append(_boss(xi - 6, xo + 6, T, TIP_BORE))

    # Box-section cross tubes tying inner and outer trusses at the exact truss nodes above AND below the belt
    for node_yz in (U0, U1, U2, U3, L0, L1, L2, L3):
        F.tube(pt(xi, node_yz), pt(xo, node_yz), (ROOT_TIE_D if node_yz == U0 else ROOT_TIE_D_LOW) if node_yz in (U0, L0) else (U2_TIE_D if node_yz == U2 else (U1_TIE_D if node_yz == U1 else STRUT_D)))
    # Non-crossing Warren top and bottom diagonal braces between inner and outer frames for torsional rigidity under G-load
    F.tube(pt(xi, U0), pt(xo, U1), DIAG_D)
    F.tube(pt(xo, U1), pt(xi, (U2[0], U2[1] + 1.0)), DIAG_D)   # inner end lifted 1 mm: clears belt
    F.tube(pt(xi, U2), pt(xo, U3), DIAG_D)
    F.tube(pt(xi, L0), pt(xo, L1), DIAG_D)
    F.tube(pt(xo, L1), pt(xi, L2), DIAG_D)
    F.tube(pt(xi, L2), pt(xo, L3), DIAG_D)

    # Radius in the crotch between the root post L0-U0 (front face) and the underside of the upper chord U0-U1, both plates: the arm FEM peaked there
    # (13.4 MPa, safety 1.50, at a sharp inner edge). OCC cannot fillet the faceted tube junction, so a fillet piece (corner triangle minus a circle
    # tangent to both faces) is fused in, as wide as the chord.
    import math
    yp = U0[0] - 3.08                                   # post front face (D7 octagon), measured
    cb = (U0[0] - 3.53, U0[1] - 2.96)                   # a point on the chord's underside facet, measured
    bd = (U1[0] - U0[0], U1[1] - U0[1]); bl = math.hypot(*bd); bd = (bd[0] / bl, bd[1] / bl)
    C = (yp, cb[1] + (yp - cb[0]) * bd[1] / bd[0])      # corner of the post face and the chord underside
    ad = (0.0, -1.0)
    phi = math.acos(ad[0] * bd[0] + ad[1] * bd[1]) / 2
    bis = ((ad[0] + bd[0]), (ad[1] + bd[1])); bn = math.hypot(*bis); bis = (bis[0] / bn, bis[1] / bn)
    tl = CROTCH_R / math.tan(phi)
    T1 = (C[0] + 0.3, C[1] - tl)                       # on the post face, 0.3 mm into the post
    T2 = (C[0] + bd[0] * tl, C[1] + bd[1] * tl + 0.3)  # on the chord underside, 0.3 mm into the chord
    Ci = (C[0] - bis[0] * 0.6, C[1] - bis[1] * 0.6)    # corner pushed into the material
    M = (C[0] + bis[0] * CROTCH_R / math.sin(phi), C[1] + bis[1] * CROTCH_R / math.sin(phi))
    for x in PLATE_X:
        w = CHORD_D
        fp = cq.Workplane('YZ', origin=(x - w / 2, 0, 0)).polyline([Ci, T1, T2]).close().extrude(w).val()
        fp = fp.cut(cq.Solid.makeCylinder(CROTCH_R, w + 2, cq.Vector(x - w / 2 - 1, M[0], M[1]), cq.Vector(1, 0, 0)))
        F.solids.append(fp)

    arm = F.build()
    assert arm.isValid() and len(arm.Solids()) == 1, 'front arm must be one valid solid, got %d' % len(arm.Solids())
    return arm if sx > 0 else arm.mirror('YZ')


