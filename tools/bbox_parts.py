"""Bounding boxes of the shell parts (final frame) and the grille vertices at its outer side."""
import sys, types, runpy, os
import cadquery as cq
os.chdir(os.path.join(os.path.dirname(__file__), '..')); sys.path.insert(0, os.getcwd())
parts = {}
fake = types.ModuleType('soma'); fake.__path__ = []
fake.add_part = lambda n, o, **k: parts.__setitem__(n, (o, k)); fake.param = lambda d, *a, **k: d
fake.import_assembly = lambda p: types.SimpleNamespace(loc=cq.Location()); fake.import_step = lambda p: None
mx = types.ModuleType('soma.meshexport'); mx.body_meshes = lambda *a, **k: None; mx.problems = lambda m: []
fake.meshexport = mx; sys.modules['soma'] = fake; sys.modules['soma.meshexport'] = mx
runpy.run_path('model.py')
for n in ('Front shell', 'Grille insert', 'Canopy', 'Rear shell'):
    s = parts[n][0]; s = s.val() if hasattr(s, 'val') else s
    b = s.BoundingBox(); print(n, [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
r = parts['Rear shell'][0]; r = r.val() if hasattr(r, 'val') else r
print('rear verts y>270:', sorted({(round(v.X,1), round(v.Y,1), round(v.Z,1)) for v in r.Vertices() if v.Y > 270}))
f = parts['Front shell'][0]; f = f.val() if hasattr(f, 'val') else f
print('front verts y<-285:', sorted({(round(v.X,1), round(v.Y,1), round(v.Z,1)) for v in f.Vertices() if v.Y < -285 and v.X >= 0}))
