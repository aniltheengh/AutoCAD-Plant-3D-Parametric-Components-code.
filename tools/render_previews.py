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


TITLES = {
    "AT_UBAND": ("Flat strap U-band", "Semicircular crown, straight legs and two drilled feet. Square foot transitions; no bend allowances."),
    "AT_UBOLT": ("Round U-bolt body", "Round rod with a semicircular crown. Smooth legs; threads, nuts and washers are not modelled."),
    "AT_CYLINDER": ("Solid cylinder", "A solid teaching primitive with one reference anchor."),
    "AT_SPACER": ("Hollow spacer", "Straight cylindrical wall with two face-centre reference points."),
    "AT_FLANGE": ("Drilled flat flange", "Flat ring and a regular bolt-hole pattern. No hub, raised face or standard rating."),
    "AT_BLIND_FLANGE": ("Blind flange plate", "Solid plate with a regular bolt-hole pattern and one face reference point."),
    "AT_REDUCER": ("Concentric reducer", "Straight conical walls with independently specified end bores; no weld bevels."),
    "AT_ELBOW90": ("Hollow 90-degree elbow", "Quarter-torus bend. Dashed lines indicate the bore in plan view."),
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
    gallery = Image.new("RGB", (width * 2, height * 4), "#e5eeee")
    for i, card in enumerate(cards):
        gallery.paste(card, ((i % 2) * width, (i // 2) * height))
    gallery.save(OUT / "component-gallery.jpg", quality=90)
    print("Rendered %d PNG/SVG reference sheets and the gallery." % len(cards))


if __name__ == "__main__":
    main()
