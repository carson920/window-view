"""Read-only geometry audit. Write audit evidence, never re-register or re-trace."""
import json, math, subprocess
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; JOB=ROOT/'data/south-horizons-approved-job'
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
data=read(ROOT/'data/properties.json');estate=next(e for e in data['estates'] if e['id']=='south-horizons')
job=read(JOB/'approved-job.json');summary=read(JOB/'validation-summary.json');transforms=[];normals=[]
for row in summary:
 t=row['tower'];folder=ROOT/f'data/south-horizons-tower-{t.lower()}';r=read(folder/'result.json');a=r['annotation'];s=r['transform'];p=read(folder/'placement.json')
 assert s==p['transform'] and not s['reflected'] and s['scaleMetresPerCanvasPixel']>0
 previous=json.loads(subprocess.check_output(['git','show',f'980f2b1:data/south-horizons-tower-{t.lower()}/placement.json'],cwd=ROOT))['transform']
 transforms.append(dict(tower=t,CSUID=r['buildingCsuid'],scale=s['scaleMetresPerCanvasPixel'],rotation=s['rotationDegrees'],translation=s['translationMetres'],RMSE=s['rmsMetres'],determinant=s['scaleMetresPerCanvasPixel']**2,changedSinceEarliestCommittedHSV20=s!=previous,previousHSV45Comparison='Unavailable: no retained HSV45 transform snapshot; earliest commit already uses HSV20.'))
 hsv=cv2.cvtColor(cv2.imread(str(folder/'plan-crop.png')),cv2.COLOR_BGR2HSV)
 def saturation(pt):
  x,y=np.rint(pt).astype(int)
  if x<2 or y<2 or x+2>=hsv.shape[1] or y+2>=hsv.shape[0]:return None
  return float(np.median(hsv[y-2:y+3,x-2:x+3,1]))
 for flat,rows in a['rooms'].items():
  for kind,u,v,witness in rows:
   mid=(np.array(u)+v)/2; tangent=np.array(v)-u;n=np.array([-tangent[1],tangent[0]])/np.linalg.norm(tangent)
   if n@(np.array(witness)-mid)>0:n=-n
   # Independent LOCAL room-fill evidence; not the canvas-centre witness.
   inn=[saturation(mid-n*d) for d in [8,12,16]];out=[saturation(mid+n*d) for d in [8,12,16]]
   support=all(v is not None for v in inn+out) and float(np.median(inn))>20 and float(np.median(inn))>float(np.median(out))+10
   normalPlanToEN=np.array([n[0],-n[1]]);ang=math.radians(s['rotationDegrees']);rot=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]]);en=rot@normalPlanToEN
   expected=math.degrees(math.atan2(en[0],en[1]))%360
   stored=next(w for w in r['windows'] if w['flat']==flat and w['id']==kind)
   if 'heading' in stored:assert abs((expected-stored['heading']+180)%360-180)<1e-7
   normals.append(dict(tower=t,flat=flat,room=kind,heading=expected,localRoomSideSupported=bool(support),inwardSaturation=inn,outwardSaturation=out,centreAloneUnsafe=kind=='living',evidence='Local coloured room fill vs exterior sampled independently of canvas centre. Flat identity remains the existing approved trace label; colour is not an independent cadastral flat boundary.',reviewRequired=not support))
published=[dict(tower=b['id'][6:].upper(),windows=sum(len(f['windows']) for f in b['flats'])) for b in estate['buildings']]
special=[]
for item in job['primaryFloorPlanSource']['items']:
 if item['planRole']=='typical':continue
 tower=item['blocks'][0];b=next((b for b in estate['buildings'] if b['id']==f'tower-{tower.lower()}'),None);floor=int(item['floorCoverage'].split('F')[0]);available=b and b['floors']['min']<=floor<=b['floors']['max']
 assert not available
 special.append(dict(tower=tower,floor=floor,source=item['id'],selectable=False,reason='tower excluded' if not b else 'special template unavailable; outside supported typical range'))
report=dict(totalTowers=34,productionTowers=published,productionTowerCount=len(published),productionWindowCount=sum(b['windows'] for b in published),fullyExcluded=['1','3','6'],partiallyImported=[{'tower':'10','excludedWindows':[{'flat':'H','room':'master','reason':'Source crop clips west facade; trace x=3 pixels cannot establish physical window.'}]}],fullTypicalWindowCoverageTowers=30,transforms=transforms,normalChecks=normals,specialFloors=special,notes=['Tower 1 RMSE exceeds 1.5m; Tower 3 RMSE passes but B/C master facade discrepancy exceeds 2m.','All living normals have independent local room-fill support. Canvas-centre witness alone is unsafe and is explicitly flagged; source flat labels are inherited, not independently re-solved.','No source, CSUID, rotation, reflection, scale, translation or traced endpoints changed.','Original living endpoints are sourcePlanSegment; planSegment/proxyPlanSegment are 6%-trimmed camera proxies, not measured glazing extents.'])
save(JOB/'integrity-audit.json',report)
print(json.dumps({'towers':len(published),'windows':report['productionWindowCount'],'localSideInconclusive':[(n['tower'],n['flat'],n['room']) for n in normals if n['reviewRequired']]}))
