# South Horizons reference implementation notes

The prior repo's `scripts/annotateSouthHorizons.py` used a `window-traces.json` containing:

- explicit source-pixel window endpoints for bedrooms;
- continuous living glazing endpoints plus a split point where applicable;
- an interior-side witness/direction for each segment;
- `extractionMethod` describing **independent visual tracing of close parallel glazing/sill lines on the approved tower-specific crop**.

The registration stage (`processLagunaApproved.py` / `validateSouthHorizons.py`) then:

- transformed the source window segment with the tower registration;
- computed a normal from the segment tangent;
- flipped the normal using the interior witness;
- intersected that ray with the official footprint only as downstream QA;
- drew the approved overlay: blue official footprint, orange registered plan, red glazing, green outward normal.

That order is mandatory here: **source window first, footprint QA second**.
