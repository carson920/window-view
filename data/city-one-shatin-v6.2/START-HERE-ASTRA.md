# START HERE — City One Shatin v6

This v6 package supersedes v2/v3/v4/v5.

## v6 priorities

### 1. Recognize Hong Kong bay-window plan symbols
City One plans frequently show projected bay-window modules where the glazing is represented by a polygonal projection rather than one obvious thin sill line. v6 explicitly supports:
- `sill-line`
- `bay-window-face`
- `corner-bay-face`
- `multi-face-bay`
- `full-height-glazing`
- `glazed-opening`

A clearly repeated projected bay module must not be rejected merely because a separate thin sill line is absent at source resolution. Identify the module, then trace the **primary outward viewing face**. Do not trace the whole bay outline.

### 2. Use approved window samples
Read:
- `window-samples/window-pattern-presets.json`
- `window-samples/window-pattern-samples.json` if present

The user may upload **multiple samples**. All user-supplied samples are approved semantic references. Samples teach what a pattern means; never copy their raw coordinates into a tower plan. Negative samples such as AC platforms and ledges are equally important.

### 3. Labels must be readable
Generated trace/review overlays must use **English-only callout labels**. The Chinese text already printed on the source plan remains untouched. Do not add mixed Chinese/English callouts on top of it.

For every generated callout:
- use a short label such as `A living`, `B bed-1`, `C bay face`;
- place the label away from the window segment;
- prefer the outward side derived from the room-specific interior witness;
- use a leader line;
- run collision avoidance so label boxes do not overlap other label boxes;
- stagger labels along the window tangent when several windows are close;
- avoid covering important source-plan room text when a free nearby location exists.

## Non-negotiable tracing order

**approved source plan → actual glazing / accepted bay-window viewing face → source endpoints + interior witness → family reuse → geospatial QA**

Never use:
- room centre → guessed facade;
- LandsD footprint → guessed source window;
- symmetry alone → invented window;
- full bay/ledge outline → fake glazing segment.

## Family reuse

1. Trace each canonical family only once.
2. Verify identical/near-identical family members with positive-handed structural registration.
3. Never reflect.
4. Inherit source-plan traces only after a family overlay pass.
5. Retrace only changed flats/rooms.
6. Keep each member tower's LandsD placement independent.

## Local failure policy

A local window mismatch or unresolved room must remain local. Do not withhold a whole tower unless its tower-level transform / identity / orientation is invalid.

## Inputs to read first

1. `approved-job.json`
2. `layout-families.json`
3. `canonical-window-traces.json`
4. `trace-spec/ASTRA-WINDOW-TRACE-METHOD.md`
5. `trace-spec/WINDOW-PATTERN-PRESETS.md`
6. `window-samples/window-pattern-presets.json`
7. `window-samples/window-pattern-samples.json` if present
8. `orientation/orientation-sources.json` if present

## Required outputs

- populated `canonical-window-traces.json`
- canonical source overlays for all 14 canonicals
- `review-results/tower-<n>/approved-overlay.png`
- `review-results/tower-<n>/family-diff-overlay.png` for inherited members
- `processing-timings.json`
- `processing-report.json`
- `needs-review.json`
- updated `review-data.js`
- tests/build logs

## Regression guard

`qa-regression/tower-8-v3-bad-example.png` is a bad trace. Red lines floating inside a room are not windows.
