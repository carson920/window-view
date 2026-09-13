# Regression: do not reproduce the v3 red lines

`tower-8-v3-bad-example.png` is a deliberately retained failure example from the previous package.

The red lines were generated from room/facade heuristics and often floated inside bedrooms/living rooms instead of overlapping the real window symbols. Any new tracing implementation must fail QA if it reproduces this pattern.

Regression rule:

> A trusted source trace must visually overlap a real window/glazing/sill symbol in the source plan. Room-centre or facade-proxy lines are not window traces.
