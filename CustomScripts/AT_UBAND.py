"""Flat strap U-band with two drilled mounting feet, dimensions in mm.

Pipe axis X, pipe centre at the origin; crown above Z=0, feet below.
The strap uses a semicircular crown and square leg/foot transitions.
This is illustrative geometry, not a load-rated or fabrication-ready clamp.
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


@activate(Group="Support", TooltipShort="AT flat strap U-band",
          TooltipLong="Flat U-band with drilled feet; pipe axis X, units mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(PD=LENGTH, TooltipShort="Pipe outside diameter (mm)")
@param(C=LENGTH0, TooltipShort="Radial clearance to pipe (mm)")
@param(W=LENGTH, TooltipShort="Strap width along X (mm)")
@param(T=LENGTH, TooltipShort="Strap thickness (mm)")
@param(H=LENGTH, TooltipShort="Pipe centre to underside of feet (mm)")
@param(F=LENGTH, TooltipShort="Foot projection beyond leg (mm)")
@param(HD=LENGTH, TooltipShort="Mounting hole diameter (mm)")
def AT_UBAND(s, PD=114.3, C=1.0, W=30.0, T=6.0,
             H=75.0, F=35.0, HD=11.0, **kw):
    PD, C = _dimension("PD", PD), _dimension("C", C, zero=True)
    W, T = _dimension("W", W), _dimension("T", T)
    H, F = _dimension("H", H), _dimension("F", F)
    HD = _dimension("HD", HD)
    if H <= T:
        raise ValueError("H must exceed T to leave straight legs above the feet.")
    if HD >= W or HD >= F:
        raise ValueError("HD must be smaller than both W and F for hole edge clearance.")

    inner = PD / 2.0 + C
    outer = inner + T
    # CYLINDER runs along Z before rotation; its bore O is a radius.
    band = CYLINDER(s, R=outer, H=W, O=inner).rotateY(90)
    band.translate((-W / 2.0, 0.0, 0.0))
    # BOX's local spans are H=X, L=Y, W=Z (Autodesk primitive diagram).
    extent = outer + W + 1.0
    lower_half = BOX(s, H=2.0 * extent, L=2.0 * extent, W=extent)
    lower_half.translate((0.0, 0.0, -extent / 2.0))
    band.subtractFrom(lower_half)
    lower_half.erase()

    for sign in (-1.0, 1.0):
        leg = BOX(s, H=W, L=T, W=H)
        leg.translate((0.0, sign * (inner + T / 2.0), -H / 2.0))
        band.uniteWith(leg)
        leg.erase()
        # The foot overlaps the leg by T, giving one connected strap solid.
        foot = BOX(s, H=W, L=T + F, W=T)
        foot.translate((0.0, sign * (inner + (T + F) / 2.0), -H + T / 2.0))
        band.uniteWith(foot)
        foot.erase()
        allowance = max(0.01, T * 0.0001)
        hole = CYLINDER(s, R=HD / 2.0, H=T + 2.0 * allowance, O=0.0)
        hole.translate((0.0, sign * (outer + F / 2.0), -H - allowance))
        band.subtractFrom(hole)
        hole.erase()

    # One support anchor at the pipe centre; this is not a flow port.
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
