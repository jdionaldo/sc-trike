# Section check of the printed articulating parts

Allowable = 20 MPa (printed PETG across the layers) / safety 2 = 10 MPa. Loads are ASSUMED, see `tools/strength_check.py`.

| Part | Load | Weakest section mm2 | Stress MPa | Allowable MPa | Utilisation | Note |
|---|---|---|---|---|---|---|
| Tie rod | 101 N axial (servo stall through the horn) | 18.1 | 5.6 | 10.0 | 56 % | Euler load 39 N (pinned ends); buckling load ratio 2.60 |
| Uplink | 80 N axial (share of the landing load carried by the link (ASSUMED)) | 42.3 | 1.9 | 10.0 | 19 % | Euler load 161 N (pinned ends); buckling load ratio 0.50 |
| Steering horn | 912 N.mm bending (stall torque at the horn root: F x 9 mm to the stud (60 % of the radius)) | 16.1 | 15.8 | 10.0 | 158 % | best case, load along the strong axis (Z 58 mm3); load along the weak axis (Z 2 mm3) is 450 MPa |
| Knuckle | 4280 N.mm bending (bump 65 N x 40 mm + side 30 N x 56 mm) | 52.3 | 41.5 | 10.0 | 415 % | best case, load along the strong axis (Z 103 mm3); load along the weak axis (Z 42 mm3) is 103 MPa |
| Carrier | 3630 N.mm bending (bump 65 N x 30 mm + side 30 N x 56 mm) | 66.9 | 43.6 | 10.0 | 436 % | best case, load along the strong axis (Z 83 mm3); load along the weak axis (Z 46 mm3) is 79 MPa |
| Lean horn | 1216 N.mm bending (lean servo stall, 80 % of the torque at the root) | 38.5 | 11.8 | 10.0 | 118 % | best case, load along the strong axis (Z 103 mm3); load along the weak axis (Z 15 mm3) is 84 MPa |
| Lean rocker | 1520 N.mm bending (lean servo stall through the rocker) | 44.2 | 14.0 | 10.0 | 140 % | best case, load along the strong axis (Z 109 mm3); load along the weak axis (Z 16 mm3) is 94 MPa |
