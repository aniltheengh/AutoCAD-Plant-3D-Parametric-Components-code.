"""Concentric hollow reducer with independently specified end bores, in mm.

Large end at X=0; small end at X=L. No weld bevels or standard dimensions.
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


@activate(Group="Reducer", TooltipShort="AT concentric reducer",
          TooltipLong="Hollow concentric reducer along X; units mm",
          LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(OD1=LENGTH, TooltipShort="Large-end outside diameter (mm)")
@param(OD2=LENGTH, TooltipShort="Small-end outside diameter (mm)")
@param(ID1=LENGTH, TooltipShort="Large-end bore diameter (mm)")
@param(ID2=LENGTH, TooltipShort="Small-end bore diameter (mm)")
@param(L=LENGTH, TooltipShort="Axial length (mm)")
def AT_REDUCER(s, OD1=168.3, OD2=114.3, ID1=154.1,
               ID2=102.3, L=150.0, **kw):
    OD1, OD2 = _positive("OD1", OD1), _positive("OD2", OD2)
    ID1, ID2 = _positive("ID1", ID1), _positive("ID2", ID2)
    L = _positive("L", L)
    if OD1 <= OD2 or ID1 <= ID2:
        raise ValueError("Both the outside diameter and bore must reduce from end 1 to end 2.")
    if ID1 >= OD1 or ID2 >= OD2:
        raise ValueError("Each bore must be smaller than its corresponding outside diameter.")
    body = CONE(s, R1=OD1 / 2.0, R2=OD2 / 2.0, H=L, E=0.0).rotateY(90)
    slope = (ID2 - ID1) / (2.0 * L)
    # Extrapolate the bore past both end faces while preserving end diameters.
    clearance = min(L * 0.0001, (ID2 / 4.0) / abs(slope))
    bore = CONE(s, R1=ID1 / 2.0 - slope * clearance,
                R2=ID2 / 2.0 + slope * clearance,
                H=L + 2.0 * clearance, E=0.0).rotateY(90)
    bore.translate((-clearance, 0.0, 0.0))
    body.subtractFrom(bore)
    bore.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
