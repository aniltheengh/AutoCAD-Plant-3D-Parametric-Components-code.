# GSKMB - flat gasket that also draws hex-head MACHINE BOLTS + one nut per bolt.
# Put in: <Shared Content>\CPak Common\CustomScripts\GSKMB.py
# Register: PLANTREGISTERCUSTOMSCRIPTS
# Test:     (arxload "PnP3dACPAdapter")  then  (testacpscript "GSKMB")
#           (testacpscript "GSKMB" "N" "8" "K" "180" "BD" "20" "BL" "70" "T" "20")
# After editing, restart Plant 3D before testing again (scripts are cached per session).
#
# Geometry: runs along +X. Port 1 at x=0 facing -X, port 2 at x=L facing +X.
# Bolt head sits on the back face of flange 1 (port-1 side), nut on the back face of flange 2.
# Defaults = JIS 10K 50A example (gasket 96/61, PCD 120, 4 x M16, flange 16) - check against your tables.

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


def _bolt_count(value):
    # N is a count, not a length: 0 (gasket only) or a whole number >= 2.
    message = "N must be 0 (no bolts) or a whole number of bolts, at least 2."
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(message)
    if math.isnan(number) or math.isinf(number) or number != int(number):
        raise ValueError(message)
    if number < 0 or number == 1:
        raise ValueError(message)
    return int(number)


@activate(Group="Gasket",
          TooltipShort="Gasket + bolts",
          TooltipLong="Flat gasket with hex machine bolts and nuts (visual)",
          FirstPortEndtypes="FL",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions")
@param(D=LENGTH,  TooltipShort="Gasket OD",        TooltipLong="Gasket outside diameter")
@param(D1=LENGTH, TooltipShort="Gasket ID",        TooltipLong="Gasket inside diameter")
@param(L=LENGTH,  TooltipShort="Gasket thickness", TooltipLong="Gasket thickness")
@group("Bolting")
@param(N=INT,     TooltipShort="No. of bolts",     TooltipLong="Number of bolt holes (0 = no bolts)")
@param(K=LENGTH,  TooltipShort="Bolt circle dia",  TooltipLong="Bolt circle diameter (PCD)")
@param(BD=LENGTH, TooltipShort="Bolt dia",         TooltipLong="Nominal bolt diameter (M size)")
@param(BL=LENGTH, TooltipShort="Bolt length",      TooltipLong="Bolt length, measured from under the head")
@param(T=LENGTH,  TooltipShort="Flange thickness", TooltipLong="Flange thickness at the bolt holes (each side)")
def GSKMB(s, D=96.0, D1=61.0, L=3.0, N=4, K=120.0, BD=16.0, BL=55.0, T=16.0, **kw):
    # --- check every input before any geometry is created ---
    D, D1, L = _positive("D", D), _positive("D1", D1), _positive("L", L)
    K, BD = _positive("K", K), _positive("BD", BD)
    BL, T = _positive("BL", BL), _positive("T", T)
    n = _bolt_count(N)
    if D1 >= D:
        raise ValueError("D1 must be smaller than D to leave a gasket ring.")

    headH = 0.65 * BD           # hex head height  (M16 ~ 10 mm)
    nutH  = 0.80 * BD           # hex nut height   (M16 ~ 13 mm)
    hexR  = 0.80 * BD           # round stand-in for the hex (between flats/2 and corners/2)
    grip = 2.0 * T + L
    if n:
        if K <= D:
            raise ValueError("K must exceed D so the bolts lie outside the gasket.")
        if BL <= grip:
            raise ValueError("BL must exceed 2T + L so each bolt reaches its nut.")
        # Neighbouring heads and nuts are 2*hexR across; their centres are a chord apart.
        if K * math.sin(math.pi / n) <= 2.0 * hexR:
            raise ValueError("Neighbouring bolt heads would overlap: use fewer or smaller bolts, or a larger K.")

    # --- gasket ring (O is the bore RADIUS, so no cutter is needed) ---
    g = CYLINDER(s, R=D/2.0, H=L, O=D1/2.0).rotateY(90)

    # --- machine bolts ---
    if n:
        step = 360.0 / n
        start = step / 2.0          # holes straddle the centrelines (JIS / ASME practice)

        xUnder = -T                 # underside of head = back face of flange 1
        xHead  = xUnder - headH     # head start
        xNut   = L + T              # nut sits on back face of flange 2

        for i in range(n):
            a = start + i * step

            shank = CYLINDER(s, R=BD/2.0, H=BL, O=0).rotateY(90) \
                    .translate((xUnder, K/2.0, 0)).rotateX(a)
            g.uniteWith(shank); shank.erase()

            head = CYLINDER(s, R=hexR, H=headH, O=0).rotateY(90) \
                   .translate((xHead, K/2.0, 0)).rotateX(a)
            g.uniteWith(head); head.erase()

            nut = CYLINDER(s, R=hexR, H=nutH, O=0).rotateY(90) \
                  .translate((xNut, K/2.0, 0)).rotateX(a)
            g.uniteWith(nut); nut.erase()

    # --- ports (compare with a stock gasket script in variants.zip if ports misbehave) ---
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L,   0.0, 0.0), ( 1.0, 0.0, 0.0))
    return
