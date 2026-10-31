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


def test_power_unit_withdraws_through_hatch():
    items = assembly.scene()
    hit = validate.removal_collisions(items, "POWER_UNIT", (0, -1, 0), 100.0, ignore=("swingarm_hatch", "pivot_plate"))
    assert hit is None, hit


def test_battery_and_receiver_lift_out():
    items = assembly.scene()
    assert validate.removal_collisions(items, "LIPO_2S", (0, 0, 1), 80.0, ignore=("battery_mount",)) is None
    assert validate.removal_collisions(items, "RECEIVER", (0, 0, 1), 80.0, ignore=("rx_mount",)) is None


def test_servo_torque_margin():
    margin, need, usable = validate.servo_torque_margin()
    assert margin >= 0.2, (margin, need, usable)


def test_lead_has_slack_and_bend_radius():
    lengths = [assembly.lead_length(t) for t in (-P.rear_travel / 2, 0.0, P.rear_travel / 2)]
    assert max(lengths) + 10.0 <= P.pu_lead_batt_len, lengths
    assert max(lengths) - min(lengths) < 5.0, lengths
    assert P.pu_lead_bend_radius >= 3 * P.pu_lead_dia / 2
