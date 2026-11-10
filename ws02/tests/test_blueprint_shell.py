"""Blueprint shell (sheet 71): 14 panels, watertight, bed fit, scale, clear of the hardware. Reads blueprint_shell/stl and shell71_report.json (made by blueprint_shell/export71.py)."""
import json, os
import numpy as np, pytest, trimesh

D = os.path.join(os.path.dirname(__file__), "..", "blueprint_shell")
REP = json.load(open(os.path.join(D, "shell71_report.json")))
PANELS = ["P1", "P2L", "P2R", "P3", "P4P5", "P6", "P7L", "P7R", "P8P10L", "P8P10R", "P9", "P11"]


def test_panel_objects():
    assert len(PANELS) == 12       # 14 sheet parts; P8 and P10 are fused per side (P8P10L/R) and P4 + P5 are one frame (P4P5), P7 is x2, P2 is L+R
    for n in PANELS:
        assert os.path.exists(os.path.join(D, "stl", f"{n}.stl")), n


@pytest.mark.parametrize("n", PANELS)
def test_watertight_and_fits_bed(n):
    import manifold3d as m3
    t = trimesh.load(os.path.join(D, "stl", f"{n}.stl"))
    assert len(trimesh.grouping.group_rows(t.edges_sorted, require_count=1)) == 0      # no open edge
    M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
    assert M.status() == m3.Error.NoError and not M.is_empty() and abs(t.volume) > 1000
    assert REP[n]["bed256"], REP[n]["extent_mm"]          # 256 mm bed (user); P8P10 L/R (301 x 31) print on the bed diagonal and do not fit 220


def test_overall_scale_matches_sheet():
    o = REP["_overall"]
    s = o["scale"]
    assert abs(o["height"] - 102 * s) < 0.08 * 102 * s
    assert abs(o["length"] - 278 * s) < 0.08 * 278 * s


def test_left_right_mirror():
    for a, b in (("P2L", "P2R"), ("P8P10L", "P8P10R"), ("P7L", "P7R")):
        ta, tb = (trimesh.load(os.path.join(D, "stl", f"{n}.stl")) for n in (a, b))
        assert abs(abs(ta.volume) - abs(tb.volume)) < 0.02 * abs(ta.volume)


def test_no_hardware_overlap_over_lean_and_steer():
    assert REP["_overall"]["overlap_after"] == {}


def test_rear_tunnel_is_one_watertight_shell():
    t = trimesh.load(os.path.join(D, "stl", "P11.stl"))
    assert t.is_watertight and t.is_winding_consistent and len(t.split(only_watertight=False)) == 1
    assert t.bounds[0][2] < 40 and np.ptp(t.bounds, 0)[0] > 70            # a tunnel front to back, walls drop to the swing envelope
    assert REP["P11"]["bed220"]
