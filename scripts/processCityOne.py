"""Reuse screenshot-fixed South Horizons registration and existing window-normal QA.
No angle enumeration, no reflection, no alternate source discovery.
"""
from annotateCityOne import ROOT,JOB,read,save
from registerSouthHorizons import fit,apply,en_frame,inside
import ast,copy,hashlib,time,re
import numpy as np
from cityOneReview import render
from PIL import Image,ImageDraw
# Reuse the established downstream functions without executing Laguna's source search.
module=ast.parse((ROOT/'scripts/processLagunaApproved.py').read_text());selected=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['normal_windows','draw_overlay']];exec(compile(ast.Module(body=selected,type_ignores=[]),'existing-window-qa','exec'))
ANGLES={n:-45 for n in range(1,53)}
for n in [5,6,15,33]:ANGLES[n]=45
for n in [13,14]:ANGLES[n]=-135
for n in [8,9,10,16,17,18,21,22]:ANGLES[n]=135
# First distinctive flat in approved NORTH-UP image. Coordinates are NOT used for positioning.
ANCHORS={**{n:'E northeast; A southwest' for n in [1,2,3,20,23,24,26,30,31,32]},**{n:'A northeast; E southwest' for n in [8,9,10,16,17,21]},**{n:'D northwest; A southwest' for n in [7,11,12]},**{n:'C north; A south' for n in [4,25,27,28]},**{n:'D north; B south' for n in [5,6,15,33]},**{n:'B north; D south' for n in [13,14,34,35]},**{n:'A northeast; D southwest' for n in [18,22]},**{n:'A northeast; E southwest' for n in [19,29,36]},**{n:'G northeast; C southwest' for n in [37,38,39,40,41,46,47,48]},**{n:'C northeast; G southwest' for n in [42,43,44,45,49,50,51,52]}}
def expected(f):
 c=int(f['canonicalTower']);flats='ABCD' if c in [4,25,27,34] else 'ABCDEF' if c in [7,18] else 'ABCDEFGH'
 def beds(k):return 2 if c in [37,42] or (c in [1,8,16,30] and k in 'CDGH') or (c in [19,36] and k in 'CDGH') else 3
 return {k:['living']+[f'bedroom-{i+1}' for i in range(beds(k))] for k in flats}
if __name__=='__main__':
 start=time.perf_counter();doc=read(JOB/'canonical-window-traces.json');families=doc['families'];verification=read(JOB/'family-verification.json');job=read(JOB/'approved-job.json');raw=read(JOB/'official-query.raw.json');prov=read(JOB/'official-query-provenance.json');reports=[];issues=[];stages=[]
 for n in range(1,53):
  tick=time.perf_counter();f=next(f for f in families if str(n) in f['members']);v=next(v for v in verification if v['tower']==str(n));out=JOB/f'review-results/tower-{n}';out.mkdir(parents=True,exist_ok=True);sheet=next(i for i in job['primaryFloorPlanSource']['items'] if str(n) in i['blocks']);matches=[a for a in raw['features'] if a['attributes'].get('BuildingNameEN')==f'City One Shatin Block {n}']
  if len(matches)!=1:issues.append(dict(tower=n,reason='official exact-name identity is not unique'));continue
  o=copy.deepcopy(matches[0]);o['provenance']={'source':'LandsD CSDI Building FSDT','queryUrl':prov.get('url',prov.get('queryUrl')),'rawFile':str((JOB/'official-query.raw.json').relative_to(ROOT)),'rawSha256':hashlib.sha256((JOB/'official-query.raw.json').read_bytes()).hexdigest(),'outputCRS':'EPSG:4326','selectionRule':'Previously approved unique exact City One Shatin Block N; no new identity/orientation solving'};save(out/'official-footprint.json',o)
  rooms={k:[] for k in expected(f)}
  for w in f['windows']:rooms[w['flat']].append([w['id'],w['p1'],w['p2'],w['interiorWitness']])
  a={'rooms':rooms,'outline':f['outline'],'source':sheet['previewUrl'],'sourcePage':job['primaryFloorPlanSource']['sourcePage'],'sourceId':sheet['id'],'sourceImageSize':f['sourceImageSize'],'templateId':f['familyId'],'extractionMethod':'Approved v6.2 glazing and projected-bay dominant straight faces; source endpoints retained, room-specific interior witnesses, no whole-bay perimeter or AC ledge substitution.'};save(out/'annotations.json',a)
  cache=out/'result.json'
  previous=read(cache) if cache.exists() else None
  if previous and previous['annotation']['outline']==a['outline'] and previous['transform']['rotationDegrees']==ANGLES[n]:
   s=previous['transform'];origin,factor,q=en_frame(np.array(o['geometry']['rings'][0]))
  else:
   if (out/'previous-result.json').exists():raise ValueError(f'Unexpected change to approved registration inputs: tower {n}')
   s,origin,factor,q=fit(a,o,ANGLES[n])
  ws=normal_windows(a,s,q,origin,factor);transformPass=v['pass_'] and s['rmsMetres']<=1.5 and s['scaleMetresPerCanvasPixel']>0
  orient={'sourceFile':'orientation/u-1789269525652-jpv0zf.png','northUp':True,'anchor':ANCHORS[n],'fixedRotationDegrees':ANGLES[n],'method':'Visual semantic label correspondence; image pixels used for direction only'}
  accepted=[]
  for w in ws:
   trace=next(x for x in f['windows'] if x['flat']==w['flat'] and x['id']==w['id'])
   w.update(planSegment=[trace['p1'],trace['p2']],interiorWitness=trace['interiorWitness'],representationClass=trace.get('representationClass','sill-line'),recognitionEvidence=trace.get('recognitionEvidence'),sourceExtentRole=trace['sourceExtentRole'])
   w.update(sourcePlanSegment=w.get('planSegment'),sourceImage=sheet['previewUrl'],sourceSha256=hashlib.sha256((JOB/f'floorplans/H-{n}-typ.jpg').read_bytes()).hexdigest(),windowVerified=True,georefVerified=bool(transformPass and not w['qaErrors']),confidence='derived-source-registration' if transformPass and not w['qaErrors'] else 'review')
   if w['georefVerified']:accepted.append(w)
   else:issues.append(dict(tower=n,flat=w['flat'],room=w['id'],reason=w['qaErrors'] or ['tower transform failed'],evidence=f'review-results/tower-{n}/approved-overlay.png',requiredDecision='Resolve the specific source/facade discrepancy before publishing this window'))
  for flat,ids in expected(f).items():
   for kind in ids:
    if any(w['flat']==flat and w['id']==kind for w in ws):continue
    issues.append(dict(tower=n,flat=flat,room=kind,reason='No unambiguous glazing or approved projected-bay primary face identified for this room',evidence=sheet['previewUrl'],requiredDecision='Identify main glazing or supported bay face on the approved source'))
  if not transformPass:issues.append(dict(tower=n,flat=None,room=None,reason='registration RMSE exceeds 1.5m or family validation failed',rmse=s['rmsMetres']))
  floors=list(map(int,re.findall(r'\d+',sheet['floorCoverage'])[:2]));floors=floors if len(floors)==2 else [floors[0],floors[0]]
  if n==8:issues.append(dict(tower=8,flat=None,room=None,reason='Source centre says 1–27/F; approved footer says 1–30/F. Floors 28–30 withheld pending reconciliation'));floors=[1,27]
  result=dict(tower=n,buildingCsuid=o['attributes'].get('BuildingCSUID',o['attributes'].get('CSUID')),transform=s,origin=origin.tolist(),factor=factor.tolist(),annotation=a,orientationEvidence=orient,windows=ws,productionWindows=accepted,floors=floors,qa={'transformPass':transformPass,'acceptedWindows':len(accepted),'rejectedWindows':len(ws)-len(accepted)},confidenceDimensions={'plan':'clear-runs-visually-reviewed; unresolved rooms excluded','horizontal':'independently-registered-to-LandsD','vertical':'building-average-estimate'})
  result['confidenceDimensions']['plan']='source glazing / approved bay-face visual review; window-level exclusions'
  result['registrationReusedUnchanged']=bool(previous and previous['transform']==s)
  save(out/'result.json',result);draw_overlay(out,a,s,q,ws)
  render(JOB/f'floorplans/H-{n}-typ.jpg',f['windows'],f['outline'],out/'window-review.png')
  render(out/'family-diff-overlay.png',f['windows'],f['outline'],out/'family-diff-overlay.png')
  if str(n)==f['canonicalTower']:render(JOB/f'floorplans/H-{n}-typ.jpg',f['windows'],f['outline'],JOB/f'canonical/{f["familyId"]}/source-trace-overlay.png')
  reports.append(dict(tower=n,csuid=result['buildingCsuid'],familyId=f['familyId'],**s,productionWindowCount=len(accepted),tracedWindowCount=len(ws),transformPass=transformPass,floors=floors,seconds=time.perf_counter()-tick));print(n,round(s['rmsMetres'],3),len(accepted),'/',len(ws),flush=True)
 save(JOB/'needs-review.json',issues);save(JOB/'processing-report.json',{'estate':'city-one-shatin','status':'processed-with-local-exclusions','towersProcessed':len(reports),'towersRepresented':sum(r['productionWindowCount']>0 for r in reports),'productionWindowCount':sum(r['productionWindowCount'] for r in reports),'geometryFamiliesConfirmed':len(families),'towers':reports,'reviewItemCount':len(issues),'policy':'Only window-level passing outputs imported; unresolved source windows excluded; no symmetry search'})
 save(JOB/'processing-timings.json',{'processingSeconds':time.perf_counter()-start,'perTower':[{k:r[k] for k in ['tower','seconds']} for r in reports],'notes':'Source-fetch, preparation and trace rendering timed separately. Human/visual inspection time not retroactively invented.'})
