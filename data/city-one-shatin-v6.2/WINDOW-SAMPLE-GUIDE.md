# Window sample guide — v6

The admin page supports **multiple** window sample images. User uploads are auto-approved.

Each sample stores:
- `presetId`
- `patternClass` / `representationClass`
- `polarity`: `positive` or `negative`
- `traceRule`
- scope: estate / family / tower
- optional human note

Recommended workflow:
1. Pick the closest preset.
2. Upload or paste one or more crops.
3. Use positive examples for real windows and negative examples for common false positives.
4. Export the direct-to-Astra ZIP.

Samples are semantic references only. Astra must locate and trace the actual instance on each approved plan.
