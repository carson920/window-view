# START HERE — Astra work order

This ZIP is a **human-approved ingestion package** for the window-view project.
You may unpack it yourself. The user should not need to unzip or rearrange files.

## Approved inputs
- Estate: South Horizons / 海怡半島
- Estate status: approved
- Processing status: pending
- Primary floor-plan source: 28Hse · complete 34-block floor-plan set
- Primary coverage: 34/34 blocks
- Approved orientation images: 3

## Non-negotiable orientation fast path
1. Approved Centaline/Centamap orientation screenshots and explicit flat-direction labels are authoritative for orientation and handedness.
2. If approved directions exist, **do not infer, search, optimize, or solve orientation from footprint geometry**.
3. **Never mirror or reflect an approved tower plan.**
4. **Do not enumerate alternative rotations** (0/90/180/270 or arbitrary candidates) and then choose the best geometric fit.
5. Apply only the **single transform consistent with the approved source semantics**. Translation/scale/geospatial placement may be solved; orientation may only follow the approved source.
6. Geometry fitting is subordinate to source semantics. A lower geometric error must never override an approved flat direction.
7. If approved orientation and official geometry cannot be reconciled, stop that tower and add it to `needs-review.json`; do not try another rotation/reflection.

## Other processing rules
8. Read `approved-job.json`, `manifest.json`, and `sources/primary-source.json` first.
9. Do not redo broad source discovery or silently replace the approved Primary source.
10. Run `node scripts/fetch-floorplans.mjs` when local copies of the approved source images are useful.
11. Phase/pre-cluster groups are workload hints only. Reuse one geometry template only after deterministic verification of identical topology and handedness, without reflection.
12. Use official LandsD/CSDI geometry for precise lat/lng, scale and building footprint placement. Orientation screenshots are not metric GIS geometry.
13. Run deterministic QA and existing project tests. Import only passing results.
14. Keep provenance/confidence separate for plan interpretation, horizontal georeferencing, window semantics and vertical height.
15. Do not expose the proprietary master window dataset in a public frontend bundle.

## Timing / bottleneck logging — REQUIRED
Record elapsed time for every tower and stage in `processing-timings.json` and append human-readable milestones to `processing.log`.
Stages: source-fetch, plan-parse, orientation-apply, footprint-match, geospatial-transform, validation, output-write, total.
The timing JSON must also summarize the slowest towers and slowest stages.

## Expected outputs
At minimum leave:
- `processing-report.json` — completed/skipped/failed work and reasons
- `needs-review.json` — unresolved items (empty array if none)
- `processing-timings.json` — per-tower/per-stage timing and bottleneck summary
- `processing.log` — chronological processing milestones
- generated registration/import data in the project’s normal locations
- tests/validation results

## User handoff
The user uploaded this ZIP directly. Handle archive extraction yourself and proceed from the approved job.
