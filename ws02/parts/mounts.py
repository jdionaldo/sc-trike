"""Printed trays for the bought electronics. Both print flat and sit loose between the chassis ribs."""
from cad import Part


def tray(p, name, inner, height):
    fit = p.mount_fit
    w = p.mount_wall
    ix, iy = inner[0] + 2 * fit, inner[1] + 2 * fit
    part = Part(name, "flat", "PETG")
    part.box((0.0, 0.0, 0.0), (ix + 2 * w, iy + 2 * w, height))
    part.box((w, w, p.mount_floor), (ix, iy, height), op="cut")
    notch = iy / 2
    part.box((-1.0, w + (iy - notch) / 2, p.mount_floor), (w + 2.0, notch, height), op="cut")
    return part


def build(p):
    return [tray(p, "rx_mount", (p.rx_l, p.rx_w), p.rx_tray_h),
            tray(p, "battery_mount", (p.lipo_l, p.lipo_w), p.batt_tray_h)]
