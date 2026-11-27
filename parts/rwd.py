"""Rear wheel drive only (November 21): the front drive and the centre differential are removed, the motor drives the rear shaft through one spur stage.

Everything is built in the chassis reference frame (world = ref + (0, CHASSIS_Y, CHASSIS_Z)).

- Front arms: they used to pivot on the front differential's output shafts. One fixed 5 mm steel axle now runs through both arms and sits in two printed
  blocks on the front deck (`pivot_block`). The tip shafts are cut back to pivot pins between arm and carrier (they no longer reach the wheel).
- Drive: motor beside the rear shaft, pinion on the motor shaft, spur gear on the front end of the rear shaft (same 12 : 33 diameters as the old crossover
  stage, so the overall ratio stays). The motor plate stands on the deck.
"""
import math
import cadquery as cq
from parts.params import INSERT_M3_D

# stand-ins that only served the front drive or the centre differential (names as in parts/chassis_ref.step)
REMOVE = ['b front pinion shaft', 'b front ring', 'mock fdiff carrier', 'w3 fdc upper', 'diff out 1', 'diff out -1',
          'mock fpulley pivot 1', 'mock fpulley pivot -1', 'mock fbelt 1', 'mock fbelt -1',
          'mock cdiff carrier', 'mock cdiff ring', 'w3 cring hub', 'w3 cdc lower', 'w3 cdc upper',
          'mock xover idler Pa', 'mock xover idler Pb', 'mock xover pin Pa', 'mock xover pin Pb', 'mock xover pinion',
          'w3 motor plate', 'b motor', 'b motor shaft', 'pod 1', 'pod -1']

AXLE_D = 5.0
AXLE_HALF = 86.0                 # the old output shafts ended at x +-86
BLOCK_X = (40.0, 54.5)           # pivot block, inner / outer face (deck edge 54.5, the arm hub starts at x 56.9)
BLOCK_HALF_Y = 7.5
BLOCK_TOP = 7.0                  # above the axle centre
INSERT_DY = BLOCK_HALF_Y - 2.1 - 1.5   # insert pockets (D4.2) 1.5 mm from the block's front and rear faces (was 4.6: 0.8 mm)
TIP_PIN_END = 110.0              # the tip pivot pin ends inside the carrier (the old shaft ran on to the wheel at x 123)

PINION_D, SPUR_D, GEAR_W = 12.0, 33.0, 7.0
MOTOR_D, MOTOR_L = 36.0, 60.0
PLATE_T = 4.0
MESH_SLOT = 1.0                  # motor screw slots +-1 mm along the centre line: the bought 32P 15T / 42T pair meshes at 22.6 mm (model 22.5)


def _name(n):
    return str(getattr(n, 'name', '')).replace('_', ' ')


def _obj(n):
    return n.obj.val() if isinstance(n.obj, cq.Workplane) else n.obj


def _node(ch, name):
    f = [n for n in ch.objects.values() if _name(n) == name]
    assert len(f) == 1, 'chassis node not found: ' + name
    return f[0]


def remove_front_drive(ch):
    """Drop the front-drive and centre-diff stand-ins. Returns the pivot axis (y, z) of the front arms and the rear shaft's front end and direction."""
    b = _obj(_node(ch, 'diff out 1')).BoundingBox()
    pivot = ((b.ymin + b.ymax) / 2, (b.zmin + b.zmax) / 2)
    sh = _obj(_node(ch, 'b rear shaft'))
    sb = sh.BoundingBox()
    ends = []
    for y0 in (sb.ymin, sb.ymax - 2.0):
        c = sh.intersect(cq.Solid.makeBox(200, 2.0, 400, cq.Vector(-100, y0, -200))).Center()
        ends.append(c)
    d = (ends[1] - ends[0]).normalized()
    front = ends[0] - d * 1.0          # slab centre is 1 mm in from the end face
    for nm in REMOVE:
        n = _node(ch, nm)
        n.parent.children.remove(n)
    return pivot, front, d


def front_axle(pivot):
    return cq.Solid.makeCylinder(AXLE_D / 2, 2 * AXLE_HALF, cq.Vector(-AXLE_HALF, pivot[0], pivot[1]), cq.Vector(1, 0, 0))


def pivot_block(sx, pivot, deck):
    """Printed block on the front deck that holds the fixed pivot axle (side sx). It is cut by the deck, so it sits exactly on it; two M3 insert pockets
    (4.2 x 6) open downward for the screws through the deck."""
    x0, x1 = (BLOCK_X[0], BLOCK_X[1]) if sx > 0 else (-BLOCK_X[1], -BLOCK_X[0])
    db = deck.BoundingBox()
    blk = cq.Solid.makeBox(x1 - x0, 2 * BLOCK_HALF_Y, pivot[1] + BLOCK_TOP - db.zmin, cq.Vector(x0, pivot[0] - BLOCK_HALF_Y, db.zmin))
    blk = blk.cut(deck)
    blk = max(blk.Solids(), key=lambda q: q.BoundingBox().zmax)      # the piece above the deck
    blk = blk.cut(cq.Solid.makeCylinder(AXLE_D / 2, 200, cq.Vector(-100, pivot[0], pivot[1]), cq.Vector(1, 0, 0)))
    zb = blk.BoundingBox().zmin
    for xs, ys in screw_xy(sx, pivot):
        blk = blk.cut(cq.Solid.makeCylinder(INSERT_M3_D / 2, 6.0 + 3.0, cq.Vector(xs, ys, zb - 3.0), cq.Vector(0, 0, 1)))
    assert blk.isValid() and len(blk.Solids()) == 1, 'pivot block broke'
    return blk


def screw_xy(sx, pivot):
    xm = sx * (BLOCK_X[0] + BLOCK_X[1]) / 2
    return [(xm, pivot[0] - INSERT_DY), (xm, pivot[0] + INSERT_DY)]


def deck_screw_holes(sx, pivot):
    """3.4 mm through holes in the deck under the pivot block's inserts."""
    return [cq.Solid.makeCylinder(1.7, 400, cq.Vector(xs, ys, -200), cq.Vector(0, 0, 1)) for xs, ys in screw_xy(sx, pivot)]


def tip_pin(shaft, sx):
    """The tip shaft cut back to a pivot pin between arm and carrier."""
    keep = cq.Solid.makeBox(TIP_PIN_END, 400, 400, cq.Vector(0 if sx > 0 else -TIP_PIN_END, -400, -200))
    p = shaft.intersect(keep)
    return max(p.Solids(), key=lambda q: q.Volume())


def drive(front, d):
    """Motor, pinion, spur, plate in a local frame (rear shaft axis = +y through the origin = the shaft's old front end), then moved onto the shaft.
    Returns [(name, solid, colour)]; the plate still has to be cut by the deck."""
    cd = (PINION_D + SPUR_D) / 2           # centre distance, motor on the -x side
    cyl = lambda r, y0, y1, x=0.0: cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, 0), cq.Vector(0, 1, 0))
    y_g1 = -2.0; y_g0 = y_g1 - GEAR_W                      # gear plane
    y_p1 = y_g0 - 3.0; y_p0 = y_p1 - PLATE_T                 # plate behind the gears
    ext = cyl(2.5, y_g0 - 1.0, 0.0)
    spur = cyl(SPUR_D / 2, y_g0, y_g1).cut(cyl(2.5, y_g0 - 1, y_g1 + 1))
    pin = cyl(PINION_D / 2, y_g0, y_g1, -cd).cut(cyl(1.6, y_g0 - 1, y_g1 + 1, -cd))
    msh = cyl(1.6, y_p0 - 0.5, y_g1 + 1.0, -cd)
    motor = cyl(MOTOR_D / 2, y_p0 - MOTOR_L, y_p0, -cd).cut(msh)
    hw, g = MOTOR_D / 2 + 1.5, 10.5        # plate half width at the motor, gusset width
    plate = cq.Solid.makeBox(2 * (hw + g), PLATE_T, 62.0, cq.Vector(-cd - hw - g, y_p0, -40.0))
    for s in (1, -1):                       # a gusset block on each side of the motor, in front of the plate: it stands on the deck and takes one M3 screw
        x0 = -cd + s * hw if s > 0 else -cd - hw - g
        plate = plate.fuse(cq.Solid.makeBox(g, 16.0, 34.0, cq.Vector(x0, y_p0 - 16.0, -40.0)))
    plate = plate.clean()
    slot = lambda r, x: cyl(r, y_p0 - 1, y_p1 + 1, x - MESH_SLOT).fuse(cyl(r, y_p0 - 1, y_p1 + 1, x + MESH_SLOT)).fuse(
        cq.Solid.makeBox(2 * MESH_SLOT, PLATE_T + 2, 2 * r, cq.Vector(x - MESH_SLOT, y_p0 - 1, -r)))
    plate = plate.cut(slot(6.5, -cd))                                                       # pinion boss, slotted with the screws
    for dx in (12.5, -12.5):
        plate = plate.cut(slot(1.6, -cd + dx))                                              # M3 motor screws, 25 mm pattern, slotted +-MESH_SLOT for the gear mesh
    for s in (1, -1):
        plate = plate.cut(cq.Solid.makeCylinder(1.7, 60.0, cq.Vector(-cd + s * (hw + g / 2), y_p0 - 8.0, -50.0), cq.Vector(0, 0, 1)))   # M3 into the deck
    out = [('b rear shaft front', ext, (0.78, 0.80, 0.84)), ('b spur gear', spur, (0.2, 0.2, 0.22)), ('b motor pinion', pin, (0.75, 0.6, 0.2)),
           ('b motor shaft', msh, (0.78, 0.80, 0.84)), ('b motor', motor, (0.25, 0.25, 0.28)), ('w3 motor plate', plate, (0.55, 0.57, 0.60))]
    ang = math.degrees(math.atan2(d.z, d.y))
    return [(n, s.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), ang).translate(front), c) for n, s, c in out]
