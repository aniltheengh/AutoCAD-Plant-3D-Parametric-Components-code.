"""Round U-bolt body, with smooth legs; no helical threads or nuts.

Pipe axis X; origin is pipe centre. Units mm. Not a load-rated fastener.
"""

import math
from varmain.primitiv import *
from varmain.custom import *


def _dimension(name, value, zero=False):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("%s must be a finite dimension." % name)
    if math.isnan(number) or math.isinf(number) or number < 0.0:
        raise ValueError("%s must be a finite nonnegative dimension." % name)
    if not zero and number == 0.0:
        raise ValueError("%s must be positive." % name)
    return number


@activate(Group="Support", TooltipShort="AT round U-bolt body",
          TooltipLong="Round U-bolt with smooth legs; pipe axis X, units mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(PD=LENGTH, TooltipShort="Pipe outside diameter (mm)")
@param(C=LENGTH0, TooltipShort="Radial clearance to pipe (mm)")
@param(RD=LENGTH, TooltipShort="Rod diameter (mm)")
@param(H=LENGTH, TooltipShort="Pipe centre to leg ends (mm)")
def AT_UBOLT(s, PD=114.3, C=1.0, RD=12.0, H=100.0, **kw):
    PD, C = _dimension("PD", PD), _dimension("C", C, zero=True)
    RD, H = _dimension("RD", RD), _dimension("H", H)
    rod_radius = RD / 2.0
    bend_radius = PD / 2.0 + C + rod_radius
    # TORUS R1 is centreline radius; R2 is the circular section radius.
    bolt = TORUS(s, R1=bend_radius, R2=rod_radius).rotateY(90)
    extent = bend_radius + rod_radius + 1.0
    lower_half = BOX(s, H=2.0 * extent, L=2.0 * extent, W=extent)
    lower_half.translate((0.0, 0.0, -extent / 2.0))
    bolt.subtractFrom(lower_half)
    lower_half.erase()
    for sign in (-1.0, 1.0):
        leg = CYLINDER(s, R=rod_radius, H=H, O=0.0)
        leg.translate((0.0, sign * bend_radius, -H))
        bolt.uniteWith(leg)
        leg.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
