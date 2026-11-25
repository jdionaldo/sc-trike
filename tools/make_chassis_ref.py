"""Convert inputs/WS03_chassis_only.glb into named, grouped reference parts (convex hulls) as STEP assemblies.
parts/chassis_ref.step: everything but the rear swingarm group; parts/rear_ref.step: rear swingarm group (rotated in model.py).
Output frame: shell frame at 1:1 (X lateral, Y = -forward, Z up, ground z = 0, original wheel axles)."""
import numpy as np, trimesh, cadquery as cq, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fit_chassis import chassis
HERE = os.path.dirname(os.path.abspath(__file__))
REAR = lambda n: n in ('w3_rear_arm', 'b_rear_shock') or n.startswith('mock_rear_')
def group(n):
    if REAR(n): return 'Rear swingarm'
    if n.startswith(('mock_tire', 'mock_rim', 'mock_hub', 'mock_axle', 'mock_joint')): return 'Wheels'
    if n.startswith(('steer_', 'knuckle_', 'carrier_', 'tie_rod_')): return 'Steering'
    if n.startswith(('arm_', 'pod_', 'uplink_', 'b_lean_shock', 'lean_', 'w3_uplink_standoff')): return 'Suspension'
    if n in ('b_battery', 'b_motor') or n.startswith('w3_motor_plate') or n=='w3_ballast_plate': return 'Electronics and power'
    if n.startswith(('w3_frame', 'w3_deck', 'w3_skid', 'battery_tray', 'w3_ballast')): return 'Frame and decks'
    return 'Drivetrain'
DETAIL = lambda m: False
def solid(m, faces):
    if len(m.faces) > faces:
        m = m.simplify_quadric_decimation(face_count=faces)
        if not DETAIL(m): m = m.convex_hull
    fs = []
    for t in m.faces:
        p = [cq.Vector(*m.vertices[i]) for i in t]
        try: fs.append(cq.Face.makeFromWires(cq.Wire.makePolygon(p, close=True)))
        except Exception: pass
    return cq.Solid.makeSolid(cq.Shell.makeShell(fs))
def solid_detail(m, faces):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopoDS import TopoDS
    from OCP.TopAbs import TopAbs_SHELL
    if len(m.faces) > faces: m = m.simplify_quadric_decimation(face_count=faces)
    sew = BRepBuilderAPI_Sewing(1e-3)
    for t in m.faces:
        p = [cq.Vector(*m.vertices[i]) for i in t]
        try: sew.Add(cq.Face.makeFromWires(cq.Wire.makePolygon(p, close=True)).wrapped)
        except Exception: pass
    sew.Perform()
    sh = cq.Shape.cast(sew.SewedShape()).Shells()[0]
    fx = ShapeFix_Solid(); so = cq.Solid(fx.SolidFromShell(sh.wrapped))
    if so.Volume() < 0: so = cq.Solid(fx.SolidFromShell(sh.wrapped).Reversed())
    return so
def nice(n): return n.replace('_', ' ')
if __name__ == "__main__":
    ch = chassis(1.0)
    ONLY_REAR = os.environ.get('ONLY_REAR') == '1'   # regenerate just parts/rear_ref.step (the other files are left alone)
    top = {'chassis': cq.Assembly(name='Chassis'), 'rear': cq.Assembly(name='Rear swingarm'), 'frame': cq.Assembly(name='Frame (simplified)')}
    subs = {}
    for n, m in sorted(ch.items()):
        if n in ('mock_rear_tire_ring', 'b_rear_shock'): continue   # parametric tire and strut are built in model.py
        if ONLY_REAR and not REAR(n): continue
        m = m.copy(); m.merge_vertices()
        if max(m.extents) < 12: continue
        which = 'rear' if REAR(n) else 'frame' if n in ('w3_frame_front', 'w3_frame_rear') else 'chassis'   # big frame hulls fill in the open frame: shown see-through
        try:
            if len(m.faces) >= 500 and n not in ('w3_frame_front', 'w3_frame_rear') and not n.startswith(('mock_tire', 'mock_rim', 'mock_rear_rim', 'mock_rear_tire')):   # real structure, not a hull
                s = solid(m, 4000) if False else solid_detail(m, 30000)
            else: s = solid(m.convex_hull, 60)
        except Exception as e: print('skip', n, e); continue
        if n == 'w3_rear_arm':
            # The original shock-mount rod on the arm (x 15..66, axis y 210.9 / z 122.4, radius about 10) sits 68 mm from the axle, inside
            # the 140 mm tire. Cut it away; model.py puts the new shock bridge over the tire from the apex node.
            s = s.cut(cq.Solid.makeCylinder(12.5, 50.0, cq.Vector(10, 210.9, 122.4), cq.Vector(1, 0, 0)))
        g = group(n)
        if which == 'chassis':
            if g not in subs: subs[g] = cq.Assembly(name=g)
            subs[g].add(s, name=nice(n))
        elif which == 'frame':
            top['frame'].add(s, name=nice(n))
        else:
            top['rear'].add(s, name=nice(n))
    for sub in subs.values(): top['chassis'].add(sub)   # add after the children are in, nesting copies
    if not ONLY_REAR:
        top['chassis'].save(os.path.join(HERE, '..', 'parts', 'chassis_ref.step'))
        top['frame'].save(os.path.join(HERE, '..', 'parts', 'frame_ref.step'))
    top['rear'].save(os.path.join(HERE, '..', 'parts', 'rear_ref.step'))
    print({k: len(v.children) for k, v in subs.items()}, len(top['rear'].children))
