import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const manifestPath = path.join(root, 'data', 'kingswood-first-towers-manifest.json');
const outDir = path.join(root, 'data', 'kingswood-footprints');
const endpoint = 'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query';

const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
await fs.mkdir(outDir, { recursive: true });

function norm(s = '') {
  return s.toUpperCase().replace(/[^A-Z0-9]+/g, ' ').trim();
}

function isTowerOne(name = '', court = '') {
  const n = norm(name);
  const c = norm(court);
  if (!n.includes(c)) return false;
  return /(?:BLOCK|TOWER)\s*0?1(?:\s|$)/.test(n);
}

async function queryCourt(courtEN) {
  const where = `BuildingNameEN LIKE '%${courtEN.replaceAll("'", "''")}%'`;
  const params = new URLSearchParams({
    where,
    outFields: '*',
    returnGeometry: 'true',
    outSR: '4326',
    f: 'json'
  });
  const url = `${endpoint}?${params}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`);
  const json = await res.json();
  if (json.error) throw new Error(JSON.stringify(json.error));
  return { url, json };
}

const summary = [];
for (const phase of manifest.phases) {
  if (phase.residential === false || phase.officialFootprintStatus === 'already-in-project') continue;
  const { url, json } = await queryCourt(phase.courtEN);
  const candidates = (json.features || []).filter(f => isTowerOne(f.attributes?.BuildingNameEN, phase.courtEN)
    && f.attributes?.BuildingNameTC?.includes(phase.courtTC)
    && f.geometry?.rings?.[0]?.every(([lng,lat]) => lng > 113.97 && lng < 114.03 && lat > 22.43 && lat < 22.49));

  const rawPath = path.join(outDir, `phase-${phase.phase}-court-query.raw.json`);
  await fs.writeFile(rawPath, JSON.stringify({ queryUrl: url, response: json }, null, 2));

  if (candidates.length !== 1) {
    summary.push({
      phase: phase.phase,
      courtEN: phase.courtEN,
      status: 'REVIEW',
      candidateCount: candidates.length,
      candidateNames: candidates.map(f => f.attributes?.BuildingNameEN),
      rawPath: path.relative(root, rawPath)
    });
    continue;
  }

  const feature = candidates[0];
  const out = {
    provenance: {
      source: 'Hong Kong Lands Department CSDI Building Framework Spatial Data Theme',
      endpoint,
      queryUrl: url,
      retrievedAt: new Date().toISOString(),
      outputCRS: 'EPSG:4326',
      selectionRule: `BuildingNameEN contains ${phase.courtEN}; Block/Tower 1; Chinese name contains ${phase.courtTC}; all coordinates inside 113.97–114.03 E, 22.43–22.49 N; exactly one candidate required`
    },
    attributes: feature.attributes,
    geometry: feature.geometry
  };
  const outPath = phase.officialFootprintFile ? path.join(root, phase.officialFootprintFile) : path.join(outDir, `phase-${phase.phase}-tower-1-official-footprint.json`);
  await fs.writeFile(outPath, JSON.stringify(out, null, 2));
  summary.push({
    phase: phase.phase,
    courtEN: phase.courtEN,
    status: 'OK',
    buildingNameEN: feature.attributes?.BuildingNameEN,
    buildingNameTC: feature.attributes?.BuildingNameTC,
    buildingCSUID: feature.attributes?.BuildingCSUID,
    baseHeight: feature.attributes?.BaseHeight,
    topHeight: feature.attributes?.TopHeight,
    storeys: feature.attributes?.Storeys,
    file: path.relative(root, outPath)
  });
}

const summaryPath = path.join(outDir, 'fetch-summary.json');
await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2));
console.table(summary.map(({ phase, courtEN, status, buildingNameEN, buildingCSUID, candidateCount }) => ({ phase, courtEN, status, buildingNameEN, buildingCSUID, candidateCount })));
console.log(`\nSaved summary: ${path.relative(root, summaryPath)}`);
if (summary.some(x => x.status !== 'OK')) process.exitCode = 2;
