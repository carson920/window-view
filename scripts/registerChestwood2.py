"""Tower 2: independent tracing of the labelled 2/4/6 plan, same ICP solver."""
import json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,solve,apply,en_frame,inside=[scope[k] for k in ['sample','solve','apply','en_frame','inside']]
annotation=json.loads((ROOT/'data/chestwood-tower-2/annotations.json').read_text())
outline=annotation['outline'];rooms=annotation['rooms']
out=ROOT/'data/chestwood-tower-2';out.mkdir(exist_ok=True)

(out/'annotations.json').write_text(json.dumps(annotation,indent=2))
official=json.loads((ROOT/'data/kingswood-footprints/phase-3-tower-2-official-footprint.json').read_text())
ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
poly=np.array(outline)*[1,-1]
solutions=solve(sample(poly),sample(q));best=solutions[0]
windows=[]
for flat,items in rooms.items():
 for kind,a,b,interior in items:
  seg=apply(np.array([a,b])*[1,-1],best);mid=seg.mean(0);t=seg[1]-seg[0];n=np.array([-t[1],t[0]])/np.linalg.norm(t)
  ip=apply(np.array([interior])*[1,-1],best)[0]
  if np.dot(n,ip-mid)>0:n=-n
  hits=[]
  for a,b in zip(q,np.roll(q,-1,axis=0)):
   mat=np.column_stack([n,a-b])
   if abs(np.linalg.det(mat))<1e-9:continue
   distance,u=np.linalg.solve(mat,a-mid)
   if 0<=u<=1:hits.append(float(distance))
  distance=min(hits,key=abs) if hits else None
  projected=mid+distance*n if distance is not None else None
  camera=mid+n*max(1,(distance or 0)+.5)
  ll=origin+mid/factor;cll=origin+camera/factor;pll=origin+projected/factor if projected is not None else [None,None]
  windows.append(dict(flat=flat,id=kind,lat=float(ll[1]),lng=float(ll[0]),cameraLat=float(cll[1]),cameraLng=float(cll[0]),heading=float(np.degrees(np.arctan2(n[0],n[1]))%360),projectedFacadeLat=pll[1],projectedFacadeLng=pll[0],facadeDistanceMeters=distance,windowVerified=False,georefVerified=False,confidence='review',interiorNormalDot=float(np.dot(n,ip-mid)),cameraOutside=not inside(camera,q)))
result=dict(buildingCsuid=official['attributes']['BuildingCSUID'],origin=origin.tolist(),transform=best,candidates=solutions,windows=windows,annotation=annotation,verification='Human tracing on published raster; source authority and independent real-world orientation remain review.')
(out/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'transform':best,'windows':len(windows),'outside':sum(w['cameraOutside'] for w in windows)}),flush=True)
