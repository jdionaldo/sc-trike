import pytest

import build
import validate

PARTS = build.all_parts()


@pytest.mark.parametrize("part", PARTS, ids=lambda p: p.name)
def test_part_prints(part):
    build.run_part(part)
    results = validate.validate_part(part.name, part.walls, part.supports)
    failed = {k: v[1] for k, v in results.items() if not v[0]}
    assert not failed, failed


@pytest.mark.parametrize("name", ["mono_left", "mono_right", "canopy_lid"])
def test_monocoque_half_prints(name):
    """The body fused with the tub and cradle: printed with supports, turned on the bed (built by mono_build.py)."""
    results = validate.validate_part(name, walls=name != "canopy_lid", supports=True)   # the lid's cut edges are knife edges
    failed = {k: v[1] for k, v in results.items() if not v[0]}
    assert not failed, failed
