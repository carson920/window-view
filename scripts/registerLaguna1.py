"""Trace L&Lam's explicit window lines, including Block 1 B/C inset plans."""
import json, sys, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tower=int(sys.argv[1]) if len(sys.argv)>1 else 1
assert tower in (1,2,3,4)
out=ROOT/f'data/laguna-tower-{tower}';out.mkdir(exist_ok=True)
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')}
exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,solve,apply,en_frame,inside=[scope[k] for k in ['sample','solve','apply','en_frame','inside']]
raw=json.loads((ROOT/'data/laguna-tower-1/court-query.raw.json').read_text());matches=[f for f in raw['features'] if f['attributes']['BuildingNameEN']==f'Laguna City Block {tower}'];assert len(matches)==1
official=matches[0];official['provenance']={'source':'LandsD CSDI Building FSDT','queryUrl':"https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query?where=BuildingNameEN%20LIKE%20%27%25Laguna%20City%25%27&outFields=*&returnGeometry=true&outSR=4326&f=json",'rawFile':'data/laguna-tower-1/court-query.raw.json','outputCRS':'EPSG:4326'}
(out/'official-footprint.json').write_text(json.dumps(official,indent=2))
# Canvas follows the source image uniformly scaled from 2000 x 2280.
outline=[[530,438],[654,438],[654,622],[738,622],[738,438],[854,438],[854,475],[953,475],[953,538],[907,581],[1030,682],[1053,638],[1072,657],[1275,657],[1275,852],[922,852],[922,936],[1275,936],[1275,1133],[1072,1133],[1053,1153],[1030,1128],[906,1208],[953,1250],[953,1317],[852,1317],[852,1355],[738,1355],[738,1168],[654,1168],[654,1355],[538,1355],[538,1317],[438,1317],[438,1250],[485,1208],[378,1128],[338,1153],[319,1133],[147,1133],[147,937],[475,937],[475,852],[147,852],[147,657],[319,657],[338,638],[378,682],[485,581],[438,538],[438,475],[538,475]]
# Window endpoints are the fine parallel glazing lines, NOT thick walls or AC boxes.
# Original main-face traces; connected small-bedroom corners override below.
# Bedroom-1 is nearer living.
rooms={
 'A':[['living',[976,1170],[1019,1128],[920,1040]],['bedroom-1',[1054,1151],[1071,1134],[1090,1090]],['bedroom-2',[1272,1058],[1272,1127],[1215,1090]],['master',[1272,944],[1272,1014],[1210,990]]],
 'B':[['living',[918,1200],[962,1157],[848,1130]],['bedroom-1',[856,1317],[933,1317],[903,1270]],['master',[746,1358],[849,1358],[790,1300]]],
 'C':[['living',[424,1180],[476,1225],[545,1150]],['bedroom-1',[462,1317],[535,1317],[490,1270]],['master',[540,1358],[645,1358],[595,1300]]],
 'D':[['living',[375,1129],[417,1170],[443,1070]],['bedroom-1',[320,1133],[338,1151],[340,1090]],['bedroom-2',[149,1058],[149,1126],[213,1090]],['master',[149,944],[149,1014],[215,985]]],
 'E':[['living',[375,682],[417,639],[441,742]],['bedroom-1',[320,657],[338,640],[340,705]],['bedroom-2',[149,662],[149,733],[213,700]],['master',[149,775],[149,845],[215,807]]],
 'F':[['living',[424,612],[474,565],[545,630]],['bedroom-1',[440,483],[440,532],[491,512]],['master',[534,437],[534,473],[590,482]]],
 'G':[['living',[916,568],[964,613],[845,631]],['bedroom-1',[951,483],[951,532],[898,512]],['master',[856,437],[856,473],[794,482]]],
 'H':[['living',[974,624],[1017,670],[958,740]],['bedroom-1',[1054,640],[1071,657],[1090,700]],['bedroom-2',[1272,663],[1272,733],[1215,700]],['master',[1272,776],[1272,845],[1210,806]]]
}
annotation={'canvas':[1472,1678],'source':'https://llam.com.hk/admin/estate_image/da96ca43.jpg','sourcePage':'https://llam.com.hk/floorplan_detail.php?sno=4','outline':outline,'rooms':rooms,'extractionMethod':'Manual fine parallel window-line tracing; largest main face per room. B/C use the Block 1/13 inset variant. Interior points choose outward normals. Published agent plan, not official surveyed glazing.','insetTranslations':{'B':[-291,-40],'C':[295,-40]},'insetNote':'B/C inset aligned by bathroom and master-bedroom partition; main facade midpoint is a traced proxy. Tiny bay side panes excluded.'}
# Connected corner glazing, in the same registered plan canvas. The first and
# last points define a virtual chord, not a physical diagonal pane of glass.
# B/C endpoints come from their Tower 1 inset, with the translations above.
corner_glazing={
 'A':[[1038,1135],[1054,1151],[1071,1134]],
 'B':[[936,1220],[956,1240],[933,1262]],
 'C':[[458,1221],[439,1238],[460,1260]],
 'D':[[320,1133],[338,1151],[352,1137]],
 'E':[[320,657],[338,640],[351,653]],
 'F':[[456,475],[440,475],[440,536]],
 'G':[[935,475],[953,475],[953,536]],
 'H':[[1038,656],[1054,640],[1071,657]],
}
for flat,points in corner_glazing.items():
 row=next(row for row in rooms[flat] if row[0]=='bedroom-1')
 row[1],row[2]=points[0],points[-1]
annotation['cornerGlazing']=corner_glazing
annotation['extractionMethod']='Manual fine parallel glazing-line tracing. Small-bedroom corner windows use the chord joining both outer endpoints; interior points determine the outward normal. Other rooms retain their main window face. B/C use the Tower 1 inset. Agent plan, not official surveyed glazing.'
annotation['insetNote']='B/C inset aligned by bathroom and master-bedroom partition; small-bedroom view now uses both connected corner panes instead of the separate longer horizontal pane.'
if tower!=1:
 # The shared plan explicitly marks only 1/13 (and 15 in the even drawing)
 # as inset variants. Towers 2/3/4 use the MAIN B/C rooms, not those insets.
 rooms['B'][2]=['master',[856,1319],[856,1355],[794,1300]]
 rooms['C'][2]=['master',[534,1319],[534,1355],[595,1300]]
 corner_glazing['B']=[[951,1254],[951,1317],[934,1317]]
 corner_glazing['C']=[[440,1254],[440,1317],[457,1317]]
 for flat in ('B','C'):
  rooms[flat][1][1:3]=[corner_glazing[flat][0],corner_glazing[flat][-1]]
 annotation['insetTranslations']={}
 annotation['insetNote']='Main standard B/C rooms; Tower 1/13/15 inset variants excluded.'
 annotation['extractionMethod']=annotation['extractionMethod'].replace('B/C use the Tower 1 inset.','B/C use the main standard plan; special insets excluded.')
 annotation['layoutVerification']={'applicableTowers':[2,4,6,8,14,15,17] if tower%2==0 else [1,3,5,7,13,16], 'variant':'even mirrored main plan' if tower%2==0 else 'odd main plan', 'checks':['A/H left, D/E right, B/C bottom, G/F top on even plan; reversed left/right on odd plan','Mirrored kitchens, lift lobby and hopper/stair core','B/C main exterior glazing differs from Tower 1 inset'], 'estateLayoutFile':'data/laguna-tower-1/estate-layout.jpg','orientationCheck':'Towers 1–4 have parallel principal axes in estate layout, consecutively southwest in official georeferenced polygons.'}
 if tower%2==0:
  # Independently matched exterior/lift-recess corners on the labelled even
  # drawing (1599x1560 canvas). Fit ONE uniform scale plus reflection/translation.
  source=np.array([[147,657],[1275,657],[654,438],[738,438],[475,852],[922,852]],float)
  target=np.array([[1497,692],[398,692],[1002,480],[923,480],[1176,882],[744,882]],float)
  reflected=source*[-1,1];a=reflected-reflected.mean(0);b=target-target.mean(0)
  scale=float(np.sum(a*b)/np.sum(a*a));shift=target.mean(0)-scale*reflected.mean(0)
  def native(points):return (np.array(points)*[-1,1]*scale+shift).tolist()
  annotation['sourceCanvasTransform']={'scale':scale,'reflection':'x','translation':shift.tolist(),'landmarksSource':source.tolist(),'landmarksTarget':target.tolist(),'rmsePixels':float(np.sqrt(np.mean(np.sum((np.array(native(source))-target)**2,axis=1))))}
  outline[:]=native(outline)
  for items in rooms.values():
   for row in items:row[1:]=native(row[1:])
  for flat in corner_glazing:corner_glazing[flat]=native(corner_glazing[flat])
  annotation['canvas']=[1599,1560]
  annotation['source']='https://llam.com.hk/admin/estate_image/df92a51a.jpg'
ring=np.array(official['geometry']['rings'][0]);origin,factor,q=en_frame(ring)
previous=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else None
if previous and previous['annotation']['outline']==outline:
 solutions=previous['candidates'];best=previous['transform']
else:
 solutions=solve(sample(np.array(outline)*[1,-1]),sample(q))
 # The estate layout resolves the near-180-degree outline ambiguity.
 aligned=[s for s in solutions if abs((s['rotationDegrees']-129.5+180)%360-180)<15]
 assert aligned,'No registration agrees with estate layout'
 best=min(aligned,key=lambda s:s['rmsMetres'])
assert best['rmsMetres']<1, best
windows=[]
for flat,items in rooms.items():
 for kind,a,b,interior in items:
  seg=apply(np.array([a,b])*[1,-1],best);mid=seg.mean(0);t=seg[1]-seg[0];n=np.array([-t[1],t[0]])/np.linalg.norm(t);ip=apply(np.array([interior])*[1,-1],best)[0]
  if np.dot(n,ip-mid)>0:n=-n
  hits=[]
  for a,b in zip(q,np.roll(q,-1,axis=0)):
   mat=np.column_stack([n,a-b])
   if abs(np.linalg.det(mat))<1e-9:continue
   distance,u=np.linalg.solve(mat,a-mid)
   if 0<=u<=1:hits.append(float(distance))
  assert hits,(flat,kind)
  distance=min(hits,key=abs);projected=mid+distance*n;offset=max(1,distance+.5)
  if inside(mid+n*offset,q):offset=min(d+.5 for d in hits if d>=1 and not inside(mid+n*(d+.5),q))
  camera=mid+n*offset;ll=origin+mid/factor;cll=origin+camera/factor;pll=origin+projected/factor
  windows.append(dict(flat=flat,id=kind,lat=float(ll[1]),lng=float(ll[0]),cameraLat=float(cll[1]),cameraLng=float(cll[0]),heading=float(np.degrees(np.arctan2(n[0],n[1]))%360),projectedFacadeLat=float(pll[1]),projectedFacadeLng=float(pll[0]),facadeDistanceMeters=distance,cameraOffsetMetres=offset,interiorNormalDot=float(np.dot(n,ip-mid)),cameraOutside=not inside(camera,q),windowVerified=False,georefVerified=False,confidence='review'))
for window in windows:
 row=next(row for row in rooms[window['flat']] if row[0]==window['id'])
 window['planSegment']=row[1:3]
 if window['id']=='bedroom-1':
  window['cornerGlazingPlanPoints']=corner_glazing[window['flat']]
  window['viewGeometry']='corner-window-outer-endpoint-chord'
result=dict(buildingCsuid=official['attributes']['BuildingCSUID'],origin=origin.tolist(),transform=best,candidates=solutions,windows=windows,annotation=annotation)
(out/'annotations.json').write_text(json.dumps(annotation,indent=2));(out/'result.json').write_text(json.dumps(result,indent=2))
from PIL import Image,ImageDraw
im=Image.open(out/'floor-plan.jpg').resize(tuple(annotation['canvas']));draw=ImageDraw.Draw(im)
for points in corner_glazing.values():draw.line([tuple(p) for p in points],fill='limegreen',width=4)
for flat,items in rooms.items():
 for kind,a,b,interior in items:draw.line([tuple(a),tuple(b)],fill='red',width=4);draw.text(tuple(np.mean([a,b],axis=0)),flat+'/'+kind,fill='blue')
im.save(out/'traced-plan.png')
print(json.dumps({'candidates':solutions,'windows':windows},indent=2))
