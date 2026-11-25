"""Roof plate of the open cockpit: a flat printed panel lying on the cage's roof frame (front and rear headers, the two side rails, the roof X).

The four roof corner nodes (A, B and their mirror images, tube centres) lie in one plane that rises to the rear. The plate is a plain slab parallel to
that plane, its outline is the roof frame's outer edge. Its underside lies SEAT_GAP above the highest point of the frame: the level headers' front
corners and the roof X stand up to 0.4 mm proud of the sloping plane through the side rails' top faces, so the plate rests on those and is that much
further above the rails (glue or foam tape fills it). The cage used to be cut out of the plate four times (shifted by the gap): that left rims and
feather edges of 0.3 mm along the outline. Fastening is not designed yet: glue on the tube tops, or screws once the roof tubes get bosses.
"""
import math
import cadquery as cq

PLATE_T = 2.0        # mm: plate thickness
SEAT_GAP = 0.2       # mm: glue gap between the plate and the highest points of the roof frame


def make_roof_plate(A, B, half, cage):
    """A, B: roof front and rear corner nodes on the +x side (tube centres). half: half the tube side. cage: the finished cage solid."""
    V = cq.Vector
    u = V(0, B[1] - A[1], B[2] - A[2]).normalized()            # along the roof, front to rear
    n = V(1, 0, 0).cross(u).normalized()                        # plate normal (up)
    if n.z < 0: n = n * -1.0
    L = math.hypot(B[1] - A[1], B[2] - A[2])
    # outline in the roof plane: local x = world x, local y = along u from A; outer faces of the tubes
    pts = [(-A[0] - half, -half), (A[0] + half, -half), (B[0] + half, L + half), (-B[0] - half, L + half)]
    base = V(0, A[1], A[2]) + n * half        # plane through the side rails' top faces
    wp = lambda o: cq.Workplane(cq.Plane(origin=o, xDir=V(1, 0, 0), normal=n)).polyline(pts).close()
    # how far the frame stands proud of that plane under the plate
    over = cage.intersect(wp(base).extrude(2 * half).val())
    proud = max([(V(v.X, v.Y, v.Z) - base).dot(n) for v in over.Vertices()] + [0.0])
    assert proud < half, 'roof plate: a tube stands %.1f mm above the roof plane' % proud
    plate = wp(base + n * (proud + SEAT_GAP)).extrude(PLATE_T).val()
    assert plate.isValid() and plate.intersect(cage).Volume() < 1e-6, 'roof plate touches the cage'
    print('roof plate: frame up to %.2f mm proud of the rail plane, plate underside %.2f mm above the rails' % (proud, proud + SEAT_GAP))
    return plate
