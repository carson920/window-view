"""Approved Laguna ingestion using the existing metre-frame ICP pipeline.
Run from any directory; only QA-passing results are offered to the importer.
"""
import json,sys,copy,hashlib,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];JOB=ROOT/'data/laguna-approved-job'
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,solve,apply,en_frame,inside=[scope[k] for k in ['sample','solve','apply','en_frame','inside']]
def read(p):return json.loads(p.read_text())
def save(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
job=read(JOB/'approved-job.json');rawfile=ROOT/'data/laguna-tower-1/court-query.raw.json';raw=read(rawfile)
query=read(ROOT/'data/laguna-tower-1/official-footprint.json')['provenance']['queryUrl']
# Coarse compass sectors transcribed from the approved NORTH-UP screenshot.
# These are stack position bearings, NOT facade headings, lat/lng or distances.
patterns={name:dict(zip('ABCDEFGH',values)) for name,values in {
 'odd':[0,45,90,135,180,225,270,315],
 'even':[315,270,225,180,135,90,45,0],
 'swOdd':[270,315,0,45,90,135,180,225],
 'swEven':[225,180,135,90,45,0,315,270],
 'south':[180,225,270,315,0,45,90,135],
 'se':[135,90,45,0,315,270,225,180]}.items()}
groups={'odd':[1,3,5,7,9,11,16,18,29,34,35,37],'even':[2,4,6,8,10,12,17,19,30,31,36,38],'swOdd':[13,27,32],'swEven':[14,15,28,33],'south':[21,23,24],'se':[20,22,25,26]}
anchors={str(t):{'bearings':patterns[k],'toleranceDegrees':40,'evidence':'data/laguna-approved-job/orientation/centamap-overview-1.png','northUp':True,'method':'Visible A-H labels transcribed to coarse compass sectors; north-up per user convention; not measurement coordinates.'} for k,ts in groups.items() for t in ts}
save(JOB/'orientation/anchors.json',anchors)
def angular(a,b):return abs((a-b+180)%360-180)
def semantic(a,s,t):
 core=apply(np.array([a['core']])*[1,-1],s)[0];errors={}
 for flat,target in anchors[str(t)]['bearings'].items():
  rows=a['rooms'][flat];p=np.mean([row[3] for row in rows],axis=0)
  d=apply(np.array([p])*[1,-1],s)[0]-core
  bearing=float(np.degrees(np.arctan2(d[0],d[1]))%360);errors[flat]={'expectedSector':target,'bearing':bearing,'error':angular(bearing,target)}
 return errors
def normal_windows(a,s,q,origin,factor):
 windows=[]
 for flat,rows in a['rooms'].items():
  for kind,p1,p2,interior in rows:
   seg=apply(np.array([p1,p2])*[1,-1],s);mid=seg.mean(0);tangent=seg[1]-seg[0]
   n=np.array([-tangent[1],tangent[0]])/np.linalg.norm(tangent);ip=apply(np.array([interior])*[1,-1],s)[0]
   if np.dot(n,ip-mid)>0:n=-n
   hits=[]
   for p,b in zip(q,np.roll(q,-1,axis=0)):
    mat=np.column_stack([n,p-b])
    if abs(np.linalg.det(mat))<1e-9:continue
    distance,u=np.linalg.solve(mat,p-mid)
    if 0<=u<=1:hits.append(float(distance))
   if not hits:windows.append({'flat':flat,'id':kind,'qaErrors':['normal has no footprint intersection']});continue
   distance=min(hits,key=abs);projected=mid+distance*n;offset=max(1,distance+.5);camera=mid+n*offset
   qa=[]
   if inside(camera,q):qa.append('camera inside official polygon; do not push through unrelated facade')
   if inside(camera+n*2,q):qa.append('forward ray enters building within two metres')
   if abs(distance)>2:qa.append('window-to-facade discrepancy exceeds 2 metres')
   if offset>3:qa.append('outward correction exceeds 3 metres')
   ll=origin+mid/factor;cll=origin+camera/factor;pll=origin+projected/factor
   w=dict(flat=flat,id=kind,lat=float(ll[1]),lng=float(ll[0]),cameraLat=float(cll[1]),cameraLng=float(cll[0]),heading=float(np.degrees(np.arctan2(n[0],n[1]))%360),projectedFacadeLat=float(pll[1]),projectedFacadeLng=float(pll[0]),facadeDistanceMeters=distance,cameraOffsetMetres=offset,interiorNormalDot=float(np.dot(n,ip-mid)),cameraOutside=not inside(camera,q),windowVerified=False,georefVerified=False,confidence='review',planSegment=[p1,p2],qaErrors=qa)
   if kind=='bedroom-1' and a.get('cornerGlazing',{}).get(flat):w.update(cornerGlazingPlanPoints=a['cornerGlazing'][flat],viewGeometry='corner-window-outer-endpoint-chord')
   windows.append(w)
 return windows
def draw_overlay(out,a,s,q,ws):
 p=apply(np.array(a['outline'])*[1,-1],s);both=np.vstack([q,p]);lo=both.min(0);hi=both.max(0);scale=min(780/(hi-lo)[0],780/(hi-lo)[1])
 def xy(v):return tuple((np.array([v[0]-lo[0],hi[1]-v[1]])*scale+60).tolist())
 im=Image.new('RGB',(900,900),'white');d=ImageDraw.Draw(im)
 d.line([xy(v) for v in np.vstack([q,q[0]])],fill='blue',width=4);d.line([xy(v) for v in np.vstack([p,p[0]])],fill='orange',width=2)
 for f,rows in a['rooms'].items():
  for kind,x,y,interior in rows:
   seg=apply(np.array([x,y])*[1,-1],s);mid=seg.mean(0);ip=apply(np.array([interior])*[1,-1],s)[0];v=seg[1]-seg[0];n=np.array([-v[1],v[0]])/np.linalg.norm(v)
   if np.dot(n,ip-mid)>0:n=-n
   d.line([xy(seg[0]),xy(seg[1])],fill='red',width=3);d.line([xy(mid),xy(mid+n*2)],fill='green',width=2);d.text(xy(mid),f+'/'+kind,fill='black')
 d.text((20,20),'N ^ | blue official; orange plan; red glazing; green outward',fill='black');im.save(out/'approved-overlay.png')
reports=[];review=[]
selected=[int(t) for t in sys.argv[1:]] or list(range(1,39))
for tower in selected:
 out=ROOT/f'data/laguna-tower-{tower}';out.mkdir(exist_ok=True)
 sheet=next(i for i in job['primaryFloorPlanSource']['items'] if str(tower) in i['blocks'])['id'];template=sheet
 template={1:'L01-special',13:'L01-special',15:'L02-special',20:'L11-special',25:'L04-standard',30:'L04-standard',32:'L05-special',34:'L05-special',33:'L06-special'}.get(tower,template)
 a=read(JOB/f'templates/{template}.json');a['templateId']=template
 matches=[f for f in raw['features'] if f['attributes'].get('BuildingNameEN')==f'Laguna City Block {tower}']
 if len(matches)!=1:review.append({'tower':tower,'reason':'Official exact name not unique','count':len(matches)});continue
 official=copy.deepcopy(matches[0]);official['provenance']={'source':'LandsD CSDI Building FSDT','queryUrl':query,'rawFile':str(rawfile.relative_to(ROOT)),'rawSha256':hashlib.sha256(rawfile.read_bytes()).hexdigest(),'outputCRS':'EPSG:4326','selectionRule':'unique exact BuildingNameEN Laguna City Block N; independent official polygon'}
 save(out/'official-footprint.json',official);ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
 key=hashlib.sha256(json.dumps([a['outline'],ring.tolist()]).encode()).hexdigest();cache=out/'approved-candidates.json'
 previous=read(cache) if cache.exists() else {}
 if previous.get('inputSha256')==key:solutions=previous['candidates']
 else:
  p=sample(np.array(a['outline'])*[1,-1]);dest=sample(q)
  solutions=solve(p,dest)+solve(p,dest,True);save(cache,{'inputSha256':key,'candidates':solutions})
 for s in solutions:s['semanticErrors']=semantic(a,s,tower);s['semanticPass']=all(v['error']<=40 for v in s['semanticErrors'].values())
 candidates=[s for s in solutions if s['semanticPass'] and s['rmsMetres']<1.5]
 errors=[]
 if not candidates:errors.append('No solution passes BOTH semantic compass anchors and 1.5m symmetric RMSE')
 # Near-equivalent optimizer results are one placement; distinct acceptable
 # rotations or handedness remain unresolved rather than using RMS to choose.
 if candidates:
  best=min(candidates,key=lambda s:s['rmsMetres'])
  if any(s['reflected']!=best['reflected'] or angular(s['rotationDegrees'],best['rotationDegrees'])>10 for s in candidates):errors.append('More than one distinct placement passes semantic constraints')
 else:best=min(solutions,key=lambda s:sum(v['error'] for v in s['semanticErrors'].values()))
 windows=normal_windows(a,best,q,origin,factor)
 for w in windows:
  if w['qaErrors']:errors.append(w['flat']+'/'+w['id']+': '+', '.join(w['qaErrors']))
 result={'tower':tower,'buildingCsuid':official['attributes']['BuildingCSUID'],'origin':origin.tolist(),'coordinateFrame':'local WGS84 ellipsoid east/north metres','transform':best,'candidates':solutions,'windows':windows,'annotation':a,'orientationEvidence':anchors[str(tower)],'approvedJob':'data/laguna-approved-job/approved-job.json','qa':{'pass':not errors,'errors':errors,'method':'symmetric boundary ICP + Powell; 72 rotation starts each handedness; semantic compass constraints; room-side normal; official polygon point-in-polygon and 2m forward probe','limits':{'rmseMetres':1.5,'facadeDiscrepancyMetres':2,'maxOffsetMetres':3}},'confidenceDimensions':{'planInterpretation':'visually-traced-approved-primary','horizontalGeoreferencing':'derived-plan-to-official-footprint' if not errors else 'needs-review','windowSemantics':'derived-from-room-side-witness','verticalGeometry':'building-average estimate; floor range must have source'}}
 save(out/'approved-result.json',result);draw_overlay(out,a,best,q,windows)
 report={'tower':tower,'template':template,'sourceSheet':sheet,'csuid':result['buildingCsuid'],'rotation':best['rotationDegrees'],'reflection':best['reflected'],'scale':best['scaleMetresPerCanvasPixel'],'rmse':best['rmsMetres'],'windows':len(windows),'qaPass':not errors,'errors':errors}
 reports.append(report)
 if errors:review.append({'tower':tower,'family':template,'candidateSolutions':solutions,'evidence':[str((out/'approved-overlay.png').relative_to(ROOT)),a['source'],anchors[str(tower)]['evidence']],'reason':errors,'humanDecisionNeeded':'Resolve listed source variant/window interpretation or orientation conflict; no coordinates guessed.'})
 print(tower,template,round(best['rmsMetres'],3),best['reflected'],round(best['rotationDegrees'],1),'PASS' if not errors else errors,flush=True)
 save(JOB/'registration-summary.json',reports);save(ROOT/'needs-review.json',review)
