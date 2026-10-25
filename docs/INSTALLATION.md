# Install and test in AutoCAD Plant 3D

These scripts require **AutoCAD Plant 3D's embedded geometry libraries**. Ordinary Python can check their syntax, but cannot generate or validate their Plant 3D solids. No Plant 3D version has been runtime-tested for this library yet.

## 1. Copy the three scripts

From the project folder, copy only the three `.py` files in `CustomScripts` into your configured Plant 3D shared-content folder:

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

Read the command-line output for registration errors. Save your drawing and restart Plant 3D to clear any cached scripts. In the new session, enter these lines separately:

```lisp
(arxload "PnP3dACPAdapter")
(testacpscript "AT_CYLINDER")
```

Use Zoom Extents if needed. Then try the spacer and flange commands in [the command reference](../examples/plant3d-test-commands.lsp). Paste one command at a time; the reference includes both default and changed dimensions. After editing a deployed script, register it again and restart Plant 3D before retesting.

This procedure follows [Autodesk's custom Python tutorial, Part 3](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-3/). Registration adds shapes to the library; see [the Plant 3D 2026 command reference](https://help.autodesk.com/cloudhelp/2026/ENU/Plant3D-CatalogBuilder/files/GUID-D86E0252-5123-41DA-8B72-202AD8D48558.htm).

## 3. Check the result

For each part, measure the dimensions listed in [COMPONENTS.md](COMPONENTS.md). Confirm the +X orientation, open bores, and flange hole positions. Change the dimensions and verify that a new instance reflects them. Invalid dimensions should produce a useful error instead of a malformed component.

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
| Geometry stays unchanged after an edit | Confirm the deployed file was updated, register again, and restart Plant 3D. |
| Adapter load or geometry error | Preserve the exact command-line message and Plant 3D version for diagnosis. |
| Solid appears but catalog insertion or connections fail | Check the part family and port/end-type configuration independently of the geometry test. |
