import numpy as np, time
import pskin_build as B, pskin_core as C, pskin_detail as D
m = B.model(); P, pn = m.mirror(); C.orient_panels(P, pn); C.ORIENTED = True
t0 = time.time(); d = D.Detail(P, pn)
D.apply_details(d)
print(round(time.time() - t0, 1), "s", d.body.volume())
t = C.to_trimesh(d.body); print(t.is_watertight, round(t.volume), len(t.faces)); t.export("out/pskin/C_body.stl")
