"""Welded T-section pipe shoe: vertical web on a flat base plate, in mm.

Pipe axis X, pipe centre at the origin; the shoe hangs below, along -Z.
The web top is cut to the pipe radius. Not a load-rated support.
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


@activate(Group="Support", TooltipShort="AT T-section pipe shoe",
          TooltipLong="Web and base plate shoe below a pipe along X; units mm",
          LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(PD=LENGTH, TooltipShort="Pipe outside diameter (mm)")
@param(L=LENGTH, TooltipShort="Shoe length along X (mm)")
@param(H=LENGTH, TooltipShort="Pipe centre to underside of base (mm)")
@param(W=LENGTH, TooltipShort="Base plate width along Y (mm)")
@param(T=LENGTH, TooltipShort="Web and base plate thickness (mm)")
def AT_PIPE_SHOE(s, PD=114.3, L=200.0, H=100.0, W=120.0, T=10.0, **kw):
    PD, L, H = _positive("PD", PD), _positive("L", L), _positive("H", H)
    W, T = _positive("W", W), _positive("T", T)
    if H <= PD / 2.0 + T:
        raise ValueError("H must exceed PD/2 + T so the base plate clears the pipe.")
    if T >= W:
        raise ValueError("W must exceed T so the base plate projects beyond the web.")
    if T >= PD:
        raise ValueError("T must be smaller than PD so the web seats on the pipe.")

    # BOX's local spans are H=X, L=Y, W=Z; its base point is its centre.
    # The web rises to the pipe centre; the pipe cut below shapes its top.
    body = BOX(s, H=L, L=T, W=H).translate((0.0, 0.0, -H / 2.0))
    base = BOX(s, H=L, L=W, W=T).translate((0.0, 0.0, -H + T / 2.0))
    body.uniteWith(base)
    base.erase()
    clearance = max(0.01, L * 0.0001)
    pipe = CYLINDER(s, R=PD / 2.0, H=L + 2.0 * clearance, O=0.0).rotateY(90)
    pipe.translate((-L / 2.0 - clearance, 0.0, 0.0))
    body.subtractFrom(pipe)
    pipe.erase()

    # One support anchor at the pipe centre; this is not a flow port.
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
