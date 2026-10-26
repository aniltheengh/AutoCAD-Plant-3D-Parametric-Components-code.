# Plant 3D Bolted Gasket (GSKMB)

AutoCAD Plant 3D custom Python parametric script that draws a flat gasket **with hex-head machine bolts and nuts**, so bolts become visible in the 3D model at every flanged joint.

Plant 3D normally treats bolt sets as non-graphical items. This script adds the bolts to the gasket geometry. The spec's bolt set still drives the BOM and isos, so bolts aren't counted twice.

> **Status:** untested inside Plant 3D.

## Parameters

| Param | Meaning | Default (JIS 10K 50A example) | Source |
|---|---|---|---|
| D  | Gasket outside diameter | 96 | Gasket standard (JIS B2404 / ASME B16.21) |
| D1 | Gasket inside diameter | 61 | Gasket standard |
| L  | Gasket thickness | 3 | Gasket spec |
| N  | Number of bolts: 0 = gasket only, otherwise a whole number of at least 2 | 4 | Flange standard (JIS B2220 / ASME B16.5) |
| K  | Bolt circle diameter (PCD) | 120 | Flange standard |
| BD | Bolt diameter (M size) | 16 | Flange standard |
| BL | Bolt length, measured from under the head (must be > 2T + L) | 55 | Bolt table |
| T  | Flange thickness at the bolt holes, each side | 16 | Flange standard |

The script calculates head height (0.65·BD) and nut height (0.8·BD) from BD. Heads and nuts are drawn 1.6·BD across.

## Input checks

The script checks every value before it draws anything. A bad value gives an error on the command line instead of a wrong part:

- D, D1, L, K, BD, BL and T must be positive numbers, and D1 must be smaller than D.
- N is a whole-number (`INT`) parameter, so Plant 3D will not convert it like a length in an inch project.
- With bolts (N ≥ 2), K must exceed D, BL must exceed 2T + L, and neighbouring heads must not overlap: K·sin(180°/N) > 1.6·BD.
- With N = 0, the bolting values are not used.

For the bolt end to show beyond the nut, BL must also exceed 2T + L + 0.8·BD. The defaults meet this: 55 > 47.8.

## Install

1. Copy `GSKMB.py` to `<Shared Content>\CPak Common\CustomScripts\` (check the path with `MODIFYSHAREDCONTENTFOLDER`).
2. In Plant 3D, run `PLANTREGISTERCUSTOMSCRIPTS`.
3. Test it:
   ```
   (arxload "PnP3dACPAdapter")
   (testacpscript "GSKMB")
   ```
4. In Catalog Builder, create a gasket catalog using the GSKMB shape and fill in each size row. Then use it in Spec Editor in place of the stock gaskets.

After editing the script, restart Plant 3D before testing again, because scripts are cached per session.

## Why a gasket and not a flange?

Plant 3D places exactly one gasket at every flanged joint, including flange-to-valve and flange-to-nozzle joints. Flange-based bolts would be duplicated at flange-to-flange joints and missing at flanged valves and nozzles.

## Hiding bolts

The bolts are part of the gasket solid. You can hide them in two ways:
- Select all gaskets (*Select Similar*), then run `HIDEOBJECTS`.
- Put gaskets on a dedicated layer via *Project Setup → Pipe Layer and Color Settings*, and freeze that layer.

## Limitations

- Assumes equal flange thickness on both sides.
- Bolt length is fixed per catalog size.
- Head and nut are drawn as round cylinders, not true hex.
- Bolts pass through flanges that have no bolt holes, so clash checks will flag them.

## References

- [Custom Python Scripts for AutoCAD Plant 3D – Part 3 (Autodesk Developer Blog)](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-3/)
