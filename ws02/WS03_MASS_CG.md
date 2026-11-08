# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 879 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2331 |
| cg_mm | [-162.5, 1.5, 11.2] |
| front_weight_fraction | 0.639 |
| cg_height_above_ground_mm | 52.7 |
| static_roll_angle_deg | 68.6 |
| rollover_speed_1m_radius_mps | 5.0 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- body3_mid: 96 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- w3_rear_arm: 62 g
- body3_rear: 62 g
- w3_frame_rear: 61 g
- body3_front: 60 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.40 |  | 2295 | -169.2, 1.6, 13.2 | 54.7 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 62.47 | +0.06 | 2300 | -168.9, 1.6, 13.2 | 54.7 |
| 2 small masses placed from an inventory (receiver already at x -44) | 62.66 | +0.19 | 2300 | -168.0, 1.5, 13.1 | 54.6 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 62.66 | +0.00 | 2300 | -168.0, 1.5, 13.1 | 54.6 |
| 4a wing and tail infill 25 % to 8 % | 63.20 | +0.54 | 2280 | -165.6, 1.5, 12.3 | 53.8 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 63.88 | +0.68 | 2331 | -162.5, 1.5, 11.2 | 52.7 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.29 | +0.41 | 2316 | -160.7, 1.5, 11.5 | 53.0 |
