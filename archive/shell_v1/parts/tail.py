"""Hollow faceted tail light housing with frame saddles and a recessed lens seat."""
import math
from parts.params import *

# Existing tail envelope and roof landing drive the replacement. The deck is
# level in the final pitched assembly; the centre stays open above the shock.
TAIL_HALF_BASE = 28.0
TAIL_OPEN_HALF_BASE = 20.5
TAIL_EDGE_HEIGHT = 11.0
TAIL_REAR_LANDING = 7.0
TAIL_FRONT_LANDING = 10.0
LIGHT_SEAT_DEPTH = 1.6 + 0.15 + WALL_PRINT
TAIL_SHORTEN = 40.0  # mm: inferred from the 09:43 termination markup
HOUSING_DEPTH = 48.0
TUBE_END_SETBACK = 34.0  # clears the rear face and the forward-facing LED sockets inside the housing


def stations(side=1):
    from parts.canopy_frame import outline
    from parts.reference_trace import traced
    front=outline(side)[4]
    rear_y=traced((1428,98,28))[1]-TAIL_SHORTEN/(SHELL_SCALE*Y_SCALE)
    from parts.reference_trace import WINDOW_BELT,frame_belt
    from parts.cage import CAGE_BEAM
    a,b=[final_point(frame_belt(p)) for p in WINDOW_BELT]
    slope=(b[2]-a[2])/(b[1]-a[1])
    angle=math.radians(SHELL_PITCH); c,s=math.cos(angle),math.sin(angle)
    cy,cz=-225.55+CHASSIS_Y,55.86+CHASSIS_Z
    ky=cy-c*cy+s*cz; kz=cz-s*cy-c*cz
    # The lower tail tube continues the sill line exactly. Its rear crossbar
    # sits beneath the middle of the compact 14 mm light housing.
    top_above_tube=CAGE_BEAM/2+WALL_PRINT+GLUE_GAP
    rear_z=(slope*(c*SHELL_SCALE*rear_y*Y_SCALE+ky-TUBE_END_SETBACK-a[1])+a[2]+top_above_tube
            -s*SHELL_SCALE*rear_y*Y_SCALE-kz)/(SHELL_SCALE*SHELL_Z*(c+slope*s))
    rear=(side*TAIL_HALF_BASE,rear_y,rear_z)
    dz=TAIL_EDGE_HEIGHT/(SHELL_SCALE*SHELL_Z)
    # Preserve the established light face rake, and its straight red profile.
    dy=dz*SHELL_Z*7.6/14.3/Y_SCALE
    rear_bottom=(rear[0],rear[1]-dy,rear[2]-dz)
    front_bottom=(front[0],front[1],front[2]-dz)
    return front,rear,rear_bottom,front_bottom


def final_point(p):
    from parts.shell_geometry import point
    x,y,z=point(p)
    angle=math.radians(SHELL_PITCH); c,s=math.cos(angle),math.sin(angle)
    cy,cz=-225.55+CHASSIS_Y,55.86+CHASSIS_Z
    return (x*SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH,
            c*SHELL_SCALE*y-s*SHELL_SCALE*SHELL_Z*z+cy-c*cy+s*cz,
            s*SHELL_SCALE*y+c*SHELL_SCALE*SHELL_Z*z+cz-s*cy-c*cz)


def light_face():
    _,top,bottom,_=stations()
    return (0.0,*final_point(top)[1:]),(0.0,*final_point(bottom)[1:])


def rear_profile():
    """Shared eight-sided housing/lens silhouette in the rear face plane."""
    half=TAIL_HALF_BASE*SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH
    shoulder=half-6.5
    return [(0,11.0),(shoulder,7.5),(half,0),(shoulder,-7.5),
            (0,-11.0),(-shoulder,-7.5),(-half,0),(-shoulder,7.5)]


def make_tail():
    """Faceted arrow housing in final coordinates, returned in shell-build space."""
    import cadquery as cq
    from parts.util import hull
    from parts.canopy_frame import offset_polygon
    from parts.cage import CAGE_BEAM,PILLAR_IN,REAR_SUP_X,CAGE_RAIL_X,RAIL_START_Y,CAGE_Z
    from parts.reference_trace import ROOF,traced,belt_station
    top,bottom=[cq.Vector(*p) for p in light_face()]
    centre=(top+bottom)*0.5
    up=(top-bottom).normalized()
    normal=cq.Vector(1,0,0).cross(up).normalized()
    if normal.y<0: normal=normal*-1
    half=TAIL_HALF_BASE*SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH
    crown=11.0
    profile=rear_profile()
    roof=tuple(round(v,1) for v in final_point(traced(ROOF[2])))
    upper=(roof[0]-PILLAR_IN,roof[1],roof[2]-CAGE_BEAM/2)
    end=(REAR_SUP_X,round(top.y-TUBE_END_SETBACK,1),
         round(top.z-WALL_PRINT-CAGE_BEAM/2-GLUE_GAP,1))
    lift=(upper[2]-end[2])/(end[1]-upper[1])
    diagonal_start=(CAGE_RAIL_X,RAIL_START_Y,CAGE_Z)
    lower_lift=(diagonal_start[2]-end[2])/(end[1]-diagonal_start[1])
    def rear(p,offset=0.0):
        x,v=p
        return centre+cq.Vector(x,0,0)+up*v-normal*offset
    def front(p,extra=0.0):
        x,v=p
        depth=HOUSING_DEPTH+extra
        # Fan the forward section around the entire converging tube bundle.
        # The upper lip follows the roof tubes, the bottom follows the long
        # chassis diagonals, rather than translating both along the roof slope.
        blend=(v+crown)/(2*crown)
        rise=lower_lift+(lift-lower_lift)*blend
        return rear(p)+cq.Vector(0,-depth,rise*depth)
    outer=hull([p.toTuple() for p in [rear(q) for q in profile]+[front(q) for q in profile]])
    inside=offset_polygon(profile,-WALL_PRINT)
    cavity=hull([p.toTuple() for p in [rear(q,LIGHT_SEAT_DEPTH) for q in inside]+
                 [front(q,8.0) for q in inside]])
    housing=outer.cut(cavity)
    # Internal saddles tie the compact housing to the frame without altering
    # its outside silhouette or exposing holes on the red lens face.
    r=CAGE_BEAM/2
    for side in (-1,1):
        rib=cq.Solid.makeBox(16,16,45,cq.Vector(side*end[0]-8,end[1]-8,end[2]-r-3))
        housing=housing.fuse(rib.intersect(outer))
    belt=tuple(round(v,1) for v in final_point(traced(belt_station(930))))
    starts=[upper,(upper[0],belt[1],belt[2]),(CAGE_RAIL_X,RAIL_START_Y,CAGE_Z)]
    cutters=[]
    def capsule(a,b,radius):
        a,b=cq.Vector(*a),cq.Vector(*b)
        return cq.Solid.makeCylinder(radius,(b-a).Length,a,b-a).fuse(
            *[cq.Solid.makeSphere(radius,p,angleDegrees1=-90,angleDegrees2=90) for p in (a,b)])
    for side in (-1,1):
        e=cq.Vector(side*end[0],end[1],end[2])
        for start in starts:
            a=cq.Vector(side*start[0],start[1],start[2])
            a=e+(a-e).normalized()*(2*HOUSING_DEPTH)
            cutters.append(capsule(a.toTuple(),e.toTuple(),r+GLUE_GAP))
    cutters.append(capsule((-end[0],end[1],end[2]),end,r+GLUE_GAP))
    # Cut overlapping tube envelopes one at a time. Passing the overlapping
    # capsules as a compound can invert the result into a saddle remnant.
    for cutter in cutters:
        housing=housing.cut(cutter).clean()
        assert housing.isValid(), 'Invalid tail frame clearance cut'
    assert housing.BoundingBox().xlen >= 2*half-0.01, 'Tail housing lost its outer walls'
    assert housing.isValid() and len(housing.Solids())==1, 'Tail housing must be one solid'
    # Inverse of model.py's final scale/pitch: soma build remains the STEP writer.
    angle=math.radians(SHELL_PITCH); c,s=math.cos(angle),math.sin(angle)
    sx,sz=SHELL_SCALE,SHELL_SCALE*SHELL_Z
    wx=SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH
    cy,cz=-225.55+CHASSIS_Y,55.86+CHASSIS_Z
    ky=cy-c*cy+s*cz; kz=cz-s*cy-c*cz
    inverse=cq.Matrix([[1/wx,0,0,0],[0,c/sx,s/sx,(-c*ky-s*kz)/sx],
                       [0,-s/sz,c/sz,(s*ky-c*kz)/sz]])
    return [housing.transformGeometry(inverse)]
