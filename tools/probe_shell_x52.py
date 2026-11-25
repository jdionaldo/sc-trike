"""Where is shell material near the deck plane on the centre line? Prints z-intervals of each shell part along vertical lines x=0."""
import sys, types, runpy, os
import cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
parts = {}
fake = types.ModuleType('soma'); fake.__path__ = []
fake.add_part = lambda n, o, **k: parts.__setitem__(n, (o, k)); fake.param = lambda d, *a, **k: d
fake.import_assembly = lambda p: types.SimpleNamespace(loc=cq.Location()); fake.import_step = lambda p: None
mx = types.ModuleType('soma.meshexport'); mx.body_meshes = lambda *a, **k: None; mx.problems = lambda m: []
fake.meshexport = mx; sys.modules['soma'] = fake; sys.modules['soma.meshexport'] = mx
ns = runpy.run_path('model.py')
zp = ns['_zp']
for name in ('Front shell', 'Rear shell', 'Canopy'):
    pass
for name in ('Front shell', 'Rear shell', 'Canopy'):
    s = parts[name][0]
    s = s.val() if hasattr(s, 'val') else s
    for y in range(-230, 131, 15):
        line = cq.Solid.makeBox(0.2, 0.2, 400, cq.Vector(52-0.1, y, -100))
        try: c = s.intersect(line)
        except Exception: continue
        zs = sorted((b.BoundingBox().zmin, b.BoundingBox().zmax) for b in c.Solids())
        if zs: print(name, 'y', y, 'deck z %.1f' % zp(y), 'material z', [(round(a, 1), round(b, 1)) for a, b in zs])
