# Starter components

All dimensions are in **millimetres**. These are original learning examples with illustrative defaults; no JIS, ASME, pressure class, material, or load rating is implied. Their solids, registration, and catalog behavior still require testing inside Plant 3D.

## AT_CYLINDER — solid cylinder

File: [AT_CYLINDER.py](../CustomScripts/AT_CYLINDER.py). Registration group: `Support`. One anchor is defined at the center of the starting face, pointing toward -X. This solid example is not a through-flow fitting or a designed pipe support.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `D` | Outside diameter | 100 | Positive and finite |
| `L` | Axial length | 300 | Positive and finite |

The cylinder extends from `x=0` to `x=L`; its centerline is the X axis.

## AT_SPACER — hollow spacer

File: [AT_SPACER.py](../CustomScripts/AT_SPACER.py). Registration group: `Sleeve`. Two scripted ports lie on the centerline at `x=0` and `x=L`, pointing outward toward -X and +X respectively.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `OD` | Outside diameter | 114.3 | Positive and finite |
| `ID` | Bore diameter | 102.3 | Positive, finite, and smaller than `OD` |
| `L` | Axial length | 100 | Positive and finite |

The default radial wall thickness is `(OD-ID)/2 = 6 mm`. The bore passes through the entire length.

## AT_FLANGE — drilled flat flange geometry

File: [AT_FLANGE.py](../CustomScripts/AT_FLANGE.py). Registration group: `Flange`. The flat ring extends from `x=0` to `x=T`. Its scripted ports are at those face centers, pointing outward toward -X and +X. Actual catalog end types are intentionally unspecified.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `OD` | Outside diameter | 180 | Positive and finite |
| `ID` | Through-bore diameter | 90 | Positive, finite, and smaller than `OD` |
| `T` | Axial thickness | 20 | Positive and finite |
| `BCD` | Bolt-circle diameter | 140 | Positive and finite |
| `HD` | Bolt-hole diameter | 18 | Positive and finite |
| `N` | Number of equally spaced holes | 4 | One of `4`, `8`, `12`, or `16` |

All bolt holes run parallel to X. The first center is on +Y; increasing hole angle moves toward +Z. For hole index `k=0,...,N-1`:

```text
theta = 2*pi*k/N
y = (BCD/2)*cos(theta)
z = (BCD/2)*sin(theta)
```

The script rejects dimensions unless each remaining gap is strictly positive:

| Check | Gap |
| --- | --- |
| Bore to a bolt-hole edge | `(BCD-HD-ID)/2` |
| Bolt-hole edge to the outside edge | `(OD-BCD-HD)/2` |
| Adjacent bolt-hole edges | `BCD*sin(pi/N)-HD` |

These checks prevent geometric overlap; they do not calculate required structural ligament or pressure resistance. There is no hub, raised face, gasket groove, or bolt hardware in this example.

## Coordinate and API notes

The scripts orient cylinders along +X using `rotateY(90)`. In the underlying cylinder primitive, `O` means **hole radius**, so a bore diameter is divided by two. The drilled flange uses subtractive cutters, which must be erased after subtraction. Scripted ports use a position and direction vector.

These conventions are documented in the [Autodesk University custom component scripting handout](https://forums.autodesk.com/autodesk/attachments/autodesk/autocad-plant-3d-forum-zh-cn/4870/1/v1_PD4214-L_Radhakrishnan_AnnexB_Custom-Script-Handout.pdf), particularly pages 9, 24, 26, 28, and 32. This legacy reference informs the implementation; it does not replace runtime verification.

Begin with [installation and testing](INSTALLATION.md), then use the [manual command reference](../examples/plant3d-test-commands.lsp).
