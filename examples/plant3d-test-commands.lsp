; Manual command reference: paste ONE form at a time into Plant 3D.
; Do not APPLOAD this file as a batch; the examples share the origin.
; First copy CustomScripts/*.py into your configured shared content folder's
; CPak Common/CustomScripts, then run PLANTREGISTERCUSTOMSCRIPTS.
; Restart Plant 3D after changes to previously loaded scripts.

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
