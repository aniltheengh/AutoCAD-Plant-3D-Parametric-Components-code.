# Validation record

## Offline checks — 2026-10-26

Environment: Windows, Python 3.14.3, same command as below. Result: **57 test methods passed** (54 geometry/metadata checks and 3 image/documentation checks) for the thirteen components.

`GSKMB` (gasket with bolts and nuts) joined the library with input checks added before any geometry. Its tests cover the gasket ring and ports, bolt positions straddling the centrelines, heads and nuts on the flange back faces, the `N=0` gasket-only case, the header's eight-bolt example, and rejection of bad bolt counts, a bolt circle inside the gasket, short bolts and overlapping heads.

Added checks cover the tee's run/branch placement, bores and three ports; the cap's head height, crown thickness and open cavity; the coupling's inset ports, pad-to-housing chord and bolt-hole clearances; and the shoe's web seat and base-plate depth. The new scripts were also deliberately broken in eight ways, two per script (wrong branch direction, short bore cutters, missing crown wall, detached pads, holes cutting the housing, a misplaced base plate, a loosened validation check); the tests failed every time. Every command in [the command reference](../examples/plant3d-test-commands.lsp) was run through the recorder: the valid examples build and the invalid ones are rejected. The parameter check now reads each parameter's declared type (`LENGTH0` may be zero), rather than special-casing the name `C`.

## Offline checks — 2026-10-25

Environment: Windows, Python 3.14.3. Command:

```powershell
python -B -m unittest discover -s tests -v
```

Expanded-library result: **38 test methods passed**, including parameterized subcases (35 geometry/metadata checks and 3 image/documentation checks).

The checks execute the actual eight component sources with a minimal call recorder in place of Plant 3D's modules. They cover source/entry-point consistency, dimension metadata, reference points, fractional dimensions, bore radii, hole patterns, cutter cleanup, and rejection of invalid dimensions before geometry is requested. Added checks cover U-band leg/foot placement and hole clearances, round U-bolt tangent alignment, reducer bore extrapolation, elbow reference directions and blind-flange geometry.

The recorder does not construct solids. These results establish Python logic and expected API arguments only. The GitHub Actions workflow repeats the offline checks on Python 3.10, 3.11, 3.13 and 3.14; see [the live run history](https://github.com/aniltheengh/AutoCAD-Plant-3D-Parametric-Components-code./actions) for its current result.

Eight dimensioned PNG/SVG sheets and an overview image were generated from source defaults and visually inspected. Automated checks compare the preview manifest with source hashes/defaults, validate image file headers and resolve local documentation links. These images do not provide evidence of successful Plant 3D rendering.

## Plant 3D checks — not yet performed

No Plant 3D release is claimed as runtime-validated. Complete these checks in a scratch drawing and a test catalog/spec before using the parts in a project.

| Check | Current result |
| --- | --- |
| Register all thirteen scripts with no errors | Not run |
| Generate solids with defaults and the changed-size examples | Not run |
| Measure diameters, lengths, bore openings, and bolt-hole placement | Not run |
| Verify error reporting for the deliberately invalid examples | Not run |
| Select shapes and build catalog size rows | Not run |
| Insert into a test spec/model and verify applicable connections | Not run |
| Verify applicable isometric symbol and BOM properties | Not run |

The cylinder, clamps and shoe have one support/reference anchor; the blind flange and cap have one face reference. The spacer, drilled flange, reducer, elbow, coupling and bolted gasket have two reference points, and the tee has three. Catalog properties determine how those points are used in the intended part family.

## Record a runtime test here

For a future test, record the Plant 3D release/build, script revision, dimensions, observed measurements, result, and exact error message if any. Add a screenshot or scratch drawing reference when available. A successful cylinder test alone does not validate the spacer, flange, or catalog behavior.
