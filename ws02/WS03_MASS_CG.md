# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 946 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2398 |
| cg_mm | [-163.3, 1.2, 14.3] |
| front_weight_fraction | 0.637 |
| cg_height_above_ground_mm | 55.8 |
| static_roll_angle_deg | 67.5 |
| rollover_speed_1m_radius_mps | 4.86 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- body3_mid: 109 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_front: 95 g
- body3_rear: 80 g
- w3_frame_rear: 63 g
- w3_rear_arm: 62 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.27 |  | 2362 | -169.8, 1.3, 16.5 | 58.0 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 62.33 | +0.06 | 2367 | -169.5, 1.2, 16.5 | 58.0 |
| 2 small masses placed from an inventory (receiver already at x -44) | 62.52 | +0.19 | 2367 | -168.7, 1.2, 16.4 | 57.9 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 62.52 | +0.00 | 2367 | -168.7, 1.2, 16.4 | 57.9 |
| 4a wing and tail infill 25 % to 8 % | 63.05 | +0.52 | 2347 | -166.3, 1.2, 15.4 | 56.9 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 63.71 | +0.66 | 2398 | -163.3, 1.2, 14.3 | 55.8 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.11 | +0.40 | 2383 | -161.5, 1.2, 14.6 | 56.1 |
