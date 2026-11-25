"""Chamfered square tubing for printed links (tie rod, front upper link). Printed lying down in PETG, so the wall is a multiple of the 0.4 mm line width."""
import cadquery as cq


def square_tube(p0, p1, side=8.0, wall=1.6, chamfer=1.2):
    """Hollow square tube between two points (mm), flats aligned with the horizontal and the vertical plane through the axis; the four long outer edges are chamfered."""
    p0, p1 = cq.Vector(*p0), cq.Vector(*p1)
    ax = p1 - p0
    L = ax.Length
    ax = ax.normalized()
    xd = ax.cross(cq.Vector(0, 0, 1)).normalized()
    outer = cq.Workplane('XY').box(side, side, L, centered=(True, True, False)).edges('|Z').chamfer(chamfer)
    inner = cq.Workplane('XY').box(side - 2 * wall, side - 2 * wall, L + 2, centered=(True, True, False)).translate((0, 0, -1))
    t = outer.cut(inner).val()
    t = t.moved(cq.Location(cq.Plane(origin=p0.toTuple(), xDir=xd.toTuple(), normal=ax.toTuple())))
    assert t.isValid() and len(t.Solids()) == 1
    return t


def square_bar(p0, p1, side=8.0, chamfer=1.2):
    """Solid bar with the same outer shape as square_tube (the solid ends of a link)."""
    p0, p1 = cq.Vector(*p0), cq.Vector(*p1)
    ax = p1 - p0
    L = ax.Length
    ax = ax.normalized()
    xd = ax.cross(cq.Vector(0, 0, 1)).normalized()
    b = cq.Workplane('XY').box(side, side, L, centered=(True, True, False)).edges('|Z').chamfer(chamfer).val()
    return b.moved(cq.Location(cq.Plane(origin=p0.toTuple(), xDir=xd.toTuple(), normal=ax.toTuple())))
