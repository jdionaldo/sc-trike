"""Watertight faceted shell construction and print checks."""
import cadquery as cq
from parts.util import hull, fuse
from parts.params import *

def point(p):
    x, y, z = p
    scale = 1.0   # the plan width warp lives in reference_trace.traced() so every traced point agrees
    # Keep the grille at the tip; sweep the light corners back in plan.
    sweep = NOSE_SWEEP * max(0, min(1, (-111-y)/28)) * max(0, min(1, (abs(x)-24)/31))
    rake_weight = max(0.0, min(1.0, (NOSE_BLEND_END-y)/(NOSE_BLEND_END+134.0)))
    rake = NOSE_RAKE*(NOSE_TOP-z)/NOSE_HEIGHT*rake_weight
    return (x*scale, (y+sweep+rake)*Y_SCALE, z)
def rake_nose(s):
    """Same shear for the grille, its opening and its backstop, all ahead of the blend."""
    k=NOSE_RAKE/NOSE_HEIGHT*Y_SCALE
    return s.transformGeometry(cq.Matrix([[1,0,0,0],[0,1,-k,k*NOSE_TOP],[0,0,1,0],[0,0,0,1]]))

def clearance_hull(points,grow=0.0):
    """Convex faceted pocket with a conservative, uniform clearance around the actual solid."""
    if grow:
        # Near-uniform normal offset: 26 unit directions (every facet is pushed out by 0.93..1.0 x grow, not 1.0..1.73 x
        # as with a +-grow cube at every point).
        import itertools, math
        dirs=[tuple(c/math.sqrt(sum(k*k for k in d)) for c in d) for d in itertools.product((-1,0,1),repeat=3) if any(d)
              for d in [d]]
        points=[(x+grow*dx*PANEL_KX,y+grow*dy,z+grow*dz) for x,y,z in points for dx,dy,dz in dirs]   # x is stretched less than y/z
    return hull(points)

def box(size,at):
    return cq.Workplane('XY').box(*size).val().translate(at)
def skin(triangles,direction,thickness=None):
    from parts.panels import panel_prisms
    facets=[[point(p) for p in tri] for tri in triangles]
    return fuse(panel_prisms(facets,direction,WALL if thickness is None else thickness))
def triangle(pts,direction):
    return skin([pts],direction)
def beam(a,b,width=4):
    # Polygonal structural frame rather than rounded tubes.
    a,b=cq.Vector(point(a)),cq.Vector(point(b)); d=b-a
    ref=cq.Vector(1,0,0) if abs(d.normalized().x)<0.9 else cq.Vector(0,1,0)
    side=d.cross(ref).normalized()*width/2
    cross=d.normalized().cross(side).normalized()*width/2
    w=cq.Wire.makePolygon([a+side+cross,a+side-cross,a-side-cross,a-side+cross],close=True)
    return cq.Solid.extrudeLinear(w,[],d)
def checked(s,name):
    s=s.clean()
    assert s.isValid() and len(s.Solids())==1, f'{name}: expected one watertight solid, got {len(s.Solids())}'
    # A CAD-valid solid can still contain edge-only joins that break slicers.
    from soma.meshexport import body_meshes, problems
    issues=problems(body_meshes(s,name,tol=0.01,ang=0.05))
    assert not issues, f'{name}: print mesh failed validation: {issues}'
    return s

def split_on_creases(shell):
    """Follow existing side-facet edges from the sill to the rocker, mirrored on both sides."""
    from parts.reference_trace import traced, belt_station
    landmarks = [(836,446,46), (943,345,62), belt_station(1082)]
    seam = [(point(traced(p))[1], point(traced(p))[2]) for p in landmarks]
    # Continue beyond the shell; only the interior ledges cross the hidden extensions.
    seam = [(seam[0][0], -40)] + seam + [(seam[-1][0], 160)]
    def mask(outside):
        return (cq.Workplane('YZ').polyline(outside + seam).close()
                .offset2D(-CLEARANCE/2, kind='intersection').extrude(100, both=True).val())
    front = shell.intersect(mask([(-200,160), (-200,-40)]))
    rear = shell.intersect(mask([(200,160), (200,-40)]))
    # Thin inner bevels can cross the projected crease. Reassign those small
    # fragments to the adjoining front/rear panel rather than dropping material.
    def separate(part):
        solids=sorted(part.Solids(),key=lambda so:so.Volume(),reverse=True)
        assert all(so.Volume()<SEAM_CHIP_LIMIT for so in solids[1:]), 'Crease split disconnected a panel'
        return solids[0], [so for so in solids[1:] if so.Volume()>=5.0]
    front,front_chips=separate(front); rear,rear_chips=separate(rear)
    def recover(part,chips):
        for chip in chips:
            tool=clearance_hull([v.toTuple() for v in chip.Vertices()],CLEARANCE)
            part=part.fuse(shell.intersect(tool))
        return part.clean()
    return recover(front,rear_chips), recover(rear,front_chips)

SEAT_BLEND = 14.0   # mm: stub length of cowl rail and seat rail that are hulled into one faired corner

LEDGE_W = 7.0       # mm: inner ledge width, measured inward from the door panel's outer face
LEDGE_TOP = 4.0     # mm: ledge top below the belt line (canopy rail bottom is 3.5 mm below it, so 0.5 mm glue gap)
PEG_D = 2.0; PEG_L = 4.5; PEG_OFF = 1.6   # peg diameter, length, inward offset from the belt line
HOLE_CLEAR = 0.3; HOLE_DEPTH = 5.2
PEG_PX = (560, 700, 840)            # peg stations (pixel X along the belt)

def inner_ledge(side):
    """Small internal peg ledge with a root below the skirt seam; no exposed rear tie block."""
    from parts.reference_trace import traced,belt_station
    sections=[]
    for px in (520,560,700,840,930,1000):
        x,y,z=traced(belt_station(px))
        root_z=z-SILL_BLEND_DEPTH-WALL
        root_x=side_surface_x(y,root_z)-WALL/2
        sections.append([(side*x,y,z-LEDGE_TOP),(side*(x-LEDGE_W),y,z-LEDGE_TOP),
                         (side*(x-LEDGE_W),y,z-LEDGE_TOP-WALL),(side*root_x,y,root_z)])
    return fuse([hull([point(p) for p in a+b]) for a,b in zip(sections,sections[1:])])

def strip_dust(s,min_volume=5.0):
    """Pocket cuts can leave slivers of a few hundredths of a mm3 on the thin panel top: drop them."""
    keep=[so for so in s.Solids() if so.Volume()>=min_volume]
    return keep[0] if len(keep)==1 else cq.Compound.makeCompound(keep)

def peg_points(side):
    from parts.reference_trace import traced, belt_station
    out=[]
    for px in PEG_PX:
        q=traced(belt_station(px),side)
        out.append((q[0]-side*PEG_OFF,q[1],q[2]-RAIL_DROP-WINDOW_RAIL_WIDTH/2))   # on the rail's bottom face
    return out

def grille_seat_tool(grille):
    return clearance_hull([v.toTuple() for v in grille.Vertices()],PANEL_GAP_M)

HOOD_EDGE_DROP = (0.8, 1.05)   # mm at the nose / rear hood corner: the hood edge sits this far lower so it meets the cheek facet flush (no ridge)

def hood_edge(p, side=1):
    """Traced hood corner with its z lowered to the cheek top."""
    from parts.reference_trace import traced
    x,y,z=traced(p,side)
    from parts.reference_trace import HOOD
    drop=HOOD_EDGE_DROP[0 if p==HOOD[0] else 1]
    return (x,y,z-drop/(SHELL_SCALE*SHELL_Z))

def flank_surface_x(y, z):
    """Exact X coordinate on the front-upper flank facet (mesh(SIDE, 1, CREASES)[0]), continuing its plane past the A-pillar foot."""
    from parts.reference_trace import SIDE, CREASES, mesh
    a, b, c = [cq.Vector(*p) for p in mesh(SIDE, 1, CREASES)[0]]
    n = (b - a).cross(c - a).normalized()
    if n.x < 0: n = -n
    return (n.dot(a) - n.y * y - n.z * z) / n.x

def hood_centres():
    """Centre-line heights (raw trace frame) that make each hood quad exactly planar.

    A quad (centre, outer, outer', centre') is planar only when the second centre height follows from the first,
    so the hood no longer folds along a diagonal ridge."""
    from parts.reference_trace import HOOD,traced
    a,b,front,back=hood_edge(HOOD[0]),hood_edge(HOOD[1]),hood_edge(HOOD[-2]),traced(HOOD[-1])
    yb, zb = back[1]+SEAT_WIDTH/2, back[2]+0.5
    back=(flank_surface_x(yb, zb), yb, zb)
    c0=a[2]+1.5
    c1=b[2]+(c0-a[2])*b[0]/a[0]
    c2=back[2]+(c1-front[2])*back[0]/front[0]
    return c0,c1,c2

def hood_outer_limits():
    """Clip cheek offsets below the hood planes, eliminating the raised brow return."""
    from parts.reference_trace import HOOD,traced
    facets=[]
    for side in (-1,1):
        c0,c1,c2=hood_centres()
        a,b=[hood_edge(p,side) for p in HOOD[:2]]
        ca=(0,a[1],c0);cb=(0,b[1],c1)
        facets.extend([[ca,a,b],[ca,b,cb]])
        front=hood_edge(HOOD[-2],side);back=traced(HOOD[-1],side)
        yb, zb = back[1]+SEAT_WIDTH/2, back[2]+0.5
        back=(side*flank_surface_x(yb, zb), yb, zb)
        top=[(0,front[1],c1),front,back,(0,back[1],c2)]
        facets.extend([[top[0],top[1],top[2]],[top[0],top[2],top[3]]])
    result=None
    for tri in facets:
        a,b,c=[cq.Vector(point(p)) for p in tri]
        n=(b-a).cross(c-a).normalized()
        if n.z<0:n=-n
        tool=cq.Workplane(cq.Plane(origin=a,normal=n)).rect(600,600).extrude(-300).val()
        result=tool if result is None else result.intersect(tool)
    return result

def make_quarter_wing(side, opening):
    """One hollow polyhedral wing avoids intersecting offset-skin corner caps."""
    import numpy as np
    from scipy.spatial import ConvexHull, HalfspaceIntersection
    from scipy.optimize import linprog
    from parts.reference_trace import QUARTER, traced, belt_station
    landmarks=QUARTER+[(815,204,50)]
    vertices=[point(traced(p,side)) for p in landmarks]
    # Root below the canopy skirt instead of leaving a feather-thin return
    # inside its seat pocket. The side wall supplies the continuous landing.
    _,root_y,root_z=traced(belt_station(930))
    root_z-=SILL_BLEND_DEPTH+GLUE_GAP
    vertices.append(point((side*(side_surface_x(root_y,root_z)-PANEL_JOIN_OVERLAP),root_y,root_z)))
    # Start the leading ramp on the body ahead of the wing. This closes the
    # transverse scoop face with a swept deflector at both upper/lower edges.
    for py in (204,282):
        _,y,z=traced((WING_LEAD_IN_PX,py,0))
        vertices.append(point((side*(side_surface_x(y,z)-PANEL_JOIN_OVERLAP),y,z)))
    vertices=np.array(vertices)
    # Master-surface coplanarity on the quarter wing: align V[1] onto the outer wing plane [0,5,2],
    # V[7] onto the upper wing plane [4,8,2] (eliminating the 7.07 deg near-miss), and the leading deflector
    # roots V[8], V[9] onto the inner wing plane [6,0,3], eliminating 2.7-7.1 deg near-misses.
    for plane_idx, targets in (((0,5,2), (1,)), ((6,0,3), (8,9))):
        a,b,c = [vertices[i] for i in plane_idx]
        n = np.cross(b-a, c-a)
        for t in targets:
            vertices[t,0] = a[0] - (n[1]*(vertices[t,1]-a[1]) + n[2]*(vertices[t,2]-a[2]))/n[0]
    a,b,c = [vertices[i] for i in (4,8,2)]
    n = np.cross(b-a, c-a)
    vertices[7,2] = a[2] - (n[0]*(vertices[7,0]-a[0]) + n[1]*(vertices[7,1]-a[1]))/n[2]
    envelope=ConvexHull(vertices)
    planes=np.unique(np.round(envelope.equations,6),axis=0)
    # Every cavity plane is one printed wall inward from its matching outer facet (the offset depends on the facet's direction,
    # see printed_thickness).
    from parts.panels import printed_thickness
    cavity=planes.copy();cavity[:,3]+=[printed_thickness(q[:3],WALL) for q in planes]
    fit=linprog([0,0,0,-1],A_ub=np.column_stack((cavity[:,:3],np.ones(len(cavity)))),
                b_ub=-cavity[:,3],bounds=[(None,None)]*3+[(0,None)],method='highs')
    assert fit.success and fit.x[3]>0.1, 'Quarter wing cavity is too small'
    inside=HalfspaceIntersection(cavity,fit.x[:3]).intersections
    wing=hull(vertices).cut(hull(inside)).cut(opening)
    # A buried edge mitre gives the new lower return a finite-width root;
    # two closed skins touching only on this edge are nonmanifold in a slicer.
    a,b,c=[np.array(point(traced(p,side))) for p in [(940,286,60),(1082,144,43),(943,345,62)]]
    n=np.cross(b-a,c-a);n/=np.linalg.norm(n)
    if n[0]*side>0:n=-n
    inward=fit.x[:3]-(a+b)/2
    inward/=np.linalg.norm(inward)
    root=hull([a,b,a+n*WALL,b+n*WALL,a+inward*WALL,b+inward*WALL])
    return wing.fuse(root).clean()

def make_shell():
    from parts.reference_trace import SIDE, CREASES, TAIL, QUARTER, HOOD, CHEEK, INTAKES, WINDOW_BELT, WING_OPENING, traced, mesh, belt_station, triangulate
    def tail_traced(p,side):
        x,y,z=traced(p,side)
        if p==(1135,98,31):
            # Land the tail on the rear OUTER top corner of the flush roof header.
            from parts.canopy_frame import outline
            return outline(side)[4]
        return (x,y,z)
    def tail_mesh(poly,side):
        return [[tail_traced(p,side) for p in tri] for tri in triangulate(poly)]
    aperture_points=[traced((px,py,0)) for px,py in WING_OPENING]
    opening=cq.Workplane('YZ',origin=(55,0,0)).polyline([(q[1]*Y_SCALE,q[2]) for q in aperture_points]).close().extrude(40).val()
    wing_tool=cq.Compound.makeCompound([opening,opening.mirror('YZ')])
    # Follow the actual wing fold, removing the narrow dangling return below it.
    side_outline=list(SIDE)
    _,qy,qz=traced((1000,210,54))
    fold=(1000,210,side_surface_x(qy,qz))
    rear_corner=next(i for i,p in enumerate(side_outline) if p[0]==1082)
    side_outline.insert(rear_corner+1,fold)
    shapes=[]
    for side in (-1,1):
        # The diagonal return below the intake continues to the marked rocker point.
        main_outline=[p for p in side_outline if p[0]!=943]
        facets=mesh(main_outline,side,CREASES)
        facets.extend([[traced(p,side) for p in tri] for tri in [
            [(889,319,56),(943,345,62),(836,446,46)],
            [(889,319,56),(940,286,60),(943,345,62)],
            [(940,286,60),(1082,144,43),(943,345,62)]]])
        shapes.append(skin(facets,(-side,0,0)).cut(sill_body_tool()))
        # The rear quarter cover is part of the canopy (parts/canopy_frame.py), not of the front shell.
        # Shared planar envelope replaces the accumulated wing/return/web overlaps.
        shapes.append(make_quarter_wing(side,wing_tool))
        # Short hood cheek stops at the front wheel cutout instead of filling it.
        cheek=list(CHEEK)   # shared with the flank regularization (parts/reference_trace.py)
        shapes.append(skin(mesh(cheek,side),(-side,0,0)).intersect(hood_outer_limits()))
    # Hood retains the traced station edges. The tail is now an open flat deck.
    for stations in (HOOD[:-1],):
        facets=[]
        for a,b in zip(stations,stations[1:]):
            for side in (-1,1):
                trace=traced if stations[0]==HOOD[0] else tail_traced
                pa,pb=hood_edge(a,side),hood_edge(b,side)
                ca=(0,pa[1],hood_centres()[HOOD.index(a)])
                cb=(0,pb[1],hood_centres()[HOOD.index(b)])
                facets.extend([[ca,pa,pb],[ca,pb,cb]])
        shapes.append(skin(facets,(0,0,-1)))
    # A shallow cowl continues the hood facets and ties both A-pillar seats underneath.
    shapes.append(make_cowl())
    # Grille frame, elevated like the reference nose above the wheel cutout.
    nose=hull([point(p) for p in [(-NOSE_BASE_HALF,-139,25),(NOSE_BASE_HALF,-139,25),(-24,-139,57),(24,-139,57),
               (-NOSE_BASE_HALF,-134,25),(NOSE_BASE_HALF,-134,25),(-24,-134,57),(24,-134,57)]])
    aperture=cq.Workplane('XZ').polyline([(-12,29),(12,29),(20,52),(-20,52)]).close().extrude(15,both=True).val().translate((0,-139*Y_SCALE,0))
    aperture=rake_nose(aperture)
    shapes.append(nose.cut(aperture))
    s=fuse(shapes)
    # Lower side panels remain continuous: former rocker apertures filled.
    slot=[(-5,106),(5,106),(8,111),(8,130),(5,134),(-5,134),(-8,130),(-8,111)]
    vent=cq.Workplane('XY').polyline([(x,y*Y_SCALE) for x,y in slot]).close().extrude(80).val().translate((0,0,60))
    s=s.cut(vent)
    # Intake tools act only on the quarter wings; the inner body skin stays closed.
    # Backstop rim for the separate grille, 0.15 mm behind its rear face.
    lip=cq.Workplane('XZ').polyline([(-14,28),(14,28),(22,53),(-22,53)]).close().polyline([(-10,31),(10,31),(17,50),(-17,50)]).close().extrude(2.0).val().translate((0,-136*Y_SCALE+GLUE_GAP+2,0))
    s=s.fuse(rake_nose(lip))
    # Only the old rear paint guide remains; the nose uses a separate lens
    # and matching channel, so its obsolete groove is removed.
    for side in (-1,1):
        s=s.cut(beam((side*2,137.8,89),(side*25,137.8,89),1.6))
    # All inner mitres at the shoulder terminate on one common trailing plane.
    tip_y=point(traced(WINDOW_BELT[-1]))[1]
    limit=cq.Solid.makeBox(500,tip_y+400,400,cq.Vector(-250,-400,-100))
    return s.intersect(limit).clean()

def lower(p):
    """Sill rail sits RAIL_DROP lower so its top is flush with the shell's top edge."""
    return (p[0],p[1],p[2]-RAIL_DROP)


def make_cowl():
    """Flush hood-to-windscreen landing, reinforced below instead of a raised square crossbar."""
    from parts.reference_trace import traced, HOOD
    panels=[]
    for side in (-1,1):
        front=hood_edge(HOOD[-2],side); back=traced(HOOD[-1],side)
        c0,c1,c2=hood_centres()
        yb, zb = back[1]+SEAT_WIDTH/2, back[2]+0.5
        top=[(0,front[1],c1),front,
             (side*flank_surface_x(yb, zb), yb, zb),
             (0,yb,c2)]
        panels.append(skin([[top[0],top[1],top[2]],[top[0],top[2],top[3]]],(0,0,-1)))
    return fuse(panels)

def side_surface_x(y,z):
    import numpy as np
    from parts.reference_trace import SIDE,CREASES,mesh
    for tri in mesh(SIDE,1,CREASES):
        pts=np.array(tri)
        weights=np.linalg.solve(np.vstack((pts[:,1],pts[:,2],np.ones(3))),[y,z,1])
        if min(weights)>=-1e-7:
            return float(weights@pts[:,0])
    raise ValueError('Sill root extends beyond the side panel')

def sill_sections(side):
    import numpy as np
    from parts.canopy_frame import outline
    from parts.reference_trace import SIDE,CREASES,mesh,belt_station,traced,shoulder_station
    triangles=mesh(SIDE,1,CREASES)
    frame=outline(1)
    # Use the single lower window-sill plane (0,3,5) so upper roof/A-pillar fold lines never crease the sill fascia.
    sill_tri=np.array([frame[0],frame[3],frame[5]])
    def frame_x(y,z):
        weights=np.linalg.solve(np.vstack((sill_tri[:,1],sill_tri[:,2],np.ones(3))),[y,z,1])
        return float(weights@sill_tri[:,0])
    stations=[(457,2.5),(500,SILL_BLEND_DEPTH),(622,SILL_BLEND_DEPTH),
              (730,SILL_BLEND_DEPTH),(930,SILL_BLEND_DEPTH),   # no station at 815: it lies on a straight run of the lower edge and only added two facets
              
              (945,SILL_BLEND_DEPTH),(SILL_END_PX,6.0),(1082,0.0)]
    # Split exactly where the lower seam crosses a body-facet edge, so the
    # fascia cannot bridge a fold and leave a stepped or open lower edge.
    refined=[]
    for a,b in zip(stations,stations[1:]):
        qa,qb=traced(shoulder_station(a[0])),traced(shoulder_station(b[0]))
        start=np.array([qa[1],qa[2]-a[1]])
        delta=np.array([qb[1],qb[2]-b[1]])-start
        knots={0.0,1.0}
        for tri in triangles:
            for v,w in zip(tri,tri[1:]+tri[:1]):
                origin=np.array(v[1:]); edge=np.array(w[1:])-origin
                matrix=np.column_stack((delta,-edge))
                if abs(np.linalg.det(matrix))<1e-9:
                    continue
                t,u=np.linalg.solve(matrix,origin-start)
                if 1e-7<t<1-1e-7 and -1e-7<=u<=1+1e-7:
                    knots.add(round(float(t),10))
        refined.extend((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])) for t in sorted(knots)[:-1])
    refined.append(stations[-1])
    sections=[]
    for px,depth in refined:
        x,y,z=traced(shoulder_station(px))
        # The end at the tail tapers into the existing quarter-window panel.
        outer=side_surface_x(y,z-depth)
        bottom=(side*outer,y,z-depth)
        if px>930:
            start=traced(belt_station(930))
            end=traced(shoulder_station(1082))
            t=(px-930)/(1082-930)
            top_x=(1-t)*frame_x(start[1],start[2]+0.5)+t*end[0]
        else:
            top_x=frame_x(y,z+0.5)
        top=bottom if px==1082 else (side*top_x,y,z+0.5)
        sections.append([top,bottom])
    # One flat fascia instead of a zig-zag of twisted quads: the sill tops up to the B-pillar lie on one straight line, so put
    # the lower edge of those stations on the best plane through that line (a nudge of SILL_PLANE_NUDGE at most, off the body
    # facet it sat on). Stations that would move further (the rear, where the body turns inward) keep their traced point.
    front=[i for i,(px,_) in enumerate(refined) if px<=SILL_PLANE_END_PX]
    if len(front)>=3:
        T=np.array([sections[i][0] for i in front]); B=np.array([sections[i][1] for i in front])
        axis=T[-1]-T[0]; axis/=np.linalg.norm(axis)
        drops=[(b-t)-((b-t)@axis)*axis for t,b in zip(T,B)][2:]            # the first two stations are the short front taper
        drop=np.mean(drops,axis=0); normal=np.cross(axis,drop); normal/=np.linalg.norm(normal)
        for i,t,b in zip(front,T,B):
            x=T[0][0]-(normal[1]*(b[1]-T[0][1])+normal[2]*(b[2]-T[0][2]))/normal[0]
            if abs(x-b[0])<=SILL_PLANE_NUDGE:
                sections[i][1]=(float(x),b[1],b[2])
    return sections

def sill_fascia(side,grow=0.0):
    from parts.panels import panel_prisms
    if grow and side == 1:
        # Construct the symmetric pocket once. Independent right-hand hulls
        # trigger unstable booleans at the shallow rear mitres.
        return sill_fascia(-1,grow).mirror("YZ")
    sections=sill_sections(side)
    facets=[]
    for a,b in zip(sections,sections[1:]):
        for tri in ([a[0],a[1],b[1]],[a[0],b[1],b[0]]):
            u=cq.Vector(tri[1])-cq.Vector(tri[0]);v=cq.Vector(tri[2])-cq.Vector(tri[0])
            if u.cross(v).Length>1e-8:
                facets.append(tri)
    panels=panel_prisms([[point(p) for p in tri] for tri in facets],(-side,0,0),WALL)
    # The trailing skirt's inward normal points partly upward. Trim its raised
    # return to the same top plane as the sill instead of leaving a separate tab.
    from parts.reference_trace import WINDOW_BELT,traced,frame_belt
    a,b=[point(frame_belt(p,side)) for p in WINDOW_BELT]
    slope=(b[2]-a[2])/(b[1]-a[1])
    def top(y):
        return a[2]+0.5+slope*(y-a[1])+grow*(1+abs(slope))
    cap=cq.Workplane('YZ').polyline([(-200,-40),(200,-40),(200,top(200)),(-200,top(-200))]).close().extrude(100,both=True).val()
    if grow:
        actual=sill_fascia(side)
        envelope=[]
        for p in panels:
            pc=p.intersect(cap)
            if pc.Volume()>1e-8:
                envelope.append(clearance_hull([v.toTuple() for v in pc.Vertices()],grow))
        pocket=fuse(envelope)
        assert pocket.isValid(), "Invalid sill clearance cutter"
        assert actual.cut(pocket).Volume()<1e-6, "Sill cutter misses fascia"
        return pocket
    return fuse(panels).intersect(cap).clean()

def sill_body_tool():
    # The canopy skirt REPLACES this band; don't leave a second paper-thin wall behind it.
    sections=sill_sections(1)
    bottom=[(q[1][1]*Y_SCALE,q[1][2]+PANEL_JOIN_OVERLAP) for q in sections]
    polygon=[(bottom[0][0]-GLUE_GAP,bottom[0][1])]+bottom+[(bottom[-1][0]+GLUE_GAP,bottom[-1][1]),
             (bottom[-1][0]+GLUE_GAP,150),(bottom[0][0]-GLUE_GAP,150)]
    return cq.Workplane('YZ').polyline(polygon).close().extrude(100,both=True).val()

def make_canopy():
    from parts.canopy_frame import make_canopy as build_frame
    return build_frame()

def canopy_seat_tool(canopy):
    from parts.canopy_frame import seat_tool
    return seat_tool(canopy)

def make_grille():
    outline=[(-11.6,29.4),(11.6,29.4),(19.3,51.5),(-19.3,51.5)]
    s=cq.Workplane('XZ').polyline(outline).close().extrude(2.5).val().translate((0,-136*Y_SCALE,0))
    holes=[]
    for r in range(5):
        for c in range(-5,6):
            x=c*4.5+(r%2)*2.25; z=32.4+r*4.0
            if abs(x)>9+(z-30)*.28: continue
            holes.append(cq.Workplane('XZ').center(x,z).polygon(6,3.0).extrude(0.6).val().translate((0,-138.0*Y_SCALE,0)))
    return rake_nose(s.cut(cq.Compound.makeCompound(holes)))
