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
