"""Build and print-check the WS-03 drivetrain parts."""
import build, validate
from params import P
from parts import w3_drive
for part in w3_drive.build(P):
    build.run_part(part)
    r = validate.validate_part(part.name, part.walls, part.supports)
    bad = {k: v[1] for k, v in r.items() if not v[0]}
    print(part.name, "OK" if not bad else bad)
