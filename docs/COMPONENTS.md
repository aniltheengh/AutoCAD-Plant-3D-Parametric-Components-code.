# Component parameter reference

All dimensions are in **millimetres**. These are original learning examples with illustrative defaults; no JIS, ASME, pressure class, material, or load rating is implied. Their solids, registration, and catalog behavior still require testing inside Plant 3D.

See the [image gallery](GALLERY.md) for all eight dimensioned reference sheets. The flat strap U-band is documented below under `AT_UBAND`; the round U-bolt is a separate part.

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

## AT_UBAND - flat strap U-band with mounting feet

[Source](../CustomScripts/AT_UBAND.py) | [Image](../images/AT_UBAND.png). Group `Support`, one reference anchor at the origin pointing -X. Pipe axis is X, the semicircular crown is above Z=0, and the legs/feet extend below Z=0.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `PD` | Reference pipe outside diameter | 114.3 | Positive and finite |
| `C` | Radial clearance from pipe to strap | 1 | Nonnegative and finite |
| `W` | Strap width along pipe axis X | 30 | Positive and finite |
| `T` | Strap thickness | 6 | Positive and finite |
| `H` | Pipe centre to underside of feet | 75 | Greater than `T` |
| `F` | Foot projection beyond outside of leg | 35 | Greater than `HD` |
| `HD` | Mounting-hole diameter | 11 | Positive, smaller than `W` and `F` |

Inner bend radius is `PD/2+C`; outer radius is `PD/2+C+T`. Straight legs meet the crown at Z=0 and end at Z=-H. Each foot overlaps the leg by T and projects an additional F outward. Hole axes run along Z at `X=0`, `Y=+/- (PD/2+C+T+F/2)`.

This produces a connected flat-strap shape with square leg-to-foot transitions. Physical bend radii, bend allowances, forming springback, fasteners and structural adequacy are not modelled. H is independently adjustable; check its relationship to the actual mounting surface. The dashed pipe in the image is a fit reference only.

## AT_UBOLT - round U-bolt body

[Source](../CustomScripts/AT_UBOLT.py) | [Image](../images/AT_UBOLT.png). Group `Support`, one anchor at pipe centre pointing -X. This is the round-rod alternative, with no modelled threads/nuts.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `PD` | Pipe outside diameter | 114.3 | Positive and finite |
| `C` | Radial clearance | 1 | Nonnegative and finite |
| `RD` | Round rod diameter | 12 | Positive and finite |
| `H` | Pipe centre to leg ends below Z=0 | 100 | Positive and finite |

Bend centreline radius is `(PD+RD)/2+C`; the straight legs are at `Y=+/-` that radius, extend from Z=-H to Z=0, and meet the upper semicircular crown tangentially. The rod is centred on X=0.

## AT_BLIND_FLANGE - solid drilled flange plate

[Source](../CustomScripts/AT_BLIND_FLANGE.py) | [Image](../images/AT_BLIND_FLANGE.png). Group `Flange`, one reference at X=0 pointing -X. The plate extends to X=T. It has no centre bore.

| Parameter | Meaning | Default |
| --- | --- | ---: |
| `OD` | Outside diameter | 180 |
| `T` | Thickness | 20 |
| `BCD` | Bolt circle diameter | 140 |
| `HD` | Hole diameter | 18 |
| `N` | Hole count: 4, 8, 12 or 16 | 4 |

Dimensions must be positive and finite. The outside-edge gap `(OD-BCD-HD)/2` and neighboring-hole gap `BCD*sin(pi/N)-HD` must both be positive. Hole orientation matches `AT_FLANGE`.

## AT_REDUCER - hollow concentric reducer

[Source](../CustomScripts/AT_REDUCER.py) | [Image](../images/AT_REDUCER.png). Group `Reducer`. Large face at X=0 points -X; small face at X=L points +X.

| Parameter | Meaning | Default |
| --- | --- | ---: |
| `OD1` | Large-end outside diameter | 168.3 |
| `OD2` | Small-end outside diameter | 114.3 |
| `ID1` | Large-end bore diameter | 154.1 |
| `ID2` | Small-end bore diameter | 102.3 |
| `L` | Axial length | 150 |

All dimensions must be positive and finite. Both outer and bore diameters reduce: `OD1>OD2`, `ID1>ID2`; each `ID` must be below the corresponding `OD`. Outside and inside profiles are linear. Specified wall thicknesses are radial at the end faces, not thickness normal to the slope. Bore cutters are extrapolated past both faces while preserving the specified end diameters.

## AT_ELBOW90 - hollow quarter bend

[Source](../CustomScripts/AT_ELBOW90.py) | [Image](../images/AT_ELBOW90.png). Group `Elbow`, two outward tangent references.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `OD` | Tube outside diameter | 114.3 | Positive and finite |
| `ID` | Tube bore diameter | 102.3 | Positive and less than `OD` |
| `BR` | Centreline bend radius | 152.4 | Greater than `OD/2` |

The first point is `(0,0,0)`, direction `(-1,0,0)`. The second is `(BR,-BR,0)`, direction `(0,-1,0)`. The bend lies in XY, with its centre at `(0,-BR,0)`. Geometry is a hollow quarter-torus; no straight tangent extensions or weld bevels are included.

## Coordinate and API notes

The scripts orient cylinders along +X using `rotateY(90)`. In the underlying cylinder primitive, `O` means **hole radius**, so a bore diameter is divided by two. The drilled flange uses subtractive cutters, which must be erased after subtraction. Scripted ports use a position and direction vector.

These conventions are documented in the [Autodesk University custom component scripting handout](https://forums.autodesk.com/autodesk/attachments/autodesk/autocad-plant-3d-forum-zh-cn/4870/1/v1_PD4214-L_Radhakrishnan_AnnexB_Custom-Script-Handout.pdf), particularly pages 9, 24, 26, 28, and 32. This legacy reference informs the implementation; it does not replace runtime verification.

Begin with [installation and testing](INSTALLATION.md), then use the [manual command reference](../examples/plant3d-test-commands.lsp).
