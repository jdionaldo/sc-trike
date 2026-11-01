import pytest

import assembly
import validate
from params import P


@pytest.mark.parametrize("pose", list(assembly.POSES))
def test_no_interference(pose):
    bad = validate.interference(assembly.scene(*assembly.POSES[pose]))
    assert not bad, bad


@pytest.mark.parametrize("pose", list(assembly.POSES))
def test_clearance_to_bought_parts(pose):
    bad = validate.clearance(assembly.scene(*assembly.POSES[pose]))
    assert not bad, bad


def test_battery_and_receiver_lift_out():
    items = assembly.scene()
    assert validate.removal_collisions(items, "LIPO_2S", (0, 0, 1), 80.0, ignore=("battery_mount", "canopy_lid")) is None
    assert validate.removal_collisions(items, "RECEIVER", (0, 0, 1), 80.0, ignore=("rx_mount", "canopy_lid")) is None


def test_servo_torque_margin():
    margin, need, usable = validate.servo_torque_margin()
    assert margin >= 0.2, (margin, need, usable)


