# AutoCAD Plant 3D Parametric Components

A small, editable Python starter library for learning custom Plant 3D component geometry.

**Start with `AT_CYLINDER`, then try `AT_SPACER` and `AT_FLANGE`.** All dimensions are in millimetres. The scripts include parameter validation, explicit reference points, and comments explaining the geometry.

## Components

| Script | Creates | Main parameters |
| --- | --- | --- |
| [AT_CYLINDER.py](CustomScripts/AT_CYLINDER.py) | Solid cylinder along X, with one reference anchor | Diameter, length |
| [AT_SPACER.py](CustomScripts/AT_SPACER.py) | Hollow cylindrical spacer, with two reference ports | Outside diameter, bore, length |
| [AT_FLANGE.py](CustomScripts/AT_FLANGE.py) | Flat ring with 4, 8, 12, or 16 bolt holes | Outside diameter, bore, thickness, bolt circle, hole diameter, hole count |

The flange validates the bore, edge clearances, and separation between neighboring holes before creating a solid. Dimensions are illustrative: these files do not contain JIS/ASME tables, pressure ratings, or finished catalog/spec data.

## First step in Plant 3D

Copy the three `.py` files from `CustomScripts` to your configured shared-content folder's `CPak Common\CustomScripts` directory. Follow [installation and testing](docs/INSTALLATION.md) to register the scripts and run the first cylinder example.

The `varmain` imports are supplied by Plant 3D. Do not install a similarly named Python package or run a component file with ordinary Python to generate CAD geometry.

## Read and change the examples

- [Parameter reference](docs/COMPONENTS.md): dimensions, axes, ports, and geometric constraints.
- [Plant 3D commands](examples/plant3d-test-commands.lsp): paste one example at a time into a scratch drawing.
- [Validation record](docs/VALIDATION.md): what has been checked and what needs a Plant 3D session.

Each script is self-contained. Its filename and entry-point function must match. Edit defaults to experiment, or supply dimensions through `testacpscript` and later through catalog size rows.

## Offline development checks

From the repository folder, using Python 3.10 or later:

```powershell
python -m unittest discover -s tests -v
```

The tests use a small recorder for calls to Autodesk's API. They check input validation, geometry arguments, hole placement, cleanup, and port directions. They **do not run Autodesk's solid modeler** or establish compatibility with any Plant 3D release. The same checks run in GitHub Actions.

## Current status

This is a starter source library. Plant 3D registration, solid generation, catalog insertion, pipe connection, and isometric/BOM behavior have not yet been tested in a Plant 3D installation. See the validation record before using the examples in a project.

## Autodesk references

- [Custom Python Scripts, Part 2](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-2/): metadata and matching script names.
- [Custom Python Scripts, Part 3](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-3/): Boolean operations, registration, and testing.
- [Plant 3D 2026 registration command](https://help.autodesk.com/cloudhelp/2026/ENU/Plant3D-CatalogBuilder/files/GUID-D86E0252-5123-41DA-8B72-202AD8D48558.htm): adding scripts to the shape library.

The implementations are original learning examples based on documented APIs. Autodesk libraries are not distributed with this repository.
