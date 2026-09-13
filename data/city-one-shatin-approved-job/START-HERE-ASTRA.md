# START HERE — City One Shatin v4

This supersedes v2/v3. **Do not reuse the 336 red semantic proxy lines from those packages.**

## Main change

I inspected the successful South Horizons code path (`annotateSouthHorizons.py` + downstream normal/overlay logic). This package now uses the same conceptual order:

**approved source plan → actual visible glazing line → source endpoints + interior witness → family reuse → geospatial QA**

Never reverse that into `room → guessed facade → proxy segment`.

## Work order

1. Read `approved-job.json`, `layout-families.json`, `canonical-window-traces.json`, and `trace-spec/ASTRA-WINDOW-TRACE-METHOD.md`.
2. Fetch/cache the approved 28Hse plans when useful. Do not redo broad source discovery.
3. Treat user-uploaded Centaline/Centamap orientation images as **already approved**. No approval UI or confirmation gate is needed.
4. For each of the 14 canonical families, manually/visually transcribe the actual window/glazing/sill segments from the canonical source image. Populate `canonical-window-traces.json` with source coordinates, source image dimensions/hash, flat, room/window id, and interior witness.
5. Generate a canonical source overlay for every traced canonical. If a red line does not sit on the source window symbol, fix it or mark unresolved.
6. Verify each candidate family member using positive-handed structural registration. No reflection.
7. Inherit canonical traces only after a target-source overlay pass. Generate `family-diff-overlay.png` for inherited members.
8. Retrace only changed flats/rooms. Do not independently redraw every tower.
9. Register against official LandsD/CSDI geometry. Official footprint is downstream geometry QA, not the source of window placement.
10. Keep window-level failures local. A single facade-distance/crop issue must not withhold unrelated windows or the whole tower unless the tower transform itself is invalid.
11. Special/unmapped floors must return `FLOOR_DATA_UNAVAILABLE`; do not silently fall back to typical-floor geometry.
12. Update `review-data.js` so `index.html` can browse source traces, approved overlays, family diffs, and issues.

## Required outputs

- populated `canonical-window-traces.json`
- canonical source-trace overlay for all 14 canonicals
- `review-results/tower-<n>/approved-overlay.png`
- `review-results/tower-<n>/family-diff-overlay.png` for inherited members
- `processing-timings.json`
- `processing-report.json`
- `needs-review.json`
- updated `review-data.js`
- tests/build logs

## Regression guard

See `qa-regression/tower-8-v3-bad-example.png`. That is a **bad** trace. Do not reproduce it.
