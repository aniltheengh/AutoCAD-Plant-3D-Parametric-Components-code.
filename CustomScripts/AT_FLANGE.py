"""Flat drilled ring/flange geometry, all dimensions in millimetres.

Illustrative only: no JIS/ASME dimensional table, hub, facing, or rating.
Catalog end types must be assigned for the actual intended component.
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


@activate(Group="Flange",
          TooltipShort="AT drilled flat flange",
          TooltipLong="Flat drilled ring along X; illustrative dimensions in mm",
          LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(OD=LENGTH, TooltipShort="Outside diameter (mm)")
@param(ID=LENGTH, TooltipShort="Bore diameter (mm)")
@param(T=LENGTH, TooltipShort="Plate thickness (mm)")
@param(BCD=LENGTH, TooltipShort="Bolt circle diameter (mm)")
@param(HD=LENGTH, TooltipShort="Bolt hole diameter (mm)")
@param(N=ENUM, TooltipShort="Number of equally spaced holes")
@enum(4, "4 holes")
@enum(8, "8 holes")
@enum(12, "12 holes")
@enum(16, "16 holes")
def AT_FLANGE(s, OD=180.0, ID=90.0, T=20.0,
              BCD=140.0, HD=18.0, N=4, **kw):
    OD = _positive("OD", OD)
    ID = _positive("ID", ID)
    T = _positive("T", T)
    BCD = _positive("BCD", BCD)
    HD = _positive("HD", HD)
    if N not in (4, 8, 12, 16):
        raise ValueError("N must be one of 4, 8, 12, or 16.")
    N = int(N)
    if ID >= OD:
        raise ValueError("ID must be smaller than OD.")
    if BCD - HD <= ID:
        raise ValueError("Bolt holes must leave material between holes and bore.")
    if BCD + HD >= OD:
        raise ValueError("Bolt holes must leave material at the outside edge.")

    # Adjacent centres are separated by a chord, not by arc length.
    if BCD * math.sin(math.pi / N) <= HD:
        raise ValueError("Adjacent bolt holes must not touch or overlap.")

    body = CYLINDER(s, R=OD / 2.0, H=T, O=ID / 2.0).rotateY(90)
    # Extend cutters beyond both faces to avoid coincident end faces.
    clearance = max(0.01, T * 0.0001)
    for index in range(N):
        angle = 2.0 * math.pi * index / N
        y = (BCD / 2.0) * math.cos(angle)
        z = (BCD / 2.0) * math.sin(angle)
        cutter = CYLINDER(s, R=HD / 2.0, H=T + 2.0 * clearance,
                          O=0.0).rotateY(90).translate((-clearance, y, z))
        # Autodesk's API subtracts cutter from body, retaining body.
        body.subtractFrom(cutter)
        cutter.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((T, 0.0, 0.0), (1.0, 0.0, 0.0))
