"""Printable shell only, reconstructed from the supplied trike references."""
from soma import add_part as _register_part, param, import_step, import_assembly
from parts.util import clean_registered

def add_part(name, geometry, **options):
    return _register_part(name, clean_registered(geometry), **options)
from parts.params import *
from parts.shell_geometry import strip_dust, make_shell, make_canopy, make_grille, canopy_seat_tool, grille_seat_tool, checked, split_on_creases

shell=make_shell()
canopy=make_canopy()
grille=make_grille()
shell=strip_dust(shell.cut(canopy_seat_tool(canopy)).cut(grille_seat_tool(grille)).clean())
# The glue seam follows the existing angular panel folds, with a 0.3 mm gap.
front=shell
from parts.tail import make_tail
from parts.util import fuse
rear=fuse(make_tail())
# Intentional glue clearances, with no interpenetration between printed parts.
for name,a,b in [('body seam',front,rear),('front canopy seat',front,canopy),
                 ('rear canopy seat',rear,canopy),('grille seat',front,grille)]:
    assert a.intersect(b).Volume()<0.001, name+' interferes'
    assert a.distance(b)>=GLUE_GAP*0.8, name+' has insufficient assembly clearance'
import math
import cadquery as cq
from parts.relief import relief_tools, rear_lift_angle, rot_yz, PIVOT, REAR_AXLE, FRONT_Y, SHOCK_TOP0, SHOCK_BOT0
_tools = relief_tools()
# Rake: the shell pitches tail-up about the front axle, so the front fenders stay on the tires.
_phi = math.radians(SHELL_PITCH); _c, _s = math.cos(_phi), math.sin(_phi)
_cy, _cz = FRONT_Y + CHASSIS_Y, 55.86 + CHASSIS_Z
_SX, _SZ = SHELL_SCALE, SHELL_SCALE*SHELL_Z
_WX = SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH
_pitch = cq.Matrix([[_WX, 0, 0, 0],
                    [0, _c*_SX, -_s*_SZ, _cy - _c*_cy + _s*_cz],
                    [0, _s*_SX,  _c*_SZ, _cz - _s*_cy - _c*_cz]])
# Round flank scoop behind each front tire (14:09 markup): one circular arch, centre ~48 mm behind the tire axle,
# replaces the ragged notches the suspension travel cuts left on the lower flank. (y, z) centre and radius in mm, final frame.
SCOOP_YZ = (-174.0, 33.4); SCOOP_R = 83.0
# The hood cheek above the tire ties the nose to the body sides, so the scoop stops just above the tire top.
SCOOP_TOP = 55.86 + CHASSIS_Z + 55.86 + TIRE_GAP + 4.0
_scoop = cq.Solid.makeCylinder(SCOOP_R, 140, cq.Vector(60, SCOOP_YZ[0], SCOOP_YZ[1]), cq.Vector(1, 0, 0)).intersect(
    cq.Workplane('XY').box(140, 400, SCOOP_TOP + 100, centered=(False, True, False)).val().translate(cq.Vector(60, SCOOP_YZ[0], -100)))
_fins = [_scoop, _scoop.mirror('YZ')]
# Trim the shell bottom flat along the chassis deck plane (deck top rises from 32.6 mm at y -221 to 59.8 mm at y 160, ground reference).
_zp = lambda y: 32.6 + (y + 221.0)*(59.8 - 32.6)/381.0 + CHASSIS_Z + DECK_TRIM
_deck_trim = cq.Workplane('YZ', origin=(-400, 0, 0)).polyline([(-420, _zp(-420)), (420, _zp(420)), (420, _zp(420) - 400), (-420, _zp(-420) - 400)]).close().extrude(800).val()
_nose_cut = [cq.Solid.makeBox(300, 300, 400, cq.Vector(sx*NOSE_HALF_WIDTH + (0 if sx > 0 else -300), NOSE_END_Y - 300, -100)) for sx in (1, -1)]
def scaled(s, name):
    s = s.transformGeometry(_pitch)
    for t in _tools + _fins + [_deck_trim] + _nose_cut:
        s = s.cut(t)
    s = strip_dust(s.clean(), min_volume=1500.0)   # slivers of rocker edge left by the relief cuts
    return checked(s, name)
_shells = {n: scaled(g, n) for n, g in (('Front shell', front), ('Rear shell', rear), ('Canopy', canopy), ('Grille insert', grille))}
# Closing panel beside the nose (markups 00:10 / 00:11 / 00:33): the fender front ends open at y = NOSE_END_Y. A two-facet arrow
# panel follows the hood lines: top edge along the hood front, a fold running from the outer hood corner to a forward tip, then
# down to the nose bottom beside the grille. It stays inside the tire and suspension envelope (check with tools/collide.py).
FRONT_CAP_T = 5.0
_nose_cap_edges = {}
def _front_cap(sx):
    # Intersect the real hood with its trimming plane: no guessed floating
    # vertices, and the bottom nose corner shares the original nose rake.
    from parts.shell_geometry import point
    def mapped(p):
        x,y,z=point(p)
        return cq.Vector(_WX*x,_c*_SX*y-_s*_SZ*z+_cy-_c*_cy+_s*_cz,
                         _s*_SX*y+_c*_SZ*z+_cz-_s*_cy-_c*_cz)
    nose_top=mapped((sx*24,-139,57))
    nose_bottom=mapped((sx*NOSE_BASE_HALF,-139,25))
    # The original hood is a pair of planar facets. Probe each end of its
    # closing edge before adding either cap.
    shape=_shells['Front shell']
    def hood_z(x):
        line=cq.Edge.makeLine((x,NOSE_END_Y+0.05,80),(x,NOSE_END_Y+0.05,170))
        pts=shape.intersect(line).Vertices()
        assert pts, 'Front cap cannot find the hood edge'
        return max(v.Z for v in pts)
    xo=sx*70.0; xi=sx*(NOSE_HALF_WIDTH-0.4)
    outer=cq.Vector(xo,NOSE_END_Y+0.15,hood_z(xo))
    inner=cq.Vector(xi,NOSE_END_Y+0.15,hood_z(xi))
    # Broad second facet follows the lower cheek edge instead of ending in a
    # long triangle from the hood corner to a floating lower point.
    lower=cq.Vector(sx*57.0,NOSE_END_Y+0.15,97.3)
    _nose_cap_edges[sx]=(nose_top,outer)
    facets=[(outer,inner,nose_top),(outer,nose_top,lower),(lower,nose_top,nose_bottom)]
    from parts.panels import panel_prisms
    cap=_hull_union(panel_prisms([[p.toTuple() for p in tri] for tri in facets],(-sx,1,0),FRONT_CAP_T))
    # Clip the mitred return to the real hood plane: its inward offset must
    # not project upward as a raised strip along the closing-panel edge.
    normal=(inner-outer).cross(nose_top-outer).normalized()
    if normal.z<0: normal=-normal
    plane=cq.Plane(origin=outer,xDir=(inner-outer).normalized(),normal=normal)
    below=cq.Workplane(plane).rect(1000,1000).extrude(-500).val()
    return cap.intersect(below).clean()
def _hull_union(solids):
    from parts.util import fuse
    return fuse(solids)
def _hull_pts(pts):
    from parts.util import hull
    return hull([p.toTuple() for p in pts])
_fs = _shells['Front shell']
for _sx in (1, -1):
    _fs = _fs.fuse(_front_cap(_sx))
_fs = _fs.clean()
_shells['Front shell'] = checked(_fs, 'Front shell')

# The canopy ends at the B-pillar. Its former rear roof-window cut is obsolete.
# Light strips: separate printed red parts that sit in channels cut into the shell, pegs (5 mm, 3 mm LED bore) pass through the wall.
from parts.light_strips import make_tail_strip, make_nose_strip, nose_backing, STRIP_FIT, NOSE_SOCKET_CUTTERS
_tail_strip, _tail_chan = make_tail_strip()
_nose_strip, _nose_chan = make_nose_strip(_nose_cap_edges)
_shells['Rear shell'] = checked(_shells['Rear shell'].cut(_tail_chan).clean(), 'Rear shell')
# The opaque backing must stay inside the hood skin: cut away everything above the hood plane of each half.
def _hood_top(x,y):
    pts=_shells['Front shell'].intersect(cq.Edge.makeLine((x,y,60),(x,y,200))).Vertices()
    return max(v.Z for v in pts)
_backing=nose_backing()
for _sx in (1,-1):
    _p=[cq.Vector(_sx*x,y,_hood_top(_sx*x,y)) for x,y in ((28,-302),(28,-286),(4,-294))]
    _n=(_p[1]-_p[0]).cross(_p[2]-_p[0]).normalized()
    if _n.z<0:_n=-_n
    _above=cq.Workplane(cq.Plane(origin=_p[0]-_n*0.3,normal=_n.toTuple())).rect(400,400).extrude(100).val()
    _half=cq.Solid.makeBox(60,60,200,cq.Vector(0 if _sx>0 else -60,-330,40))
    _backing=_backing.cut(_above.intersect(_half))
_front_cut=_shells['Front shell'].fuse(_backing).cut(_nose_chan,tol=1e-4)
for _socket_cut in NOSE_SOCKET_CUTTERS:
    _front_cut=_front_cut.cut(_socket_cut,tol=1e-4)
_big=[x for x in _front_cut.Solids() if x.Volume()>1.0]   # zero-volume slivers left where the lens channel meets the nose edge
_front_cut=_big[0] if len(_big)==1 else cq.Compound.makeCompound(_big)
_shells['Front shell']=checked(strip_dust(_front_cut.clean(),min_volume=0.001).fix(),'Front shell')
from parts.util import weld
_shells['Front shell']=weld(_shells['Front shell'],'Hood and front shell')
assert _shells['Front shell'].intersect(_nose_strip).Volume()<0.001, 'Nose lens interferes with shell'
# Trim the stray lump ahead of each A-pillar foot: nothing of the hood corner stands above z 128.8 there.
_v0=_shells['Front shell'].Volume()
for _sx in (1,-1):
    _lump=cq.Solid.makeBox(9.5,8.0,12.0,cq.Vector(80.5 if _sx>0 else -90.0,-220.0,128.8))
    _shells['Front shell']=_shells['Front shell'].cut(_lump).clean()
_shells['Front shell']=checked(strip_dust(_shells['Front shell'],min_volume=0.001).fix(),'Front shell')
print('A-pillar foot lump removed, mm3:',round(_v0-_shells['Front shell'].Volume(),1))
assert _v0-_shells['Front shell'].Volume()<600,'foot trim cut too much hood'
# One flat hood panel per side: lift the fender facet onto the hood plane with a thin wedge, so hood and fender top become a single face.
def _top_face(shape, x, y):
    c=cq.Vertex.makeVertex(x,y,max(v.Z for v in shape.intersect(cq.Edge.makeLine((x,y,60),(x,y,200))).Vertices()))
    return min((f for f in shape.Faces() if f.normalAt(cq.Vector(x,y,c.Z)).z>0.5 if True),key=lambda f:f.distance(c))
_v1=_shells['Front shell'].Volume()
for _sx in (1,-1):
    _hood=_top_face(_shells['Front shell'],_sx*25.0,-271.0)
    _fender=_top_face(_shells['Front shell'],_sx*48.7,-269.0)
    _hv=[cq.Vector(*v.toTuple()) for v in _hood.Vertices()]
    _n=(_hv[1]-_hv[0]).cross(_hv[2]-_hv[0]).normalized()
    if _n.z<0:_n=-_n
    _proj=lambda p:p+cq.Vector(0,0,-((p-_hv[0]).dot(_n))/_n.z)
    _fv=[q for q in (cq.Vector(*v.toTuple()) for v in _fender.Vertices()) if abs(q.x)>39.0 and q.y>-297.0]
    # Every near-coplanar top facet beside this hood plane (fender, nose-end hood piece, cap top) joins the plate.
    _near=[]
    for _f in _shells['Front shell'].Faces():
        _c=_f.Center()
        if _c.x*_sx<=0 or abs(_c.x)>80 or not (-306.0<_c.y<-245.0): continue
        if _f.normalAt(_c).dot(_n)<0.985: continue
        _fvv=[cq.Vector(*v.toTuple()) for v in _f.Vertices()]
        if all(-1.2<=(q-_hv[0]).dot(_n)<=0.15 for q in _fvv): _near.extend(q for q in _fvv if q.y>-306.0 and (abs(q.x)>34.0 or q.y>-297.0 or abs(q.x)<1.0))
    _top=[_proj(q) for q in _fv]+[_proj(q) for q in _hv]+[_proj(q) for q in _near]
    # Plate on the hood plane, 1.5 mm deep inside the wall: top face is one plane covering hood and fender facet.
    _pts=_top+[p-_n*1.5 for p in _top]
    from parts.util import hull as _h
    _wedge=_h([p.toTuple() for p in _pts])
    # Keep the plate behind the raked nose face (no wall sticking out of the nose), and shave anything that crosses above the hood plane.
    from parts.light_strips import _plane as _face_plane, NOSE_TOP as _NT, NOSE_BOT as _NB
    _fp,_fn=_face_plane(_NT,_NB,(0,-1,-0.3))
    _behind=cq.Workplane(_fp).rect(600,600).extrude(-300).val()
    _wedge=_wedge.intersect(_behind)
    _above=_h([p.toTuple() for p in _top+[p+_n*3.0 for p in _top]]).intersect(_behind)
    _shells['Front shell']=_shells['Front shell'].fuse(_wedge).cut(_above).clean()
_shells['Front shell']=checked(strip_dust(_shells['Front shell'],min_volume=0.001).fix(),'Front shell')
def _unify_flat(shape,name,volume_tol=0.005):
    """Merge faces that lie in one plane (also B-spline faces that are numerically planar) across the whole part.
    Loosest tolerance first; accepted only if valid, one solid and the volume moves by under 0.5 %."""
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    for lt,at in ((0.1,0.015),(0.05,0.01),(0.02,0.005),(1e-3,1e-3)):
        u=ShapeUpgrade_UnifySameDomain(shape.wrapped,True,True,True); u.SetLinearTolerance(lt); u.SetAngularTolerance(at); u.Build()
        g=cq.Shape.cast(u.Shape()).fix()
        ok=g.isValid() and len(g.Solids())==1 and abs(g.Volume()-shape.Volume())<volume_tol*shape.Volume()
        print(name,'flat-face merge tol',lt,len(shape.Faces()),'->',len(g.Faces()),'valid',g.isValid(),'solids',len(g.Solids()),'dvol',round(g.Volume()-shape.Volume(),1),'accepted' if ok else 'rejected')
        if ok: return g
    return shape
_shells['Front shell']=_unify_flat(_shells['Front shell'],'Front shell')
print('hood/fender wedge added, mm3, face verts:',len(_fv),'; ',round(_shells['Front shell'].Volume()-_v1,1))
assert _shells['Front shell'].Volume()-_v1<1400,'hood/fender wedge too large'
add_part('Front shell',_shells['Front shell'],color=BODY,group='Print shell')
assert _shells['Rear shell'].intersect(_tail_strip).Volume()<0.001, 'Tail lens interferes with housing'
assert _shells['Rear shell'].distance(_tail_strip)>=STRIP_FIT*0.8, 'Tail lens clearance is too small'
add_part('Tail light housing',_shells['Rear shell'],color=BODY,group='Print shell')
_shells['Canopy']=_unify_flat(_shells['Canopy'],'Canopy')
add_part('Canopy',_shells['Canopy'],color=ROOF,group='Print shell')
add_part('Grille insert',_shells['Grille insert'],color=(0.06,0.06,0.07),group='Print shell')
add_part('Tail light strip',_tail_strip,color=(0.85,0.05,0.05),alpha=1,group='Lights')
_nose_strip=_unify_flat(_nose_strip,'Nose light strip')
add_part('Nose light strip',_nose_strip,color=(0.85,0.05,0.05),alpha=1,group='Lights')

# Chassis and components, imported from inputs/WS03_chassis_only.glb as named parts grouped by function
# (tools/make_chassis_ref.py: each component as a light convex-hull stand-in, standard 1:10 size, reference only).
_off = cq.Vector(0, CHASSIS_Y, CHASSIS_Z)
_ch = import_assembly('parts/chassis_ref.step')
_ch.loc = cq.Location(_off)
add_part('Chassis', _ch, role='hardware', alpha=1, color=(0.55, 0.57, 0.60))
# Rear swingarm group rotates about its pivot to carry the bigger rear tire; the axle rises with the tire radius.
_th = rear_lift_angle()
_ry = PIVOT[0]*math.cos(_th) - PIVOT[1]*math.sin(_th); _rz = PIVOT[0]*math.sin(_th) + PIVOT[1]*math.cos(_th)
_rr = import_assembly('parts/rear_ref.step')
_rr.loc = cq.Location(cq.Vector(0, PIVOT[0]-_ry+CHASSIS_Y, PIVOT[1]-_rz+CHASSIS_Z), cq.Vector(1, 0, 0), math.degrees(_th))
add_part('Rear swingarm', _rr, role='hardware', alpha=1, color=(0.55, 0.57, 0.60))
_ay = PIVOT[0] + (REAR_AXLE[0]-PIVOT[0])*math.cos(_th) - (REAR_AXLE[1]-PIVOT[1])*math.sin(_th)
_az = PIVOT[1] + (REAR_AXLE[0]-PIVOT[0])*math.sin(_th) + (REAR_AXLE[1]-PIVOT[1])*math.cos(_th)
_tire = cq.Solid.makeCylinder(REAR_TIRE_OD/2, 62, cq.Vector(-31, _ay, _az), cq.Vector(1, 0, 0)).translate(_off)
add_part('Rear tire', _tire, role='hardware', group='Chassis', alpha=1, color=(0.10, 0.10, 0.11))
# Rear suspension. The original shock mount rod over the tire was cut from the arm (it sat inside the 140 mm tire, tools/make_chassis_ref.py).
# The shock now stands on the wheel centre plane (x = 0): lower eye on a printed bridge that hooks over the tire from the arm apex node,
# upper eye on the pin nodes of the cage tube frame. Eyes in the final frame at ride height.
from parts.relief import BRIDGE_ARM
_eb = cq.Vector(0.0, rot_yz(SHOCK_BOT0, _th)[1], rot_yz(SHOCK_BOT0, _th)[2]) + _off                 # lower eye (on the bridge pin)
_et = cq.Vector(SHOCK_TOP0[0], SHOCK_TOP0[1], SHOCK_TOP0[2] + REAR_SHOCK_RISE) + _off               # upper eye (tower pin)
_u = (_et - _eb).normalized(); _L = (_et - _eb).Length
def _cyl(r, ln, p, d): return cq.Solid.makeCylinder(r, ln, p, d)
_X = cq.Vector(1, 0, 0)
def _eye(c): return _cyl(7.0, 8.0, c - _X*4.0, _X).cut(_cyl(3.2, 10.0, c - _X*5.0, _X))   # eye ring OD 14, bore for an M6 pin
_shock = _cyl(11.0, 0.45*_L - 9.0, _eb + _u*9.0, _u).fuse(_cyl(2.5, 0.55*_L - 5.5, _eb + _u*(0.45*_L), _u))
_shock=_shock.fuse(_cyl(3.5,4.0,_eb+_u*5.5,_u)).fuse(_eye(_eb)).fuse(_eye(_et))
for _eye_centre in (_eb,_et):
    _shock=_shock.cut(_cyl(3.2,24.0,_eye_centre-_X*12.0,_X))
_shock=_shock.clean()
assert _shock.isValid() and len(_shock.Solids())==1, 'Shock eyelets must join the strut'
add_part('Rear shock (100 mm class)', _shock, role='hardware', group='Chassis', alpha=1, color=(0.80, 0.15, 0.12))
# Shock bridge: tube D 14 from the apex node up and across over the tire, ending in the pin the shock eye sits on (PETG, FEM check pending).
_BR = 7.0
_a0 = cq.Vector(BRIDGE_ARM[0][0], *rot_yz(BRIDGE_ARM[0], _th)[1:]) + _off
_a1 = cq.Vector(BRIDGE_ARM[1][0], *rot_yz(BRIDGE_ARM[1], _th)[1:]) + _off
_a2 = cq.Vector(BRIDGE_ARM[2][0], *rot_yz(BRIDGE_ARM[2], _th)[1:]) + _off
def _tube(p, q, r):
    v = q - p
    return _cyl(r, v.Length, p, v).fuse(cq.Solid.makeSphere(r, p, angleDegrees1=-90, angleDegrees2=90)).fuse(cq.Solid.makeSphere(r, q, angleDegrees1=-90, angleDegrees2=90))
_a2m = cq.Vector(12.5, _a2.y, _a2.z)   # main tube ends clear of the shock body, a pin (the M6 bolt) carries the eye
_bridge = _tube(_a0, _a1, _BR).fuse(_tube(_a1, _a2m, _BR)).fuse(_cyl(3.0, 12.5 + 8.0, _a2, _X))
# Saddle: the bridge sits on the arm's upper tube (circled spot, markup 00:30), held by two zip ties; the tube top is at z ~106.5 in the arm frame.
_bridge = _bridge.clean()
add_part('Rear shock bridge', _bridge, color=(0.20, 0.45, 0.85), group='Rear suspension')
# No separate tower: the shock top pin is carried by the tube frame (parts/cage.py), two pin nodes tied and braced into the rear of the cage.
_pin = _cyl(3.0, 28.0, _et - _X*14.0, _X)   # M6 bolt through both cage pin nodes and the shock eye
add_part('M6 shock pin (hardware)', _pin, role='hardware', group='Rear suspension', alpha=1, color=(0.75, 0.75, 0.78))
# Magnetic power connection for the lights, built into the cage (front and rear, on the centre line, above all the componentry).
from parts.light_contacts import make_connector, roof_underside, LIGHT_FRONT_Y, LIGHT_REAR_Y
from parts.cage import make_cage, belt_profile
_belt = belt_profile([_shells['Front shell'], _shells['Rear shell']], LIGHT_FRONT_Y, max(LIGHT_REAR_Y,20.0))
print('cage belt line vertices (y, z):', [(y, round(z, 1)) for y, z in _belt])
# Frame nodes of the shell (A pillar, B pillar, roof, rear quarter) in the final frame, from the same trace the canopy is built from.
from parts.reference_trace import ROOF, WINDOW_BELT, traced, belt_station
from parts.shell_geometry import point as _pt
def _final(p):
    c = cq.Solid.makeSphere(0.05, cq.Vector(*p)).transformGeometry(_pitch).Center()
    return (round(c.x, 1), round(c.y, 1), round(c.z, 1))   # rounded: coincident float noise makes the tube booleans invalid
_nodes = {k: _final(_pt(traced(p, 1))) for k, p in {'belt0': WINDOW_BELT[0], 'roof0': ROOF[0], 'roof1': ROOF[1], 'roof2': ROOF[2], 'roofN': ROOF[-1],
                                                    'belt930': belt_station(930)}.items()}
# Underside of the rear shell hump above the rear tire at the support stations (6 mm clear of the skin)
from parts.cage import REAR_SUP_X
_sup = []
from parts.tail import light_face,TUBE_END_SETBACK
from parts.cage import CAGE_BEAM
_tail_top,_ = light_face()
_tail_node=(REAR_SUP_X,round(_tail_top[1]-TUBE_END_SETBACK,1),round(_tail_top[2]-WALL_PRINT-CAGE_BEAM/2-GLUE_GAP,1))
print('cage nodes', {k: tuple(round(v, 1) for v in p) for k, p in _nodes.items()}, 'supports', _sup)
_cage, _, _ = make_cage(LIGHT_FRONT_Y, LIGHT_REAR_Y, _belt, _nodes, _sup, tie=(_et.y, _et.z),tail=_tail_node)
from parts.cage import FRONT_LEG_X, REAR_LEG_X, FRONT_FOOT_Z, CAGE_Z, CAGE_BEAM
assert _cage.isValid() and len(_cage.Solids()) == 1, 'cage: expected one valid solid'
add_part('Cage', _cage, color=(0.05, 0.05, 0.06), group='Cage')   # matt black so it disappears behind the shell windows
for _n, (_y, _sh) in {'Front': (LIGHT_FRONT_Y, _shells['Front shell']), 'Rear': (LIGHT_REAR_Y, _shells['Canopy'])}.items():
    _rz = roof_underside(_sh, _y, 90.0)
    _, _block, _zd = make_connector(_y, _rz, _n, FRONT_LEG_X if _n == 'Front' else REAR_LEG_X, 0.0, legs=False,roof=_sh)
    add_part(_n + ' light contact block', _block, color=(0.05, 0.05, 0.06), group='Cage/Light connectors')
