import fs from 'node:fs/promises';
const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await fs.readFile(new URL('data/kingswood-first-towers-manifest.json', root)));
await fs.mkdir(new URL('data/kingswood-plans/', root), {recursive:true});
for (const phase of manifest.phases.filter(p=>p.residential!==false)) {
  const response = await fetch(phase.floorPlanUrl);
  if (!response.ok) throw new Error(`${phase.phase}: ${response.status}`);
  await fs.writeFile(new URL(`data/kingswood-plans/phase-${phase.phase}.png`, root), Buffer.from(await response.arrayBuffer()));
  console.log(`Saved phase ${phase.phase} source plan`);
}
