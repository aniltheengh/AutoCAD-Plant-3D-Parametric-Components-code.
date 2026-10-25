# Autodesk forum research

Checked 2026-10-25. These are the closest verified matches to a forum discussion sharing decompiled Plant 3D component scripts. The exact downloadable full `varmain` folder mentioned by the user has **not** been verified.

## Decompiled scripts: what was found

1. [Decompiled Pipe Supports - Plant 3D Python Scripts](https://forums.autodesk.com/t5/autocad-plant-3d-forum/decompiled-pipe-supports-plant-3d-python-scripts/td-p/12847105). Dave Wolfe's accepted reply, dated 2024-06-21, points to his [Custom Python Scripts page](https://pipinglabs.com/2024/06/21/custom-python-scripts/). The forum reply was accessible, but that external page timed out during this research. No linked archive or its contents was verified. A later 2025 reply discusses older installed bytecode and decompiler compatibility; it is a community report about those versions.
2. [Plant 3D Custom Supports](https://forums.autodesk.com/t5/autocad-plant-3d-forum/plant-3d-custom-supports/m-p/10896394). On 2022-01-20, arron.craig posted examples described as decompiled installed supports. The thread also discusses `varmain.zip`, support metadata and reference points. This confirms the existence of shared example code, not the completeness or compatibility of a downloadable full library.
3. [How to decomplied pyc to py?](https://forums.autodesk.com/t5/autocad-plant-3d-forum/how-to-decomplied-pyc-to-py/m-p/10748016). A 2021 discussion of decompilation tools and bytecode-version errors. It is historical troubleshooting context, not proof that the same tools support current Plant 3D bytecode.

This repository contains original examples using the public primitive API. It does not include a decompiled Autodesk library or replace installed `varmain` files.

## Geometry references used

- [Autodesk's parametric script-development reference](https://forums.autodesk.com/autodesk/attachments/autodesk/autocad-plant-3d-forum-en/61916/2/Parametric%20Script%20Development.pdf), figures on pages 13-15 and 28, documents primitive dimensions and origins. The BOX figure maps its local spans to `H=X`, `L=Y`, `W=Z`. Cylinder bore input `O` is a radius. CONE can create a frustum.
- [Custom Python Scripts, Part 2](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-2/) explains decorators and matching source/function names.
- [Custom Python Scripts, Part 3](https://blog.autodesk.io/custom-python-scripts-for-autocad-plant-3d-part-3/) demonstrates Boolean operations and the registration/testing workflow.
- [Custom Python Scripts Use in Spec Editor](https://forums.autodesk.com/t5/autocad-plant-3d-forum/custom-python-scripts-use-in-spec-editor/m-p/9603944/highlight/true) contains an author's U-bolt example using a torus and straight cylindrical legs. It corroborates the torus centreline/rod-radius convention, and illustrates that successful geometry testing does not by itself establish working catalog sizes.

## Current version distinction

Autodesk's [Plant 3D 2026.2 update article](https://blog.autodesk.io/autocad-plant-3d-2026-2-update-python-3-13-upgrade-and-isometric-improvements/comment-page-1/) states that 2026.2 uses Python 3.13.11, compared with 3.11 in 2026/2026.1. It also describes script reload on the next run and improved traceback reporting. The older tutorial's restart-after-every-edit advice should therefore be applied according to the installed version.

The release/build used to validate this library remains unrecorded because no Plant 3D runtime test has been performed.
