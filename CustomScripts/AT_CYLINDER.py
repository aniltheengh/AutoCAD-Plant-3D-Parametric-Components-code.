"""Parametric learning cylinder; millimetres, longitudinal axis +X.

Load through AutoCAD Plant 3D, not a standalone Python interpreter.
The single point is a support/reference anchor, not a pipe connection.
"""

import math

from varmain.primitiv import *
from varmain.custom import *


def _positive(name, value):
    """Validate before asking Plant 3D to construct any geometry."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("%s must be a positive finite number." % name)
    if math.isnan(number) or math.isinf(number) or number <= 0.0:
        raise ValueError("%s must be a positive finite number." % name)
    return number


@activate(Group="Support",
          TooltipShort="AT learning cylinder",
          TooltipLong="Solid cylinder along X; illustrative dimensions in mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="Outside diameter (mm)")
@param(L=LENGTH, TooltipShort="Length along X (mm)")
def AT_CYLINDER(s, D=100.0, L=300.0, **kw):
    D = _positive("D", D)
    L = _positive("L", L)

    # A cylinder starts at Z=0 and extends along +Z; turn it along +X.
    CYLINDER(s, R=D / 2.0, H=L, O=0.0).rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
