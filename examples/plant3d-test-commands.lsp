; Manual command reference: paste ONE form at a time into Plant 3D.
; Do not APPLOAD this file as a batch; the examples share the origin.
; First copy CustomScripts/*.py into your configured shared content folder's
; CPak Common/CustomScripts, then run PLANTREGISTERCUSTOMSCRIPTS.
; Older releases may need restart after edits; 2026.2 documents live reloading.

(arxload "PnP3dACPAdapter")

; Start here, in a scratch drawing:
(testacpscript "AT_CYLINDER")
; Expected: outside diameter 100, X length 300; one origin anchor.
(testacpscript "AT_CYLINDER" "D" "60" "L" "150")

; Hollow spacer: default outside diameter 114.3, bore 102.3, length 100.
(testacpscript "AT_SPACER")
(testacpscript "AT_SPACER" "OD" "80" "ID" "60" "L" "50")

; Flat drilled flange: default OD 180, bore 90, thickness 20,
; bolt circle 140, four holes diameter 18. Not a standard flange size.
(testacpscript "AT_FLANGE")
(testacpscript "AT_FLANGE" "OD" "220" "ID" "110" "T" "25" "BCD" "175" "HD" "18" "N" "8")

; Deliberately invalid cases: should report a validation error, create no part.
(testacpscript "AT_SPACER" "OD" "100" "ID" "100")
(testacpscript "AT_FLANGE" "BCD" "170" "HD" "20")

; Flat strap U-band: main clamp example. Pipe axis X; feet below Z=0.
(testacpscript "AT_UBAND")
(testacpscript "AT_UBAND" "PD" "60.3" "C" "1" "W" "25" "T" "5" "H" "55" "F" "30" "HD" "9")

; Separate round U-bolt body, with smooth rods and no nuts/threads.
(testacpscript "AT_UBOLT")
(testacpscript "AT_UBOLT" "PD" "60.3" "C" "1" "RD" "10" "H" "70")

; Solid blind flange, no centre bore.
(testacpscript "AT_BLIND_FLANGE")
(testacpscript "AT_BLIND_FLANGE" "OD" "220" "T" "25" "BCD" "175" "HD" "18" "N" "8")

; Hollow reducer along +X.
(testacpscript "AT_REDUCER")
(testacpscript "AT_REDUCER" "OD1" "114.3" "OD2" "60.3" "ID1" "102.3" "ID2" "52.3" "L" "120")

; Hollow elbow in XY, from +X toward -Y.
(testacpscript "AT_ELBOW90")
(testacpscript "AT_ELBOW90" "OD" "60.3" "ID" "52.3" "BR" "90")

; Invalid examples: expect validation errors and no component geometry.
(testacpscript "AT_UBAND" "HD" "30")
(testacpscript "AT_UBOLT" "C" "-1")
(testacpscript "AT_BLIND_FLANGE" "N" "6")
(testacpscript "AT_REDUCER" "ID2" "114.3")
(testacpscript "AT_ELBOW90" "BR" "30")
