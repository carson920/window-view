# START HERE — Astra work order

This ZIP is a **human-approved ingestion package** for the window-view project.
You may unpack it yourself. The user should not need to unzip or rearrange files.

## Approved inputs
- Estate: Laguna City / 麗港城
- Estate status: approved
- Processing status: pending
- Primary floor-plan source: L&Lam · 11組圖則覆蓋38座
- Primary coverage: 38/38 blocks
- Approved orientation images: 1

## Non-negotiable rules
1. Read `approved-job.json`, `manifest.json`, and `sources/primary-source.json` first.
2. Do not redo broad source discovery or silently replace the approved Primary source.
3. Run `node scripts/fetch-floorplans.mjs` when local copies of the approved source images are useful.
4. Provider/source grouping and pre-clustered geometry families are hypotheses, not permission to merge blindly.
5. Verify geometry, mirror/reflection, unit topology, important wall/window differences, and plan-family reuse before applying one canonical template to multiple towers.
6. Orientation screenshots are only for stack identity, rotation, reflection, and tower relationships. Do not derive precise lat/lng, scale, or metre distances from screenshot pixels.
7. Precise georeferencing must use official LandsD/CSDI geometry.
8. Run deterministic QA and existing project tests.
9. If ambiguity remains, create/update `needs-review.json` with exact tower/family/candidates/reason. Do not guess.
10. Keep provenance and confidence separate for plan interpretation, horizontal georeferencing, window semantics, and vertical height.
11. Do not expose the proprietary master window dataset in the public frontend bundle.

## Expected outputs
At minimum leave:
- `processing-report.json` — what was completed, skipped, failed, and why
- `needs-review.json` — unresolved items (empty array if none)
- generated registration/import data in the project’s normal locations
- tests/validation results

## User handoff
The user uploaded this ZIP directly. Handle archive extraction yourself and proceed from the approved job.
