# Indoor venue coverage report

Source: official LandsD Indoor Map API venue_polygon response saved as data/indoor/venue_polygon.json (689 features).

## Unique venue_category values

- businesscampus
- conventioncenter
- governmentfacility
- healthcarefacility
- hotel
- museum
- resort
- shoppingcenter
- stadium

## Requested-name matches

- 愉景新城 / Discovery Park — venue_id `7a1aef4b-33fd-4442-b0fb-4cc3e71b0726`, category shoppingcenter, address 398 CASTLE PEAK ROAD TSUEN WAN, TSUEN WAN; windows_line=not queried, unit_polygon=not queried, levels=not queried; not queried.
- 海逸豪園第四座 / Laguna Verde Tower 4 — venue_id `6bc9cf2d-e6f5-407a-bf92-2998ac84f29d`, category resort, address 8 LAGUNA VERDE AVENUE; windows_line=911, unit_polygon=423, levels=3rd Floor | 5th Floor | Roof  | 23rd Floor | 6th Floor | 7th Floor | 8th Floor | 9th Floor | 10th Floor | 11th Floor | 12th Floor | 15th Floor | 16th Floor | 17th Floor | 18th Floor | 19th Floor | 20th Floor | 21st Floor | 22nd Floor | 25th Floor | 26th Floor; level_polygon not queried; levels from unit_polygon.
- 康怡廣場（北） / Kornhill Plaza (North) — venue_id `e5f46612-a903-45da-ac8d-44df1d25c352`, category shoppingcenter, address 2 KORNHILL ROAD; windows_line=not queried, unit_polygon=not queried, levels=not queried; not queried.
- 康怡廣場（南） / Kornhill Plaza (South) — venue_id `12145565-9910-416e-be64-c73d4c083ab9`, category shoppingcenter, address 2 KORNHILL ROAD; windows_line=not queried, unit_polygon=not queried, levels=not queried; not queried.

## Provenance

Laguna Verde Tower 4 windows_line and unit_polygon were previously retrieved venue-by-venue and saved locally; its listed levels come from unit_polygon. level_polygon was not retrieved. The complete venue response was already downloaded to the local project from the same official endpoint. Subsequent venue-by-venue requests were blocked by the environment approval limit, so blank counts are explicitly unqueried; no venue is inferred to have windows data.
