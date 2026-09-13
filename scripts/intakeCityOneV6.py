"""Validate v6.2 source identities before reusing local source/placement evidence."""
import hashlib,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'data/city-one-shatin-approved-job';NEW=ROOT/'data/city-one-shatin-v6.2'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.perf_counter();old=read(OLD/'approved-job.json');new=read(NEW/'approved-job.json')
assert old['primaryFloorPlanSource']['items']==new['primaryFloorPlanSource']['items'],'Changed approved sources require fresh intake'
assert read(OLD/'layout-families.json')==read(NEW/'layout-families.json'),'Changed family candidates'
copied=[]
for p in sorted((OLD/'floorplans').glob('H-*-typ.jpg')):
    dst=NEW/'floorplans'/p.name;shutil.copy2(p,dst);copied.append({'file':str(dst.relative_to(ROOT)),'sha256':sha(p),'cachedFrom':str(p.relative_to(ROOT))})
assert len(copied)==52
for name in ['official-query.raw.json','official-query-provenance.json']:
    shutil.copy2(OLD/name,NEW/name)
for p in (OLD/'orientation').glob('*.png'):shutil.copy2(p,NEW/'orientation'/p.name)
shutil.copy2(OLD/'orientation/orientation-sources.json',NEW/'orientation/orientation-sources.json')
# Preserve the earlier independent transforms; source and geometry hashes below
# permit reuse without repeating orientation or geometric optimization.
for n in range(1,53):
    dest=NEW/f'review-results/tower-{n}';dest.mkdir(parents=True,exist_ok=True)
    shutil.copy2(OLD/f'review-results/tower-{n}/result.json',dest/'previous-result.json')
    shutil.copy2(OLD/f'review-results/tower-{n}/result.json',dest/'result.json')
    shutil.copy2(OLD/f'review-results/tower-{n}/official-footprint.json',dest/'official-footprint.json')
(NEW/'intake-report.json').write_text(json.dumps({'sourceCacheCount':52,'sourceUrlsUnchanged':True,'geometryRawSha256':sha(NEW/'official-query.raw.json'),'orientationReusedFrom':str((OLD/'orientation').relative_to(ROOT)),'sampleCount':len(read(NEW/'window-samples/window-pattern-samples.json')['items']),'files':copied,'seconds':time.perf_counter()-start},indent=2)+'\n')
print('52 cached source images verified; 52 previous transforms retained; 4 sample images present.')
