"""Flat drilled blind flange, one face reference point, dimensions in mm.

Illustrative solid plate geometry; no facing, bolts, or pressure rating.
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


@activate(Group="Flange", TooltipShort="AT blind flange",
          TooltipLong="Solid drilled flange plate along X; units mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(OD=LENGTH, TooltipShort="Outside diameter (mm)")
@param(T=LENGTH, TooltipShort="Plate thickness (mm)")
@param(BCD=LENGTH, TooltipShort="Bolt circle diameter (mm)")
@param(HD=LENGTH, TooltipShort="Bolt hole diameter (mm)")
@param(N=ENUM, TooltipShort="Number of equally spaced holes")
@enum(4, "4 holes")
@enum(8, "8 holes")
@enum(12, "12 holes")
@enum(16, "16 holes")
def AT_BLIND_FLANGE(s, OD=180.0, T=20.0, BCD=140.0, HD=18.0, N=4, **kw):
    OD, T = _positive("OD", OD), _positive("T", T)
    BCD, HD = _positive("BCD", BCD), _positive("HD", HD)
    if N not in (4, 8, 12, 16):
        raise ValueError("N must be one of 4, 8, 12, or 16.")
    N = int(N)
    if BCD + HD >= OD:
        raise ValueError("Bolt holes must leave material at the outside edge.")
    if BCD * math.sin(math.pi / N) <= HD:
        raise ValueError("Adjacent bolt holes must not touch or overlap.")
    body = CYLINDER(s, R=OD / 2.0, H=T, O=0.0).rotateY(90)
    clearance = max(0.01, T * 0.0001)
    for index in range(N):
        angle = 2.0 * math.pi * index / N
        cutter = CYLINDER(s, R=HD / 2.0, H=T + 2.0 * clearance, O=0.0).rotateY(90)
        cutter.translate((-clearance, BCD / 2.0 * math.cos(angle),
                          BCD / 2.0 * math.sin(angle)))
        body.subtractFrom(cutter)
        cutter.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
