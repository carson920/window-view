"""Fit the confirmed window template to every independent official tower footprint.
Published plan group headings and A–H labels determine reflection and renaming.
"""
import json, sys, copy, re
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,solve,apply,en_frame,inside=[scope[k] for k in ['sample','solve','apply','en_frame','inside']]
CONFIG={1:('locwood',[35,35,32,32,28,28,27,27,28,28,32,32,35,35],list(range(8,15)),['4390_20231121230230576395','4390_20231121230301972753']),6:('maywood',[38,38,37,36,35,35,32,32],[1,3,5,7],['4390_20231121230027776835','4390_20231121230032611258']),7:('kenswood',[31,33,33,35,35,37,37,37,37,35,35,33,33,31],[1,2,4,6,8,10,12],['4390_20231121230105128449','4390_20231121230100585649'])}
summary=[]
for phase,(court,floors,mirrors,assets) in CONFIG.items():
 rawfile=f'data/kingswood-footprints/phase-{phase}-court-query.raw.json'
 raw=json.loads((ROOT/rawfile).read_text())
 for tower,maxfloor in enumerate(floors,1):
  target=ROOT/f'data/{court}-tower-{tower}';target.mkdir(exist_ok=True)
  matches=[f for f in raw['response']['features'] if re.search(r'Block '+str(tower)+r'$',f['attributes']['BuildingNameEN'])]
  assert len(matches)==1,(phase,tower,len(matches))
  official=copy.deepcopy(matches[0]);official['provenance']={'source':'LandsD CSDI Building FSDT','queryUrl':raw['queryUrl'],'rawFile':rawfile,'outputCRS':'EPSG:4326','selectionRule':'Exact court name and block number, unique match in saved official response'}
  officialfile=f'data/kingswood-footprints/phase-{phase}-tower-{tower}-official-footprint.json'
  (ROOT/officialfile).write_text(json.dumps(official,indent=2,ensure_ascii=False))
  annotation=json.loads((ROOT/'data/chestwood-tower-2/annotations.json').read_text())
  if phase==1:
   mapping=dict(zip('ABCDEFGH','BAHGFEDC'))
   annotation['rooms']={mapping[k]:v for k,v in annotation['rooms'].items()}
  else:mapping={k:k for k in 'ABCDEFGH'}
  reflected=tower in mirrors
  annotation.update(templateSource='data/chestwood-tower-2/annotations.json',layoutSource='https://i1.28hse.com/estate_data/108/4390/FLOOR/'+assets[int(reflected)]+'_large.jpg',stackMapping=mapping,layoutEvidence='Published plan group heading; A–H, master bedrooms and two-bedroom E/F cluster checked. Locwood 1–7/8–14; Maywood even/odd; Kenswood 3,5,7,9,11,13,14 / 1,2,4,6,8,10,12.',sourceAuthority='Published estate plan; developer-original provenance not established')
  ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
  solutions=solve(sample(np.array(annotation['outline'])*[1,-1]),sample(q),reflected=reflected);best=solutions[0]
  windows=[]
  for flat,items in annotation['rooms'].items():
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
    assert hits
    distance=min(hits,key=abs);projected=mid+distance*n
    offset=max(1,distance+.5);camera=mid+n*offset
    if inside(camera,q):
     exits=[d+.5 for d in hits if d>=1 and not inside(mid+n*(d+.5),q)]
     assert exits,(phase,tower,flat,kind)
     offset=min(exits);camera=mid+n*offset
    ll=origin+mid/factor;cll=origin+camera/factor;pll=origin+projected/factor
    windows.append(dict(flat=flat,id=kind,lat=float(ll[1]),lng=float(ll[0]),cameraLat=float(cll[1]),cameraLng=float(cll[0]),heading=float(np.degrees(np.arctan2(n[0],n[1]))%360),projectedFacadeLat=float(pll[1]),projectedFacadeLng=float(pll[0]),facadeDistanceMeters=distance,cameraOffsetMetres=offset,windowVerified=False,georefVerified=False,confidence='review',interiorNormalDot=float(np.dot(n,ip-mid)),cameraOutside=not inside(camera,q)))
  assert best['rmsMetres']<2 and all(w['cameraOutside'] for w in windows)
  result=dict(phase=phase,tower=tower,court=court,maxFloor=maxfloor,buildingCsuid=official['attributes']['BuildingCSUID'],origin=origin.tolist(),transform=best,candidates=solutions,windows=windows,annotation=annotation,officialFile=officialfile,verification='Template-derived window proxies; raster and independent absolute orientation remain review; floor altitude estimated.')
  (target/'annotations.json').write_text(json.dumps(annotation,indent=2))
  (target/'result.json').write_text(json.dumps(result,indent=2))
  record=dict(phase=phase,tower=tower,csuid=result['buildingCsuid'],**best,windows=len(windows))
  summary.append(record);print(json.dumps(record),flush=True)
(ROOT/'data/remaining-courts-summary.json').write_text(json.dumps(summary,indent=2))
