"""Manually traced landmarks in Screenshot 2026-11-10 at 2.44.31 PM.png.
Pixel X follows vehicle length, pixel Y points down. A uniform calibration
maps the visible shell from pixel 280 to 1428 onto 278 mm. The rocker is Y=450.
Mechanical parts, mirrors and roof lights are deliberately excluded.
"""
PIXEL_FRONT=280.0
PIXEL_REAR=1428.0
PIXEL_ROCKER=450.0
MM_PER_PIXEL=278.0/(PIXEL_REAR-PIXEL_FRONT)

# Every entry is (image X, image Y, transverse half-width in mm).
SIDE=[(437,219,56),(457,170,50),(622,234,46),(815,204,50),(930,157,44),
      (1082,144,43),(940,286,60),(889,319,56),(943,345,62),
      (836,446,46),(473,435,35),(522,368,48),(510,259,61)]
CREASES=[(674,295,57),(650,359,45),(825,414,45)]
TAIL=[(1082,144,43),(1135,98,31),(1241,33,28),(1428,70,28),
      (1412,100,27),(1316,119,25),(1237,171,24),(1195,232,24),
      (1143,239,25),(1127,220,29),(1165,145,32)]
QUARTER=[(889,319,56),(826,282,66),(928,174,69.5),
         (1082,144,43),(1000,210,54),(940,286,60)]
ROOF=[(660,63,34),(760,33,34),(905,12,34),(1135,98,31)]
HOOD=[(280,214,24),(390,174,42),(457,170,50)]
INTAKES=[[(538,420),(620,394),(720,381),(664,412)],
         [(690,422),(780,415),(865,363)]]
# Lower window sill: one single straight rail, angled up from the A-pillar to the rear canopy corner.
WINDOW_BELT=[(457,170,50),(1082,144,43)]
def belt_station(px):
    for a,b in zip(WINDOW_BELT,WINDOW_BELT[1:]):
        if a[0] <= px <= b[0]:
            t=(px-a[0])/(b[0]-a[0])
            return (px,a[1]+t*(b[1]-a[1]),a[2]+t*(b[2]-a[2]))
    raise ValueError(f'Belt station {px} is outside the sill')
# Bring the body top up to the same line instead of leaving the old dipped edge.
SIDE=[belt_station(p[0]) if p[0] in (457,622,815,930,1082) else p for p in SIDE]
from parts.params import WHEEL_NOTCH_HALF_WIDTH
SIDE=[(px,py,WHEEL_NOTCH_HALF_WIDTH if px==510 else width) for px,py,width in SIDE]
WING_OPENING=[(870,260),(943,192),(1005,160),(956,230),(914,275)]

def plan_width(y):
    """Transverse width factor at blueprint station y (mm): slims the cabin, full width at nose and tail."""
    from parts.params import PLAN_STATIONS
    if y<=PLAN_STATIONS[0][0]: return PLAN_STATIONS[0][1]
    for (ya,sa),(yb,sb) in zip(PLAN_STATIONS,PLAN_STATIONS[1:]):
        if ya<=y<=yb: return sa+(sb-sa)*(y-ya)/(yb-ya)
    return PLAN_STATIONS[-1][1]

def traced(p,side=1):
    px,py,x=p
    if px==1082 and abs(py-144)<1e-8:
        from parts.params import REAR_SHOULDER_WIDTH,REAR_SHOULDER_PY
        x=REAR_SHOULDER_WIDTH
        py=REAR_SHOULDER_PY
    if px==928 and abs(py-174)<1e-8:
        py=230.0
    y=(px-PIXEL_FRONT)*MM_PER_PIXEL-139
    return (side*x*plan_width(y),y,(PIXEL_ROCKER-py)*MM_PER_PIXEL)


def frame_belt(p,side=1):
    """Virtual straight window rail is independent of the lowered shoulder tip."""
    px,py,width=p
    if px==1082:
        y=(px-PIXEL_FRONT)*MM_PER_PIXEL-139
        from parts.params import REAR_SHOULDER_WIDTH
        return (side*REAR_SHOULDER_WIDTH*plan_width(y),y,(PIXEL_ROCKER-144)*MM_PER_PIXEL)
    return traced(p,side)


def shoulder_station(px):
    """The body shoulder drops after the B-pillar, while the main window stays straight."""
    if px<=930:
        return belt_station(px)
    from parts.params import REAR_SHOULDER_WIDTH,REAR_SHOULDER_PY
    a=belt_station(930);t=(px-930)/(1082-930)
    return (px,a[1]+t*(REAR_SHOULDER_PY-a[1]),a[2]+t*(REAR_SHOULDER_WIDTH-a[2]))

def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def inside(p,a,b,c):
    q=[cross(a,b,p),cross(b,c,p),cross(c,a,p)]
    return min(q)>=-1e-7 or max(q)<=1e-7

def triangulate(poly,interior=()):
    """Ear clipping keeps concave traced panel boundaries exact."""
    poly=list(poly)
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))
    orientation=1 if area>0 else -1
    remaining=list(range(len(poly))); result=[]
    while len(remaining)>3:
        for k,i in enumerate(remaining):
            a,b,c=[poly[j] for j in (remaining[k-1],i,remaining[(k+1)%len(remaining)])]
            if cross(a,b,c)*orientation<=1e-8: continue
            if any(inside(poly[j],a,b,c) for j in remaining if poly[j] not in (a,b,c)): continue
            result.append([a,b,c]);remaining.pop(k);break
        else: raise ValueError('Trace polygon cannot be triangulated')
    result.append([poly[i] for i in remaining])
    for p in interior:
        for k,(a,b,c) in enumerate(result):
            if inside(p,a,b,c):
                result[k:k+1]=[[a,b,p],[b,c,p],[c,a,p]];break
    return result

def mesh(poly,side=1,interior=()):
    return [[traced(p,side) for p in tri] for tri in triangulate(poly,interior)]
