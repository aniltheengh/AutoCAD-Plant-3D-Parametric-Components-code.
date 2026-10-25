"""Hollow spacer geometry with two reference ports, all dimensions in mm.

No pipe schedule, pressure class, or end treatment is implied.
"""

import math

from varmain.primitiv import *
from varmain.custom import *


def _positive(name, value):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("%s must be a positive finite number." % name)
    if math.isnan(number) or math.isinf(number) or number <= 0.0:
        raise ValueError("%s must be a positive finite number." % name)
    return number


@activate(Group="Sleeve",
          TooltipShort="AT hollow spacer",
          TooltipLong="Hollow spacer along X; illustrative dimensions in mm",
          LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(OD=LENGTH, TooltipShort="Outside diameter (mm)")
@param(ID=LENGTH, TooltipShort="Bore diameter (mm)")
@param(L=LENGTH, TooltipShort="Face-to-face length (mm)")
def AT_SPACER(s, OD=114.3, ID=102.3, L=100.0, **kw):
    OD = _positive("OD", OD)
    ID = _positive("ID", ID)
    L = _positive("L", L)
    if ID >= OD:
        raise ValueError("ID must be smaller than OD to leave a positive wall.")

    # O is the bore RADIUS, not the bore diameter.
    CYLINDER(s, R=OD / 2.0, H=L, O=ID / 2.0).rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
