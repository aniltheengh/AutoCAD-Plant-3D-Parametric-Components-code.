"""Hollow straight tee, equal or reducing branch, dimensions in mm.

Origin at the run/branch centreline intersection; run along X, branch +Y.
No weld bevels, forged contours, crotch radius, or standard dimensions.
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


@activate(Group="Tee", TooltipShort="AT straight tee",
          TooltipLong="Hollow tee; run along X, branch along +Y; units mm",
          LengthUnit="mm", Ports=3)
@group("MainDimensions")
@param(OD1=LENGTH, TooltipShort="Run outside diameter (mm)")
@param(ID1=LENGTH, TooltipShort="Run bore diameter (mm)")
@param(OD2=LENGTH, TooltipShort="Branch outside diameter (mm)")
@param(ID2=LENGTH, TooltipShort="Branch bore diameter (mm)")
@param(C=LENGTH, TooltipShort="Centre to run end (mm)")
@param(M=LENGTH, TooltipShort="Centre to branch end (mm)")
def AT_TEE(s, OD1=114.3, ID1=102.3, OD2=114.3, ID2=102.3,
           C=105.0, M=105.0, **kw):
    OD1, ID1 = _positive("OD1", OD1), _positive("ID1", ID1)
    OD2, ID2 = _positive("OD2", OD2), _positive("ID2", ID2)
    C, M = _positive("C", C), _positive("M", M)
    if ID1 >= OD1 or ID2 >= OD2:
        raise ValueError("Each bore must be smaller than its outside diameter.")
    if OD2 > OD1 or ID2 > ID1:
        raise ValueError("The branch may not be larger than the run.")
    if C <= OD2 / 2.0:
        raise ValueError("C must exceed OD2/2 so the branch fits on the run.")
    if M <= OD1 / 2.0:
        raise ValueError("M must exceed OD1/2 so the branch projects beyond the run.")

    clearance = max(0.01, max(C, M) * 0.0001)
    body = CYLINDER(s, R=OD1 / 2.0, H=2.0 * C, O=0.0).rotateY(90)
    body.translate((-C, 0.0, 0.0))
    # rotateY(90) turns +Z to +X; rotateZ(90) then turns +X to +Y.
    branch = CYLINDER(s, R=OD2 / 2.0, H=M, O=0.0).rotateY(90).rotateZ(90)
    body.uniteWith(branch)
    branch.erase()

    run_bore = CYLINDER(s, R=ID1 / 2.0, H=2.0 * (C + clearance), O=0.0).rotateY(90)
    run_bore.translate((-C - clearance, 0.0, 0.0))
    body.subtractFrom(run_bore)
    run_bore.erase()
    # The branch bore starts on the run axis, inside the run bore.
    branch_bore = CYLINDER(s, R=ID2 / 2.0, H=M + clearance, O=0.0).rotateY(90).rotateZ(90)
    body.subtractFrom(branch_bore)
    branch_bore.erase()

    s.setPoint((-C, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, M, 0.0), (0.0, 1.0, 0.0))
