"""Lynwood 1–10: reuse confirmed Chestwood template with plan-verified grouping."""
import json, math, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
tower=int(sys.argv[1]);assert tower in tuple(range(1,11))
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,solve,apply,en_frame,inside=[scope[k] for k in ['sample','solve','apply','en_frame','inside']]
# Reuse confirmed Tower 2 segments unchanged; mirror the entire template.
annotation2=json.loads((ROOT/'data/chestwood-tower-2/annotations.json').read_text())
outline=annotation2['outline'];rooms=annotation2['rooms']
out=ROOT/f'data/lynwood-tower-{tower}';out.mkdir(exist_ok=True)
annotation={'templateSource':'data/chestwood-tower-2/annotations.json','placementMethod':f'User-confirmed Tower 2 template fitted to Tower {tower} official footprint; reflected={tower in (1,2,4,6,8)}','canvas':[1464,1696],'outline':outline,'rooms':rooms,'source':'https://i1.28hse.com/estate_data/108/4390/FLOOR/4390_20231121230203211831_large.jpg','layoutSource':('https://i1.28hse.com/estate_data/108/4390/FLOOR/4390_20231121230348928362_large.jpg' if tower in (1,2,4,6,8) else 'https://i1.28hse.com/estate_data/108/4390/FLOOR/4390_20231121230358668751_large.jpg'),'sourceAuthority':'28Hse published plan; developer-original provenance not established','mapping':'Lynwood groups 1/2/4/6/8 and 3/5/7/9/10 are mirrors. A–H and room ordering retained from confirmed Chestwood template; orientation solved in local metres.'}
(out/'annotations.json').write_text(json.dumps(annotation,indent=2))
official=json.loads((ROOT/f'data/kingswood-footprints/phase-5-tower-{tower}-official-footprint.json').read_text())
ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
poly=np.array(outline)*[1,-1]
solutions=solve(sample(poly),sample(q),reflected=tower in (1,2,4,6,8));best=solutions[0]
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
