"""Trim the scaled shell around the 1:1 chassis, including suspension and steering travel.

Tool data comes from tools/make_relief.py (parts/relief.json): hull vertices of every chassis part that reaches
into the shell, tire cylinders and the rear swingarm pivot. Frame = shell frame at 1:1 (X lateral, Y = -forward,
Z up, ground z = 0); the tools are moved by CHASSIS_Y / CHASSIS_Z.
"""
import json, math, os
import cadquery as cq
from parts.util import hull
from parts.params import *

_DATA = json.load(open(os.path.join(os.path.dirname(__file__), 'relief.json')))
PIVOT = (_DATA['pivot'][1], _DATA['pivot'][2])            # rear swingarm pivot (y, z)
REAR_AXLE = (_DATA['rear_axle'][1], _DATA['rear_axle'][2])  # rear axle at the original 112 mm tire
SHOCK_TOP0 = (0.0, 136.3, 129.5)     # upper eye on the frame (x, y, z), on the wheel centre plane, raised by REAR_SHOCK_RISE
SHOCK_BOT0 = (0.0, 150.0, 114.0)   # lower eye (arm frame): the pin of the shock bridge over the tire, final (215, 139) at ride
BRIDGE_ARM = [(57.0, 150.0, 114.0), (30.0, 150.0, 114.0), (-8.0, 150.0, 114.0)]   # shock bridge path in the arm frame (x, y, z): apex node, up, across
FRONT_X, FRONT_Y = 144.0, -225.55                         # front axle centres (|x|, y)


def rear_lift_angle():
    """Swingarm rotation (rad) that lifts the rear axle to the new tire radius."""
    dy, dz = REAR_AXLE[0]-PIVOT[0], REAR_AXLE[1]-PIVOT[1]
    L = math.hypot(dy, dz)
    return math.asin((REAR_TIRE_OD/2 - PIVOT[1])/L) - math.atan2(dz, dy)

def rot_yz(p, ang, c=PIVOT):
    """Rotate point p=(x,y,z) about the lateral axis through c=(y,z); positive raises the tail."""
    x, y, z = p; dy, dz = y-c[0], z-c[1]
    return (x, c[0] + dy*math.cos(ang) - dz*math.sin(ang), c[1] + dy*math.sin(ang) + dz*math.cos(ang))

def rot_xy(p, ang, c):
    """Rotate point about a vertical axis through c=(x,y) (steering)."""
    x, y, z = p; dx, dy = x-c[0], y-c[1]
    return (c[0] + dx*math.cos(ang) - dy*math.sin(ang), c[1] + dx*math.sin(ang) + dy*math.cos(ang), z)

def _grown(pts, g):
    out = []
    for x, y, z in pts:
        out += [(x+g, y, z), (x-g, y, z), (x, y+g, z), (x, y-g, z), (x, y, z+g), (x, y, z-g)]
    return out

def _circle(cx, cy, cz, r, hw, n=28):
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        for sx in (-hw, hw):
            pts.append((cx+sx, cy + r*math.cos(a), cz + r*math.sin(a)))
    return pts

def _circle2(c, r, n=12):
    return [(c[0]+r*math.cos(2*math.pi*i/n), c[1]+r*math.sin(2*math.pi*i/n), c[2]+s*r) for i in range(n) for s in (-1, 1)]

def relief_tools():
    """Cut-out tools in final (scaled) shell coordinates: tire arches and suspension travel."""
    off = cq.Vector(0, CHASSIS_Y, CHASSIS_Z)
    T = BUMP_TRAVEL; L = math.radians(STEER_LOCK)
    th0 = rear_lift_angle(); thb = math.asin(min(1.0, T/math.hypot(REAR_AXLE[0]-PIVOT[0], REAR_AXLE[1]-PIVOT[1])))
    tools = []
    # --- tires
    for t in _DATA['tires']:
        cx, cy, cz = t['center']
        if t['name'] == 'mock_rear_tire_ring':
            R = REAR_TIRE_OD/2
            pts = []
            for k in (0, 0.5, 1.0):                      # axle path along the swingarm arc
                c = rot_yz((cx, cy, cz), th0 + k*thb)
                pts += _circle(0, c[1], c[2], R + RELIEF, t['hw'] + RELIEF)
        else:
            pts = []
            for a in (-L, 0, L):                         # steering lock sweep about the wheel centre
                for lift in (0, T):                      # bump travel
                    pts += [rot_xy(p, a, (cx, cy)) for p in _circle(cx, cy, cz+lift, t['r'] + TIRE_GAP, t['hw'] + TIRE_GAP)]
        tools.append(hull(pts).translate(off))
    # --- suspension, steering and swingarm parts
    for h in _DATA['hulls']:
        P = [tuple(p) for p in h['pts']]; kind = h['kind']
        if kind == 'susp':
            pts = P + [(x, y, z + T*min(1.0, max(0.0, (abs(x)-30)/114.0))) for x, y, z in P]
        elif kind == 'steer':
            cx = math.copysign(FRONT_X, P[0][0])
            pts = []
            for a in (-L, 0, L):
                for lift in (0, T):
                    pts += [rot_xy((x, y, z+lift), a, (cx, FRONT_Y)) for x, y, z in P]
        elif kind == 'rear':
            pts = [rot_yz(p, th0) for p in P] + [rot_yz(p, th0 + thb) for p in P]
        else:
            pts = P
        tools.append(hull(_grown(pts, RELIEF)).translate(off))
    # --- rear shock strut: top mount fixed on the frame (raised), bottom eye rides on the swingarm
    top = (SHOCK_TOP0[0], SHOCK_TOP0[1], SHOCK_TOP0[2] + REAR_SHOCK_RISE)
    pts = []
    for k in (0, thb):
        b = rot_yz(SHOCK_BOT0, th0 + k)
        for f in (0.0, 0.5, 1.0):
            pts += _circle2(tuple(top[i] + f*(b[i]-top[i]) for i in range(3)), 12.0 + RELIEF)
    tools.append(hull(pts).translate(off))
    # --- shock bridge over the rear tire swings with the arm
    bp = []
    for k in (0, thb):
        bp += [rot_yz(p, th0 + k) for p in BRIDGE_ARM]
    tools.append(hull(_grown(bp, RELIEF + 8.0)).translate(off))
    return tools
