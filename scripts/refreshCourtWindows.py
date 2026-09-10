"""Reproject reviewed sill-line windows, preserving all six existing placements."""
import json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
apply,en_frame,inside=[scope[k] for k in ['apply','en_frame','inside']]
annotation=json.loads((ROOT/'data/chestwood-tower-2/annotations.json').read_text())
rooms=annotation['rooms']
court=sys.argv[1];assert court in ('sherwood','lynwood')
phase,count=(2,6) if court=='sherwood' else (5,10)
for tower in range(1,count+1):
 out=ROOT/f'data/{court}-tower-{tower}'
 result=json.loads((out/'result.json').read_text())
 best=result['transform']
 footprint=f'data/kingswood-footprints/phase-{phase}-tower-{tower}-official-footprint.json'
 official=json.loads((ROOT/footprint).read_text())
 ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
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

 assert all(w['cameraOutside'] for w in windows)
 assert len(windows)==30
 result['windows']=windows
 result['annotation']={**result['annotation'],**annotation,'placementMethod':'Existing tower transform preserved; reviewed sill-line template reprojected'}
 result['verification']='Sill lines visually reviewed on published plan; georeferencing remains derived, not surveyed.'
 (out/'result.json').write_text(json.dumps(result,indent=2))
 (out/'annotations.json').write_text(json.dumps(result['annotation'],indent=2))
 print(tower,len(windows),sum(w['cameraOutside'] for w in windows))
