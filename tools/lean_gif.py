"""Offline animated GIF of the lean-steer kinematics (front view and front quarter). usage (SOMA python, from the project folder): python -I tools/lean_gif.py renders/lean_steer"""
import sys, math; sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
import cadquery as cq, vtk
from PIL import Image
import front_check as fc
from parts import wishbone as wb
parts = fc.load('output/model.step')                      # {key: shape}
groups = fc.moving_groups()
name_of = {k: fc.short(k) for k in parts}
gid = {}
for g, names in groups.items():
    for n in names: gid[n] = g
ren = vtk.vtkRenderer(); ren.SetBackground(0.94, 0.96, 0.98)
actors = []
def col(k):
    n = name_of[k]
    if 'tire' in n: return (0.18, 0.18, 0.2)
    if 'shock body' in n: return (0.8, 0.15, 0.12)
    if any(t in n for t in ('arm', 'Knuckle', 'Lean head', 'horn', 'mount')): return (0.95, 0.55, 0.1)
    if 'Cage' in k or 'Roof' in n: return (0.1, 0.1, 0.11)
    return (0.7, 0.72, 0.75)
for k, s in parts.items():
    n = name_of[k]; b = s.BoundingBox()
    if 'Print_shell' in k or 'Cage' in k or 'Roof' in n or 'light' in n.lower() or b.ymin > -40: continue
    v, t = s.tessellate(0.4, 0.4)
    pts = vtk.vtkPoints(); [pts.InsertNextPoint(p.x, p.y, p.z) for p in v]
    ca = vtk.vtkCellArray()
    for tri in t:
        ca.InsertNextCell(3); [ca.InsertCellPoint(i) for i in tri]
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(ca)
    m = vtk.vtkPolyDataMapper(); m.SetInputData(pd)
    ac = vtk.vtkActor(); ac.SetMapper(m); ac.GetProperty().SetColor(*col(k)); ren.AddActor(ac); actors.append((ac, gid.get(n)))
gp = vtk.vtkPlaneSource(); gp.SetOrigin(-260, -330, wb.GROUND_Z); gp.SetPoint1(260, -330, wb.GROUND_Z); gp.SetPoint2(-260, -40, wb.GROUND_Z)
gm = vtk.vtkPolyDataMapper(); gm.SetInputConnection(gp.GetOutputPort()); ga = vtk.vtkActor(); ga.SetMapper(gm); ga.GetProperty().SetColor(0.82, 0.84, 0.86); ren.AddActor(ga)
def mat(loc):
    T = loc.wrapped.Transformation(); M = vtk.vtkMatrix4x4()
    for i in range(3):
        for j in range(4): M.SetElement(i, j, T.Value(i + 1, j + 1))
    return M
w = vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.SetSize(900, 560); w.AddRenderer(ren)
def frames(view, seq):
    out = []
    c = ren.GetActiveCamera()
    if view == 'front': c.SetPosition(0, -1200, 45); c.SetFocalPoint(0, -180, 45); c.ParallelProjectionOn()
    else: c.SetPosition(420, -640, 260); c.SetFocalPoint(0, -170, 40); c.ParallelProjectionOff()
    c.SetViewUp(0, 0, 1); ren.ResetCamera(-185, 185, -280, -60, -16, 110); c.Zoom(1.25 if view == 'front' else 1.15)
    for phi, eta in seq:
        locs, bad, eye, psi = fc.pose_locs(phi, eta)
        roll = wb.roll_loc(phi)
        for ac, g in actors:
            ac.SetUserMatrix(mat(roll * locs[g]) if g in locs else mat(roll))
        ren.ResetCameraClippingRange(); w.Render()
        f = vtk.vtkWindowToImageFilter(); f.SetInput(w); f.Update()
        img = f.GetOutput(); d = img.GetDimensions(); arr = img.GetPointData().GetScalars()
        buf = bytes(bytearray(int(arr.GetValue(i)) for i in range(arr.GetNumberOfTuples() * arr.GetNumberOfComponents())))
        im = Image.frombytes('RGB' if arr.GetNumberOfComponents() == 3 else 'RGBA', (d[0], d[1]), buf).transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
        out.append(im)
    return out
def ease(a, b, n): return [(a[0] + (b[0] - a[0]) * (0.5 - 0.5 * math.cos(math.pi * k / n)), a[1] + (b[1] - a[1]) * (0.5 - 0.5 * math.cos(math.pi * k / n))) for k in range(1, n + 1)]
lean = ease((0, 0), (10, 0), 10) + ease((10, 0), (-10, 0), 18) + ease((-10, 0), (0, 0), 10)
both = ease((0, 0), (10, -30), 10) + ease((10, -30), (-10, 30), 18) + ease((-10, 30), (0, 0), 10)
F = frames('front', lean + both)
F[0].save(sys.argv[1] + '_front.gif', save_all=True, append_images=F[1:], duration=70, loop=0, optimize=True)
Q = frames('quarter', lean + both)
Q[0].save(sys.argv[1] + '_quarter.gif', save_all=True, append_images=Q[1:], duration=70, loop=0, optimize=True)
F[10].save(sys.argv[1] + '_front_lean.png'); Q[48].save(sys.argv[1] + '_quarter_leansteer.png')
print('frames', len(F), len(Q))
