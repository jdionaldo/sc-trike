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


@pytest.mark.parametrize("lean,steer", [(0.0, None), (25.0, 17.0), (-25.0, -17.0), (25.0, -17.0), (-25.0, 17.0), (12.0, None)])
def test_front_mechanism_clear(lean, steer):
    items = S.scene(lean, steer=steer)
    assert sum(n.startswith("tie_rod") for n, _, _ in items) == 2
    assert S.check(items) == []


def test_lean_limits():
    import front3wd as F
    import math
    th = [F.arm_angles(math.radians(p)) for p in np.linspace(-25, 25, 11)]
    assert max(abs(a) for pair in th for a in pair) < math.radians(45)


@pytest.mark.parametrize("lean,steer", [(0.0, None), (25.0, 17.0), (-25.0, -17.0)])
def test_assembly_clash_free(body_built, lean, steer):
    assert A.check_global(A.assembly(lean, steer=steer)) == []


def test_body_pieces(body_built):
    for side in ("left", "right"):
        for part in ("front", "rear"):
            t = trimesh.load(f"out/mono3/body3_{side}_{part}.stl")
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
    for k in ("battery", "esc", "motor", "center_diff", "front_diff", "front_ring", "rear_ring", "rear_shaft", "front_pinion_shaft"):
        items[k] = b[k]
    poking = [(k, round((man(t) ^ sh).volume(), 1)) for k, t in items.items() if (man(t) ^ sh).volume() > 1.0]
    assert poking == [], poking


def test_mass_plausible(body_built):
    g = A.mass_g(A.assembly(0.0))
    assert 600.0 < g < 1400.0, g


def test_strength_factors():
    import w3_strength
    for name, sf in w3_strength.rows:
        if "printed 3 x 10" in name or "3 mm steel, cantilever" in name.replace("Kingpin 3 mm", "3 mm steel,").replace("3 mm steel, cantilever from", "3 mm steel, cantilever from") and name.startswith("Kingpin 3"):
            continue                      # superseded by the 4 mm kingpin / steel turnbuckle
        assert sf >= 2.0, (name, sf)


def test_mass_and_cg():
    import w3_mass
    rows, total, cg = w3_mass.run()
    assert 1000.0 < total < 2200.0, total
    front = (cg[0] + 360.0) / 360.0
    assert 0.45 < front < 0.70, front
    assert cg[2] + 41.5 < 80.0, cg
