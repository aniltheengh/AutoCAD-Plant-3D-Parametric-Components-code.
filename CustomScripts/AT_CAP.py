"""Hollow pipe cap with a 2:1 ellipsoidal head, dimensions in mm.

Open end at X=0 (one port pointing -X); outer crown at X=L, along +X.
Illustrative: no weld bevel, knuckle contour, or standard dimensions.
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


@activate(Group="Cap", TooltipShort="AT ellipsoidal pipe cap",
          TooltipLong="Hollow cap with 2:1 head along +X; units mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(OD=LENGTH, TooltipShort="Outside diameter (mm)")
@param(WT=LENGTH, TooltipShort="Wall thickness (mm)")
@param(L=LENGTH, TooltipShort="Open end to outer crown (mm)")
def AT_CAP(s, OD=114.3, WT=6.0, L=64.0, **kw):
    OD, WT, L = _positive("OD", OD), _positive("WT", WT), _positive("L", L)
    if 2.0 * WT >= OD:
        raise ValueError("WT must be less than OD/2 to leave a bore.")
    outer_radius = OD / 2.0
    inner_radius = outer_radius - WT
    # ELLIPSOIDHEAD2 is a 2:1 head: its height is half its radius.
    outer_base = L - outer_radius / 2.0
    # Lowering the inner head by WT gives a crown as thick as the wall.
    inner_base = L - WT - inner_radius / 2.0
    if inner_base <= 0.0:
        raise ValueError("L must exceed OD/4 + WT/2 to fit the head and crown wall.")

    body = CYLINDER(s, R=outer_radius, H=outer_base, O=0.0).rotateY(90)
    head = ELLIPSOIDHEAD2(s, R=outer_radius).rotateY(90)
    head.translate((outer_base, 0.0, 0.0))
    body.uniteWith(head)
    head.erase()

    clearance = max(0.01, L * 0.0001)
    cavity = CYLINDER(s, R=inner_radius, H=inner_base + clearance, O=0.0).rotateY(90)
    cavity.translate((-clearance, 0.0, 0.0))
    inner_head = ELLIPSOIDHEAD2(s, R=inner_radius).rotateY(90)
    inner_head.translate((inner_base, 0.0, 0.0))
    cavity.uniteWith(inner_head)
    inner_head.erase()
    body.subtractFrom(cavity)
    cavity.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
