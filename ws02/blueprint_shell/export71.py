"""Build, fit and export the blueprint shell. usage (from ws02/): python blueprint_shell/export71.py"""
import os, sys, json
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'blueprint_shell'))
import numpy as np, trimesh
import shell71 as B, fit71 as F

OUT = 'blueprint_shell'
COL = {'P1': (190, 60, 60), 'P2': (60, 110, 200), 'P3': (60, 170, 220), 'P4': (130, 70, 170), 'P5': (110, 60, 150), 'P6': (150, 100, 200),
       'P7': (120, 60, 180), 'P8': (50, 150, 70), 'P9': (240, 140, 40), 'P10': (230, 120, 30), 'P11': (230, 200, 40)}
NAMES = {'P1': 'Front Nose / Grille', 'P2': 'Front Side Panel', 'P3': 'Hood Panel', 'P4': 'Windshield Frame', 'P5': 'Roof Frame', 'P6': 'Roof Panel', 'P7': 'Roof Light',
         'P8': 'Side Panel', 'P9': 'Rear Upper Cover', 'P10': 'Rear Side Cover', 'P11': 'Rear Lower Diffuser'}


def key(n): return n[:3] if n.startswith(('P10', 'P11')) else n[:2]


def main():
    panels = B.build_all()
    panels = F.cut_channels(panels)
    panels, hit, removed = F.hardware_relief(panels)
    dropped = {}
    for n, t in list(panels.items()):                      # the arm-sweep cut leaves loose slivers: keep only bodies that are a real part of the panel
        parts = t.split(only_watertight=False)
        if len(parts) > 1:
            vols = [abs(p.volume) for p in parts]
            keep = [p for p, v in zip(parts, vols) if v > 0.02 * max(vols)]
            dropped[n] = len(parts) - len(keep)
            panels[n] = trimesh.util.concatenate(keep) if len(keep) > 1 else keep[0]
    print('slivers dropped', dropped)
    os.makedirs(f'{OUT}/stl', exist_ok=True)
    rep = {}
    sc = trimesh.Scene()
    R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)       # z-up -> glTF y-up
    for n, t in panels.items():
        t.export(f'{OUT}/stl/{n}.stl')
        ext = np.ptp(t.bounds, 0)
        rep[n] = dict(faces=len(t.faces), watertight=bool(t.is_watertight), volume_cm3=round(abs(t.volume) / 1e3, 2), extent_mm=[round(float(e), 1) for e in ext],
                      bed220=bool(sorted(ext[:2])[1] <= 220 and sorted(ext[:2])[0] <= 220), bed256=bool(max(ext[:2]) <= 256))
        c = np.array(COL[key(n)] + (255,), np.uint8)
        tt = t.copy(); tt.visual.face_colors = np.tile(c, (len(tt.faces), 1)); tt.apply_transform(R)
        sc.add_geometry(tt, node_name=f'{n}_{NAMES[key(n)].replace(" / ", "_").replace(" ", "_")}', geom_name=n)
    sc.export(f'{OUT}/WS03_blueprint_shell.glb')
    allv = np.vstack([t.vertices for t in panels.values()])
    rep['_overall'] = dict(length=round(float(np.ptp(allv[:, 0])), 1), width=round(float(np.ptp(allv[:, 1])), 1), height=round(float(np.ptp(allv[:, 2])), 1),
                           scale=B.SCALE, nose_x=B.NOSE_X, relieved_items=hit, removed_mm3=removed, slivers_dropped=dropped)
    json.dump(rep, open(f'{OUT}/shell71_report.json', 'w'), indent=1)
    post = F.overlaps(panels)
    rep['_overall']['overlap_after'] = {k: list(v) for k, v in post.items()}
    json.dump(rep, open(f'{OUT}/shell71_report.json', 'w'), indent=1)
    for k, v in rep.items(): print(k, v)


if __name__ == '__main__':
    main()
