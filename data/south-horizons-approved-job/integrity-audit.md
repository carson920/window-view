# South Horizons final integrity audit

Production: **31 towers / 910 windows**. 30 complete typical-window sets; Tower 10 partial (31 windows, H/master excluded); Towers 1, 3, 6 fully excluded. No special-floor data implied.

Reconciliation: 995 traced windows − 28 (Tower 1) − 28 (Tower 3) − 28 (Tower 6) = previous 911; minus 10/H/master = final 910.

Tower 1 RMSE 1.706 m fails the 1.5 m threshold. Tower 3 RMSE 0.762 m passes; B/C master facade discrepancy exceeds 2 m. Tower 6 excluded for A/master crop issue. Tower 10 H/master also lies on clipped crop edge (x=3), now individually excluded.

All 272 living normals have independent local coloured-room-side support. Canvas centre alone is unsafe, and colour does not independently certify flat identity. 25 room-side checks are inconclusive (including excluded windows); exact tower/flat/room evidence is in integrity-audit.json and needs-review.json. These checks do not prove reversed headings, so no automatic flipping was performed.

Original traced living endpoints are preserved as sourcePlanSegment; 6% trimmed endpoints are explicitly camera/proxy segments, not measured physical glazing extents. No retained coordinates or headings changed.

All 17 special-floor sheets are excluded from selectors; out-of-range API requests return FLOOR_DATA_UNAVAILABLE. Tower 13 remains 4–33/F; Tower 30 remains 1–29/F. API responses include floor applicability even without a requested floor.

Build passed; 95 tests passed, including exclusions, provenance, source/proxy endpoints, handedness, bounds, outward camera clearance and count reconciliation.

## Final transforms

Scale: metres per crop pixel. Translation: local east/north metres. Rotation follows stored plan-to-local convention. Determinant positive for every tower. No changes from earliest committed HSV20 run (980f2b1). Previous HSV45 transforms were not retained, so material-change comparison with that run is unavailable.

| Tower | CSUID | Scale | Rotation ° | Translation E,N m | RMSE m |
|---|---|---:|---:|---|---:|
| 1 | 3327911817T20050430 | 0.03194496 | 0 | -15.8839, 15.7065 | 1.7055 |
| 2 | 3327811769T20050430 | 0.03389958 | 0 | -16.7852, 16.5161 | 0.7237 |
| 3 | 3322411781T20050430 | 0.05858858 | 3.5 | -20.3425, 18.1856 | 0.7615 |
| 4 | 3318911779T20050430 | 0.05486429 | 3.5 | -19.2194, 18.4436 | 0.5125 |
| 5 | 3314711776T20050430 | 0.05844020 | 3.5 | -18.3801, 18.1146 | 0.4783 |
| 6 | 3311311773T20050430 | 0.05417568 | 3.5 | -18.4068, 18.1395 | 0.4720 |
| 7 | 3301811766T20050430 | 0.04096092 | -45 | -2.0009, 26.7740 | 0.3336 |
| 8 | 3299011735T20050430 | 0.04120101 | -45 | -1.8351, 28.4907 | 0.5124 |
| 9 | 3296011703T20050430 | 0.04036497 | -45 | -0.3399, 28.0893 | 0.5222 |
| 10 | 3293111673T20050430 | 0.04185931 | -45 | 0.0017, 29.4614 | 0.5515 |
| 11 | 3306911733T20050430 | 0.03615084 | -12 | -15.3188, 20.8130 | 0.9263 |
| 12 | 3306211695T20050430 | 0.03616911 | -12 | -15.0239, 20.9716 | 0.9370 |
| 13 | 3305211659T20050430 | 0.03992062 | -12 | -16.4929, 22.7370 | 0.3150 |
| 13A | 3306011614T20050430 | 0.04023195 | -12 | -15.1800, 23.2982 | 0.2479 |
| 15 | 3310011604T20050430 | 0.04101386 | -12 | -16.6619, 21.4470 | 0.2451 |
| 16 | 3313811595T20050430 | 0.03998761 | -12 | -15.9308, 23.7056 | 0.2532 |
| 17 | 3323911569T20050430 | 0.04188262 | -12 | -16.2592, 22.2809 | 0.3190 |
| 18 | 3328011561T20050430 | 0.04723741 | -12 | -16.0206, 23.3287 | 0.3860 |
| 19 | 3331911551T20050430 | 0.04443736 | -12 | -15.9546, 22.9133 | 0.2813 |
| 20 | 3335811543T20050430 | 0.04334954 | -12 | -14.3613, 21.1012 | 0.7215 |
| 21 | 3327111479T20050430 | 0.04042145 | -12 | -14.3828, 23.2801 | 0.3132 |
| 22 | 3331011471T20050430 | 0.04437461 | -12 | -16.7505, 23.7141 | 0.3448 |
| 23 | 3335411478T20050430 | 0.04433629 | 20 | -23.6034, 12.0668 | 0.3165 |
| 23A | 3339111493T20050430 | 0.04412172 | 20 | -25.1783, 10.0572 | 0.3244 |
| 25 | 3343711527T20050430 | 0.03650743 | 37 | -25.0588, 2.0880 | 0.4242 |
| 26 | 3347111551T20050430 | 0.03667062 | 37 | -24.5349, 0.5592 | 0.6210 |
| 27 | 3350311575T20050430 | 0.03648366 | 37 | -24.9601, 2.2568 | 0.4220 |
| 28 | 3353811599T20050430 | 0.03706528 | 37 | -24.6955, 1.5624 | 0.3931 |
| 29 | 3351111675T20050430 | 0.06010872 | -12 | -14.1530, 19.9625 | 0.2612 |
| 30 | 3347111682T20050430 | 0.06105456 | -12 | -14.1619, 20.1406 | 0.2772 |
| 31 | 3343211691T20050430 | 0.06275570 | -12 | -14.7400, 19.8206 | 0.3208 |
| 32 | 3342311653T20050430 | 0.03532213 | -12 | -14.1300, 19.7981 | 0.3016 |
| 33 | 3341511615T20050430 | 0.03596682 | -12 | -13.7314, 19.7722 | 0.2864 |
| 33A | 3340711577T20050430 | 0.03475809 | -12 | -13.6634, 19.6406 | 0.3316 |

## Production tower/window counts

2: 26, 4: 28, 5: 28, 7: 32, 8: 32, 9: 32, 10: 31, 11: 32, 12: 32, 13: 32, 13A: 32, 15: 32, 16: 32, 17: 32, 18: 28, 19: 28, 20: 28, 21: 29, 22: 28, 23: 28, 23A: 28, 25: 28, 26: 28, 27: 28, 28: 28, 29: 28, 30: 28, 31: 28, 32: 28, 33: 28, 33A: 28

## Special-floor exclusions

| Tower | Floor | Source | Behaviour |
|---|---:|---|---|
| 1 | 40 | H-1-special-40F | tower excluded |
| 3 | 35 | H-3-special-35F | tower excluded |
| 4 | 35 | H-4-special-35F | special template unavailable; outside supported typical range |
| 5 | 35 | H-5-special-35F | special template unavailable; outside supported typical range |
| 6 | 35 | H-6-special-35F | tower excluded |
| 7 | 42 | H-7-special-42F | special template unavailable; outside supported typical range |
| 8 | 42 | H-8-special-42F | special template unavailable; outside supported typical range |
| 9 | 42 | H-9-special-42F | special template unavailable; outside supported typical range |
| 10 | 42 | H-10-special-42F | special template unavailable; outside supported typical range |
| 13A | 40 | H-13A-special-40F | special template unavailable; outside supported typical range |
| 15 | 40 | H-15-special-40F | special template unavailable; outside supported typical range |
| 16 | 40 | H-16-special-40F | special template unavailable; outside supported typical range |
| 17 | 40 | H-17-special-40F | special template unavailable; outside supported typical range |
| 18 | 40 | H-18-special-40F | special template unavailable; outside supported typical range |
| 19 | 40 | H-19-special-40F | special template unavailable; outside supported typical range |
| 22 | 36 | H-22-special-36F | special template unavailable; outside supported typical range |
| 30 | 30 | H-30-special-30F-special-variant | special template unavailable; outside supported typical range |
