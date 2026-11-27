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
# Master Surface Workflow: verify the outer body forms a single unified, watertight faceted master solid before splitting into panels.
_master_body=shell.fuse(canopy).clean()
assert _master_body.isValid() and len(_master_body.Solids())==1, 'Master outer body must be a single unified watertight solid'
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
    assert a.distance(b)>=PANEL_GAP_M*0.8, name+' has insufficient assembly clearance'
import math
import cadquery as cq
from parts.relief import relief_tools, wishbone_relief_tools, rear_lift_angle, rot_yz, PIVOT, REAR_AXLE, FRONT_Y, SHOCK_TOP0, SHOCK_BOT0
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
SCOOP_YZ = (-170.0, 33.4); SCOOP_R = 91.0; SCOOP_X0 = 56.5   # X0 and R cover every suspension/servo clearance cut through the flank (they start at x 56.9 and reach 94 mm from the old centre), so the arch edge is one clean arc
# The hood cheek above the tire ties the nose to the body sides, so the scoop stops just above the tire top.
SCOOP_TOP = 55.86 + CHASSIS_Z + 55.86 + TIRE_GAP + 4.0
_scoop = cq.Solid.makeCylinder(SCOOP_R, 140, cq.Vector(SCOOP_X0, SCOOP_YZ[0], SCOOP_YZ[1]), cq.Vector(1, 0, 0)).intersect(
    cq.Workplane('XY').box(140, 400, SCOOP_TOP + 100, centered=(False, True, False)).val().translate(cq.Vector(SCOOP_X0, SCOOP_YZ[0], -100)))
_fins = [_scoop, _scoop.mirror('YZ')]
# Trim the shell bottom flat along the chassis deck plane (deck top rises from 32.6 mm at y -221 to 59.8 mm at y 160, ground reference).
_zp = lambda y: DECK_REF_Z0 + DECK_SLOPE*(y - CHASSIS_Y + 189.0) + CHASSIS_Z + DECK_TRIM   # the deck top plane (DECK_TRIM 0), -6.06 = its underside
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
FRONT_CAP_T = WALL_PRINT   # same printed wall as the rest of the shell (was 5 mm, the thickest panel on the part)
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
    # Broad second facet follows the lower cheek edge and lies exactly in the plane of (outer, nose_top, nose_bottom).
    _np=(outer-nose_top).cross(nose_bottom-nose_top)
    _ly=NOSE_END_Y+0.15; _lz=97.3
    _lx=nose_top.x-(_np.y*(_ly-nose_top.y)+_np.z*(_lz-nose_top.z))/_np.x
    lower=cq.Vector(_lx,_ly,_lz)
    _nose_cap_edges[sx]=(nose_top,outer)
    facets=[(outer,inner,nose_top),(outer,nose_top,lower),(lower,nose_top,nose_bottom)]
    from parts.panels import panel_prisms
    cap=_hull_union(panel_prisms([[p.toTuple() for p in tri] for tri in facets],(-sx,1,0),FRONT_CAP_T,final_frame=True))
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
_nose_strip, _nose_chan = make_nose_strip(_shells['Front shell'])
_shells['Rear shell'] = checked(_shells['Rear shell'].cut(_tail_chan).clean(), 'Rear shell')
# Tail housing screws (2 x M3 countersunk, behind the red lens): boss on the inside of the wall, hole + countersink through the seat floor.
from parts.light_strips import make_tail_screws, TAIL_SCREW_INFO
_tail_scr = make_tail_screws()
_rs = _shells['Rear shell']
for _pad in _tail_scr['pads']: _rs = _rs.fuse(_pad)
_rs = _rs.clean()
for _cut in _tail_scr['cuts']: _rs = _rs.cut(_cut)
_shells['Rear shell'] = checked(_rs.clean(), 'Rear shell')
assert len(_shells['Rear shell'].Solids())==1, 'tail screw bosses must stay one solid with the housing'
print('tail screws: M3 countersunk, axial length to insert bottom', {k: v['screw_axial_to_insert_bottom'] for k, v in TAIL_SCREW_INFO.items()}, 'tilt deg', TAIL_SCREW_INFO[1]['tilt_deg'])
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
# Wing ends of the nose strip: close the open end faces with a short backing block, so no red end shows from inside the cabin.
from parts.util import hull as _hull
_end_blocks=[]
for _f in _nose_strip.Faces():
    if _f.geomType()!='PLANE': continue
    _c=_f.Center(); _nn=_f.normalAt(_c)
    if abs(_c.x)>50 and _c.y>-256 and _nn.y>0.7 and _nn.dot(cq.Vector(0.49*(1 if _c.x>0 else -1),0.87,0))>0.95:
        _vs=[v.Center() for v in _f.Vertices()]
        _pts=[(q+_nn*0.15).toTuple() for q in _vs]+[(q+_nn*(3.0+0.15)).toTuple() for q in _vs]
        _end_blocks.append(_hull(_pts))
print('nose strip end faces closed:',len(_end_blocks))
import os as _os
if _end_blocks and _os.environ.get('FUGU_LEGACY_NOSE_PATCH'):
    _fs2=_shells['Front shell'].fuse(*_end_blocks).clean()
    assert len(_fs2.Solids())==1 and _fs2.isValid(),'wing end backing broke the shell'
    _shells['Front shell']=_fs2
# Cover every flat strip face that looks into the cabin with a 2 mm backing, so no red strip shows from inside (0.15 mm clearance).
_cover_n = 0
for _f in (_nose_strip.Faces() if _os.environ.get('FUGU_LEGACY_NOSE_PATCH') else []):
    if _f.geomType() != 'PLANE' or _f.Area() < 30.0: continue
    _c = _f.Center(); _nn = _f.normalAt(_c)
    if _nn.y < -0.3 or _nn.z > 0.3: continue                    # forward-facing lens stays visible; upward faces sit under the hood skin
    _vs = [v.Center() for v in _f.Vertices()]
    _blk = _hull([(q + _nn*0.15).toTuple() for q in _vs] + [(q + _nn*2.15).toTuple() for q in _vs])
    for _cut in list(NOSE_SOCKET_CUTTERS) + [_nose_strip]:
        _blk = _blk.cut(_cut)
    try:
        _fs3 = _shells['Front shell'].fuse(_blk).clean()
        if len(_fs3.Solids()) == 1 and _fs3.isValid() and _fs3.intersect(_nose_strip).Volume() < 0.001:
            _shells['Front shell'] = _fs3; _cover_n += 1
    except Exception:
        pass
print('nose strip inner faces covered:', _cover_n)
assert _shells['Front shell'].intersect(_nose_strip).Volume()<0.001, 'Nose lens interferes with shell'
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
    _pre=_shells['Front shell'].fuse(_wedge)
    _shells['Front shell']=_pre.cut(_above).clean()
    print('hood plane cut side',_sx,'removed mm3',round(_pre.Volume()-_shells['Front shell'].Volume(),1),'cutter vol',round(_above.Volume(),1))
    # Convex crease hood-front/cowl: the surface is the lower of the two planes. The front plane stands up to ~1.1 mm proud
    # of the cowl plane just ahead of the cowl edge (step wall). Shave everything above the cowl plane in that strip.
    _cowl=_top_face(_shells['Front shell'],_sx*25.0,-240.0)
    _cv=[cq.Vector(*v.toTuple()) for v in _cowl.Vertices()]
    _cn=(_cv[1]-_cv[0]).cross(_cv[2]-_cv[0]).normalized()
    if _cn.z<0:_cn=-_cn
    _cpl=cq.Plane(origin=(_cv[0]+_cn*0.0).toTuple(),normal=_cn.toTuple())
    _slab=cq.Workplane(_cpl).rect(1000,1000).extrude(4.0).val()
    _strip=cq.Solid.makeBox(75,16,80,cq.Vector(0.0 if _sx>0 else -75.0,-262.0,90.0))
    _cutc=_slab.intersect(_strip)
    # Keep the skin (1.5 mm) over the nose light strip: shaving it away would expose the strip from inside.
    _keep=cq.Compound.makeCompound([_nose_strip.translate(cq.Vector(0,0,_dz)) for _dz in (0.0,0.5,1.0,1.5)])
    _cutc=_cutc.cut(_keep)
    _pre=_shells['Front shell']; _shells['Front shell']=_pre.cut(_cutc).clean()
    print('cowl step shaved side',_sx,'mm3',round(_pre.Volume()-_shells['Front shell'].Volume(),1))
_shells['Front shell']=checked(strip_dust(_shells['Front shell'],min_volume=0.001).fix(),'Front shell')
def _unify_flat(shape,name,volume_tol=0.005,max_tol=1.0):
    """Merge faces that lie in one plane (also B-spline faces that are numerically planar) across the whole part.
    Loosest tolerance first; accepted only if valid, one solid and the volume moves by under 0.5 %."""
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    for lt,at in ((0.1,0.015),(0.05,0.01),(0.02,0.005),(0.01,0.003),(0.005,0.002),(1e-3,1e-3)):
        if lt>max_tol: continue   # max_tol: skip the looser merges (they can move a face by that much)
        u=ShapeUpgrade_UnifySameDomain(shape.wrapped,True,True,True); u.SetLinearTolerance(lt); u.SetAngularTolerance(at); u.Build()
        g=cq.Shape.cast(u.Shape()).fix()
        ok=g.isValid() and len(g.Solids())==1 and abs(g.Volume()-shape.Volume())<volume_tol*shape.Volume()
        print(name,'flat-face merge tol',lt,len(shape.Faces()),'->',len(g.Faces()),'valid',g.isValid(),'solids',len(g.Solids()),'dvol',round(g.Volume()-shape.Volume(),1),'accepted' if ok else 'rejected')
        if ok: return g
    return shape
_shells['Front shell']=_unify_flat(_shells['Front shell'],'Front shell',volume_tol=0.001)
print('hood/fender wedge added, mm3, face verts:',len(_fv),'; ',round(_shells['Front shell'].Volume()-_v1,1))
# Cowl-edge groove (markup 15:45): a narrow V slot (wall + ramp facet, about 0.7 mm deep, 30 mm long) runs along the outer cowl edge
# from the A-pillar foot to y = -242. Fill it up to the cowl plane (2 mm slab under the plane, over the slot footprint), stopping
# short of the canopy pocket at the foot (y < -216).
def _fill_cowl_groove(shell):
    import numpy as _np
    from scipy.spatial import ConvexHull as _CH
    _done={}; _failed=[]
    for _sx in (1,-1):
        _cowl=max((f for f in shell.Faces() if f.normalAt(f.Center()).z>0.97 and f.Area()>1000 and f.Center().x*_sx>0),key=lambda f:f.Area())
        _c0=_cowl.Center(); _cn=_cowl.normalAt(_c0)
        _x0,_x1=sorted((_sx*74.0,_sx*82.0))
        _probe=cq.Solid.makeBox(_x1-_x0,20,3.5,cq.Vector(_x0,-236,128.5))
        _sel=[f for f in shell.Faces() if _probe.isInside(f.Center()) and 20<f.Area()<200]
        if len(_sel)!=2: print('cowl groove side',_sx,'not found (%d faces), skipped'%len(_sel)); continue
        _P=_np.array([[v.X,v.Y] for f in _sel for v in f.Vertices()]); _P=_P[_P[:,1]>-243.5]
        _poly=[tuple(map(float,_P[i])) for i in _CH(_P).vertices]
        _prism=cq.Workplane('XY').workplane(offset=100).polyline(_poly).close().extrude(80).val()
        # The slab depth and a fuzzy fuse are retried: an exact fuse fails when the slab's underside lands on an inner facet.
        _new=None
        for _depth,_tol in ((2.0,None),(2.0,1e-3),(2.4,1e-3),(1.6,1e-3)):
            _slab=cq.Workplane(cq.Plane(origin=_c0.toTuple(),normal=_cn.toTuple())).rect(600,600).extrude(-_depth).val()
            _fill=_prism.intersect(_slab).intersect(cq.Solid.makeBox(200,40,200,cq.Vector(-100,-256,0)))
            _try=(shell.fuse(_fill) if _tol is None else shell.fuse(_fill,tol=_tol)).clean()
            if _try.isValid() and len(_try.Solids())==1 and _try.Volume()>shell.Volume():
                _new=_try; break
        if _new is None:
            _failed.append(_sx); continue
        print('cowl groove filled side',_sx,'mm3',round(_new.Volume()-shell.Volume(),1))
        shell=_new; _done[_sx]=_fill
    # The shell is symmetric: a side whose own fill would not fuse takes the mirrored fill of the other side.
    for _sx in _failed:
        _new=None
        if -_sx in _done:
            for _tol in (None,1e-3,5e-3):
                _m=_done[-_sx].mirror('YZ')
                _try=(shell.fuse(_m) if _tol is None else shell.fuse(_m,tol=_tol)).clean()
                if _try.isValid() and len(_try.Solids())==1 and _try.Volume()>shell.Volume():
                    _new=_try; break
        if _new is None:
            print('cowl groove side',_sx,'fill would not join the shell (groove geometry changed), skipped'); continue
        print('cowl groove filled side',_sx,'with the mirrored fill, mm3',round(_new.Volume()-shell.Volume(),1))
        shell=_new
    return shell
assert _shells['Front shell'].Volume()-_v1<1400,'hood/fender wedge too large'
_shells['Front shell']=_fill_cowl_groove(_shells['Front shell'])
# The Front shell is symmetric by design, but the patches above act on each side on their own and do not always land the same
# way (the cowl groove fill joined on one side only). Rebuild it from one half and its mirror image; keep the half with the
# larger volume (the filled one). Accepted only if it is one valid solid within 0.5 % of the volume before.
def _symmetric(shell,name,pick=lambda h:h.Volume()):
    _halves=[]
    for _sx in (1,-1):
        _box=cq.Solid.makeBox(600,1200,800,cq.Vector(0 if _sx>0 else -600,-600,-200))
        _halves.append(shell.intersect(_box))
    _h=max(_halves,key=pick)
    for _tol in (None,1e-3):
        _m=_h.mirror('YZ')
        _try=(_h.fuse(_m) if _tol is None else _h.fuse(_m,tol=_tol)).clean()
        _ok=_try.isValid() and len(_try.Solids())==1 and abs(_try.Volume()-shell.Volume())<0.005*shell.Volume()
        print(name,'symmetric rebuild: halves mm3',[round(h.Volume(),1) for h in _halves],'faces',len(shell.Faces()),'->',len(_try.Faces()),'dvol',round(_try.Volume()-shell.Volume(),1),'accepted' if _ok else 'rejected')
        if _ok: return checked(_try,name)
    return shell
_shells['Front shell']=_symmetric(_shells['Front shell'],'Front shell')
assert _shells['Rear shell'].intersect(_tail_strip).Volume()<0.001, 'Tail lens interferes with housing'
assert _shells['Rear shell'].distance(_tail_strip)>=STRIP_FIT*0.8, 'Tail lens clearance is too small'
# ---- Stealth shell (parts/stealth_shell.py) replaces the traced Front shell, Canopy and Grille insert built above. It is built
# in printed coordinates from a few convex faceted blocks with an exact wall, then gets the same wheel-arch, deck and
# suspension-travel cuts. The traced shell above is still built because the tail housing and the light strips come from it.
STEALTH = True
EXACT_ARCH_CHAMFER = True   # arch rims: exact 45 deg chamfer per skin facet (parts/stealth_shell.py exact_arch_chamfer), not the stepped chamfer_rims
# Open cockpit (Yeti style): the Canopy is not built into the model, the stealth Front shell is the lower body up to the belt line and the cage's
# cabin tubes (parts/cage.py) are the visible cabin. False restores the closed stealth canopy.
OPEN_COCKPIT = param(True, 'Open cockpit: no canopy, the cage forms the visible cabin', group='Cage')
_traced = dict(_shells)   # the cage keeps following the traced shell's belt and lower edge: the stealth skin was fitted around that cage
if STEALTH:
    import parts.stealth_shell as _ss
    _sf, _sc, _, _ = _ss.make()
    for _t in _ss.arch_cut() + [_deck_trim] + _tools:
        _sf = _sf.cut(_t)
    for _t in _tools:
        _sc = _sc.cut(_t)
    # 0.5 mm break on the outside edge of the wheel arches (stepped, the arch outline is curved). The bottom trim line and, with the open cockpit, the
    # cabin opening (the visible belt rim) get theirs as an exact facet further down, where those rims are squared off (square_cuts).
    if not EXACT_ARCH_CHAMFER: _sf = _ss.chamfer_rims(_sf, [lambda g: _ss.arch_cut(grow=g)[:2]])   # stepped (3 terraces of 0.17 mm): replaced by the exact chamfer after the liners
    _shells['Front shell'] = checked(strip_dust(_sf.clean(), min_volume=50.0), 'Front shell')
    if OPEN_COCKPIT: _shells.pop('Canopy')     # the traced canopy (in _traced) stays: the cage tail tubes follow its rear quarter
    else: _shells['Canopy'] = checked(strip_dust(_sc.clean(), min_volume=50.0), 'Canopy')
    _shells['Grille insert'] = checked(_ss.grille_insert(), 'Grille insert')
    assert OPEN_COCKPIT or _shells['Front shell'].intersect(_shells['Canopy']).Volume() < 0.01, 'Canopy sits inside the body skin'
    assert _shells['Front shell'].intersect(_shells['Grille insert']).Volume() < 0.01, 'Grille insert interferes with the nose'
    _stealth_strip = checked(_ss.nose_strip(), 'Nose light strip')
    assert _shells['Front shell'].intersect(_stealth_strip).Volume() < 0.01 and _shells['Grille insert'].intersect(_stealth_strip).Volume() < 0.01, 'Nose light strip interferes'
    # (The fill of the pocket beside each strip end is gone: since the hood filler closes that pocket in parts/stealth_shell.py, all it still found was
    # the 0.5 mm bevel of the hood edge over the cheek, a 6 mm3 hairline 50 mm long, which it filled back in and left a lump on the nose corner.)
    import numpy as _np
    _env = _ss.outer_solid()
    # The groove behind each strip end is open to the outside (no skin over it, marked hole): close it with a plug that fills the groove void behind the strip end,
    # between the cheek's outer skin and the hollow, bounded by the outer envelope so the outer face stays the faceted skin.
    for _sx in (1, -1):
        _A = _np.array([_sx * 56.5, -262.0]); _d = _np.array([_sx * 0.315, 0.949]); _n = _np.array([_sx * 0.949, -0.315])
        _ring = [tuple(_A + t * _d + u * _n) for t, u in ((-7, -5.0), (16, -5.0), (16, 12), (-7, 12))]      # from 6 mm ahead of the strip's end: no open recess between strip end and plug
        _prism = cq.Workplane('XY').workplane(offset=99.0).polyline(_ring).close().extrude(26.0).val()
        _plug = _env.intersect(_prism).cut(_shells['Front shell']).cut(_stealth_strip)
        for _g in (0.25, 0.5):      # the strip's fit gap (0.25 mm) at its end face
            _plug = _plug.cut(_stealth_strip.translate(cq.Vector(_d[0] * _g, _d[1] * _g, 0)))
        _plug = cq.Compound.makeCompound([q for q in _plug.Solids() if q.Volume() > 0.5])
        print('nose strip rear groove plug side', _sx, 'solids', len(_plug.Solids()), 'mm3', round(_plug.Volume(), 1))
        for _tol in (None, 1e-3):
            _t = (_shells['Front shell'].fuse(_plug) if _tol is None else _shells['Front shell'].fuse(_plug, tol=_tol)).clean()
            if _t.isValid() and len(_t.Solids()) == 1 and _t.Volume() > _shells['Front shell'].Volume():
                _shells['Front shell'] = _t; break
        else:
            raise AssertionError('groove plug did not fuse on side %d' % _sx)
    assert _shells['Front shell'].intersect(_stealth_strip).Volume() < 0.01, 'groove plug touched the strip'
    assert OPEN_COCKPIT or _shells['Front shell'].distance(_shells['Canopy']) > 0.15, 'Canopy tabs have no clearance'
    print('stealth shell: Front shell faces', len(_shells['Front shell'].Faces()), 'Canopy faces', len(_shells['Canopy'].Faces()) if 'Canopy' in _shells else '(open cockpit)')
add_part('Tail light housing',_shells['Rear shell'],color=BODY,group='Print shell')
if not STEALTH: _shells['Canopy']=_unify_flat(_shells['Canopy'],'Canopy')
# Continuous recessed backing flanges (stepped lap joints) are built directly into make_canopy() and canopy_seat_tool()
# along the entire side/rear seam, mechanically stopping both outer surfaces flush with a uniform 0.3 mm PANEL_GAP.
# travel of the new front end (upper arms with their shock posts, knuckles): cut from the finished front shell (after all later fills)
_wb_tools = wishbone_relief_tools()
for _t in _wb_tools:
    _shells['Front shell'] = _shells['Front shell'].cut(_t)
if STEALTH:
    # These cutters and the deck trim cross the skin at an angle or only graze it, which left feather edges (the wall running out to nothing over up to
    # 8 mm beside the upper arm notch above the arch) and knife edges along the bottom line; the cabin opening is cut straight up through a deck that
    # slopes. Every such opening is squared off through the wall, facet by facet (parts/stealth_shell.py square_cuts), and its outside edge gets the
    # 0.5 mm break of the other rims as one exact facet.
    _v0 = _shells['Front shell'].Volume()
    # (the upper arm's own envelope is left out: its opening through skin and liner is the arm tunnel, cut further down)
    _sq_tools = [_deck_trim] + ([_ss.cabin_cut(convex=True)] if OPEN_COCKPIT else []) + _tools + wishbone_relief_tools(kinds=('knuckle', 'tyre'))
    _shells['Front shell'], _sq = _ss.square_cuts(_shells['Front shell'], _sq_tools, chamfer=_ss.CHAMFER)
    print('front shell rims squared and broken 0.5 mm: %d openings (cutter x facet), mm3 removed %.1f' % (len(_sq), _v0 - _shells['Front shell'].Volume()))
_shells['Front shell'] = strip_dust(_shells['Front shell'].clean(), min_volume=1500.0)
assert _shells['Front shell'].isValid() and len(_shells['Front shell'].Solids()) == 1, 'wishbone relief broke the front shell (%d solids)' % len(_shells['Front shell'].Solids())
# Wheel-well liners (owner, November 23): a wall inside the skin around the swept space of each front tyre and knuckle closes the part of the arch
# above the fender line, so the cage and the deck are not seen through it; the upper arm and its shock post keep their own opening
# (parts/relief.py wheel_well_liners). Clipped to the inside of the skin and to the arch, trim and travel cuts here; the cage gap and the fuse
# follow after the cage is built, where the Front shell is registered.
LINER_CAGE_GAP = 1.0
LINER_RIM = 1.5
LINER_BEVEL_CLIP = True   # liners clipped by the skin's own bevelled boundary (without the bevels their corner poked through them at SHOULDER)
LINER_CORNER_R = 0.0   # tried 2.5 (liners kept out of a ball at the outer hood corner): the corner slivers moved to the ball edge, ledges 35 -> 43
LINER_INSET = 0.0   # tried 1.5 (liners half a wall inside the skin): the 2 shoulder slivers went, but the liner top showed as a step in the open
                    # cockpit's rim: 20 more ledges (4 on the shoulder edge at (89, -217, 134), 14 at the arch top y -160)
_liners = {}
if STEALTH:
    from parts.relief import wheel_well_liners
    _lo_body = _ss.outer_solid(inset=LINER_INSET, bevel=LINER_BEVEL_CLIP)
    for _sx, _w in wheel_well_liners().items():
        _w = _w.intersect(_lo_body)
        for _t in _ss.arch_cut() + [_deck_trim] + _tools:
            _w = _w.cut(_t)
        # square rim: the liner's ceiling meets the lower trim line at a shallow angle, which left feather edges (0.02 to 0.6 mm). Only the columns
        # of the wall that stand at least LINER_RIM above the trim line are kept, so the rim ends in a step of that height
        _hi = _w
        for _t in _ss.arch_cut() + [_deck_trim] + _tools:      # every cut the liner ends on (the flat arch top at z 102.4 is the one that mattered)
            _hi = _hi.cut(_t.translate(cq.Vector(0, 0, LINER_RIM)))
        _keep = _hi                     # plus the prism under each of its downward faces, down to the trim line (an exact sweep, no stacked copies)
        for _f in _hi.Faces():
            if _f.geomType() == 'PLANE' and _f.normalAt(_f.Center()).z < -0.9 and _f.Area() > 0.5:
                _keep = _keep.fuse(cq.Solid.extrudeLinear(_f, cq.Vector(0, 0, -LINER_RIM - 0.05)))
        _liners[_sx] = _w.intersect(_keep).clean()
if 'Canopy' in _shells: add_part('Canopy',_shells['Canopy'],color=ROOF,group='Print shell')
add_part('Grille insert',_shells['Grille insert'],color=(0.06,0.06,0.07),group='Print shell')
add_part('Tail light strip',_tail_strip,color=(0.85,0.05,0.05),alpha=1,group='Lights')
if STEALTH:
    add_part('Nose light strip',_stealth_strip,color=(0.85,0.05,0.05),alpha=1,group='Lights')   # plain bar in the slot across the nose face
else:
    _nose_strip=_unify_flat(_nose_strip,'Nose light strip')
    # E1 collision fix: the strip sat 78 mm3 into the Front shell groove; trim it flush so it touches instead of interpenetrating.
    _ns0=_nose_strip.Volume(); _nose_strip=_nose_strip.cut(_shells['Front shell']).clean()
    assert _nose_strip.isValid() and len(_nose_strip.Solids())==1 and _ns0-_nose_strip.Volume()<150,'nose strip trim failed'
    print('E1 nose strip trimmed mm3',round(_ns0-_nose_strip.Volume(),1))
    # The trim can leave a speck of dust on one side (0.004 mm3 at x 34, flagged by the kit mesh audit); the strip is symmetric,
    # so rebuild it from the half with fewer faces.
    _nose_strip=_symmetric(_nose_strip,'Nose light strip',pick=lambda h:-len(h.Faces()))
    add_part('Nose light strip',_nose_strip,color=(0.85,0.05,0.05),alpha=1,group='Lights')

# Chassis and components, imported from inputs/WS03_chassis_only.glb as named parts grouped by function
# (tools/make_chassis_ref.py: each component as a light convex-hull stand-in, standard 1:10 size, included in the print build).
_off = cq.Vector(0, CHASSIS_Y, CHASSIS_Z)
_ch = import_assembly('parts/chassis_ref.step')
_ch.loc = cq.Location(_off)
# The front deck plate is lifted so its top sits flush against the base of the front diff housing (deck and diff were 0.9-1.0 mm apart).
from parts.params import DECK_FRONT_RAISE
for _dn in _ch.objects.values():
    if getattr(_dn, 'name', None) == 'w3 deck front':
        _dv = _dn.obj.val() if isinstance(_dn.obj, cq.Workplane) else _dn.obj
        _dn.obj = _dv.translate(cq.Vector(0, 0, DECK_FRONT_RAISE))

# Deck mounting for the cage feet: M3 screws come from the top, so the decks get heat-set insert pockets (M3 x 4 mm insert, pocket D3.8 x 5 deep for the OD 4.2 insert).
# The rail feet are outboard of the deck edge (x 54.5): a small ear (5 mm wide, 14 long, 6 thick) carries the pocket there.
from parts.cage import RAIL_FEET, RAIL_FOOT_X, RAIL_FOOT_DY, FRONT_LEG_X as _FLX, FRONT_FOOT_Y as _FFY, FRONT_TAB_DY as _FTD
from parts.cage import FRONT_TAB_Z as _FTZ, RAIL_TAB_LIFT as _RTL, FOOT_SEAT as _FSEAT, HOOP_FEET as _HOOPF, HOOP_FOOT_X as _HOOPX
from parts import foot_sockets as _fsock
DECK_SCREWS = []   # (deck node, world x, world y, ear) for the hardware list
FRONT_FOOT_SITES = []   # cage feet on the front deck: made again on the flat front deck further down (parts/flat_deck.py replaces the old plate)
def _foot_site(deck, X, y, rail):
    """Deck (chassis frame) with the screw hole, pocket and socket for the cage foot at world (X, y). rail: bracket keyed into the side wall
    (rear deck), otherwise a free-standing collar (front deck)."""
    yr = y - CHASSIS_Y
    for _px in (53.0, 50.0, 46.0, 42.0):
        probe = deck.intersect(cq.Solid.makeBox(0.2, 0.2, 300, cq.Vector(math.copysign(min(abs(X), _px), X) - 0.1, yr - 0.1, -100)))
        if probe.Solids(): break
    assert probe.Solids(), 'no deck under the screw at x %.1f y %.1f' % (X, y)
    bb = probe.BoundingBox(); zt, zb = bb.zmax, bb.zmin
    # M3 countersunk screw from the underside: clearance hole 3.4 through the deck, 90 degree countersink 6.3 at the bottom face
    deck = deck.cut(cq.Solid.makeCylinder(1.7, zt - zb + 2.0, cq.Vector(X, yr, zb - 1.0), cq.Vector(0, 0, 1)))
    deck = deck.cut(cq.Solid.makeCone(3.15 + 1.0, 1.7, 1.45 + 1.0, cq.Vector(X, yr, zb - 1.0), cq.Vector(0, 0, 1)))
    assert deck.isValid() and len(deck.Solids()) == 1, 'deck screw hole broke the deck at x %.1f y %.1f' % (X, y)
    # pocket under the foot and the socket it slots into (parts/foot_sockets.py)
    _zf = [z for yy, z in tuple(RAIL_FEET) + tuple(_HOOPF) if abs(yy - y) < 1.0][0] + _RTL - _FSEAT - CHASSIS_Z
    _add, _cut = _fsock.socket(X, yr, zt, _zf, rail)
    deck = deck.fuse(_add).clean().cut(_cut).clean()
    assert deck.isValid() and len(deck.Solids()) == 1, 'foot socket broke the deck at x %.1f y %.1f' % (X, y)
    return deck
def _deck_pockets(assembly):
    nodes = {n.name: n for n in assembly.objects.values() if getattr(n, 'name', None) in ('w3 deck front', 'w3 deck rear')}
    for X, y in [(sx*RAIL_FOOT_X, y) for y, _ in RAIL_FEET for sx in (-1, 1)]:
        front = y - CHASSIS_Y < -71.0
        node = nodes['w3 deck front'] if front else nodes['w3 deck rear']
        if front:
            FRONT_FOOT_SITES.append((X, y))
        else:
            node.obj = _foot_site(node.obj.val() if isinstance(node.obj, cq.Workplane) else node.obj, X, y, True)
        DECK_SCREWS.append((node.name, X, y, False))
    for X, y in [(sx * _HOOPX, y) for y, _ in _HOOPF for sx in (-1, 1)]:   # front hoop legs: on the front deck (made on the flat deck further down)
        FRONT_FOOT_SITES.append((X, y)); DECK_SCREWS.append((nodes['w3 deck front'].name, X, y, False))
    print('deck insert pockets:', len(DECK_SCREWS))
# Clean up deck plates: plug unused leftover holes from the old layout, widen rear cage foot margin (markup 13:41),
# and extend w3 deck tail to y_ref = 139.0 to fully support w3 rbc lower and its rear slots (markup 13:42).
from parts.deck import band_pieces, clean_deck_plates
clean_deck_plates(_ch)
# Debris walls along both side edges of the rear (centre) deck (parts/deck_walls.py), fused into the plate.
from parts.deck_walls import make_deck_walls
_dr = [n for n in _ch.objects.values() if getattr(n, 'name', None) == 'w3 deck rear']
assert len(_dr) == 1, 'rear deck node not found'
_d0 = _dr[0].obj.val() if isinstance(_dr[0].obj, cq.Workplane) else _dr[0].obj
_d1 = _d0
for _w in make_deck_walls(_d0):
    _d1 = _d1.fuse(_w)
_d1 = _d1.clean()
assert _d1.isValid() and len(_d1.Solids()) == 1, 'deck walls broke the rear deck'
print('rear deck walls added, mm3', round(_d1.Volume() - _d0.Volume(), 1))
_dr[0].obj = _d1
_dt = [n for n in _ch.objects.values() if getattr(n, 'name', None) == 'w3 deck tail']
assert len(_dt) == 1, 'tail deck node not found'
from parts.deck_walls import make_tail_walls
_t0 = _dt[0].obj.val() if isinstance(_dt[0].obj, cq.Workplane) else _dt[0].obj
_t1 = _t0
for _w in make_tail_walls(_t0):
    _t1 = _t1.fuse(_w)
_t1 = _t1.clean()
assert _t1.isValid() and len(_t1.Solids()) == 1, 'deck walls broke the tail deck (%d solids)' % len(_t1.Solids())
print('tail deck walls added, mm3', round(_t1.Volume() - _t0.Volume(), 1))
_dt[0].obj = _t1
# The ballast carrier, lid and plate (hung under the tail deck) are dropped: no ballast pocket in this build.
for _bn in [n for n in _ch.objects.values() if getattr(n, 'name', None) in ('w3 ballast carrier', 'w3 ballast lid', 'w3 ballast plate')]:
    _bn.parent.children.remove(_bn)
_ch.objects = {k: v for k, v in _ch.objects.items() if getattr(v, 'name', None) not in ('w3 ballast carrier', 'w3 ballast lid', 'w3 ballast plate')}
_nodes_d = {n.name: n for n in _ch.objects.values() if getattr(n, 'name', None) in ('w3 deck front', 'w3 deck rear', 'w3 deck tail')}
for _band, _dn in band_pieces([_shells[k] for k in ('Front shell', 'Canopy', 'Rear shell') if k in _shells]):
    _node = _nodes_d[_dn]
    _deck = _node.obj.val() if isinstance(_node.obj, cq.Workplane) else _node.obj
    _deck2 = _deck.fuse(_band.translate(-_off)).clean()
    assert _deck2.isValid() and len(_deck2.Solids()) == 1, 'deck band broke ' + _dn
    _node.obj = _deck2
_deck_pockets(_ch)
_nm0 = lambda _n: str(getattr(_n, 'name', ''))
_ob0 = lambda _n: (_n.obj.val() if isinstance(_n.obj, cq.Workplane) else _n.obj)
_deckf = [n for n in _ch.objects.values() if _nm0(n) == 'w3 deck front'][0]
# Deck front corners: the diagonal bevel (54.5, -200) -> (37.3, -212.5) left an open triangle beside the skid. A gusset closes it: the corner now runs
# (54.5, -200) -> (54.5, -205) -> (40, -212.5), following the skid side, and has the same thickness and slope as the deck plate (world frame, converted to ref).
_gp = [(37.0, -212.5), (40.0, -212.5), (54.5, -205.0), (54.5, -199.0), (50.0, -199.0)]
_slope = (19.6 - 18.7) / 12.0   # deck top rise per mm of y between y -212 and -200
_gzb = lambda y: 12.7 + (y + 212.0) * _slope + DECK_FRONT_RAISE * 0.0
for _sg in (1, -1):
    _pr = cq.Workplane('XY').polyline([(_sg * x, y - 9.0) for x, y in _gp]).close().extrude(80).translate(cq.Vector(0, 0, -20))
    _y0, _y1 = -213.0, -198.0
    _sl = (cq.Workplane('YZ').polyline([(_y0 - 9.0, _gzb(_y0) + 15.3), (_y1 - 9.0, _gzb(_y1) + 15.3), (_y1 - 9.0, _gzb(_y1) + 15.3 + 6.0), (_y0 - 9.0, _gzb(_y0) + 15.3 + 6.0)]).close().extrude(200).translate(cq.Vector(-100, 0, 0)))
    _gus = _pr.intersect(_sl).val()
    _d0 = _ob0(_deckf)
    _d1 = _d0.fuse(_gus).clean()
    assert _d1.isValid() and len(_d1.Solids()) == 1, 'deck corner gusset broke the front deck'
    print('deck corner gusset side', _sg, 'added mm3', round(_d1.Volume() - _d0.Volume(), 1))
    _deckf.obj = _d1
# Rear wheel drive only (parts/rwd.py): the front belts, pulleys, front and centre differential and their housings are removed,
# the motor drives the rear shaft through one spur stage.
from parts.pulleys import make_pulley as _mkp, belt_loop as _mkbelt, belt_length as _blen, tooth_od as _tod
from parts import rwd as _rwd
_nn = lambda n: str(getattr(n, 'name', ''))
def _bb0(n):
    _o = _ob0(n); _b = _o.BoundingBox(); return _b, ((_b.ymin + _b.ymax) / 2, (_b.zmin + _b.zmax) / 2)
_piv_yz, _rs_front, _rs_dir = _rwd.remove_front_drive(_ch)
print('rwd: front arm pivot (y, z)', [round(v, 2) for v in _piv_yz], 'rear shaft front end', [round(v, 1) for v in _rs_front.toTuple()])
_dfn = [n for n in _ch.objects.values() if _nn(n) == 'w3 deck front'][0]
_drn = [n for n in _ch.objects.values() if _nn(n) == 'w3 deck rear'][0]
# printed ring gear hub: the rear shaft's end touched its face (0.11 mm3, found by collide.py --all); the hub is cleared 0.3 mm around the shaft
_rgh = [n for n in _ch.objects.values() if _nn(n) == 'w3 rring hub'][0]
_rsh = [n for n in _ch.objects.values() if _nn(n) == 'b rear shaft'][0]
_hw, _sw = _ob0(_rgh).moved(_rgh.loc), _ob0(_rsh).moved(_rsh.loc)
_hv0 = _hw.Volume()
for _d in ((0, 0, 0), (0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)):
    _hw = _hw.cut(_sw.translate(cq.Vector(*_d)))
_hw = max(_hw.Solids(), key=lambda q: q.Volume())
_rgh.obj = _hw.moved(_rgh.loc.inverse)
print('ring gear hub cleared around the rear shaft, mm3 removed', round(_hv0 - _hw.Volume(), 2))
for _dn_, _ds_, _dc_ in _rwd.drive(_rs_front, _rs_dir):
    if _dn_ == 'w3 motor plate':
        _v0 = _ds_.Volume()
        for _dkn in (_drn, _dfn): _ds_ = _ds_.cut(_ob0(_dkn))
        _ds_ = max(_ds_.Solids(), key=lambda q: q.BoundingBox().zmax)   # the piece above the deck
        print('rwd: motor plate seated on the deck, removed mm3', round(_v0 - _ds_.Volume(), 1), 'z', round(_ds_.BoundingBox().zmin, 1), round(_ds_.BoundingBox().zmax, 1))
        assert _v0 - _ds_.Volume() > 50.0, 'motor plate does not reach the deck'
    _ch.add(_ds_, name=_dn_, color=cq.Color(*_dc_))
# Printed 6-spoke wheels (parts/wheels.py) replace the solid rim stand-ins: 1.9 in front wheels (bead seat 48.3 mm, 34 mm wide) carry bought rubber tyres.
# The tyre stand-in becomes a ring around the wheel's flange lips (a bought part: it only has to show where the rubber is).
from parts.wheels import make_wheel as _mkw, bead_seat as _bseat, tyre_seat_radius as _tsr
FRONT_WHEEL_IN, FRONT_WHEEL_W = 1.9, 34.0
FRONT_WHEEL_X = 144.0    # wheel centre plane (tyre centre)
def _relieve(_w, _s, _d=0.2):
    """Cut `_s` out of `_w`, then again shifted 0.2 mm each way (sequential cuts: fusing the shifted copies fails on the faceted stand-ins)."""
    _r = _w.cut(_s)
    for _v in ((_d, 0, 0), (-_d, 0, 0), (0, _d, 0), (0, -_d, 0), (0, 0, _d), (0, 0, -_d)): _r = _r.cut(_s.translate(cq.Vector(*_v)))
    return _r
for _sx in (1, -1):
    _rim = [n for n in _ch.objects.values() if _nn(n) == 'mock rim %d' % _sx]
    _rdc = [n for n in _ch.objects.values() if _nn(n) == 'mock rimdisc %d' % _sx]
    _tyr = [n for n in _ch.objects.values() if _nn(n) == 'mock tire %d' % _sx]
    assert len(_rim) == len(_rdc) == len(_tyr) == 1, 'front rim / tyre stand-ins not found'
    _rb_, _rc = _bb0(_rim[0])
    _xc = (_rb_.xmin + _rb_.xmax) / 2
    _w = _mkw(_bseat(FRONT_WHEEL_IN), FRONT_WHEEL_W, axle_bore=4.4)
    if _sx < 0: _w = _w.mirror('YZ')
    _w = _w.translate(cq.Vector(_xc, *_rc))
    for _n in (_rim[0], _rdc[0]): _n.parent.children.remove(_n)
    _ch.add(_w, name='wheel f %d' % _sx, color=cq.Color(0.72, 0.45, 0.30))
    _t0 = _ob0(_tyr[0])
    _t1 = _t0.cut(cq.Solid.makeCylinder(_tsr(_bseat(FRONT_WHEEL_IN)), 80, cq.Vector(_xc - 40, *_rc) if False else cq.Vector(_xc - 40, _rc[0], _rc[1]), cq.Vector(1, 0, 0)))
    assert _t1.isValid() and len(_t1.Solids()) == 1, 'tyre ring broke'
    _tyr[0].obj = _t1
    print('front wheel side', _sx, 'centre x %.1f y %.1f z %.1f' % (_xc, *_rc), 'wheel mm3 %.0f' % _w.Volume(), 'tyre ring mm3 %.0f' % _t1.Volume())
# Old lean mechanism (servo, mount, ears, horn, rocker, lean shock stand-ins) and the lower front differential box: removed. Passive lean now runs
# through the balance beam of parts/lean_beam.py (added with the cage further down).
for _lname in ('lean servo c', 'w3 fdc lower', 'lean mount c', 'lean ears c', 'lean horn c', 'lean rocker c', 'b lean shock 1', 'b lean shock -1'):
    _lf = [n for n in _ch.objects.values() if str(getattr(n, 'name', '')).replace('_', ' ') == _lname]
    assert len(_lf) == 1, 'lean node not found: ' + _lname
    _lf[0].parent.children.remove(_lf[0])
# Front suspension and steering rebuilt after the lean-steer build in the reference video (parts/wishbone.py): the old swingarms, uplinks, lean beam, shocks, knuckles,
# carriers, tie rods, servos and their hardware are removed. The front deck becomes one plain flat slab (parts/flat_deck.py: no old mounting holes, pockets,
# sockets or recesses), the battery turns crosswise and moves back to just ahead of the motor, the steering servo sits behind the head inside the body.
from parts import wishbone as _wb
from parts.flat_deck import make_flat_deck, lap_skid as _lap_skid, lap_decks as _lap_decks
_big = lambda _o: max(_o.Solids(), key=lambda q: q.Volume())
_flat = make_flat_deck(_ob0(_dfn), _ob0(_drn))                 # ends on the plane of the rear deck's front face (made a half lap below)
for _X, _y in FRONT_FOOT_SITES:                              # cage feet on the flat front deck: screw hole, pocket and collar
    _flat = _foot_site(_flat, _X, _y, False)
_skn = [n for n in _ch.objects.values() if _nn(n) == 'w3 skid'][0]
_flat, _skn.obj = _lap_skid(_flat, _ob0(_skn))                 # the skid's flange is let into the underside of the deck (stepped lap, 2 x M3)
_flat, _drn.obj = _lap_decks(_flat, _ob0(_drn))               # front / rear deck seam: full-thickness half lap, 4 x M3 from below into inserts
# battery and its tray are gone (owner, November 22): both stand-ins are removed from the chassis
for _nm in ('b battery', 'battery tray c'):
    _bn = [n for n in _ch.objects.values() if _nn(n) == _nm][0]
    _bn.parent.children.remove(_bn)
# receiver: in a printed box in the left front bay beside the steering servo; battery: raised tray over the servo (parts/electronics.py)
from parts import electronics as _el
_rcn = [n for n in _ch.objects.values() if _nn(n) == 'mock receiver'][0]
_elx = _el.build(_flat.translate(_off), _ob0(_rcn).translate(_off))
_rcn.obj = _elx['receiver'].translate(-_off)
_flat = _el.deck_holes(_flat, _elx['holes'], _off)
for _n, _k, _c in (('Battery tray', 'tray', (0.16, 0.17, 0.20)), ('Receiver box', 'rx_box', (0.16, 0.17, 0.20)), ('Receiver lid', 'rx_lid', (0.16, 0.17, 0.20)), ('b battery', 'battery', (0.12, 0.25, 0.55))):
    add_part(_n, _elx[_k], group='Chassis/Electronics and power', alpha=1, color=_c)
print('old front removed:', sorted(_wb.strip_old_front(_ch)))
for _sx in (1, -1):   # front wheels centred on the new axle (wheel centre of the tyre), 6 mm axle bore
    _wn = [n for n in _ch.objects.values() if _nn(n) == 'wheel f %d' % _sx]
    _tn_ = [n for n in _ch.objects.values() if _nn(n) == 'mock tire %d' % _sx]
    assert len(_wn) == 1 and len(_tn_) == 1, 'front wheel / tyre not found'
    _tc = _ob0(_tn_[0]).BoundingBox().center
    assert abs(abs(_tc.x) - FRONT_WHEEL_X) < 0.2 and abs(_tc.y + _off.y - _wb.KY) < 0.2 and abs(_tc.z + _off.z - _wb.ZC) < 0.2, 'tyre is not on the new axle'
    # the wheel sits on the axle itself (not on the bounding box of the faceted tyre stand-in, which differs from side to side): both wheels are exact
    # mirror images. Hub boss 1 mm proud: 2 mm floor over the hex pocket, the axle nut (x 160) seats on it.
    _wc = cq.Vector(_sx * FRONT_WHEEL_X, _wb.KY - _off.y, _wb.ZC - _off.z)    # chassis frame, like the tyre
    _w = _mkw(_bseat(FRONT_WHEEL_IN), FRONT_WHEEL_W, axle_bore=6.2, hub_out=1.0, bearing=(12.0, 4.0), hub_in=5.5)   # two 6x12x4 bearings, hub x 142.5..160 (parts/wishbone.py WHEEL_BRG_X)
    if _sx < 0: _w = _w.mirror('YZ')
    _wn[0].obj = _w.translate(_wc)
    # the tyre ring is bored again around this centre (it was bored around the old rim stand-in, up to 0.2 mm off)
    _t1 = _ob0(_tn_[0]).cut(cq.Solid.makeCylinder(_tsr(_bseat(FRONT_WHEEL_IN)), 80, _wc - cq.Vector(40, 0, 0), cq.Vector(1, 0, 0)))
    assert _t1.isValid() and len(_t1.Solids()) == 1, 'tyre ring broke'
    _tn_[0].obj = _t1
_deck_w = _flat.moved(cq.Location(_off)); _skid_w = _ob0(_skn).moved(cq.Location(_off))
_wparts = []
for _n, _s, _g, _c in _wb.all_parts():
    if _n in ('Lean head', 'Steer servo mount'):   # seated on the deck: the head's rails under it, the servo mount on top
        _v0 = _s.Volume(); _s = _s.cut(_deck_w).cut(_skid_w)
        _s = max(_s.Solids(), key=lambda q: q.BoundingBox().zmax).clean()      # the piece on top of the deck (the largest piece of the servo mount used to be the one under it)
        if _n == 'Steer servo mount':
            for _sx in (1, -1):
                for _hx, _hw in _wb.SERVO_SCREWS:   # M3 heat-set insert bore in the pillar, M3 clearance hole through the deck
                    _hy = _wb.servo_pillar_y(_hw)
                    _s = _s.cut(cq.Solid.makeCylinder(_wb.INSERT_POCKET_D / 2, 36.0, cq.Vector(_sx * _hx, _hy, 0.0), cq.Vector(0, 0, 1)))
                    _flat = _flat.cut(cq.Solid.makeCylinder(1.7, 60.0, cq.Vector(_sx * _hx, _hy, -10.0) - _off, cq.Vector(0, 0, 1)))
        if _n == 'Lean head':
            # the front frame's upper corners reach the inside of the nose skin: trimmed 1 mm clear of it
            _s = _big(_s.cut(_shells['Front shell']).cut(_shells['Front shell'].translate(cq.Vector(0, 1.0, 0)))).clean()
            for _sx in (1, -1):
                for _hx, _hy in _wb.HEAD_SCREWS:   # M3 heat-set insert bore in the rail, M3 clearance hole through the deck
                    _s = _s.cut(cq.Solid.makeCylinder(_wb.INSERT_POCKET_D / 2, 32.0, cq.Vector(_sx * _hx, _hy, 0.0), cq.Vector(0, 0, 1)))      # ends in the base tube, below the lower cross bar (z 36.3)
                    _flat = _flat.cut(cq.Solid.makeCylinder(1.7, 60.0, cq.Vector(_sx * _hx, _hy, -10.0) - _off, cq.Vector(0, 0, 1)))
        assert _s.isValid() and len(_s.Solids()) == 1, _n + ' broke when seated on the deck'
        print('seated on the deck:', _n, 'removed mm3', round(_v0 - _s.Volume(), 1))
    _wparts.append((_n, _s, _g, _c))
# Travel stops (parts/stops.py): droop stops under the lower arms, seated on the deck like the head; M3 inserts in the base, clearance holes in the deck
from parts import stops as _stops
_stop_parts = []
for _n, _s, _g, _c, _seat in _stops.all_parts():
    if _seat:
        _sd = int(_n.rsplit(' ', 1)[-1])
        _s = max(_s.cut(_deck_w).Solids(), key=lambda q: q.BoundingBox().zmax).clean()
        for _bore in _stops.insert_bores(_sd):
            _s = _s.cut(_bore)
        for _hx, _hy in _stops.screw_points(_sd):
            _flat = _flat.cut(cq.Solid.makeCylinder(1.7, 60.0, cq.Vector(_hx, _hy, -10.0) - _off, cq.Vector(0, 0, 1)))
        assert _s.isValid() and len(_s.Solids()) == 1, _n + ' broke when seated on the deck'
    _stop_parts.append((_n, _s, _g, _c))
# front deck edge relieved under the lower arms: at the droop stop (psi of parts/stops.py droop_psi, also the lean limit's low side) the arm came
# 0.97 mm from the deck's top edge; the deck is cut by the arm turned DECK_RELIEF_DEG further down (about 1.8 mm more at the edge)
DECK_RELIEF_DEG = 3.0
for _sx in (1, -1):
    _la = [q for n_, q, g_, c_ in _wparts if n_ == 'Lower arm %d' % _sx][0]
    _lp = _la.moved(_wb._loc_axis((_sx * _wb.XI, 0, _wb.ZL), (0, 1, 0), _stops.droop_psi(_sx) + _sx * DECK_RELIEF_DEG))
    _v0 = _flat.Volume(); _flat = _big(_flat.cut(_lp.moved(cq.Location(-_off))))
    print('deck edge relief under lower arm', _sx, 'removed mm3', round(_v0 - _flat.Volume(), 1))
assert _flat.isValid() and len(_flat.Solids()) == 1, 'head screw holes broke the flat deck'
_dfn.obj = _flat
# Sill fixing of the Front shell (November 27): ISO 10642 M3 from under the deck, head flush in the deck underside, into an insert in a tab on the shell's
# inner skin. World positions (x, y); the deck holes are cut here, the tabs and inserts in the shell fixing block further down.
SILL_FIX_X = 50.0
SILL_FIX = ((1, -80.0), (1, -20.0), (-1, -20.0))   # (side, world y): no front fixing on the -x side, the receiver box fills that deck margin (y -120.5 .. -69.9, x to -52.7)
from soma.fasteners import Screw as _Scr0
_sill_screws = []
for _sx, _sy in SILL_FIX:
    _dn = _dfn if _sy < -60.0 else _drn            # front deck ahead of the lap (y -69 world), rear deck behind it
    _d = _ob0(_dn)
    if True:
        _xc, _yc = _sx * SILL_FIX_X, _sy - _off.y          # chassis frame
        _seg = _d.intersect(cq.Solid.makeCylinder(0.05, 200.0, cq.Vector(_xc, _yc, -80.0), cq.Vector(0, 0, 1)))
        _zs = [v.Z for v in _seg.Vertices()]
        assert _zs, 'sill fixing: no deck at x %.1f y %.1f' % (_sx * SILL_FIX_X, _sy)
        _zb, _zt = min(_zs), max(_zs)
        _s0 = _Scr0("ISO 10642", "M3x10", at=(_xc, _yc, _zb), direction="+Z")
        _d = _d.cut(_s0.clearance_hole())
        assert _d.isValid() and len(_d.Solids()) == 1, 'sill fixing broke the deck'
        _sill_screws.append((_s0.translate((_off.x, _off.y, _off.z)), _sx, _sy, _zt + _off.z))
    _dn.obj = _d
    if _dn is _dfn: _flat = _d
print('sill fixing: %d deck holes (ISO 10642 M3 countersunk from below)' % len(_sill_screws))
# Edge break of every printed part that moves or carries a moving joint (owner, November 24; parts/util.py chamfer_moving: EDGE_OUT outside,
# EDGE_BORE on bore entries, nothing on gear or pulley teeth). NOT the traced drivetrain blocks (w3 pillow, w3 rbc, w3 rring hub): they are faceted
# meshes from parts/chassis_ref.step; the chamfer took 8 of 24 edges on the pillow block and crashed the kernel (segmentation fault) on the carrier.
# They need a CadQuery rebuild before they can get edge breaks (open).
from parts.util import chamfer_moving as _chm
CHAMFER_MOVING = param(True, 'Edge break on moving parts (outside 0.6 mm, bore entries 0.4 mm)', group='Print')
_CHM_NODES = ('wheel f 1', 'wheel f -1')
# FEM de-featuring: FUGU_FEM_SHARP_BORES='Knuckle,Upper arm' builds those parts with their bore / insert entries sharp (outside edges kept) for an
# analysis run only; never set for soma build. The kit is always built with every entry broken.
import os as _os
_FEM_NO_CHAMFER = tuple(t.strip() for t in _os.environ.get('FUGU_FEM_NO_CHAMFER', '').split(',') if t.strip()) or ('\0',)
_FEM_SHARP_BORES = tuple(t.strip() for t in _os.environ.get('FUGU_FEM_SHARP_BORES', '').split(',') if t.strip()) or ('\0',)
_CHM_PARTS = ('Lean head', 'Lower arm', 'Upper arm', 'Knuckle', 'Steer horn', 'Steer servo mount', 'Heave bump stop', 'Droop stop')
def _chm_obj(_n, _label, **_kw):
    _o = _n.obj.val() if isinstance(_n.obj, cq.Workplane) else _n.obj
    _n.obj = _chm(clean_registered(_o), _label, **_kw)      # cleaned before; add_part's clean skips chamfered shapes (parts/util.py NO_CLEAN)
if CHAMFER_MOVING:
    for _n in list(_ch.objects.values()):
        if _nn(_n) in _CHM_NODES and _n.obj is not None: _chm_obj(_n, _nn(_n))
add_part('Chassis', _ch, alpha=1, color=(0.55, 0.57, 0.60))
_UPPER_ARMS = {}   # registered upper arms (for the up stop pads under the cage brace)
for _n, _s, _g, _c in _wparts + _stop_parts:
    if _n.startswith(_FEM_NO_CHAMFER):          # FEM diagnosis only (environment FUGU_FEM_NO_CHAMFER): the part without any edge break
        pass
    elif CHAMFER_MOVING and _n.startswith(_CHM_PARTS) and _n.startswith(_FEM_SHARP_BORES):   # FEM de-featuring only (environment FUGU_FEM_SHARP_BORES)
        _s = _chm(clean_registered(_s), _n, bore=0.0)
    elif CHAMFER_MOVING and _n.startswith(_CHM_PARTS):
        # cleaned first, then chamfered; add_part's clean skips chamfered shapes: OCC's clean() crashed (segmentation fault) on the chamfered upper arm
        # upper arm: edges under 4 mm stay sharp (the 2 to 4 mm edges at the apex nose left 0.0018 mm edges after the break: the FEM mesh failed as built)
        _s = _chm(clean_registered(_s), _n, **({'min_len': 4.0} if _n.startswith('Upper arm') else {}))
    add_part(_n, _s, group=_g, alpha=1, color=_c)
    if _n in ('Upper arm 1', 'Upper arm -1'): _UPPER_ARMS[int(_n.rsplit(' ', 1)[-1])] = _s
# Rear swingarm group rotates about its pivot to carry the bigger rear tire; the axle rises with the tire radius.
# Redesigned as one printable high-strength part (parts/swingarm.py): twin ladder-truss plates around the belt, arch over the top ending in twin shock ears.
from parts.swingarm import make_rear_arm
_th = rear_lift_angle()
_ry = PIVOT[0]*math.cos(_th) - PIVOT[1]*math.sin(_th); _rz = PIVOT[0]*math.sin(_th) + PIVOT[1]*math.cos(_th)
_rr = import_assembly('parts/rear_ref.step')
_arm_nodes = [n for n in _rr.objects.values() if getattr(n, 'name', None) == 'w3 rear arm']
assert len(_arm_nodes) == 1, 'rear arm node not found in parts/rear_ref.step'
_arm_nodes[0].obj = make_rear_arm()
_rr.loc = cq.Location(cq.Vector(0, PIVOT[0]-_ry+CHASSIS_Y, PIVOT[1]-_rz+CHASSIS_Z), cq.Vector(1, 0, 0), math.degrees(_th))
# Rear arm belt drive: printed GT2 pulleys 26T (pivot) and 30T (axle) and a bought 6 mm GT2 closed loop belt (2GT-300). The ratio 26:30 keeps the rear wheel speed with the
# 140 mm tyre (the old 22T:20T pair on a 112 mm tyre, x 112/140).
_nr = lambda n: str(getattr(n, 'name', ''))
_rp = [n for n in _rr.objects.values() if _nr(n) == 'mock rear pulley pivot']
_ra = [n for n in _rr.objects.values() if _nr(n) == 'mock rear pulley axle']
_rb = [n for n in _rr.objects.values() if _nr(n) == 'mock rear belt']
assert len(_rp) == len(_ra) == len(_rb) == 1, 'rear pulley stand-ins not found'
_bp, _bq = _rp[0].obj.val().BoundingBox() if isinstance(_rp[0].obj, cq.Workplane) else _rp[0].obj.BoundingBox(), None
_ba = _ra[0].obj.val().BoundingBox() if isinstance(_ra[0].obj, cq.Workplane) else _ra[0].obj.BoundingBox()
_cp = ((_bp.ymin + _bp.ymax) / 2, (_bp.zmin + _bp.zmax) / 2); _ca = ((_ba.ymin + _ba.ymax) / 2, (_ba.zmin + _ba.zmax) / 2)
_xr = (_bp.xmin + _bp.xmax) / 2 + 1.6     # 1.6 mm toward the outer plate: the flange stands 0.4 mm off the inner plate face (x 52.3)
_rax = [n for n in _rr.objects.values() if _nr(n) == 'mock rear axle']
assert len(_rax) == 1, 'rear axle stand-in not found'
_bx = _rax[0].obj.val().BoundingBox() if isinstance(_rax[0].obj, cq.Workplane) else _rax[0].obj.BoundingBox()
_ca = ((_bx.ymin + _bx.ymax) / 2, (_bx.zmin + _bx.zmax) / 2)   # axle pulley centred on the steel axle
_dr = math.hypot(_cp[0] - _ca[0], _cp[1] - _ca[1])
print('rear belt centre distance %.2f' % _dr, 'length 26/30 %.2f (2GT-300)' % _blen(26, 30, _dr))
assert abs(_blen(26, 30, _dr) - 300.0) < 1.0, 'rear belt is not the stock length'
for _n in (_rp[0], _ra[0], _rb[0]): _n.parent.children.remove(_n)
_rr.add(_mkp(26, 5.0, side=1).translate(cq.Vector(_xr, *_cp)), name='pulley r pivot', color=cq.Color(0.2, 0.2, 0.22))
_rr.add(_mkp(30, 8.0, side=1).translate(cq.Vector(_xr, *_ca)), name='pulley r axle', color=cq.Color(0.2, 0.2, 0.22))
_rr.add(_mkbelt(_cp, 26, _ca, 30, _xr), name='b gt2 belt r', color=cq.Color(0.08, 0.08, 0.08))
# Rear wheel: 2.2 in printed 6-spoke wheel (bead seat 55.9 mm, 40 mm wide), outer face toward -x where the hub stand-in sits.
_rrim = [n for n in _rr.objects.values() if _nr(n) == 'mock rear rim']
_rrdc = [n for n in _rr.objects.values() if _nr(n) == 'mock rear rim disc']
assert len(_rrim) == len(_rrdc) == 1, 'rear rim stand-ins not found'
_rbb = _rrim[0].obj.val().BoundingBox() if isinstance(_rrim[0].obj, cq.Workplane) else _rrim[0].obj.BoundingBox()
_rrc = ((_rbb.xmin + _rbb.xmax) / 2, (_rbb.ymin + _rbb.ymax) / 2, (_rbb.zmin + _rbb.zmax) / 2)
REAR_WHEEL_IN, REAR_WHEEL_W = 2.2, 46.0
for _n in (_rrim[0], _rrdc[0]): _n.parent.children.remove(_n)
_rhub = [n for n in _rr.objects.values() if _nr(n) == 'mock rear hub']
assert len(_rhub) == 1, 'rear hub stand-in not found'
_rw = _mkw(_bseat(REAR_WHEEL_IN), REAR_WHEEL_W, axle_bore=8.4, hub_od=22.0).mirror('YZ').translate(cq.Vector(*_rrc))
_rw0 = _rw; _rw = _relieve(_rw, _rhub[0].obj.val() if isinstance(_rhub[0].obj, cq.Workplane) else _rhub[0].obj); _rw = max(_rw.Solids(), key=lambda q: q.Volume())   # pocket for the hub stand-in
print('rear wheel relief around the hub mm3', round(_rw0.Volume() - _rw.Volume(), 1))
_rr.add(_rw, name='wheel r', color=cq.Color(0.72, 0.45, 0.30))
if CHAMFER_MOVING:
    for _n in list(_rr.objects.values()):
        if _nr(_n) == 'w3 rear arm':
            # exception to the edge-break rule (owner's rule allows it where it costs strength): the bearing seat entries stay sharp, so the seats keep
            # their full 4 / 5 mm and the FEM support on them has no chamfer edge (with 0.4 mm breaks the rear arm FEM diverged: 1.62 at 1.5 mm, 1.33 at 1.2)
            from parts.swingarm import PIVOT_BRG as _PB, AXLE_BRG as _AB, BRG_FIT as _BF
            _chm_obj(_n, _nr(_n), keep_sharp_r=((_PB[0] + _BF) / 2, (_AB[0] + _BF) / 2))
        elif _nr(_n) == 'wheel r': _chm_obj(_n, _nr(_n))
        elif _nr(_n) in ('pulley r pivot', 'pulley r axle'): _chm_obj(_n, _nr(_n), circles_only=True)     # hub, flanges, bore; not the teeth
add_part('Rear swingarm', _rr, alpha=1, color=(0.55, 0.57, 0.60))
_ay = PIVOT[0] + (REAR_AXLE[0]-PIVOT[0])*math.cos(_th) - (REAR_AXLE[1]-PIVOT[1])*math.sin(_th)
_az = PIVOT[1] + (REAR_AXLE[0]-PIVOT[0])*math.sin(_th) + (REAR_AXLE[1]-PIVOT[1])*math.cos(_th)
_tire = cq.Solid.makeCylinder(REAR_TIRE_OD/2, 62, cq.Vector(-31, _ay, _az), cq.Vector(1, 0, 0)).translate(_off)
_tire = _tire.cut(cq.Solid.makeCylinder(_tsr(_bseat(REAR_WHEEL_IN)) + 0.2, 80, cq.Vector(-40, _ay, _az), cq.Vector(1, 0, 0)).translate(_off))   # ring around the wheel lips
add_part('Rear tire', _tire, group='Chassis', alpha=1, color=(0.10, 0.10, 0.11))
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
# Damper body at the top (sprung mass, starting 10.5 mm below _et to clear the top clevis ears) and shaft at the bottom (unsprung mass)
_shock = _cyl(9.0, 0.48*_L, _et - _u*(10.5 + 0.48*_L), _u).fuse(_cyl(2.5, 0.52*_L - 7.5, _eb + _u*7.5, _u))
_shock = _shock.fuse(_cyl(3.5, 5.5, _et - _u*11.0, _u)).fuse(_cyl(3.5, 4.0, _eb + _u*5.5, _u)).fuse(_eye(_eb)).fuse(_eye(_et))
for _eye_centre in (_eb,_et):
    _shock=_shock.cut(_cyl(3.2,24.0,_eye_centre-_X*12.0,_X))
_shock=_shock.clean()
assert _shock.isValid() and len(_shock.Solids())==1, 'Shock eyelets must join the strut'
add_part('Rear shock (100 mm class)', _shock, group='Chassis', alpha=1, color=(0.80, 0.15, 0.12))
def _m6_clevis_bolt(c, half_span):
    """M6 socket-head shoulder bolt + nylon locknut clamping a double-shear clevis of outer half-width `half_span`."""
    shank = _cyl(3.0, 2 * half_span + 9.0, c - _X * (half_span + 5.0), _X)
    head = _cyl(5.0, 5.0, c + _X * half_span, _X).cut(_cyl(2.5, 3.5, c + _X * (half_span + 2.0), _X))
    nut_hex = cq.Workplane(cq.Plane(origin=(c - _X * half_span).toTuple(), normal=(-1, 0, 0))).polygon(6, 11.5).extrude(4.5).val()
    nut_dome = _cyl(4.5, 1.5, c - _X * (half_span + 6.0), _X)
    return shank.fuse(head).fuse(nut_hex).fuse(nut_dome).clean()

from parts.swingarm import EAR_GAP as _EG, EAR_T as _ET
_pin_lo = _m6_clevis_bolt(_eb, _EG / 2 + _ET)   # M6 bolt + locknut clamping the lower swingarm clevis ears (|x| = 4.4..12.8 mm)
add_part('M6 shock pin (lower)', _pin_lo, group='Chassis', alpha=1, color=(0.78, 0.80, 0.84))
# No separate tower: the shock top pin is carried by the cage's overhead double-shear clevis bracket (|x| = 4.4..12.0 mm).
_pin = _m6_clevis_bolt(_et, 12.0)      # M6 bolt + locknut clamping the upper cage clevis ears (|x| = 4.4..12.0 mm)
add_part('M6 shock pin', _pin, group='Chassis', alpha=1, color=(0.78, 0.80, 0.84))
# Magnetic power connection for the lights, built into the cage (front and rear, on the centre line, above all the componentry).
from parts.light_contacts import make_connector, roof_underside, LIGHT_FRONT_Y, LIGHT_REAR_Y
from parts.cage import make_cage, belt_profile
_belt = belt_profile([_traced['Front shell'], _traced['Rear shell']], LIGHT_FRONT_Y, max(LIGHT_REAR_Y,20.0))
print('cage belt line vertices (y, z):', [(y, round(z, 1)) for y, z in _belt])
if STEALTH:
    # The stealth belt line rises straight from the cowl (y -208, z 134) to the tail apex (y 116, z 171): the cage side rails follow it, the same
    # BELT_CLEAR below the sill, instead of staying on the old flat belt (which left them up to 40 mm under the sill at the tail).
    _bz = lambda y: round(134.0 + (y + 208.0) * (171.0 - 134.0) / (116.0 + 208.0), 1)
    _belt = list(_belt) + [(float(y), _bz(y)) for y in (-150, -50, 38, 60)]
    print('cage belt line (stealth):', _belt)
# Frame nodes of the shell (A pillar, B pillar, roof, rear quarter) in the final frame, from the same trace the canopy is built from.
from parts.reference_trace import ROOF, WINDOW_BELT, traced, belt_station
from parts.shell_geometry import point as _pt
def _final(p):
    c = cq.Solid.makeSphere(0.05, cq.Vector(*p)).transformGeometry(_pitch).Center()
    return (round(c.x, 1), round(c.y, 1), round(c.z, 1))   # rounded: coincident float noise makes the tube booleans invalid
_nodes = {k: _final(_pt(traced(p, 1))) for k, p in {'belt0': WINDOW_BELT[0], 'roof0': ROOF[0], 'roof1': ROOF[1], 'roof2': ROOF[2], 'roofN': ROOF[-1],
                                                    'belt930': belt_station(930)}.items()}
# The visor lies in the windscreen glass plane, whose underside runs through the front roof header (node roof0). The header node drops by this much so the
# header tube clears the visor underside by 0.3 mm; the A pillars, the strut and the roof side rails that end on the node re-angle with it.
ROOF0_DROP = 3.3
_nodes['roof0'] = (_nodes['roof0'][0], _nodes['roof0'][1], round(_nodes['roof0'][2] - ROOF0_DROP, 1))
# Underside of the rear shell hump above the rear tire at the support stations (6 mm clear of the skin)
from parts.cage import REAR_SUP_X
_sup = []
from parts.tail import light_face,TUBE_END_SETBACK
from parts.cage import CAGE_BEAM
_tail_top,_ = light_face()
_tail_node=(REAR_SUP_X,round(_tail_top[1]-TUBE_END_SETBACK,1),round(_tail_top[2]-WALL_PRINT-CAGE_BEAM/2-GLUE_GAP,1))
print('cage nodes', {k: tuple(round(v, 1) for v in p) for k, p in _nodes.items()}, 'supports', _sup)
if STEALTH:
    import parts.cage as _cage_mod
    _cage_mod.BOSS_TARGETS[:] = [_shells[k] for k in ('Front shell', 'Canopy') if k in _shells]   # boss stubs run to the stealth skin
_cabin = None
if STEALTH and OPEN_COCKPIT:
    # exposed cabin frame on the stealth canopy outline (cowl post, roof front edge, roof peak, B-pillar foot) and the cabin opening's rim
    import parts.stealth_shell as _ssh      # (_ss is reused further up for another module)
    _cabin = dict(cowl=_ssh.COWL_POST, roof_front=_ssh.ROOF_FRONT, roof_peak=_ssh.ROOF_PEAK, b_foot=_ssh.B_FOOT, ring=_ssh.cabin_ring(),
                  rim_z=lambda x, y, _s=_shells['Front shell']: max(q.BoundingBox().zmax for q in _s.intersect(cq.Solid.makeBox(0.6, 0.6, 120.0, cq.Vector(x - 0.3, y - 0.3, 90.0))).Solids()))
_cage, _, _ = make_cage(LIGHT_FRONT_Y, LIGHT_REAR_Y, _belt, _nodes, _sup, tie=(_et.y, _et.z),tail=_tail_node,tail_screws=_tail_scr['cage'],cabin=_cabin)
from parts.cage import FRONT_LEG_X, REAR_LEG_X, FRONT_FOOT_Z, CAGE_Z, CAGE_BEAM
assert _cage.isValid() and len(_cage.Solids()) == 1, 'cage: expected one valid solid'
# (old passive lean bridge, balance beam, front shocks and uplink lugs removed: front end rebuilt in parts/wishbone.py)
SHOW_CAGE = param(True, 'Show the cage (cage, roof plate, light contact block); off while the front end is redesigned', group='Cage')
if STEALTH:     # lower-arch side panels (parts/relief.py arch_side_panels), kept off the cage like the liners and fused the same way
    from parts.relief import arch_side_panels
    for _sx, _w in arch_side_panels().items():
        _liners[('panel', _sx)] = _w
    # upper arm tunnel (parts/relief.py arm_tunnels): one prism through skin and liner, its frame fused like the liners
    from parts.relief import arm_tunnels
    for _sx, (_tc, _tf) in arm_tunnels().items():
        _shells['Front shell'] = strip_dust(_shells['Front shell'].cut(_tc).clean(), min_volume=1500.0)
        _liners[('tunnel', _sx)] = _tf
for _sx, _w in _liners.items():
    _wb_ = _w.BoundingBox(); _g = LINER_CAGE_GAP
    _near = _cage.intersect(cq.Solid.makeBox(_wb_.xlen + 8, _wb_.ylen + 8, _wb_.zlen + 8, cq.Vector(_wb_.xmin - 4, _wb_.ymin - 4, _wb_.zmin - 4)))
    if _near.Volume() > 0.01:
        for _d in ((0, 0, 0), (_g, 0, 0), (-_g, 0, 0), (0, _g, 0), (0, -_g, 0), (0, 0, _g), (0, 0, -_g)):
            _w = _w.cut(_near.translate(cq.Vector(*_d)))
    if STEALTH and not isinstance(_sx, tuple) and LINER_CORNER_R:   # wheel-well liner: kept out of a small ball at the outer hood corner (SHOULDER), where
        # the hood, cheek and flank planes meet: its fuse there left a fan of 0.02 to 0.57 mm2 faces (the ball lies inside the 3 mm wall at that corner)
        _w = _w.cut(cq.Solid.makeSphere(LINER_CORNER_R, cq.Vector(_sx * abs(_ss.SHOULDER[0]), _ss.SHOULDER[1], _ss.SHOULDER[2])))
    _w = strip_dust(_w.clean(), min_volume=30.0)
    _f0 = _shells['Front shell']
    _f1 = strip_dust(_f0.fuse(_w).clean(), min_volume=1500.0)
    assert _f1.isValid() and len(_f1.Solids()) == 1 and _f1.Volume() > _f0.Volume(), 'wheel-well liner did not fuse into the front shell (%d solids)' % len(_f1.Solids())
    print('wheel-well liner' if not isinstance(_sx, tuple) else 'arch side panel' if _sx[0] == 'panel' else 'arm tunnel frame', _sx, 'wall mm3', round(_w.Volume(), 1), 'added mm3', round(_f1.Volume() - _f0.Volume(), 1))
    _shells['Front shell'] = _f1
# shoulder seam region (November 26): the liner fuses leave 0.00 mm2 faces where the liner's clip planes meet the skin's creases (both ends of the
# shoulder edge, 88 / 90, -228 / -208, z 134.2); one more flat-face merge after the last fuse folds them into their planes
if STEALTH and EXACT_ARCH_CHAMFER: _shells['Front shell'] = _ss.exact_arch_chamfer(_shells['Front shell'])   # after the liners, which reach the rim
if STEALTH: _shells['Front shell'] = _unify_flat(_shells['Front shell'], 'Front shell (after liners)', volume_tol=0.001, max_tol=0.01)   # pinned at 0.01: the 0.1 merge flips between accepted (+88 mm3) and a -1867 mm3 collapse as the hull changes
# Shell fixing (November 27): the Front shell is screwed to the cage's two shell bosses (B upright, y 38), which carry M3 heat-set inserts (parts/cage.py
# BOSS_INSERT). Per boss: a pad on the inner skin out to SHELL_PAD_GAP off the boss face, a clearance hole on the boss axis and a counterbore deep enough
# that the ISO 7380 button head sits below the slanted skin (31 deg to the axis) all round; screw length picked for the grip and the 4 mm insert.
SHELL_PAD_D, SHELL_PAD_GAP, SHELL_HEAD_SINK = 14.0, 0.2, 0.2
from soma.fasteners import Screw as _Screw, pick_length as _pick_length
import parts.cage as _cage_bosses
_shell_screws = []
if STEALTH and SHOW_CAGE:
    import math as _m
    for (_bx, _by, _bz, _sx, _br) in _cage_bosses.BOSS_LOG:
        _face = _bx + _sx * _br
        _f = _shells['Front shell']
        def _skin_x(y, z, _f=_f, _sx=_sx, _face=_face):      # outer skin along the axis direction at (y, z): the far end of the first wall from the boss face
            seg = _f.intersect(cq.Solid.makeCylinder(0.02, 40.0, cq.Vector(_face, y, z), cq.Vector(_sx, 0, 0)))
            xs = [v.X for v in seg.Vertices()]
            return (max(xs) if _sx > 0 else min(xs)) if xs else None
        _probe = _Screw("ISO 7380", "M3x10", at=(0, 0, 0))
        _rc = (_probe.head_diameter + 0.6) / 2
        _rim = [_skin_x(_by + _rc * _m.cos(a), _bz + _rc * _m.sin(a)) for a in [k * _m.pi / 8 for k in range(16)]]
        assert all(v is not None for v in _rim), 'shell fixing: no shell wall on the boss axis at y %.1f' % _by
        _top = (min(_rim) if _sx > 0 else max(_rim)) - _sx * SHELL_HEAD_SINK          # head top: below the skin everywhere on the counterbore rim
        _seat = _top - _sx * _probe.head_height
        _grip = abs(_seat - _face)
        _L = _pick_length("ISO 7380", "M3", _grip + 2.0, _grip + 4.0)
        _scr = _Screw("ISO 7380", "M3x%g" % _L, at=(_seat, _by, _bz), direction=('-X' if _sx > 0 else '+X'))
        _pad = cq.Solid.makeCylinder(SHELL_PAD_D / 2, 40.0, cq.Vector(_face + _sx * SHELL_PAD_GAP, _by, _bz), cq.Vector(_sx, 0, 0)).intersect(_ss.outer_solid(inset=1.0))
        _cb = cq.Solid.makeCylinder(_rc, 30.0, cq.Vector(_seat, _by, _bz), cq.Vector(_sx, 0, 0))
        _f = _f.fuse(_pad).clean().cut(_scr.clearance_hole()).cut(_cb).clean()
        assert _f.isValid() and len(_f.Solids()) == 1, 'shell fixing broke the Front shell'
        _shells['Front shell'] = _f
        _shell_screws.append(_scr)
        print('shell fixing: boss face x %.2f, skin on the rim x %.2f..%.2f, head top %.2f, grip %.2f mm, screw ISO 7380 M3x%g' % (_face, min(_rim), max(_rim), _top, _grip, _L))
add_part('Front shell',_shells['Front shell'],color=BODY,group='Print shell')
SILL_TAB_X0, SILL_TAB_W, SILL_TAB_H, SILL_TAB_GAP = 46.0, 12.0, 7.0, 0.1
if STEALTH:
    _f = _shells['Front shell']
    _deck_all = _ob0(_dfn).moved(cq.Location(_off)).fuse(_ob0(_drn).moved(cq.Location(_off)))
    for (_s0, _sx, _sy, _zt) in _sill_screws:
        _x0, _x1 = sorted((_sx * SILL_TAB_X0, _sx * 75.0))
        _tab = cq.Solid.makeBox(_x1 - _x0, SILL_TAB_W, SILL_TAB_H + 1.0, cq.Vector(_x0, _sy - SILL_TAB_W / 2, _zt - 1.0))
        _tab = _tab.intersect(_ss.outer_solid(inset=1.0)).cut(_deck_all.translate(cq.Vector(0, 0, SILL_TAB_GAP)))   # inside the skin, 0.1 mm off the deck top
        _tab = max(_tab.Solids(), key=lambda q: q.Volume())
        _f = _f.fuse(_tab).clean()
        _f = _f.cut(cq.Solid.makeCylinder(_cage_bosses.INSERT_M3_POCKET_D / 2, 5.0, cq.Vector(_sx * SILL_FIX_X, _sy, _zt), cq.Vector(0, 0, 1))).clean()   # M3 x 4 insert from below
        assert _f.isValid() and len(_f.Solids()) == 1, 'sill tab broke the Front shell at y %.1f' % _sy
    _shells['Front shell'] = _f
    print('sill fixing: %d tabs on the Front shell' % len(_sill_screws))
for _k, _scr in enumerate(_shell_screws): add_part('Shell screw %d' % (_k + 1), _scr, group='Hardware')
for _k, (_s0, _sx, _sy, _zt) in enumerate(_sill_screws): add_part('Sill screw %d' % (_k + 1), _s0, group='Hardware')
UP_STOPS = True    # up stop pads under the cage brace (the brace is the lean stop: the front hoop legs carry its 257 N, analyses/cage_upstop.py, NOTES)
if UP_STOPS and SHOW_CAGE and len(_UPPER_ARMS) == 2:   # up stops (lean stops): TPU saddles bonded under the cage's front brace (parts/stops.py up_stop_pad)
    for _sx in (1, -1):
        _up, _upc, _upd, _pilot, _ups = _stops.up_stop_pad(_sx, _UPPER_ARMS[_sx], _cage)
        assert _up.intersect(_cage).Volume() < 0.01, 'up stop pad overlaps the cage'
        _cage = _cage.cut(_pilot)       # M2 pilot hole for the pad's screw
        print('up stop pad', _sx, 'mm3', round(_up.Volume(), 1), 'at', tuple(round(v, 1) for v in _upc), 'arm to brace at the end pose %.2f mm' % _upd, 'arm psi %.2f' % _stops.up_psi(_sx), 'screw at', tuple(round(v, 1) for v in _ups))
        add_part('Up stop pad %d' % _sx, _up, group='Chassis/Stops', alpha=1, color=(0.05, 0.05, 0.05))
if SHOW_CAGE: add_part('Cage', _cage, color=(0.05, 0.05, 0.06), group='Cage')   # matt black so it disappears behind the shell windows
if _cabin and SHOW_CAGE:   # roof plate on the cage's roof frame (parts/roof_plate.py)
    from parts.cage import cabin_nodes as _cabn, CABIN_BEAM as _CBM, _half as _hf
    from parts.roof_plate import make_roof_plate
    _K, _A, _B = _cabn(_cabin)
    _roofp = make_roof_plate(_A, _B, _hf(_CBM), _cage)
    print('roof plate mm3', round(_roofp.Volume()), 'bbox z', round(_roofp.BoundingBox().zmin, 1), round(_roofp.BoundingBox().zmax, 1))
    add_part('Roof plate', _roofp, color=(0.19, 0.22, 0.26), group='Cage')   # roof colour of parts/params.py (ROOF is the roof trace here)
# open cockpit: no roof above the rear contact any more, so the rear contact (cage boss and block) is dropped; the tail light wiring runs along the cage
for _n, (_y, _sh) in {k: v for k, v in {'Front': (LIGHT_FRONT_Y, _shells['Front shell']), 'Rear': (LIGHT_REAR_Y, _shells.get('Canopy'))}.items() if v[1] is not None}.items():
    _rz = roof_underside(_sh, _y, 90.0)
    _, _block, _zd = make_connector(_y, _rz, _n, FRONT_LEG_X if _n == 'Front' else REAR_LEG_X, 0.0, legs=False,roof=_sh)
    _b0=_block.Volume(); _block=_block.cut(_sh).clean()   # E1: rear block sat 226 mm3 inside the canopy roof
    assert _block.isValid() and len(_block.Solids())==1 and _b0-_block.Volume()<400,'contact block trim failed'
    print('E1 contact block',_n,'trimmed mm3',round(_b0-_block.Volume(),1))
    if SHOW_CAGE: add_part(_n + ' light contact block', _block, color=(0.05, 0.05, 0.06), group='Cage/Light connectors')
