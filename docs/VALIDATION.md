# Validation record

## Offline checks — 2026-10-25

Environment: Windows, Python 3.14.3. Command:

```powershell
python -B -m unittest discover -s tests -v
```

Result: **20 test methods passed**, including parameterized subcases.

The checks execute the actual component source with a minimal call recorder in place of Plant 3D's modules. They cover source/entry-point consistency, dimension metadata, reference points, fractional dimensions, bore radii, hole patterns, cutter cleanup, and rejection of invalid dimensions before geometry is requested.

The recorder does not construct solids. These results establish Python logic and expected API arguments only. The GitHub Actions workflow repeats the offline checks on Python 3.10 and 3.14; see [the live run history](https://github.com/aniltheengh/AutoCAD-Plant-3D-Parametric-Components-code./actions) for its current result.

## Plant 3D checks — not yet performed

No Plant 3D release is claimed as runtime-validated. Complete these checks in a scratch drawing and a test catalog/spec before using the parts in a project.

| Check | Current result |
| --- | --- |
| Register all three scripts with no errors | Not run |
| Generate solids with defaults and the changed-size examples | Not run |
| Measure diameters, lengths, bore openings, and bolt-hole placement | Not run |
| Verify error reporting for the deliberately invalid examples | Not run |
| Select shapes and build catalog size rows | Not run |
| Insert into a test spec/model and verify applicable connections | Not run |
| Verify applicable isometric symbol and BOM properties | Not run |

The solid cylinder has one reference anchor; the spacer and flange have two reference points. Catalog properties determine how those points are used in the intended part family.

## Record a runtime test here

For a future test, record the Plant 3D release/build, script revision, dimensions, observed measurements, result, and exact error message if any. Add a screenshot or scratch drawing reference when available. A successful cylinder test alone does not validate the spacer, flange, or catalog behavior.
