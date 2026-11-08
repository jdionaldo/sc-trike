# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 940 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2392 |
| cg_mm | [-163.7, 1.2, 14.2] |
| front_weight_fraction | 0.636 |
| cg_height_above_ground_mm | 55.7 |
| static_roll_angle_deg | 67.5 |
| rollover_speed_1m_radius_mps | 4.87 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- body3_mid: 108 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_front: 89 g
- body3_rear: 80 g
- w3_frame_rear: 63 g
- w3_rear_arm: 62 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.17 |  | 2355 | -170.2, 1.3, 16.4 | 57.9 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 62.23 | +0.06 | 2360 | -170.0, 1.2, 16.4 | 57.9 |
| 2 small masses placed from an inventory (receiver already at x -44) | 62.43 | +0.19 | 2360 | -169.1, 1.2, 16.3 | 57.8 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 62.43 | +0.00 | 2360 | -169.1, 1.2, 16.3 | 57.8 |
| 4a wing and tail infill 25 % to 8 % | 62.95 | +0.52 | 2340 | -166.7, 1.2, 15.3 | 56.8 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 63.62 | +0.67 | 2392 | -163.7, 1.2, 14.2 | 55.7 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.02 | +0.40 | 2377 | -161.9, 1.2, 14.5 | 56.0 |
