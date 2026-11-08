"""WS-03 (3WD lean-steer trike) checks: every printed part prints, the front mechanism and the whole assembly are clash free over
the lean and steer range, the body is watertight, fits the bed and contains the interior."""
import numpy as np
import pytest
import trimesh
import manifold3d as m

import build
import validate
import w3_assembly as A
import w3_scene as S
import w3_parts
import body3_build
import split_shell3
import layout3wd as LY
import w3_drive_scene as DS
from parts import w3_drive as D

PARTS = w3_parts.all_parts()


@pytest.mark.parametrize("part", PARTS, ids=lambda p: p.name)
def test_part_prints(part):
    build.run_part(part)
    results = validate.validate_part(part.name, part.walls, part.supports)
    failed = {k: v[1] for k, v in results.items() if not v[0]}
    assert not failed, failed


@pytest.fixture(scope="module")
def body_built():
    body3_build.main()
    split_shell3.main()


@pytest.mark.parametrize("lean,steer", [(0.0, None), (20.0, 17.0), (-20.0, -17.0), (20.0, -17.0), (-20.0, 17.0), (12.0, None)])
def test_front_mechanism_clear(lean, steer):
    items = S.scene(lean, steer=steer)
    assert sum(n.startswith("tie_rod") for n, _, _ in items) == 2
    assert S.check(items) == []


def test_lean_limits():
    import front3wd as F
    import math
    th = [F.arm_angles(math.radians(p)) for p in np.linspace(-20, 20, 11)]
    assert max(abs(a) for pair in th for a in pair) < math.radians(45)


@pytest.mark.parametrize("lean,steer", [(0.0, None), (20.0, 17.0), (-20.0, -17.0)])
def test_assembly_clash_free(body_built, lean, steer):
    assert A.check_global(A.assembly(lean, steer=steer)) == []


def test_body_pieces(body_built):
    for part in ("front", "mid", "rear"):
        t = trimesh.load(f"out/mono3/body3_{part}.stl")
        assert t.is_watertight
        pm = t.copy()
        pm.apply_translation((0, 0, -pm.bounds[0][2]))
        ok, msg = validate.check_bed(pm, 3.0)
        assert ok, msg


def test_interior_inside_body(body_built):
    man = lambda t: m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))
    sh = man(trimesh.load("out/mono3/body3.stl"))
    b = LY.blocks()
    items = dict(DS.placed())
    for k in ("battery", "motor", "center_diff", "front_diff", "front_ring", "rear_ring", "rear_shaft", "front_pinion_shaft"):
        items[k] = b[k]
    poking = [(k, round((man(t) ^ sh).volume(), 1)) for k, t in items.items() if (man(t) ^ sh).volume() > 1.0]
    assert poking == [], poking


def test_mass_plausible(body_built):
    g = A.mass_g(A.assembly(0.0))
    assert 600.0 < g < 2400.0, g      # solid-volume mass of the printed parts (before infill), plausibility bound


def test_strength_factors():
    import w3_strength
    for name, sf in w3_strength.rows:
        if "printed 3 x 10" in name or "3 mm steel, cantilever" in name.replace("Kingpin 3 mm", "3 mm steel,").replace("3 mm steel, cantilever from", "3 mm steel, cantilever from") and name.startswith("Kingpin 3"):
            continue                      # superseded by the 4 mm kingpin / steel turnbuckle
        assert sf >= 2.0, (name, sf)


def test_mass_and_cg():
    import w3_mass
    rows, total, cg = w3_mass.run()
    assert 1000.0 < total < 2400.0, total
    from w3_stretch import WHEELBASE as WB
    front = (cg[0] + WB) / WB
    assert 0.45 < front < 0.70, front
    assert cg[2] + 41.5 < 80.0, cg


@pytest.mark.parametrize("dz", [-20.0, -10.0, 10.0, 20.0, 25.0])
def test_rear_wheel_travel_clear(dz):
    """The rear wheel, rim, hub and swing arm clear every fixed part over 20 mm of droop and 25 mm of bump."""
    import w3_swing as SW
    M = {n: m for n, m, k in A.assembly(0.0, 0.0)}
    mov = [n for n in M if n.startswith(("mock_rear_", "w3_rear_arm"))]
    fixed = [n for n in M if n not in mov and n != "b_rear_shock" and (not n.startswith("mock_") or n == "mock_cdiff_ring")]      # the shock follows the arm: test_rear_shock_clear sweeps it
    import mono_build as MB
    ang = float(np.degrees(np.arcsin(dz / np.hypot(D.XR - D.RAXLE[0], D.RAXLE[1]))))
    for n in mov:
        mr = SW.rot_pivot(MB.man(M[n]), ang)
        for f in fixed:
            assert (mr ^ MB.man(M[f])).volume() < 0.5, (n, f, dz)


def _shock_angle(dz):
    return float(np.degrees(np.arcsin(dz / np.hypot(D.XR - D.RAXLE[0], D.RAXLE[1]))))


def test_rear_shock_length():
    """Eye to eye stays inside the 55..80 mm stroke over 20 mm droop to 25 mm bump, about 2/3 extended at rest."""
    from parts import w3_shock as SK
    ls = {dz: SK.eye_to_eye(_shock_angle(dz)) for dz in np.linspace(-20.0, 25.0, 46)}
    lmin, lmax, rest = min(ls.values()), max(ls.values()), SK.eye_to_eye(0.0)
    print(f"shock eye to eye: min {lmin:.1f} (bump), rest {rest:.1f}, max {lmax:.1f} (droop)")
    assert SK.LMIN + 3.0 <= lmin and lmax <= SK.LMAX - 0.2, (lmin, lmax)
    assert 0.6 <= (rest - SK.LMIN) / (SK.LMAX - SK.LMIN) <= 0.75, rest


@pytest.mark.parametrize("dz", [-20.0, -10.0, 0.0, 10.0, 20.0, 25.0])
def test_rear_shock_clear(dz, body_built):
    """The coilover (envelope with the spring as a solid cylinder) touches nothing but its two bolt bosses' faces, over the whole travel; the lug and tab are fixed to the arm / frame."""
    import w3_swing as SW
    import mono_build as MB
    from parts import w3_shock as SK
    ang = _shock_angle(dz)
    M = {n: m for n, m, k in A.assembly(0.0, 0.0)}
    shock = SK.shock_manifold(ang)
    for n, mesh in M.items():
        if n == "b_rear_shock":
            continue
        mv = n.startswith(("mock_rear_", "w3_rear_arm"))
        part = SW.rot_pivot(MB.man(mesh), ang) if mv else MB.man(mesh)
        assert (shock ^ part).volume() < 0.5, (n, dz)


def test_lean_shock_stroke():
    """The two lean coilovers stay inside their stroke (3 mm spare at each end) over the full lean range and sit near 70 % extension at lean 0."""
    import math
    import parts.w3_lean as LN
    lo, hi = LN.SHOCK["lmin"] + 3.0, LN.SHOCK["lmax"] - 3.0
    for ph in np.linspace(-20.0, 20.0, 41):
        _, _, _, ln = S.lean_geometry(math.radians(ph))
        assert all(lo <= v <= hi for v in ln.values()), (ph, ln)
    _, _, _, l0 = S.lean_geometry(0.0)
    ext = (l0[1] - LN.SHOCK["lmin"]) / LN.SHOCK["stroke"]
    assert 0.65 <= ext <= 0.75, ext
    for ph in (0.0, 20.0, -20.0):
        names = [n for n, _, _ in S.scene(ph)]
        assert "b_lean_shock_1" in names and "b_lean_shock_-1" in names
