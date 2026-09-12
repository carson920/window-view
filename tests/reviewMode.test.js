import test from 'node:test';
import assert from 'node:assert/strict';
import { lookup } from '../server/api.mjs';

test('estate review returns every published tower with all windows', () => {
  const result = lookup('/api/estate-review', new URLSearchParams({ estate: 'laguna-city' }));
  assert.equal(result.status, 200);
  assert.equal(result.body.buildings.length, 4);
  for (const building of result.body.buildings) {
    assert.ok(building.outline?.length > 10);
    assert.equal(building.flats.length, 8);
    assert.equal(building.flats.reduce((count, flat) => count + flat.windows.length, 0), 28);
  }
});
