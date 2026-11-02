# WS-03 strength checks

Loads: 3 g landing, front wheel 14.3 N, rear wheel 18.6 N, cornering force 0.6 x load. Beam FE on the real tube graphs (PETG E 1500 MPa), design stress 25 MPa. Factor of safety below 2 is flagged.

| check | factor of safety | verdict |
|---|---|---|
| Front arm (truss FE), 3 g landing + cornering; max 8.0 MPa in U0i-U1i, tip deflection 2.1 mm | 3.1 | ok |
| Rear arm (truss FE), 3 g landing + cornering, wheel 46 mm off the arm; max 11.9 MPa in 4ni-4no, tip deflection 1.1 mm | 2.1 | ok |
| Tube frame (FE), 6 g equivalent on the pivot pads, feet fixed; max 9.3 MPa in PS2+-FP1+, deflection 1.19 mm | 2.7 | ok |
| Kingpin 4 mm steel, cantilever from the carrier tab, cornering | 5.5 | ok |
| Steer tie rod, 3 mm steel turnbuckle, buckling at servo stall | 7.3 | ok |
| Upper link (6 mm bar), buckling under 16 N | 5.9 | ok |
| Carrier kingpin cantilever tube (brace ignored), 3 g landing | 2.2 | ok |
| Knuckle steering V tubes, axial at servo stall | 5.8 | ok |
