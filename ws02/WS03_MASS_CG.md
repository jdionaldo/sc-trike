# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 832 |
| bought_g | 1381 |
| misc_g | 85.0 |
| total_g | 2298 |
| cg_mm | [-160.2, 1.1, 8.9] |
| front_weight_fraction | 0.644 |
| cg_height_above_ground_mm | 50.4 |
| static_roll_angle_deg | 69.5 |
| rollover_speed_1m_radius_mps | 5.12 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_rear: 79 g
- body3_front: 71 g
- w3_rear_arm: 62 g
- w3_frame_rear: 60 g
- w3_frame_front: 58 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 65.16 |  | 2227 | -156.8, 1.3, 10.2 | 51.7 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 65.22 | +0.06 | 2232 | -156.5, 1.2, 10.2 | 51.7 |
| 2 small masses placed from an inventory (receiver already at x -44) | 65.32 | +0.09 | 2232 | -156.1, 1.2, 10.1 | 51.6 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 65.32 | +0.00 | 2232 | -156.1, 1.2, 10.1 | 51.6 |
| 4a wing and tail infill 25 % to 8 % | 65.32 | +0.00 | 2232 | -156.1, 1.2, 10.1 | 51.6 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 64.41 | -0.91 | 2298 | -160.2, 1.1, 8.9 | 50.4 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.83 | +0.42 | 2283 | -158.3, 1.1, 9.1 | 50.6 |
