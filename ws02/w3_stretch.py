"""WS-03 wheelbase stretch: everything behind the seam plane x = SEAM moves back by STRETCH; anything that straddles it stretches.

The seam crosses only tubes, the skin, the base plate and the rear shaft (the centre diff ends at x -195, the rear bevel case starts at x -244 before the shift).
"""
SEAM = -213.0
STRETCH = 90.0
import math

WHEELBASE = 360.0 + STRETCH
RAKE_DEG = 4.0
RAXLE_Z = -WHEELBASE * math.tan(math.radians(RAKE_DEG))       # rear axle height in the chassis frame (ground line stays raked 4 deg)


def fx(x):
    """Map an old x to the stretched x (points behind the seam move back; the seam itself is fixed)."""
    return x - STRETCH if x < SEAM else x


def back(x):
    """Rigid shift for something that lies wholly behind the seam (a wheel, a gear case, a wing)."""
    return x - STRETCH


def pts(points):
    """fx applied to the x of every (x, v) point."""
    return [(fx(x), v) for x, v in points]
