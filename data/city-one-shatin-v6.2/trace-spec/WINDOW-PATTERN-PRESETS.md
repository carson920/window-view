# Window pattern presets

`window-samples/window-pattern-presets.json` is the canonical preset list for v6.

Important rules:
- Samples teach **semantics**, not coordinates.
- Positive samples may establish a supported window representation class.
- Negative samples explicitly teach Astra what **not** to classify as a window.
- For bay windows, identify the bay module first, then trace the primary outward viewing face or distinct glazing faces.
- Never turn the entire bay/ledge/AC-platform outline into a window segment.
