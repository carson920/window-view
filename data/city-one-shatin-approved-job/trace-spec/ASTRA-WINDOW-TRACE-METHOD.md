# Canonical window tracing method — copied from the successful South Horizons workflow

This package deliberately removes the v2/v3 `canonical-annotations.json` semantic proxies. They were not physical window traces.

## What Astra actually did on South Horizons

The successful pipeline did **manual visual transcription on the source crop**:

1. Read the approved floor-plan image.
2. Locate the **actual visible glazing / sill / window line** on the exterior wall.
3. Store the two source-image endpoints `p1` / `p2` of that physical line.
4. Store an **interior witness** (or equivalent interior-side direction) inside the room.
5. Derive the outward normal from the segment tangent and flip it away from the witness.
6. Only after that, transform the source segment into the geospatial registration and compare it with the official footprint.

The South Horizons implementation explicitly says:

`Coordinates reference plan-crop.png pixels; no official-polygon window inference.`

and sets:

`planInterpretation = visually-reviewed-main-window-segments`

The physical trace therefore comes from the floor plan, **not** from room centre, not from the government footprint, and not from a guessed facade.

## City One rules

For each of the 14 canonical families:

- trace only habitable-room view windows that are clearly visible in the source plan;
- the red segment must overlap the actual source window/glazing symbol when rendered on the source image;
- if a room has two distinct exterior glazing runs, preserve them as separate segments unless the downstream schema intentionally models them as a corner-window chord;
- do not assume one window per room;
- do not draw across Chinese room labels or through room interiors;
- do not trace air-conditioner ledges, bay-window outer outlines, dimension lines, balcony/utility edges, or the thick exterior wall itself unless that exact line is the drawn glazing/sill line;
- if the source is too blurry or a watermark hides the opening, write `unresolved` for that room/window and continue;
- keep source coordinates, source image dimensions/hash, room/flat identity, and interior witness as provenance.

## Living-room runs

On South Horizons some living glazing was one continuous diagonal run shared across adjacent flats. Astra traced the full visible glazing run, split it at the separating flat wall, and trimmed only the masonry ends. Do this **only when the City One source visibly has the same geometry**. Do not invent a continuous run just because two living rooms are adjacent.

## Family reuse

After the canonical trace is complete:

1. positive-handed structural registration to the member plan;
2. verify core, flat-label order, party walls, facade corners, and window-bearing walls;
3. transform the canonical source segments;
4. render `family-diff-overlay.png` on the target source plan;
5. inherit only the segments that still sit on the target's actual glazing symbols;
6. retrace only changed flats/rooms;
7. reflection is forbidden.

## Required trace QA

A window is not `source-traced` unless the overlay shows the red segment on the visible source window symbol. A line merely near the correct room is a failure.
