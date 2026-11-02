"""Paint scheme for WS-03: per-face colours on the body (recessed panels, canopy, grilles black), parts coloured by role. Exports out/WS03_painted.glb."""
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point
import w3_assembly as A
import body3_build as B

RED, BLACK, GREY, WHITE, ORANGE, BLUE, GOLD, TIRE = [196, 40, 28], [22, 22, 26], [120, 125, 135], [235, 235, 235], [226, 122, 40], [47, 95, 158], [232, 185, 35], [28, 28, 28]


def body_colors(mesh):
    c = mesh.triangles_center
    n = mesh.face_normals
    cols = np.tile(np.array(RED + [255], np.uint8), (len(c), 1))
    canopy = Polygon(B.PANELS and [(-225, -24), (-205, -30), (-150, -30), (-128, -22), (-128, 22), (-150, 30), (-205, 30), (-225, 24)])
    top = n[:, 2] > 0.3
    for i in np.where(top)[0]:
        if canopy.contains(Point(c[i, 0], c[i, 1])) and c[i, 2] > 40:
            cols[i] = BLACK + [255]
    for poly in B.PANELS:
        pg = Polygon(poly)
        for i in np.where(np.abs(n[:, 1]) > 0.7)[0]:
            if pg.contains(Point(c[i, 0], c[i, 2])) and abs(c[i, 1]) > 30:
                cols[i] = BLACK + [255]
    low = (c[:, 2] < -11) & (c[:, 2] > -27) & (np.abs(c[:, 1]) > 60) & (c[:, 0] < -120) & (c[:, 0] > -241)      # rocker armor band
    cols[low] = GREY + [255]
    return cols


def yup_matrix():
    """Level the ground (the chassis is raked 4 deg nose-down), then z-up -> y-up, ground at y = 0, centred in x and z."""
    gx = np.array([-360.0, 0.0, -25.2])                     # front contact -> rear contact (assembly frame)
    R1 = trimesh.geometry.align_vectors(gx / np.linalg.norm(gx), [-1.0, 0.0, 0.0])
    Rx = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    return Rx @ R1


def build(path="out/WS03_painted.glb", phi=0.0, steer=None, yup=False):
    sc = trimesh.Scene()
    for n, mesh, k in A.assembly(phi, steer=steer):
        m = mesh.copy()
        if n.startswith("body3"):
            m.visual = trimesh.visual.ColorVisuals(m, face_colors=body_colors(m))
        elif n == "lid3":
            m.visual.face_colors = BLACK + [255]
        elif n.startswith("mock_") and "tire" in n:
            m.visual.face_colors = TIRE + [255]
        elif n.startswith("w3_frame"):
            m.visual.face_colors = [25, 195, 214, 255]
        elif n.startswith("w3_deck"):
            m.visual.face_colors = [225, 225, 225, 255]
        elif n.startswith(("wing", "w3_skid")):
            m.visual.face_colors = WHITE + [255]
        elif "belt" in n:
            m.visual.face_colors = [15, 15, 15, 255]
        elif n.startswith("mock_") and any(t in n for t in ("pinion", "ring", "carrier", "pulley", "joint")):
            m.visual.face_colors = GOLD + [255]
        elif n.startswith(("b_motor", "b_battery", "b_esc", "mock_receiver")):
            m.visual.face_colors = BLUE + [255]
        elif k == "bought":
            m.visual.face_colors = GREY + [255]
        else:
            m.visual.face_colors = ORANGE + [255]
        sc.add_geometry(m, node_name=n, geom_name=n)
    if yup:
        sc.apply_transform(yup_matrix())
        lo = sc.bounds[0]
        c = 0.5 * (sc.bounds[0] + sc.bounds[1])
        sc.apply_translation([-c[0], -lo[1], -c[2]])               # ground at y = 0, centred
    sc.export(path)
    return path


if __name__ == "__main__":
    import sys
    ph = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    st = float(sys.argv[2]) if len(sys.argv) > 2 else None
    print(build(phi=ph, steer=st))
    print(build(path="out/WS03_yup.glb", phi=ph, steer=st, yup=True))
