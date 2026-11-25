"""Final-frame coordinates (mm) of the canopy frame nodes (A pillar, B pillar, roof) for the cage."""
import os, sys, math, types
import cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
fake = types.ModuleType('soma'); fake.param = lambda d, *a, **k: d; sys.modules['soma'] = fake
from parts.params import *
from parts.reference_trace import ROOF, WINDOW_BELT, traced, belt_station
from parts.shell_geometry import point
from parts.relief import FRONT_Y
_phi = math.radians(SHELL_PITCH); _c, _s = math.cos(_phi), math.sin(_phi)
_cy, _cz = FRONT_Y + CHASSIS_Y, 55.86 + CHASSIS_Z
_SX, _SZ = SHELL_SCALE, SHELL_SCALE*SHELL_Z
_WX = SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH
_m = cq.Matrix([[_WX, 0, 0, 0], [0, _c*_SX, -_s*_SZ, _cy - _c*_cy + _s*_cz], [0, _s*_SX, _c*_SZ, _cz - _s*_cy - _c*_cz]])
def final(p):
    return cq.Solid.makeSphere(0.05, cq.Vector(*p)).transformGeometry(_m).Center()
nodes = {'belt0': WINDOW_BELT[0], 'roof0': ROOF[0], 'roof1': ROOF[1], 'roof2': ROOF[2], 'roofN': ROOF[-1], 'beltN': WINDOW_BELT[-1],
         'belt930': belt_station(930), 'belt945': belt_station(945)}
for n, p in nodes.items():
    c = final(point(traced(p, 1)))
    print(f'{n:8s} x {c.x:7.1f} y {c.y:7.1f} z {c.z:7.1f}')
