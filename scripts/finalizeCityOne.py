"""Audit existing v6 artifacts and build the local review deliverables; no fitting."""
from annotateCityOne import ROOT,JOB,read,save
from registerSouthHorizons import apply,en_frame
from cityOneReview import render
from PIL import Image,ImageDraw
import numpy as np
import hashlib,json,time,subprocess,collections,datetime,re

start=time.perf_counter()
doc=read(JOB/'canonical-window-traces.json');report=read(JOB/'processing-report.json');issues=read(JOB/'needs-review.json');families=doc['families']
intake=read(JOB/'intake-report.json')
assert hashlib.sha256((JOB/'official-query.raw.json').read_bytes()).hexdigest()==intake['geometryRawSha256']
results=[];index=[];transformAudit=[]
for t in report['towers']:
    n=t['tower'];out=JOB/f'review-results/tower-{n}';r=read(out/'result.json');previous=read(out/'previous-result.json');official=read(out/'official-footprint.json')
    assert r['transform']==previous['transform'],f'Transform unexpectedly changed: {n}'
    assert r['orientationEvidence']==previous['orientationEvidence'],f'Orientation changed: {n}'
    baseline=read(ROOT/f'data/city-one-shatin-approved-job/review-results/tower-{n}/official-footprint.json')
    assert official['geometry']==baseline['geometry'] and r['buildingCsuid']==previous['buildingCsuid']
    s=r['transform'];assert s['scaleMetresPerCanvasPixel']>0 and not s['reflected'] and s['rmsMetres']<=1.5
    transformAudit.append(dict(tower=n,csuid=r['buildingCsuid'],**s,changedFromPrevious=False,officialGeometryUnchanged=True,orientationUnchanged=True))
    origin,factor,q=en_frame(np.array(official['geometry']['rings'][0]));p=apply(np.array(r['annotation']['outline'])*[1,-1],s)
    both=np.vstack([q,p]);lo=both.min(0);hi=both.max(0);scale=1000/max(hi-lo)
    def xy(v):return (np.array([v[0]-lo[0],hi[1]-v[1]])*scale+90).tolist()
    im=Image.new('RGB',(1180,1180),'white');d=ImageDraw.Draw(im)
    d.line([tuple(xy(x)) for x in np.vstack([q,q[0]])],fill='#267cab',width=4)
    d.line([tuple(xy(x)) for x in np.vstack([p,p[0]])],fill='#d58823',width=2)
    d.text((20,20),f'Tower {n} | N ^ | blue LandsD / orange plan / red source windows',fill='black')
    windows=[]
    for w in r['windows']:
        source=np.array(w['sourcePlanSegment']);seg=apply(source*[1,-1],s);ip=apply(np.array([w['interiorWitness']])*[1,-1],s)[0]
        windows.append(dict(flat=w['flat'],id=w['id'],p1=xy(seg[0]),p2=xy(seg[1]),interiorWitness=xy(ip)))
    render(im,windows,[xy(x) for x in p],out/'approved-overlay.png')
    results.append(r)
    index.append(dict(tower=n,familyId=t['familyId'],accepted=len(r['productionWindows']),rejected=len(r['windows'])-len(r['productionWindows']),sourceOverlay=f'review-results/tower-{n}/window-review.png',registrationOverlay=f'review-results/tower-{n}/approved-overlay.png',familyDiff=f'review-results/tower-{n}/family-diff-overlay.png',result=f'review-results/tower-{n}/result.json'))

labels=[]
for path in JOB.rglob('*.labels.json'):
    a=read(path)['labels']
    for i,x in enumerate(a):
        assert x['text'].isascii()
        bx=x['box'];normal=x['outwardNormal'];mid=x['windowMidpoint']
        assert sum((((bx[k]+bx[k+2])/2)-mid[k])*normal[k] for k in range(2))>0
        for y in a[i+1:]:
            by=y['box'];assert bx[2]<by[0] or bx[0]>by[2] or bx[3]<by[1] or bx[1]>by[3],str(path)
    labels.append(str(path.relative_to(JOB)))
familyReports=[]
for f in families:
    rs=[r for r in results if str(r['tower']) in f['members']]
    familyReports.append(dict(familyId=f['familyId'],canonicalTower=f['canonicalTower'],members=f['members'],canonicalCount=len(f['windows']),inheritedCount=sum(len(r['windows']) for r in rs if str(r['tower'])!=f['canonicalTower']),locallyRetracedCount=0,unresolvedCount=sum(1 for i in issues if str(i['tower']) in f['members'] and i.get('room') and isinstance(i['reason'],str)),qaRejectedCount=sum(len(r['windows'])-len(r['productionWindows']) for r in rs),productionCount=sum(len(r['productionWindows']) for r in rs)))
total=sum(len(r['windows']) for r in results);accepted=sum(len(r['productionWindows']) for r in results)
assert accepted==report['productionWindowCount']
doc['status']='source-reviewed-and-geospatial-qa-complete-with-local-exclusions';save(JOB/'canonical-window-traces.json',doc)
report.update(packageVersion='6.2',canonicalWindowCount=sum(len(f['windows']) for f in families),expandedTracedWindowCount=total,qaRejectedWindowCount=total-accepted,unresolvedRoomCount=sum(f['unresolvedCount'] for f in familyReports),families=familyReports,transformsReusedUnchanged=52,previousProductionWindowCount=read(ROOT/'data/city-one-shatin-approved-job/processing-report.json')['productionWindowCount'],completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),fullyExcludedTowers=[],fullyPassingTowers=[r['tower'] for r in results if len(r['windows'])==len(r['productionWindows'])],partiallyImportedTowers=[r['tower'] for r in results if len(r['windows'])!=len(r['productionWindows'])],sourcePolicy='All 52 approved cached images hash-checked. Four approved samples used semantically. No new source/CSUID/orientation search.',sourceEndpointCorrections=[{'family':'COS-F06','flats':['C','F'],'room':'bedroom-1','reason':'Magnified source inspection tightened the visible glazing opening to exclude adjacent thick jamb; no government snapping.'}])
save(JOB/'transform-audit.json',transformAudit);save(JOB/'review-index.json',index)
save(JOB/'canonical-snap-report.json',{'sourceEndpointsPreserved':True,'snappedToGovernmentPolygon':False,'samplePixelsUsedAsCoordinates':False,'method':'Trace source glazing or primary bay face; project facade separately; camera may offset outward within existing QA thresholds.','corrections':report['sourceEndpointCorrections']})
summary={'status':'pass-with-local-exclusions','towerCount':52,'canonicalCount':14,'canonicalWindows':doc['tracedWindowCount'],'expandedWindows':total,'productionWindows':accepted,'qaRejectedWindows':total-accepted,'unresolvedRooms':report['unresolvedRoomCount'],'floorIssues':len([i for i in issues if not i.get('room')]),'unchangedTransforms':52,'maxRmseMetres':max(t['rmsMetres'] for t in transformAudit),'calloutArtifactsChecked':len(labels),'calloutCollisions':0}
save(JOB/'validation-summary.json',summary)
timings=read(JOB/'processing-timings.json');timings['stages']=[{'stage':'source-cache-intake','seconds':intake.get('seconds'),'status':'reused-and-hash-checked'},{'stage':'source-parsing-and-family-verification','seconds':read(JOB/'prepare-timing.json')['seconds']},{'stage':'canonical-trace-artifact-generation','seconds':read(JOB/'trace-timing.json')['seconds']},{'stage':'visual-source-review','seconds':None,'status':'completed; duration not instrumented'},{'stage':'registration','seconds':0,'status':'52 prior transforms reused unchanged; no optimizer run'},{'stage':'inheritance-window-normal-qa-and-review-rendering','seconds':timings['processingSeconds']},{'stage':'final-audit-and-registration-callouts','seconds':time.perf_counter()-start}];save(JOB/'processing-timings.json',timings)
changed=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines();report['filesChanged']=changed
if (JOB/'tests.log').exists():
    text=(JOB/'tests.log').read_text();passed=re.search(r'# pass (\d+)',text);failed=re.search(r'# fail (\d+)',text);duration=re.search(r'# duration_ms ([\d.]+)',text)
    report['tests']={'command':'npm test','passed':int(passed[1]) if passed else None,'failed':int(failed[1]) if failed else None,'log':'tests.log'}
    assert report['tests']['passed'] and report['tests']['failed']==0
    timings['stages'].append({'stage':'tests','seconds':float(duration[1])/1000 if duration else None,'status':'pass'})
if (JOB/'build.log').exists():
    text=(JOB/'build.log').read_text();assert 'built in' in text
    report['build']={'command':'npm run build','status':'pass','log':'build.log'}
    timings['stages'].append({'stage':'build','status':'pass','durationSource':'build.log'})
save(JOB/'processing-timings.json',timings)
save(JOB/'processing-report.json',report)
data={'version':'6.2','summary':summary,'families':familyReports,'towers':index,'issues':issues}
(JOB/'review-data.js').write_text('window.REVIEW_DATA = '+json.dumps(data,ensure_ascii=False)+';\n')
# Preserve the supplied authoring UI; this generated read-only review is served locally.
if not (JOB/'package-index.html').exists():(JOB/'index.html').rename(JOB/'package-index.html')
(JOB/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>City One v6.2 review</title>
<style>body{font:16px system-ui;margin:32px;background:#f2f6f8;color:#16323b}header{position:sticky;top:0;background:#f2f6f8;padding:12px;z-index:1}select{font:inherit;padding:8px}main{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%;background:white}article{background:white;padding:16px}a{color:#116d8a}pre{white-space:pre-wrap}h2{font-size:18px}</style>
<header><h1>City One Shatin — v6.2 review</h1><p id="summary"></p><label>Tower <select id="tower"></select></label> <a href="processing-report.json">Report</a> · <a href="needs-review.json">Needs review</a> · <a href="processing.log">Log</a></header>
<main><article><h2>Source windows — English outward callouts</h2><a id="source-link"><img id="source"></a></article><article><h2>Independent LandsD registration</h2><a id="registration-link"><img id="registration"></a></article><article><h2>Family structural difference + inherited windows</h2><img id="diff"></article><article><h2>Local QA exclusions</h2><pre id="issues"></pre></article></main>
<script src="review-data.js"></script><script>const D=window.REVIEW_DATA,s=document.querySelector('#tower');document.querySelector('#summary').textContent=`${D.summary.towerCount} towers · ${D.summary.productionWindows} production windows · ${D.summary.qaRejectedWindows} local QA exclusions`;for(const t of D.towers){s.add(new Option(`Tower ${t.tower} — ${t.accepted} accepted / ${t.rejected} review`,t.tower))}function show(){const t=D.towers.find(t=>t.tower===Number(s.value));for(const [id,path] of [['source',t.sourceOverlay],['registration',t.registrationOverlay],['diff',t.familyDiff]]){document.getElementById(id).src=path;const a=document.getElementById(id+'-link');if(a)a.href=path}document.querySelector('#issues').textContent=JSON.stringify(D.issues.filter(i=>i.tower===t.tower),null,2)}s.onchange=show;show();</script>''')
with (JOB/'processing.log').open('a') as log:log.write(json.dumps({'stage':'final-artifact-audit','summary':summary})+'\n')
print(json.dumps(summary,indent=2))
