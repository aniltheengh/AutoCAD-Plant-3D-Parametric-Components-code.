# Component parameter reference

All dimensions are in **millimetres**. These are original learning examples with illustrative defaults; no JIS, ASME, pressure class, material, or load rating is implied. Their solids, registration, and catalog behavior still require testing inside Plant 3D.

See the [image gallery](GALLERY.md) for all twelve dimensioned reference sheets. The flat strap U-band is documented below under `AT_UBAND`; the round U-bolt is a separate part.

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

## AT_TEE - straight tee, equal or reducing

[Source](../CustomScripts/AT_TEE.py) | [Image](../images/AT_TEE.png). Group `Tee`, three outward references. The origin is the intersection of the run and branch centrelines.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `OD1` | Run outside diameter | 114.3 | Positive and finite |
| `ID1` | Run bore diameter | 102.3 | Less than `OD1` |
| `OD2` | Branch outside diameter | 114.3 | Greater than `ID2`, no larger than `OD1` |
| `ID2` | Branch bore diameter | 102.3 | Less than `OD2`, no larger than `ID1` |
| `C` | Centre to each run end | 105 | Greater than `OD2/2` |
| `M` | Centre to branch end | 105 | Greater than `OD1/2` |

The ports are `(-C,0,0)` pointing `(-1,0,0)`, `(C,0,0)` pointing `(1,0,0)`, and `(0,M,0)` pointing `(0,1,0)`, the same layout as Plant 3D's stock tees. The branch cylinder starts on the run axis and is turned to +Y with `rotateY(90)` then `rotateZ(90)`. Its bore cutter also starts on the run axis, inside the run bore, so the branch opening has no coincident faces; the run bore cutter extends past both run faces. There is no crotch radius or forged contour, and the defaults are not a standard size table. An equal tee makes tangent cylinder intersections, so check that solid in Plant 3D.

## AT_CAP - ellipsoidal pipe cap

[Source](../CustomScripts/AT_CAP.py) | [Image](../images/AT_CAP.png). Group `Cap`, one port at the open end `(0,0,0)` pointing `-X`. The outer crown is at `X=L`.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `OD` | Outside diameter | 114.3 | Positive and finite |
| `WT` | Wall thickness | 6 | Less than `OD/2` |
| `L` | Open end to outer crown | 64 | Greater than `OD/4 + WT/2` |

The head is the `ELLIPSOIDHEAD2` primitive: a 2:1 semi-ellipsoid whose height is half its radius. The outer head's base is at `X = L - OD/4`. The inner head is set lower by `WT`, so the crown is exactly `WT` thick; elsewhere on the head the thickness varies, because two ellipses are not parallel curves. The `L` limit keeps the inner straight bore longer than zero. The build order follows Autodesk's cap example `CPC`: a skirt cylinder united with a head, then a cavity cylinder united with a smaller head and subtracted. The cavity cutter extends past the open face.

## AT_GROOVED_COUPLING - grooved coupling housing

[Source](../CustomScripts/AT_GROOVED_COUPLING.py) | [Image](../images/AT_GROOVED_COUPLING.png). Group `Coupling`, two ports. The housing runs from X=0 to X=`HL`. The pipe ends meet at its centre, separated by `G`. The ports are at `X=(HL-G)/2` pointing -X and `X=(HL+G)/2` pointing +X, so connected pipes run inside the housing up to the ports. Autodesk's stock `CCOUPLING` uses the same idea, with ports at its insertion depths.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `PD` | Pipe outside diameter, equal to the housing bore | 114.3 | Less than `HD` |
| `HD` | Housing outside diameter | 150 | Positive and finite |
| `HL` | Housing length along X | 60 | Greater than `G` and `BH` |
| `G` | Gap between the pipe ends | 3 | Positive, less than `HL` |
| `P` | Bolt-pad projection beyond the housing | 30 | Greater than `BH` |
| `PH` | Bolt-pad height along Z | 40 | Less than `HD` |
| `BH` | Bolt-hole diameter | 14 | Less than `P` and `HL` |

The two bolt pads are at +Y and -Y, centred on X=`HL/2` and as long as the housing. Each pad starts at `Y = +/- sqrt((HD/2)^2 - (PH/2)^2)`, where its top and bottom faces meet the housing surface, so it blends into the housing without a step. The bolt holes run along Z at `Y = +/- (HD/2 + P/2)`, entirely outside the housing. Keys, gasket, pipe grooves, bolts, nuts and the split between the housing halves are not modelled, and the defaults are not a manufacturer's dimensions.

## AT_PIPE_SHOE - T-section pipe shoe

[Source](../CustomScripts/AT_PIPE_SHOE.py) | [Image](../images/AT_PIPE_SHOE.png). Group `Support`, one anchor at the pipe centre pointing -X. The pipe axis is X; the shoe is centred on X=0 and lies below Z=0.

| Parameter | Meaning | Default | Requirement |
| --- | --- | ---: | --- |
| `PD` | Pipe outside diameter | 114.3 | Greater than `T` |
| `L` | Shoe length along X | 200 | Positive and finite |
| `H` | Pipe centre to underside of the base plate | 100 | Greater than `PD/2 + T` |
| `W` | Base-plate width along Y | 120 | Greater than `T` |
| `T` | Web and base-plate thickness | 10 | Less than `W` and `PD` |

The web is built from the pipe centre down to Z=-H. Subtracting a pipe cylinder then shapes its top to the pipe radius, the same technique as Plant 3D's stock shoe `CSGB000`. The base plate spans Z=-H to Z=-H+T, below the pipe. The shoe is not load-rated, and has no slots, hold-downs, stiffeners or weld details.

## Coordinate and API notes

The scripts orient cylinders along +X using `rotateY(90)`. In the underlying cylinder primitive, `O` means **hole radius**, so a bore diameter is divided by two. The drilled flange uses subtractive cutters, which must be erased after subtraction. Scripted ports use a position and direction vector.

These conventions are documented in the [Autodesk University custom component scripting handout](https://forums.autodesk.com/autodesk/attachments/autodesk/autocad-plant-3d-forum-zh-cn/4870/1/v1_PD4214-L_Radhakrishnan_AnnexB_Custom-Script-Handout.pdf), particularly pages 9, 24, 26, 28, and 32. This legacy reference informs the implementation; it does not replace runtime verification.

Notes added with the tee, cap, coupling and shoe:

- **`ELLIPSOIDHEAD2(s, R)`** is a 2:1 ellipsoidal head with semi-axes `R` and `R/2`; its base point is the centre of its flat side (handout page 11). `uniteWith` keeps the calling object and the other object must then be erased (page 23). The cap's build order follows the handout's `CPC` example (pages 33-34).
- **`BOX`** has its base point at its centre, with spans `H` along X, `L` along Y and `W` along Z, as described in the [forum references](FORUM_REFERENCES.md).
- **`rotateY(90).rotateZ(angle)`** is how Autodesk's welded tee points its branches within the XY plane. `rotateZ(90)` turns +X into +Y. The handout's eccentric-adapter example (page 25) places its ports consistently with a right-handed `rotateZ`.
- **Parameter named `ID`.** Every stock Autodesk script declares a keyword argument `ID='<script name>'`. Whether Plant 3D passes `ID` into custom scripts at run time has not been verified. The four newer scripts avoid a parameter named exactly `ID`, using `ID1`/`ID2` or `WT`. `AT_SPACER`, `AT_FLANGE` and `AT_ELBOW90` still use `ID` for a bore. If one of them reports a bore validation error with default dimensions during the first Plant 3D test, suspect this clash.

Begin with [installation and testing](INSTALLATION.md), then use the [manual command reference](../examples/plant3d-test-commands.lsp).
