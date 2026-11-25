"""Cross section of the shell parts at a station y: prints the x/z extents of every material piece at x > 0."""
import sys, types, runpy, os
import cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
parts = {}
fake = types.ModuleType('soma'); fake.__path__ = []
fake.add_part = lambda n, o, **k: parts.__setitem__(n, (o, k)); fake.param = lambda d, *a, **k: d
fake.import_assembly = lambda p: types.SimpleNamespace(loc=cq.Location()); fake.import_step = lambda p: None
mx = types.ModuleType('soma.meshexport'); mx.body_meshes = lambda *a, **k: None; mx.problems = lambda m: []
fake.meshexport = mx; sys.modules['soma'] = fake; sys.modules['soma.meshexport'] = mx
ys = [float(a) for a in sys.argv[1:]] or [-20.0]
ns = runpy.run_path('model.py')
for y in ys:
    print('--- y', y)
    for name in ('Front shell', 'Rear shell', 'Canopy'):
        s = parts[name][0]; s = s.val() if hasattr(s, 'val') else s
        c = s.intersect(cq.Solid.makeBox(200, 0.4, 300, cq.Vector(0, y - 0.2, 0)))
        for k in c.Solids():
            b = k.BoundingBox(); print(f'{name:12s} x {b.xmin:6.1f}..{b.xmax:6.1f}  z {b.zmin:6.1f}..{b.zmax:6.1f}  vol {k.Volume():.0f}')
