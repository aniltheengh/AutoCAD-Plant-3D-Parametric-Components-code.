"""Grooved mechanical coupling housing with two bolt pads, dimensions in mm.

Housing along X from 0 to HL; the pipe ends meet at its centre with gap G.
Ports sit at the pipe ends, inside the housing, like a socket fitting.
Illustrative envelope: no keys, gasket, grooves, bolts or rated sizes.
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


@activate(Group="Coupling", TooltipShort="AT grooved coupling",
          TooltipLong="Grooved coupling housing with bolt pads along X; units mm",
          LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(PD=LENGTH, TooltipShort="Pipe outside diameter (mm)")
@param(HD=LENGTH, TooltipShort="Housing outside diameter (mm)")
@param(HL=LENGTH, TooltipShort="Housing length along X (mm)")
@param(G=LENGTH, TooltipShort="Gap between pipe ends (mm)")
@param(P=LENGTH, TooltipShort="Bolt pad projection beyond housing (mm)")
@param(PH=LENGTH, TooltipShort="Bolt pad height along Z (mm)")
@param(BH=LENGTH, TooltipShort="Bolt hole diameter (mm)")
def AT_GROOVED_COUPLING(s, PD=114.3, HD=150.0, HL=60.0, G=3.0,
                        P=30.0, PH=40.0, BH=14.0, **kw):
    PD, HD, HL = _positive("PD", PD), _positive("HD", HD), _positive("HL", HL)
    G, P = _positive("G", G), _positive("P", P)
    PH, BH = _positive("PH", PH), _positive("BH", BH)
    if PD >= HD:
        raise ValueError("HD must exceed PD to leave a housing wall.")
    if PH >= HD:
        raise ValueError("PH must be smaller than HD so each pad meets the housing.")
    if BH >= P or BH >= HL:
        raise ValueError("BH must be smaller than P and HL for hole edge clearance.")
    if G >= HL:
        raise ValueError("G must be smaller than HL so both pipe ends are inside.")

    body = CYLINDER(s, R=HD / 2.0, H=HL, O=0.0).rotateY(90)
    # Each pad starts on the chord where its top and bottom faces meet
    # the housing, so the pad and housing blend without a step.
    pad_start = math.sqrt((HD / 2.0) ** 2 - (PH / 2.0) ** 2)
    pad_end = HD / 2.0 + P
    clearance = max(0.01, HL * 0.0001)
    for sign in (-1.0, 1.0):
        # BOX's local spans are H=X, L=Y, W=Z (Autodesk primitive diagram).
        pad = BOX(s, H=HL, L=pad_end - pad_start, W=PH)
        pad.translate((HL / 2.0, sign * (pad_start + pad_end) / 2.0, 0.0))
        body.uniteWith(pad)
        pad.erase()

    bore = CYLINDER(s, R=PD / 2.0, H=HL + 2.0 * clearance, O=0.0).rotateY(90)
    bore.translate((-clearance, 0.0, 0.0))
    body.subtractFrom(bore)
    bore.erase()
    for sign in (-1.0, 1.0):
        # Bolt axes run along Z, through the pad outside the housing.
        hole = CYLINDER(s, R=BH / 2.0, H=PH + 2.0 * clearance, O=0.0)
        hole.translate((HL / 2.0, sign * (HD / 2.0 + P / 2.0), -PH / 2.0 - clearance))
        body.subtractFrom(hole)
        hole.erase()

    s.setPoint(((HL - G) / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint(((HL + G) / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
