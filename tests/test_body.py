import pytest

import assembly
import validate


@pytest.mark.parametrize("pose", list(assembly.POSES))
def test_body_no_interference(pose):
    items = assembly.scene(*assembly.POSES[pose], body=True)
    assert not validate.interference(items)


@pytest.mark.parametrize("pose", list(assembly.POSES))
def test_body_clears_moving_parts_by_3mm(pose):
    items = assembly.scene(*assembly.POSES[pose], body=True)
    assert not validate.body_clearance(items)
