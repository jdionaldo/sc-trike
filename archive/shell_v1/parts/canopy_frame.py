"""Continuous window-frame panels: mitred outline and cut windows, no beam-end knuckles."""
import numpy as np
import cadquery as cq
from parts.params import *
from parts.reference_trace import ROOF, WINDOW_BELT, traced, belt_station,frame_belt
from parts.util import fuse, hull


def offset_polygon(points, distance):
    """Offset a simple straight-sided polygon with exact line-intersection mitres."""
    points=np.array(points,float)
    area=sum((a[0]*b[1]-a[1]*b[0]) for a,b in zip(points,np.roll(points,-1,axis=0)))
    sign=1 if area>0 else -1
    result=[]
    for i,b in enumerate(points):
        a=points[i-1]; c=points[(i+1)%len(points)]
        d0=b-a; d1=c-b
        n0=sign*np.array([d0[1],-d0[0]])/np.linalg.norm(d0)
        n1=sign*np.array([d1[1],-d1[0]])/np.linalg.norm(d1)
        q0=b+distance*n0; q1=b+distance*n1
        t=np.linalg.solve(np.column_stack((d0,-d1)),q1-q0)[0]
        result.append(tuple(q0+t*d0))
    return result


def outline(side=1):
    nodes=[WINDOW_BELT[0]]+ROOF+[WINDOW_BELT[-1]]
    raw=[frame_belt(p,side) for p in nodes]
    outer=offset_polygon([(y*Y_SCALE,z) for x,y,z in raw],FRAME_WIDTH/2)
    result=[(x+side*(WINDOW_RAIL_WIDTH/2 if i in (0,len(raw)-1) else FRAME_WIDTH/2),
             yz[0]/Y_SCALE,yz[1]) for i,((x,y,z),yz) in enumerate(zip(raw,outer))]
    x,y,z=traced(ROOF[-1],side)
    result[4]=(x+side*FRAME_WIDTH/2,y+FRAME_WIDTH/(2*Y_SCALE),z+FRAME_WIDTH/2)
    x,y,z=traced(WINDOW_BELT[0],side)
    result[0]=(x+side*WINDOW_RAIL_WIDTH/2,y-1.0/Y_SCALE,z-0.5)
    return result


def window_tools(grow=0.0):
    windows=[ [WINDOW_BELT[0],ROOF[0],ROOF[1],ROOF[2],belt_station(930)],
              [ROOF[2],ROOF[-1],belt_station(945),belt_station(930)] ]
    tools=[]
    for poly in windows:
        yz=[(traced(p)[1]*Y_SCALE,traced(p)[2]) for p in poly]
        # An enlarged frame pocket has slightly smaller window voids.
        inner=offset_polygon(yz,-FRAME_WIDTH/2-grow)
        tools.append(cq.Workplane('YZ').polyline(inner).close().extrude(100,both=True).val())
    return cq.Compound.makeCompound(tools)


def side_frame(side,grow=0.0):
    from parts.shell_geometry import skin,clearance_hull
    p=outline(side)
    triangles=[[p[i] for i in tri] for tri in [(0,1,2),(0,2,3),(0,3,5),(3,4,5)]]
    from parts.panels import panel_prisms
    from parts.shell_geometry import point
    panels=panel_prisms([[point(q) for q in tri] for tri in triangles],(-side,0,0),WALL)
    if grow:
        panels=[clearance_hull([v.toTuple() for v in p.Vertices()],grow) for p in panels]
    # The fascia owns the material below the belt. Trim the frame's obsolete
    # lower return before union, keeping only a small buried joining overlap.
    a,b=[point(frame_belt(q,side)) for q in WINDOW_BELT]
    slope=(b[2]-a[2])/(b[1]-a[1])
    def bottom(y):
        return a[2]+0.5+slope*(y-a[1])-PANEL_JOIN_OVERLAP-grow*(1+abs(slope))
    upper=cq.Workplane('YZ').polyline([(-200,bottom(-200)),(200,bottom(200)),(200,200),(-200,200)]).close().extrude(100,both=True).val()
    return fuse(panels).cut(window_tools(grow)).intersect(upper).clean()


def roof_panel(grow=0.0):
    from parts.shell_geometry import skin,clearance_hull
    left=outline(-1)[1:5];right=outline(1)[1:5]
    triangles=[]
    for i in range(3):
        triangles.extend([[left[i],right[i],right[i+1]],[left[i],right[i+1],left[i+1]]])
    from parts.panels import panel_prisms
    from parts.shell_geometry import point
    panels=panel_prisms([[point(q) for q in tri] for tri in triangles],(0,0,-1),WALL)
    if grow:
        panels=[clearance_hull([v.toTuple() for v in p.Vertices()],grow) for p in panels]
    return fuse(panels)


def sill_rail(side):
    """Keep the peg rail inside the skirt envelope, including its shallow hood end."""
    from parts.shell_geometry import sill_sections,beam,lower,point
    envelope=[]
    sections=sill_sections(side)
    for a,b in zip(sections,sections[1:]):
        pts=[]
        for top,bottom in (a,b):
            for p in (top,bottom):
                pts.extend([point(p),point((p[0]-side*2*WINDOW_RAIL_WIDTH,p[1],p[2]))])
        envelope.append(hull(pts))
    rail=beam(lower(traced(WINDOW_BELT[0],side)),lower(traced(belt_station(945),side)),WINDOW_RAIL_WIDTH)
    return rail.intersect(fuse(envelope)).clean()


def make_canopy():
    from parts.shell_geometry import sill_fascia
    pieces=[side_frame(-1),side_frame(1),roof_panel()]
    for side in (-1,1):
        pieces.append(sill_fascia(side))
    main=fuse(pieces).cut(window_edge_trim()).intersect(canopy_keep()).clean()
    # The triangular rear quarter covers behind the B-pillar belong to the canopy.
    return fuse([main]+[rear_side_cover(side) for side in (-1,1)]).clean()


def rear_side_cover(side,grow=0.0):
    """Triangular quarter cover restored per the 09:42 markup; roof stays open."""
    from parts.shell_geometry import sill_sections,point,clearance_hull
    from parts.panels import panel_prisms
    sections=sill_sections(side)
    # The refined fascia already contains the exact B-pillar foot station.
    station_y=traced(belt_station(930))[1]
    rear=[q for q in sections if q[0][1]>=station_y-1e-7]
    edge=[q[0] for q in rear]
    triangles=[[point(outline(side)[3]),point(a),point(b)] for a,b in zip(edge,edge[1:])]
    # Mesh the cover and its lower transition together so shared fold edges
    # get proper mitres, rather than two skins touching only on an edge.
    for a,b in zip(rear,rear[1:]):
        for tri in ([a[0],a[1],b[1]],[a[0],b[1],b[0]]):
            p=[point(q) for q in tri]
            if (cq.Vector(p[1])-cq.Vector(p[0])).cross(cq.Vector(p[2])-cq.Vector(p[0])).Length>1e-8:
                triangles.append(p)
    panels=panel_prisms(triangles,(-side,0,-1),WALL)
    if grow:
        panels=[clearance_hull([v.toTuple() for v in p.Vertices()],grow) for p in panels]
    return fuse(panels)


def canopy_keep(grow=0.0):
    """Shell ends at the B-pillar; the rear triangle is exposed tube framing."""
    from parts.shell_geometry import point
    top=point(outline(1)[3])
    foot=list(point(traced(belt_station(930))))
    foot[1]+=FRAME_WIDTH/2
    slope=(foot[1]-top[1])/(foot[2]-top[2])
    def edge(z):
        return top[1]+slope*(z-top[2])+grow*(1+abs(slope))
    return cq.Workplane('YZ').polyline([(-200,-40),(edge(-40),-40),
                                        (edge(200),200),(-200,200)]).close().extrude(100,both=True).val()


def window_edge_trim(grow=0.0):
    # Apply the opening profile to the roof-edge joins as well as the side skin.
    # This removes little overlapping triangles beneath the roof/A-pillar mitre.
    from parts.shell_geometry import box
    edge=ROOF[-1][2]-WALL-GLUE_GAP
    bands=cq.Compound.makeCompound([box((100,400,250),(side*(edge+50),0,80)) for side in (-1,1)])
    return window_tools(grow).intersect(bands)


def seat_tool(canopy):
    from parts.shell_geometry import sill_fascia
    tools=[side_frame(-1,GLUE_GAP),side_frame(1,GLUE_GAP),roof_panel(GLUE_GAP)]
    for side in (-1,1):
        tools.append(sill_fascia(side,GLUE_GAP))
    main=fuse(tools).cut(window_edge_trim(GLUE_GAP)).intersect(canopy_keep(GLUE_GAP)).clean()
    main=fuse([main]+[rear_side_cover(side,GLUE_GAP) for side in (-1,1)]).clean()
    assert main.isValid(), "Invalid canopy seat cutter"
    assert canopy.cut(main).Volume()<1e-6, "Canopy seat cutter misses canopy"
    return main
