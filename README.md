# 窗外景觀 · Window View

Small bilingual Vite + vanilla JavaScript launcher for LandsD Open3Dhk. Select estate, building, floor, flat and window; open the calculated camera in a new tab. No backend or authentication.

## Run

Node.js 22+ and npm:

```sh
npm install
npm run dev
npm test
npm run build
```

Production files are in `dist/`, including the research report and source data. Python is only needed to repeat geometric research, not to run the app.

## Included records

- 嘉湖山莊：1、2、3、5、6、7期第1座，A–H 共48個客廳外牆 proxy。All enabled as labelled approximate previews. Phase4 has no residential first tower.
- YOHO WEST Tower 2B B6: approximate main-bedroom position, heading36°, 3/F only; brochure floor datum27.4m plus1.5m eye height. Other floor heights remain unavailable.
- Synthetic test estate: clearly labelled arbitrary fixtures; never surveyed property data.

See [Kingswood results](KINGSWOOD-FIRST-TOWERS.md) and [visual registration report](kingswood-report.html). Full48-stack records and3/F demo links: `data/kingswood-48-stacks.json`. Raw plans, official footprints, annotations, registration candidates and independent validation URLs are included in `data/`.

## Confidence and estimates

Horizontal geometry, heading and vertical geometry have separate confidence metadata. Unknown numbers remain null. A real window normally needs verification; an explicitly enabled `allowApproximate:true` review record may launch with numeric data while retaining `windowVerified:false`. Unresolved windows never launch.

Estimated floor models use `allowEstimated:true, confidence:estimated, verified:false`. The UI labels their displayed altitude as unverified. Kingswood assumes G/F at official BaseHeight and uses `(TopHeight−BaseHeight)/Storeys` as a building-average spacing, plus eye height. Neither exact slab elevation nor roof/podium/storey-count correction is verified. Typical-floor scope excludes the noted duplex floors.

Window coordinates already include the derived1m outward offset; `cameraOffsetMeters` is metadata and is not applied again at runtime. Floor changes affect altitude only. Heading is clockwise from north. Tilt0.1° retains the earlier tested near-horizontal viewer behavior.

The48 proxies are provisional: manual tracing and footprint simplification limit accuracy. Lynwood has an unresolved mirror alternative and low horizontal confidence. Other phases are moderate, not survey grade. RMS measures fit residual, not absolute accuracy.

## Extend

Add estates/buildings/flats/windows to `data/properties.json`, with parent-local unique IDs, bilingual labels and sources. `defaultEstateId` and `defaultBuildingId` control initial selection. `floors` specifies the supported range and exclusions. Floor models support a verified `lookup` or a `formula` with explicit verified/estimated status. No estate-specific selection code is needed.

`src/cameraCalculator.js` controls eligibility and altitude; `src/landsdUrl.js` validates camera numbers and constructs the LandsD link; `src/main.js` manages selections and labels. Tests cover filters, invalid inputs, approximate authorization, estimated-height gating and all48 records.
