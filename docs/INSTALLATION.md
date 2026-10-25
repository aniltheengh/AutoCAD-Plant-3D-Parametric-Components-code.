# Install and test in AutoCAD Plant 3D

These scripts require **AutoCAD Plant 3D's embedded geometry libraries**. Ordinary Python can check their syntax, but cannot generate or validate their Plant 3D solids. No Plant 3D version has been runtime-tested for this library yet.

## 1. Copy the eight scripts

From the project folder, copy only the eight `.py` files in `CustomScripts` into your configured Plant 3D shared-content folder:

```text
<Shared Content Folder>\CPak Common\CustomScripts\
```

A typical installation uses `C:\AutoCAD Plant 3D 2026 Content`, but the year and location depend on your installation. Use the actual configured folder. Create `CustomScripts` if necessary. If a file with the same name already exists there, preserve it before replacing it.

Keep each filename identical to its entry-point function: for example, `AT_SPACER.py` contains `def AT_SPACER(...)`. Do not copy test helpers into the content folder or install replacement versions of `varmain`.

## 2. Register, then test

Open Plant 3D and a scratch drawing. Enter:

```text
PLANTREGISTERCUSTOMSCRIPTS
```

Read the command-line output for registration errors. Load the adapter and test the flat U-band by entering these lines separately:

```lisp
(arxload "PnP3dACPAdapter")
(testacpscript "AT_UBAND")
```

Use Zoom Extents if needed. The U-band's support anchor is at the pipe centre, so part of it lies below Z=0. A pipe solid is not generated. Then try the other components in [the command reference](../examples/plant3d-test-commands.lsp). Paste one command at a time in a scratch drawing; the reference includes both default and changed dimensions.

**Version-specific reload:** older releases cache loaded scripts, so save your drawing, register the edited script and restart Plant 3D before retesting. Autodesk states that **2026.2** picks up script changes on the next run without restarting/reloading the adapter for every edit. See [the 2026.2 release explanation](https://blog.autodesk.io/autocad-plant-3d-2026-2-update-python-3-13-upgrade-and-isometric-improvements/comment-page-1/). Initial registration is still part of setup; confirm the behavior in your installed build.

This procedure follows [Autodesk's custom Python tutorial, Part 3](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-3/). Registration adds shapes to the library; see [the Plant 3D 2026 command reference](https://help.autodesk.com/cloudhelp/2026/ENU/Plant3D-CatalogBuilder/files/GUID-D86E0252-5123-41DA-8B72-202AD8D48558.htm).

## 3. Check the result

For each part, measure the dimensions listed in [COMPONENTS.md](COMPONENTS.md) against its [reference image](GALLERY.md). Straight parts use +X; the elbow turns from +X toward -Y. Clamp anchors are at the pipe centre, with their crowns above and feet/legs below it. Check bores, hole positions, joining faces and reference-point directions. Change the dimensions and verify that a new instance reflects them. Invalid dimensions should produce a useful error instead of a malformed component.

Record your Plant 3D version, parameters, observed dimensions, and any command-line error. Passing the repository's offline checks is not evidence that these checks passed in Plant 3D.

## 4. Create catalog parts when geometry passes

Use Catalog Builder or Spec Editor to select the registered shape and create a part family. Populate the size table and select the intended component class, nominal size, material, end types, and other required properties. The sample defaults are geometry examples, not a standard size catalog.

Add the resulting family to a test spec and verify insertion, connection directions, dimensions, and any required isometric/BOM output. The flange intentionally leaves end-type metadata unspecified; choose it for the actual catalog application. Port count and scripted points alone do not establish connection readiness.

The metadata and matching-name conventions are described in [Autodesk's tutorial, Part 2](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-2/). Catalog integration remains unverified until tested in your installation.

## If a test fails

| Symptom | First check |
| --- | --- |
| `No module named varmain` in ordinary Python | Run geometry through Plant 3D; this is an application-provided library. |
| Script is not found | Check the configured content folder, matching filename/function, and registration output. |
| Geometry stays unchanged after an edit | Confirm the deployed file and installed release; older releases may need a restart. |
| Adapter load or geometry error | Preserve the exact command-line message and Plant 3D version for diagnosis. |
| Solid appears but catalog insertion or connections fail | Check the part family and port/end-type configuration independently of the geometry test. |

The `images` folder contains documentation previews. This library does not claim that they are registered Spec Editor thumbnails. Only copy the eight source scripts for the initial geometry test; keep the documents, test recorder and preview generator outside Plant 3D's content folder.
