"""Hollow 90-degree elbow; inlet at origin, bends from +X toward -Y.

A quarter of a hollow torus gives an unambiguous bend-centre convention.
Units mm; no straight tangents, bevels, or pressure class are included.
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


@activate(Group="Elbow", TooltipShort="AT hollow 90-degree elbow",
          TooltipLong="Hollow quarter bend in XY plane; units mm",
          LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(OD=LENGTH, TooltipShort="Tube outside diameter (mm)")
@param(ID=LENGTH, TooltipShort="Tube bore diameter (mm)")
@param(BR=LENGTH, TooltipShort="Bend centreline radius (mm)")
def AT_ELBOW90(s, OD=114.3, ID=102.3, BR=152.4, **kw):
    OD, ID, BR = _positive("OD", OD), _positive("ID", ID), _positive("BR", BR)
    if ID >= OD:
        raise ValueError("ID must be smaller than OD.")
    if BR <= OD / 2.0:
        raise ValueError("BR must exceed OD/2 to avoid a self-intersecting bend.")
    body = TORUS(s, R1=BR, R2=OD / 2.0)
    bore = TORUS(s, R1=BR, R2=ID / 2.0)
    body.subtractFrom(bore)
    bore.erase()
    extent = BR + OD / 2.0 + 1.0
    negative_x = BOX(s, H=extent, L=2.0 * extent, W=2.0 * extent)
    negative_x.translate((-extent / 2.0, 0.0, 0.0))
    body.subtractFrom(negative_x)
    negative_x.erase()
    negative_y = BOX(s, H=2.0 * extent, L=extent, W=2.0 * extent)
    negative_y.translate((0.0, -extent / 2.0, 0.0))
    body.subtractFrom(negative_y)
    negative_y.erase()
    body.translate((0.0, -BR, 0.0))
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((BR, -BR, 0.0), (0.0, -1.0, 0.0))
