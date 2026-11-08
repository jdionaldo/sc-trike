"""Print-prep checks: run `python print_prep.py` first (writes out/print/report.json and plate_NN.3mf).

Every plate fits 256 x 256 x 250 mm, no two parts overlap on a plate, every part is a watertight single body, and the split
helper works on a synthetic bar."""
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest
import trimesh

import print_checks as PC
import print_prep as PP

REPORT = Path("out/print/report.json")
pytestmark = pytest.mark.skipif(not REPORT.exists(), reason="run python print_prep.py first")


@pytest.fixture(scope="module")
def rep():
    return json.loads(REPORT.read_text())


@pytest.fixture(scope="module")
def plates(rep):
    out = []
    for p in rep["plates"]:
        f = Path(f"out/print/plate_{p['plate']:02d}.3mf")
        assert f.exists(), f
        out.append((p, PP.read_3mf_objects(f)))
    return out


def test_no_failures(rep):
    assert not rep["failed"], rep["failed"]


def test_plates_fit_bed(plates):
    for p, objs in plates:
        for name, v, f in objs:
            lo, hi = v.min(0), v.max(0)
            assert lo[0] >= 0 and lo[1] >= 0 and hi[0] <= 256 and hi[1] <= 256, (p["plate"], name, lo, hi)
            assert lo[2] > -0.01 and hi[2] <= 250.0, (p["plate"], name, hi[2])


def test_no_overlap_on_plate(plates):
    from shapely.geometry import MultiPoint
    for p, objs in plates:
        polys = [(n, MultiPoint(v[:, :2]).convex_hull) for n, v, f in objs]
        for (a, pa), (b, pb) in combinations(polys, 2):
            assert pa.distance(pb) >= PP.SPACING - 0.05, (p["plate"], a, b, pa.distance(pb))


def test_parts_watertight(plates):
    for p, objs in plates:
        for name, v, f in objs:
            m = trimesh.Trimesh(v, f, process=False)
            assert m.is_watertight and m.is_winding_consistent and m.volume > 0, (p["plate"], name)
            assert len(m.split(only_watertight=False)) == 1, name


def test_source_stls_watertight(rep):
    bad = {r["name"]: r["topo_after"]["problems"] for r in rep["parts"] if r["topo_after"]["problems"]}
    assert not bad, bad


def test_split_bar():
    bar = trimesh.creation.box((300, 30, 20))
    a, b, info = PP.propose_split(bar)
    assert info["axis"] == "x" and info["pegs"] >= 1
    assert a.is_watertight and b.is_watertight
    assert max(a.extents[0], b.extents[0]) < 200
    assert PC.topology(a)["bodies"] == 1


def test_nest_spacing_synthetic():
    ms = [trimesh.creation.box((100, 100, 10)) for _ in range(6)]
    items = []
    for i, m in enumerate(ms):
        m.apply_translation(-m.bounds[0])
        items.append(PP.Item(f"b{i}", 0, m, PP.Recipe(), {}, PP.footprint(m)))
    plates = PP.nest(items)
    assert len(plates) == 2
