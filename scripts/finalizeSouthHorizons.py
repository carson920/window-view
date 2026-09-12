"""Audit saved artifacts and write publication decisions; never fetch or refit."""
import json, math, hashlib, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / 'data/south-horizons-approved-job'
def read(p): return json.loads(p.read_text())
def write(name, value): (JOB/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(p): return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
def inside(p, ring):
    x,y=p; yes=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: yes=not yes
    return yes
def move(p,s):
    angle=math.radians(s['rotationDegrees']); x,y=p[0],-p[1]; scale=s['scaleMetresPerCanvasPixel']; tx,ty=s['translationMetres']
    return [scale*(x*math.cos(angle)-y*math.sin(angle))+tx,scale*(x*math.sin(angle)+y*math.cos(angle))+ty]

job=read(JOB/'approved-job.json'); summary=read(JOB/'validation-summary.json')
prep={r['tower']:r for r in read(JOB/'preparation.json')}
placements={r['tower']:r for r in read(JOB/'placement-summary.json')}
assert [r['tower'] for r in summary]==job['estate']['blockIds'], 'Incomplete saved validation run'
assert '>20' in (ROOT/'scripts/prepareSouthHorizons.py').read_text()
# Modification times support this resume audit, but are not portable after checkout.
sources=read(JOB/'sources/downloads.json')
for src in sources:
    p=JOB/'floorplans/primary'/f'{src["id"]}.jpg'
    assert digest(p)==src['sha256'] and p.stat().st_size==src['bytes'], src['id']
assert len(sources)==len(job['primaryFloorPlanSource']['items'])==51
checks=[]; review=[]; timings=[]; preserved={}
for row in summary:
    start=time.perf_counter(); tower=row['tower']; folder=ROOT/f'data/south-horizons-tower-{tower.lower()}'
    for name in ['annotations.json','official-footprint.json','placement.json','result.json','plan-crop.png','window-review.png','approved-overlay.png']:
        p=folder/name; preserved[str(p.relative_to(ROOT))]=digest(p)
    r=read(folder/'result.json'); a=read(folder/'annotations.json'); p=read(folder/'placement.json'); o=read(folder/'official-footprint.json')
    assert r['annotation']==a and r['transform']==p['transform']
    assert r['buildingCsuid']==o['attributes']['BuildingCSUID']==prep[tower]['csuid']
    assert r['qa']['pass']==row['qaPass'] and r['qa']['errors']==row['errors']
    assert len(r['windows'])==row['windows'] and r['transform']['rmsMetres']==row['rmse']
    assert not r['transform']['reflected'] and r['transform']['rotationDegrees']==placements[tower]['rotationDegrees']
    assert set(a['rooms'])==set('ABCDEFGH')
    assert len({(w['flat'],w['id']) for w in r['windows']})==sum(map(len,a['rooms'].values()))
    src=next(s for s in sources if s['id']==a['sourceId']); assert a['source']==src['url']
    origin=p['origin']; factor=p['factor']; ring=o['geometry']['rings'][0]
    for w in r['windows']:
        if 'lat' not in w: assert w['qaErrors']; continue
        _,s1,s2,interior=next(v for v in a['rooms'][w['flat']] if v[0]==w['id'])
        u,v=move(s1,r['transform']),move(s2,r['transform']); mid=[(u[i]+v[i])/2 for i in range(2)]
        assert abs(w['lng']-(origin[0]+mid[0]/factor[0]))<1e-10
        assert abs(w['lat']-(origin[1]+mid[1]/factor[1]))<1e-10
        tangent=[v[i]-u[i] for i in range(2)]; length=math.hypot(*tangent); normal=[-tangent[1]/length,tangent[0]/length]
        witness=move(interior,r['transform'])
        if sum(normal[i]*(witness[i]-mid[i]) for i in range(2))>0: normal=[-n for n in normal]
        heading=math.degrees(math.atan2(*normal))%360
        assert abs((heading-w['heading']+180)%360-180)<1e-7
        assert w['interiorNormalDot']<0
        for i,key in enumerate(['cameraLng','cameraLat']):
            assert abs(w[key]-(origin[i]+(mid[i]+normal[i]*w['cameraOffsetMetres'])/factor[i]))<1e-10
        if row['qaPass']:
            assert not w['qaErrors'] and not inside([w['cameraLng'],w['cameraLat']],ring)
            for distance in [.25,.5,1,1.5,2]:
                assert not inside([w['cameraLng']+normal[0]*distance/factor[0],w['cameraLat']+normal[1]*distance/factor[1]],ring)
            assert abs(w['facadeDistanceMeters'])<=2 and 1<=w['cameraOffsetMetres']<=3
    visual=[]
    if tower=='6': visual=['A/master: segment x=2 touches crop boundary; original left facade/window identity needs review.']
    publish=row['qaPass'] and not visual
    issues=row['errors']+visual
    if issues:
        review.append(dict(tower=tower,scope='entire tower withheld',issues=issues,
            affectedWindows=[{k:w.get(k) for k in ['flat','id','lat','lng','heading','facadeDistanceMeters','cameraOffsetMetres','qaErrors']} for w in r['windows'] if w['qaErrors'] or (tower=='6' and w['flat']=='A' and w['id']=='master')],
            evidence=[str((folder/f).relative_to(ROOT)) for f in ['result.json','approved-overlay.png','window-review.png']],
            candidateSolutions=['Keep approved orientation and existing trace pending source/footprint reconciliation','Correct only the identified exterior/window extraction after confirming its source evidence'],
            humanDecision='Confirm the indicated facade/window on the approved plan against the saved official footprint; no alternate orientation is proposed.'))
    floors=[int(n) for n in a['floorCoverage'].replace('F','').split('–')]
    if tower=='13': floors[0]=4
    if tower=='30': floors[1]=29
    checks.append(dict(tower=tower,buildingCsuid=r['buildingCsuid'],windows=row['windows'],numericalQaPass=row['qaPass'],artifactAuditPass=True,publicationPass=publish,issues=issues,floors=floors,rmse=row['rmse']))
    timings.append(dict(tower=tower,seconds={'source-fetch':None,'plan-parse':prep[tower]['plan-parse'],'orientation-apply':None,'footprint-match':None,'geospatial-transform':placements[tower]['seconds'],'validation':row['seconds'],'output-write':None,'total':None},resumptionAuditSeconds=time.perf_counter()-start))
for item in job['primaryFloorPlanSource']['items']:
    if item['planRole']!='typical': review.append(dict(tower=item['blocks'][0],scope=item['floorCoverage'],source=item['id'],status='not processed in existing artifacts',issues=['No saved trace/placement for this special-floor variant; excluded from import.'],humanDecision='A separate floor-specific window template is needed; standard-floor windows were not extrapolated.'))
review.append(dict(tower='13',scope='1–3/F G/H variant; whole building limited to 4–33/F',source='H-13-typ',issues=['Inset variant has no saved independent trace.'],humanDecision='Confirm separate G/H inset window template before enabling these floors.'))
write('artifact-audit.json',dict(validationRunCompleted=True,threshold=20,evidence={'preparationScriptMtime':stamp(ROOT/'scripts/prepareSouthHorizons.py'),'placementSummaryMtime':stamp(JOB/'placement-summary.json'),'validationSummaryMtime':stamp(JOB/'validation-summary.json'),'savedResults':len(checks),'sourceHashesChecked':len(sources)},towers=checks,preservedArtifactSha256=preserved))
write('needs-review.json',review)
totals={stage:sum(t['seconds'][stage] or 0 for t in timings) for stage in timings[0]['seconds'] if any(t['seconds'][stage] is not None for t in timings)}
write('processing-timings.json',dict(perTower=timings,slowestTowers=sorted([dict(tower=t['tower'],recordedSubtotalSeconds=sum(v or 0 for v in t['seconds'].values())) for t in timings],key=lambda t:-t['recordedSubtotalSeconds']),slowestStages=sorted(totals.items(),key=lambda x:-x[1]),limitations='Historical stages were not fully instrumented. Null means unrecorded, not zero. plan-parse includes preparation I/O; geospatial-transform includes fit and overlay I/O; validation includes result/overlay output. Subtotals are not full job elapsed time. No times were fabricated.'))
with (JOB/'processing.log').open('a') as log:
    log.write(f'{datetime.now(timezone.utc).isoformat()} Resume audit: saved HSV20 validation complete; 51 source hashes, 34 result/placement pairs checked; no fetch, matching, orientation search or tracing rerun.\n')
    for c in checks: log.write(f"Tower {c['tower']}: numerical={c['numericalQaPass']} publication={c['publicationPass']} windows={c['windows']} RMSE={c['rmse']:.4f}; {'; '.join(c['issues'])}\n")
print(json.dumps({'audited':len(checks),'publishable':sum(c['publicationPass'] for c in checks),'windows':sum(c['windows'] for c in checks if c['publicationPass']),'reviewTowers':[c['tower'] for c in checks if not c['publicationPass']]}))
