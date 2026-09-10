# YOHO WEST: Tower 2B, B6 stack

Checked 9 September 2026. This is a sourced research candidate, not a verified window camera.

## Result

Selected stack: Tower 2B, Flat B6, main-bedroom front facade. Imported typical-floor subset: 5–12, 15–23, 25–33, 35–43/F. Other floors are outside this import, not asserted nonexistent.

- Candidate facade location: approximately **22.45950 N, 114.00240 E**.
- Candidate outward direction: approximately **36° (northeast)**.
- Exact window coordinate, eye-level altitude and viewer tilt: **unverified**.
- Live camera latitude/longitude/heading remain null; confidence is review; launch stays disabled.

These candidate numbers are derived from official sources, not coordinates published by the developer for a window. Do not use them as a surveyed window position. No measured error bound has been established.

## Sources and reproducible derivation

1. [Developer's sales brochure, fifth revision, 19 November 2024](https://www.yohowest.com.hk/download/brochure/YOHO%20WEST_SalesBrochure%285th%20Revision%29_20241119_final.pdf), printed AL007 (PDF page 33): identifies B6, its main bedroom, typical floor ranges and north arrow. AL006 (PDF page 32) lists multiple floor-to-floor heights for B6; it does not justify choosing one uniform value without further interpretation.
2. [LandsD Building dataset metadata](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html) and [official ArcGIS service](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0). Query `BuildingCSUID='1830835561T20240929'`, `outFields=*`, `outSR=4326`, `f=pjson`. The returned record is **Yoho West Tower 2B**, distinct from the YOHO WEST podium. Raw feature is saved in `data/tower-2b-official-footprint.json`.

For audit, zero-based outer-ring vertices 7 and 10 are:

- 7: longitude 114.00236635660214, latitude 22.45952175347358
- 10: longitude 114.00241204474601, latitude 22.45949159687914

Their outward normal, using local east/north distances, is about 35.5°. These are official polygon vertices, not window coordinates. The side agrees approximately with the brochure's north-arrow orientation.

A visual comparison places the B6 main-bedroom front opening toward the right of this candidate facade segment. Interpolating about 75% from vertex 7 toward vertex 10 gives the rounded candidate above. This correspondence is provisional: the government footprint generalizes facade detail, while the architectural plan shows balconies, bay windows and recesses. It has not been checked with a full georeferenced overlay or surveyed control points. Therefore the derived point is retained only in research metadata, never in verified camera fields.

## What remains

- Confirm plan-to-map registration using several matching surveyed corners, with residual errors; identify the exact glazing plane and intended camera offset.
- Verify the brochure against the current/as-built layout.
- Establish floor-specific elevation and its compatibility with LandsD's camera vertical datum. Government BaseHeight/TopHeight describe the building, not a verified eye-height reference for a named floor.
- Use physical storey indices or a verified per-floor lookup for altitude. Numeric floor labels skip 13, 14, 24 and 34 in this subset: `15 - 12` is not three physical storeys. The original generic formula must not be applied to this building without a verified model that accounts for that numbering.
- Confirm viewer heading/tilt and height semantics before enabling a live link.

## Exploratory 3/F test

The developer section AT001 (PDF page 111) explicitly places the lowest residential floor, 3/F, at 27.40 m above Hong Kong Principal Datum. The 3/F plan AL005 also contains B6. A 1.5 m assumed eye height gives 28.90 m in that datum. This establishes a documented 3/F datum, not the elevations of the imported upper-floor subset.

Exploratory link: https://3d.map.gov.hk/mapviewer/app/map?flyto=22.45950,114.00240,28.9,36,0,0&l=zh-HK

This uses the provisional facade coordinate and direction, with tilt 0 as the horizontal-view test parameter. Compatibility of HKPD with the viewer camera altitude and exact window alignment remain unverified. It must not be presented as a verified B6 window view.

Browser test: the initial tilt=90 link loaded successfully but produced a downward view. The exploratory link was changed to tilt=0 for a horizon-facing view.

Final browser observation: the tilt=0 request rendered a downward-oblique scene. LandsD's visible share-current-view field returned latitude 22.459499999999995, longitude 114.00240000000001, altitude 28.90000000109346, heading 36.00000000000005, tilt 35.66432358586552, roll 359.905464969947. Thus the requested position and numeric altitude were retained, but the final tilt/roll differed. The cause was not established. A loaded scene does not verify the glazing position or altitude datum. The application's verified View button remains disabled.

Near-horizontal follow-up: requesting tilt=0.1 returned tilt=0.1000000000000065 in LandsD's share-current-view field, with position/altitude unchanged. Thus near-horizontal viewing works. Exactly zero appears to trigger different handling (possible zero/default-value handling; implementation not verified). The camera's visible scene intersected or was obstructed by model surfaces, so this is not a validated window location. Use 0.1 degrees for exploratory near-horizontal links, not a claim of exact zero support.
