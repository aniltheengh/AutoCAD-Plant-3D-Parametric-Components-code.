"""Render dimensioned PNG/SVG reference drawings from component defaults.

These are analytical orthographic illustrations, NOT Plant 3D screenshots.
Only this optional drawing tool requires matplotlib and Pillow.
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, Wedge, Arc
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
INK, FILL, DIM, GREY = "#153e4a", "#c6e2e4", "#b65a20", "#71818b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "svg.fonttype": "none", "svg.hashsalt": "plant3d-reference-v1",
                     "savefig.facecolor": "white"})


def defaults(name):
    source = ROOT / "CustomScripts" / (name + ".py")
    tree = ast.parse(source.read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    parameters = function.args.args[-len(function.args.defaults):]
    return {p.arg: ast.literal_eval(v) for p, v in zip(parameters, function.args.defaults)}


def rect(ax, x, y, w, h, **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=kw.pop("facecolor", FILL),
                           edgecolor=INK, linewidth=1.5, **kw))


def circle(ax, x, y, r, **kw):
    ax.add_patch(Circle((x, y), r, facecolor=kw.pop("facecolor", FILL),
                        edgecolor=kw.pop("edgecolor", INK), linewidth=1.5, **kw))


def horizontal(ax, a, b, y, label):
    ax.annotate("", (a, y), (b, y), arrowprops={"arrowstyle": "<->", "color": DIM, "lw": 1.1})
    ax.annotate(label, ((a + b) / 2, y), xytext=(0, 5), textcoords="offset points",
                color=DIM, ha="center", va="bottom")


def vertical(ax, x, a, b, label):
    ax.annotate("", (x, a), (x, b), arrowprops={"arrowstyle": "<->", "color": DIM, "lw": 1.1})
    ax.text(x, (a + b) / 2, label, color=DIM, ha="center", va="center", rotation=90,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})


def frame(ax, limits, title):
    ax.set_aspect("equal")
    ax.set_xlim(limits[0], limits[1])
    ax.set_ylim(limits[2], limits[3])
    ax.axis("off")
    ax.set_title(title, fontsize=11, color=GREY, pad=12)


def ring_face(ax, od, bore=0, bcd=0, hole=0, count=0, od_label="OD", bore_label="ID"):
    r = od / 2
    circle(ax, 0, 0, r)
    if bore:
        circle(ax, 0, 0, bore / 2, facecolor="white")
        ax.text(0, 0, "%s = %g" % (bore_label, bore), ha="center", va="center", color=INK)
    if count:
        circle(ax, 0, 0, bcd / 2, facecolor="none", edgecolor=GREY, linestyle="--")
        for i in range(count):
            angle = 2 * math.pi * i / count
            circle(ax, bcd / 2 * math.cos(angle), bcd / 2 * math.sin(angle), hole / 2, facecolor="white")
        ax.text(0, r + 12, "%g x hole diameter %g on BCD %g" % (count, hole, bcd), ha="center", color=INK)
    horizontal(ax, -r, r, -r - 20, "%s = %g" % (od_label, od))
    frame(ax, (-r * 1.35, r * 1.35, -r - 40, r + 30), "Face view / looking along X")


def straight(ax, diameter, length, bore=0, label="L"):
    r = diameter / 2
    rect(ax, 0, -r, length, diameter)
    if bore:
        for y in (-bore / 2, bore / 2):
            ax.plot([0, length], [y, y], "--", color=GREY, lw=1)
    ax.plot([-length * 0.08, length * 1.08], [0, 0], "-.", color=GREY, lw=0.7)
    horizontal(ax, 0, length, -r - max(diameter * 0.25, 15), "%s = %g" % (label, length))
    margin = max(diameter * 0.25, length * 0.15)
    frame(ax, (-margin, length + margin, -r - margin * 1.9, r + margin), "Side view / X to the right")


def draw_uband(ax, detail, p):
    inner, outer = p["PD"] / 2 + p["C"], p["PD"] / 2 + p["C"] + p["T"]
    h, t, f, w, hd = (p[k] for k in ("H", "T", "F", "W", "HD"))
    ax.add_patch(Wedge((0, 0), outer, 0, 180, width=t, facecolor=FILL, edgecolor=INK, lw=1.5))
    rect(ax, inner, -h, t, h)
    rect(ax, -outer, -h, t, h)
    rect(ax, inner, -h, t + f, t)
    rect(ax, -outer - f, -h, t + f, t)
    circle(ax, 0, 0, p["PD"] / 2, facecolor="none", edgecolor=GREY, linestyle="--")
    ax.text(0, 0, "PIPE\nPD = %g\nC = %g radial" % (p["PD"], p["C"]), ha="center", va="center", color=GREY)
    for sign in (-1, 1):
        centre = sign * (outer + f / 2)
        for edge in (-hd / 2, hd / 2):
            ax.plot([centre + edge] * 2, [-h, -h + t], "--", color=GREY, lw=1)
    vertical(ax, -outer - f - 17, -h, 0, "H = %g" % h)
    horizontal(ax, -inner, inner, -h - 22, "Inside width = %g" % (2 * inner))
    ax.annotate("T = %g" % t, (outer * 0.7, outer * 0.7), (outer + f * 0.45, outer * 0.92),
                color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    frame(ax, (-outer - f - 35, outer + f + 25, -h - 40, outer + 25), "Front view / pipe axis X out of page")
    rect(detail, 0, -w / 2, t + f, w)
    detail.plot([t, t], [-w / 2, w / 2], "--", color=GREY)
    circle(detail, t + f / 2, 0, hd / 2, facecolor="white")
    horizontal(detail, t, t + f, -w / 2 - 11, "F = %g" % f)
    vertical(detail, -10, -w / 2, w / 2, "W = %g" % w)
    detail.annotate("HD = %g" % hd, (t + f / 2, hd / 2), (t + f / 2, w / 2 + 10),
                    ha="center", color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    frame(detail, (-22, t + f + 14, -w / 2 - 25, w / 2 + 25), "One mounting foot / top view")


def draw_ubolt(ax, detail, p):
    rr = p["RD"] / 2
    r = p["PD"] / 2 + p["C"] + rr
    h = p["H"]
    ax.add_patch(Wedge((0, 0), r + rr, 0, 180, width=2 * rr, facecolor=FILL, edgecolor=INK, lw=1.5))
    rect(ax, r - rr, -h, 2 * rr, h)
    rect(ax, -r - rr, -h, 2 * rr, h)
    circle(ax, 0, 0, p["PD"] / 2, facecolor="none", edgecolor=GREY, linestyle="--")
    ax.text(0, 0, "PIPE\nPD = %g\nC = %g radial" % (p["PD"], p["C"]), ha="center", va="center", color=GREY)
    vertical(ax, -r - rr - 20, -h, 0, "H = %g" % h)
    horizontal(ax, -r, r, -h - 20, "Leg centres = %g" % (2 * r))
    frame(ax, (-r - rr - 40, r + rr + 30, -h - 35, r + rr + 25), "Front view / pipe axis X out of page")
    circle(detail, 0, 0, rr)
    horizontal(detail, -rr, rr, -rr - 4, "RD = %g" % p["RD"])
    frame(detail, (-rr * 2.5, rr * 2.5, -rr * 2.5, rr * 2), "Round rod section / enlarged")


def draw_reducer(ax, detail, p):
    length, a, b, ai, bi = (p[k] for k in ("L", "OD1", "OD2", "ID1", "ID2"))
    for sign in (-1, 1):
        ax.add_patch(Polygon([(0, sign * a / 2), (length, sign * b / 2),
                              (length, sign * bi / 2), (0, sign * ai / 2)],
                             facecolor=FILL, edgecolor=INK, lw=1.5))
    ax.plot([-10, length + 10], [0, 0], "-.", color=GREY, lw=0.8)
    horizontal(ax, 0, length, -a / 2 - 20, "L = %g" % length)
    vertical(ax, -22, -a / 2, a / 2, "OD1 = %g" % a)
    vertical(ax, length + 22, -b / 2, b / 2, "OD2 = %g" % b)
    frame(ax, (-45, length + 45, -a / 2 - 40, a / 2 + 20), "Axial section / X to the right")
    ring_face(detail, a, ai, od_label="OD1", bore_label="ID1")
    detail.set_title("Large-end face", fontsize=11, color=GREY)


def draw_elbow(ax, detail, p):
    r, od, bore = p["BR"], p["OD"], p["ID"]
    centre = (0, -r)
    ax.add_patch(Wedge(centre, r + od / 2, 0, 90, width=od, facecolor=FILL, edgecolor=INK, lw=1.5))
    for radius in (r - bore / 2, r + bore / 2):
        ax.add_patch(Arc(centre, 2 * radius, 2 * radius, theta1=0, theta2=90, color=GREY, ls="--", lw=1))
    ax.add_patch(Arc(centre, 2 * r, 2 * r, theta1=0, theta2=90, color=GREY, ls="-.", lw=0.8))
    ax.annotate("BR = %g" % r, (r / math.sqrt(2), -r + r / math.sqrt(2)), (r * 0.05, -r * 0.65),
                color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    ax.annotate("P1 / origin", (0, 0), (-od * 0.15, od * 0.8), ha="center", color=INK,
                arrowprops={"arrowstyle": "->", "color": INK})
    ax.annotate("P2", (r, -r), (r * 0.8, -r - od * 0.5), color=INK,
                arrowprops={"arrowstyle": "->", "color": INK})
    frame(ax, (-od * 0.65, r + od * 0.9, -r - od * 0.75, od), "Plan view / bend from +X toward -Y")
    ring_face(detail, od, bore)
    detail.set_title("End section / both ends equal", fontsize=11, color=GREY)


def draw_tee(ax, detail, p):
    a, ai, b, bi, c, m = (p[k] for k in ("OD1", "ID1", "OD2", "ID2", "C", "M"))
    rect(ax, -b / 2, 0, b, m)
    rect(ax, -c, -a / 2, 2 * c, a)
    for y in (-ai / 2, ai / 2):
        ax.plot([-c, c], [y, y], "--", color=GREY, lw=1)
    for x in (-bi / 2, bi / 2):
        ax.plot([x, x], [ai / 2, m], "--", color=GREY, lw=1)
    ax.plot([-c * 1.1, c * 1.1], [0, 0], "-.", color=GREY, lw=0.7)
    ax.plot([0, 0], [-a / 2 - 8, m * 1.08], "-.", color=GREY, lw=0.7)
    horizontal(ax, 0, c, -a / 2 - 18, "C = %g" % c)
    vertical(ax, c + 20, 0, m, "M = %g" % m)
    vertical(ax, -c - 20, -a / 2, a / 2, "OD1 = %g" % a)
    horizontal(ax, -b / 2, b / 2, m + 10, "OD2 = %g" % b)
    frame(ax, (-c - 45, c + 45, -a / 2 - 45, m + 35), "Front view / run along X, branch +Y")
    ring_face(detail, a, ai, od_label="OD1", bore_label="ID1")
    detail.set_title("Run end face / branch: OD2 %g, ID2 %g" % (b, bi), fontsize=11, color=GREY)


def ellipse_arc(base, radius, reverse=False):
    """Half-outline of a 2:1 head: semi-axes radius/2 along X, radius across."""
    angles = [math.pi * (i / 48.0 - 0.5) for i in range(49)]
    if reverse:
        angles.reverse()
    return [(base + radius / 2 * math.cos(t), radius * math.sin(t)) for t in angles]


def draw_cap(ax, detail, p):
    od, wt, length = p["OD"], p["WT"], p["L"]
    r, ri = od / 2, od / 2 - wt
    outer_base, inner_base = length - r / 2, length - wt - ri / 2
    # One C-shaped section: outer profile out, inner profile back.
    outline = ([(0, -r), (outer_base, -r)] + ellipse_arc(outer_base, r) + [(0, r), (0, ri)]
               + ellipse_arc(inner_base, ri, reverse=True) + [(0, -ri)])
    ax.add_patch(Polygon(outline, facecolor=FILL, edgecolor=INK, lw=1.5))
    ax.plot([-12, length + 12], [0, 0], "-.", color=GREY, lw=0.7)
    ax.plot([outer_base] * 2, [-r, r], ":", color=GREY, lw=0.8)
    horizontal(ax, 0, length, -r - 20, "L = %g" % length)
    vertical(ax, -22, -r, r, "OD = %g" % od)
    horizontal(ax, outer_base, length, r + 10, "Head = %g" % (r / 2))
    ax.annotate("WT = %g wall and crown" % wt, (length - wt / 2, 0), (length - 6, r * 0.45),
                color=DIM, ha="right", arrowprops={"arrowstyle": "->", "color": DIM})
    frame(ax, (-45, length + 30, -r - 40, r + 30), "Axial section / open end at X=0")
    ring_face(detail, od, od - 2 * wt, bore_label="Bore")
    detail.set_title("Open-end face", fontsize=11, color=GREY)


def draw_coupling(ax, detail, p):
    pd, hd, hl, g, pr, ph, bh = (p[k] for k in ("PD", "HD", "HL", "G", "P", "PH", "BH"))
    r = hd / 2
    start = math.sqrt(r * r - (ph / 2) ** 2)
    circle(ax, 0, 0, r)
    for sign in (-1, 1):
        inner, outer = sign * start, sign * (r + pr)
        ax.add_patch(Rectangle((min(inner, outer), -ph / 2), abs(outer - inner), ph,
                               facecolor=FILL, edgecolor="none"))
        ax.plot([inner, outer, outer, inner], [ph / 2, ph / 2, -ph / 2, -ph / 2], color=INK, lw=1.5)
        for edge in (-bh / 2, bh / 2):
            ax.plot([sign * (r + pr / 2) + edge] * 2, [-ph / 2, ph / 2], "--", color=GREY, lw=1)
    circle(ax, 0, 0, pd / 2, facecolor="white")
    ax.text(0, 0, "PIPE\nPD = %g" % pd, ha="center", va="center", color=GREY)
    horizontal(ax, -r, r, -r - 18, "HD = %g" % hd)
    horizontal(ax, r, r + pr, ph / 2 + 8, "P = %g" % pr)
    vertical(ax, -r - pr - 16, -ph / 2, ph / 2, "PH = %g" % ph)
    ax.annotate("BH = %g bolt hole" % bh, (r + pr / 2, -ph / 2), (r + pr / 2, -r * 0.75),
                ha="center", color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    frame(ax, (-r - pr - 35, r + pr + 25, -r - 40, r + 25), "End view / looking along X")
    rect(detail, 0, -r - pr, hl, 2 * (r + pr))
    for sign in (-1, 1):
        detail.plot([0, hl], [sign * start] * 2, color=INK, lw=0.8)
        circle(detail, hl / 2, sign * (r + pr / 2), bh / 2, facecolor="white")
    # Dashed pipes enter from both sides and stop at the two ports.
    for pipe_end, outside in (((hl - g) / 2, -15), ((hl + g) / 2, hl + 15)):
        for y in (-pd / 2, pd / 2):
            detail.plot([pipe_end, outside], [y, y], "--", color=GREY, lw=1)
        detail.plot([pipe_end] * 2, [-pd / 2, pd / 2], "--", color=GREY, lw=1)
    horizontal(detail, 0, hl, -r - pr - 24, "HL = %g" % hl)
    detail.annotate("Pipe ends\nG = %g" % g, ((hl + g) / 2, 0), (hl + 22, 0), ha="left",
                    va="center", color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    frame(detail, (-25, hl + 75, -r - pr - 45, r + pr + 15), "Top view / ports at the pipe ends")


def draw_shoe(ax, detail, p):
    pd, length, h, w, t = (p[k] for k in ("PD", "L", "H", "W", "T"))
    r = pd / 2
    seat = math.sqrt(r * r - (t / 2) ** 2)
    # The web top follows the pipe's underside across the web thickness.
    arc = [(y, -math.sqrt(r * r - y * y)) for y in (-t / 2 + t * i / 12.0 for i in range(13))]
    ax.add_patch(Polygon([(-t / 2, -h + t)] + arc + [(t / 2, -h + t)],
                         facecolor=FILL, edgecolor=INK, lw=1.5))
    rect(ax, -w / 2, -h, w, t)
    circle(ax, 0, 0, r, facecolor="none", edgecolor=GREY, linestyle="--")
    ax.text(0, 0, "PIPE\nPD = %g" % pd, ha="center", va="center", color=GREY)
    vertical(ax, -w / 2 - 16, -h, 0, "H = %g" % h)
    horizontal(ax, -w / 2, w / 2, -h - 18, "W = %g" % w)
    ax.annotate("T = %g web and base" % t, (t / 2, -h + t + (h - t - seat) / 2),
                (w / 2 * 0.55, -h + t + (h - t - seat) * 0.85), color=DIM,
                arrowprops={"arrowstyle": "->", "color": DIM})
    frame(ax, (-w / 2 - 40, w / 2 + 30, -h - 40, r + 25), "End view / pipe axis X out of page")
    rect(detail, -length / 2, -h, length, h - seat)
    detail.plot([-length / 2, length / 2], [-h + t] * 2, color=INK, lw=0.8)
    for y in (-r, r):
        detail.plot([-length / 2 - 15, length / 2 + 15], [y, y], "--", color=GREY, lw=1)
    detail.plot([-length / 2 - 15, length / 2 + 15], [0, 0], "-.", color=GREY, lw=0.7)
    horizontal(detail, -length / 2, length / 2, -h - 24, "L = %g" % length)
    frame(detail, (-length / 2 - 25, length / 2 + 25, -h - 45, r + 20), "Side view / X to the right")


def draw_gasket(ax, detail, p):
    d, d1, gl, n, k, bd, bl, t = (p[k] for k in ("D", "D1", "L", "N", "K", "BD", "BL", "T"))
    head_h, nut_h, hex_r = 0.65 * bd, 0.80 * bd, 0.80 * bd
    reach = k / 2 + hex_r + 10
    # Dashed flanges either side; the script draws only the gasket and bolting.
    for x0 in (-t, gl):
        ax.add_patch(Rectangle((x0, -reach), t, 2 * reach, fill=False, edgecolor=GREY, ls="--", lw=1))
    for sign in (-1, 1):
        rect(ax, 0, d1 / 2 if sign > 0 else -d / 2, gl, (d - d1) / 2)
        y = sign * k / 2
        rect(ax, -t, y - bd / 2, bl, bd)
        rect(ax, -t - head_h, y - hex_r, head_h, 2 * hex_r)
        rect(ax, gl + t, y - hex_r, nut_h, 2 * hex_r)
    ax.plot([-t - head_h - 12, -t + bl + 12], [0, 0], "-.", color=GREY, lw=0.7)
    horizontal(ax, -t, -t + bl, -reach - 12, "BL = %g" % bl)
    horizontal(ax, -t, 0, reach + 4, "T = %g each side" % t)
    vertical(ax, -t - head_h - 16, -k / 2, k / 2, "K = %g" % k)
    ax.annotate("Gasket L = %g" % gl, (gl / 2, d / 2 - 2), (gl + t + nut_h + 6, d / 2 + 4),
                color=DIM, arrowprops={"arrowstyle": "->", "color": DIM})
    frame(ax, (-t - head_h - 35, -t + bl + 30, -reach - 32, reach + 26), "Section through two opposite bolts / X to the right")
    circle(detail, 0, 0, d / 2)
    circle(detail, 0, 0, d1 / 2, facecolor="white")
    circle(detail, 0, 0, k / 2, facecolor="none", edgecolor=GREY, linestyle="--")
    for i in range(n):
        angle = math.pi / n + 2 * math.pi * i / n
        circle(detail, k / 2 * math.cos(angle), k / 2 * math.sin(angle), hex_r)
        circle(detail, k / 2 * math.cos(angle), k / 2 * math.sin(angle), bd / 2, facecolor="white")
    detail.text(0, 0, "D = %g\nD1 = %g" % (d, d1), ha="center", va="center", color=INK)
    detail.text(0, -reach - 8, "%g bolts, BD = %g, on K = %g" % (n, bd, k), ha="center", color=INK)
    frame(detail, (-reach - 8, reach + 8, -reach - 22, reach + 8), "Face view / bolts straddle the centrelines")


TITLES = {
    "AT_UBAND": ("Flat strap U-band", "Semicircular crown, straight legs and two drilled feet. Square foot transitions; no bend allowances."),
    "AT_UBOLT": ("Round U-bolt body", "Round rod with a semicircular crown. Smooth legs; threads, nuts and washers are not modelled."),
    "AT_CYLINDER": ("Solid cylinder", "A solid teaching primitive with one reference anchor."),
    "AT_SPACER": ("Hollow spacer", "Straight cylindrical wall with two face-centre reference points."),
    "AT_FLANGE": ("Drilled flat flange", "Flat ring and a regular bolt-hole pattern. No hub, raised face or standard rating."),
    "AT_BLIND_FLANGE": ("Blind flange plate", "Solid plate with a regular bolt-hole pattern and one face reference point."),
    "AT_REDUCER": ("Concentric reducer", "Straight conical walls with independently specified end bores; no weld bevels."),
    "AT_ELBOW90": ("Hollow 90-degree elbow", "Quarter-torus bend. Dashed lines indicate the bore in plan view."),
    "AT_TEE": ("Straight tee", "Run along X and branch along +Y, joined at the centreline intersection. No forged crotch contour."),
    "AT_CAP": ("Ellipsoidal pipe cap", "Straight skirt and 2:1 ellipsoidal head; the crown is as thick as the wall."),
    "AT_GROOVED_COUPLING": ("Grooved coupling housing", "Housing envelope with two bolt pads. Keys, gasket, pipe grooves and bolts are not modelled."),
    "AT_PIPE_SHOE": ("T-section pipe shoe", "Web cut to the pipe radius on a flat base plate. The dashed pipe is a fit reference only."),
    "GSKMB": ("Gasket with bolts and nuts", "Flat gasket with machine bolts; heads and nuts are round stand-ins for hex. Dashed flanges are references only."),
}


def render(name, p):
    title, note = TITLES[name]
    fig = plt.figure(figsize=(12, 8), dpi=140)
    fig.text(0.055, 0.94, title, fontsize=25, weight="bold", color=INK)
    fig.text(0.055, 0.895, name + "  |  DEFAULT DIMENSIONS IN mm", fontsize=11, color=GREY)
    ax = fig.add_axes((0.06, 0.255, 0.55, 0.57))
    detail = fig.add_axes((0.68, 0.30, 0.27, 0.47))
    if name == "AT_UBAND":
        draw_uband(ax, detail, p)
    elif name == "AT_UBOLT":
        draw_ubolt(ax, detail, p)
    elif name == "AT_REDUCER":
        draw_reducer(ax, detail, p)
    elif name == "AT_ELBOW90":
        draw_elbow(ax, detail, p)
    elif name == "AT_TEE":
        draw_tee(ax, detail, p)
    elif name == "AT_CAP":
        draw_cap(ax, detail, p)
    elif name == "AT_GROOVED_COUPLING":
        draw_coupling(ax, detail, p)
    elif name == "AT_PIPE_SHOE":
        draw_shoe(ax, detail, p)
    elif name == "GSKMB":
        draw_gasket(ax, detail, p)
    elif name in ("AT_FLANGE", "AT_BLIND_FLANGE"):
        ring_face(ax, p["OD"], p.get("ID", 0), p["BCD"], p["HD"], p["N"])
        straight(detail, p["OD"], p["T"], p.get("ID", 0), label="T")
    else:
        diameter = p.get("OD", p.get("D"))
        ring_face(ax, diameter, p.get("ID", 0), od_label="D" if name == "AT_CYLINDER" else "OD")
        straight(detail, diameter, p["L"], p.get("ID", 0))
    parameter_line = "   |   ".join("%s = %g" % item for item in p.items())
    fig.text(0.055, 0.18, parameter_line, fontsize=11, color=INK,
             bbox={"facecolor": "#edf5f5", "edgecolor": "none", "pad": 9})
    fig.text(0.055, 0.11, textwrap.fill(note, 112), fontsize=10, color=GREY)
    fig.text(0.055, 0.045, "REFERENCE ILLUSTRATION  |  Not a Plant 3D render or a manufacturing drawing.",
             fontsize=9, color=GREY)
    for extension in ("png", "svg"):
        fig.savefig(OUT / (name + "." + extension), metadata={"Creator": "Parametric component reference drawing", "Date": None} if extension == "svg" else {})
    svg_path = OUT / (name + ".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    manifest = {}
    for name in TITLES:
        p = defaults(name)
        render(name, p)
        source = ROOT / "CustomScripts" / (name + ".py")
        # Normalize line endings so checks work on Windows and Linux checkouts.
        source_text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        manifest[name] = {"defaults": p, "source_sha256": hashlib.sha256(source_text.encode()).hexdigest(),
                          "png": name + ".png", "svg": name + ".svg"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    cards = [Image.open(OUT / (name + ".png")).convert("RGB") for name in TITLES]
    width, height = cards[0].size
    gallery = Image.new("RGB", (width * 2, height * math.ceil(len(cards) / 2)), "#e5eeee")
    for i, card in enumerate(cards):
        gallery.paste(card, ((i % 2) * width, (i // 2) * height))
    gallery.save(OUT / "component-gallery.jpg", quality=90)
    print("Rendered %d PNG/SVG reference sheets and the gallery." % len(cards))


if __name__ == "__main__":
    main()
