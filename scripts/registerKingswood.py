"""Reproducible metre-space outline registration; requires numpy scipy pillow.
Run with this project as cwd, or anywhere (paths resolved from this file).
Uses no compass bearing, listing direction, or preselected government edge.
"""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/kingswood-registration'; OUT.mkdir(exist_ok=True)
annotations=json.loads((ROOT/'data/kingswood-plan-annotations.json').read_text())
manifest=json.loads((ROOT/'data/kingswood-first-towers-manifest.json').read_text())

def sample(poly,n=700):
 p=np.asarray(poly,float)
 if np.linalg.norm(p[0]-p[-1])<1e-9:p=p[:-1]
 q=np.roll(p,-1,axis=0);length=np.linalg.norm(q-p,axis=1);cs=np.r_[0,np.cumsum(length)]
 d=np.arange(n)*cs[-1]/n;idx=np.searchsorted(cs,d,side='right')-1
 return p[idx]+(q-p)[idx]*((d-cs[idx])/length[idx])[:,None]

def fit(a,b):
 ac=a.mean(0);bc=b.mean(0);x=a-ac;y=b-bc
 u,s,vt=np.linalg.svd(x.T@y);d=np.eye(2);d[-1,-1]=np.linalg.det(u@vt)
 r=u@d@vt;scale=np.sum(s*np.diag(d))/np.sum(x*x)
 return scale,r,bc-scale*ac@r

def transform(p,v):
 t,logscale,x,y=v;c=math.cos(t);s=math.sin(t)
 return np.exp(logscale)*p@np.array([[c,s],[-s,c]])+[x,y]

def solve(p,q,reflected=False):
 p=p.copy()
 if reflected:p[:,0]*=-1
 pc=p.mean(0);p-=pc
 qc=q.mean(0);qt=cKDTree(q)
 initial=np.sqrt(np.sum((q-qc)**2)/np.sum(p*p))
 candidates=[]
 for angle in np.arange(0,360,5):
  rad=np.deg2rad(angle);r=np.array([[np.cos(rad),np.sin(rad)],[-np.sin(rad),np.cos(rad)]])
  scale=initial;shift=qc.copy()
  for iteration in range(65):
   moved=scale*p@r+shift
   _,iq=qt.query(moved);_,ip=cKDTree(moved).query(q)
   ns,nr,nt=fit(np.vstack([p,p[ip]]),np.vstack([q[iq],q]))
   if np.linalg.norm(nt-shift)+abs(ns-scale)*1000+np.linalg.norm(nr-r)<1e-7:break
   scale,r,shift=ns,nr,nt
  moved=scale*p@r+shift
  err=np.sqrt((np.mean(qt.query(moved)[0]**2)+np.mean(cKDTree(moved).query(q)[0]**2))/2)
  theta=np.arctan2(r[0,1],r[0,0])
  if not any(abs(np.angle(np.exp(1j*(theta-c['theta']))))<.1 for c in candidates):
   candidates.append(dict(theta=theta,scale=scale,shift=shift,error=err))
 candidates.sort(key=lambda c:c['error'])
 results=[]
 for cand in candidates[:8]:
  def obj(v):
   m=transform(p,v)
   return (np.mean(qt.query(m)[0]**2)+np.mean(cKDTree(m).query(q)[0]**2))/2
  v0=[cand['theta'],np.log(cand['scale']),*cand['shift']]
  opt=minimize(obj,v0,method='Powell',options={'xtol':1e-8,'ftol':1e-8,'maxiter':100})
  v=opt.x;m=transform(p,v);dist=np.r_[qt.query(m)[0],cKDTree(m).query(q)[0]]
  theta=v[0];scale=np.exp(v[1]);r=np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
  results.append({'rotationDegrees':float(np.degrees(theta)%360),'scaleMetresPerCanvasPixel':float(scale),'translationMetres':(v[2:]-scale*pc@r).tolist(),'reflected':reflected,'rmsMetres':float(np.sqrt(np.mean(dist**2))),'p95Metres':float(np.percentile(dist,95))})
 return sorted(results,key=lambda x:x['rmsMetres'])

def apply(p,solution):
 p=np.asarray(p,float).copy()
 if solution['reflected']:p[:,0]*=-1
 return transform(p,[np.radians(solution['rotationDegrees']),np.log(solution['scaleMetresPerCanvasPixel']),*solution['translationMetres']])

def en_frame(ring):
 origin=np.mean(ring[:-1],axis=0);lat=np.radians(origin[1]);a=6378137.;e2=6.6943799901413165e-3
 N=a/np.sqrt(1-e2*np.sin(lat)**2);M=a*(1-e2)/(1-e2*np.sin(lat)**2)**1.5
 factor=np.radians(1)*np.array([N*np.cos(lat),M])
 return origin,factor,(ring-origin)*factor

def inside(point,polygon):
 x,y=point;yes=False
 for a,b in zip(polygon,np.roll(polygon,-1,axis=0)):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes

def overlay(phase,annotation,poly,q,solution,facades):
 im=Image.new('RGB',(1100,850),'#fafafa');draw=ImageDraw.Draw(im)
 moved=apply(poly,solution)
 allp=np.vstack([q,moved]);lo=allp.min(0);hi=allp.max(0);sc=min(950/(hi-lo)[0],680/(hi-lo)[1])
 def px(p):return [tuple(v) for v in np.column_stack([70+(p[:,0]-lo[0])*sc,760-(p[:,1]-lo[1])*sc])]
 draw.line(px(np.vstack([q,q[0]])),fill='#146eb4',width=5)
 draw.line(px(np.vstack([moved,moved[0]])),fill='#db7221',width=3)
 for flat,rec in facades.items():
  f=np.array(rec['facadeLocalMetres']);mid=f.mean(0);cam=np.array(rec['cameraLocalMetres']);normal=cam-mid
  draw.line(px(f),fill='#ab156c',width=6);draw.line(px(np.array([mid,mid+normal*3])),fill='#ab156c',width=3)
  draw.text(px(np.array([mid+normal*3]))[0],flat,fill='black')
 draw.text((20,15),f'Phase {phase} Tower 1 | blue LandsD | orange registered plan | magenta living facade + normal',fill='black')
 draw.text((20,36),f"RMS {solution['rmsMetres']:.2f} m | rotation {solution['rotationDegrees']:.2f} deg | north up",fill='black')
 draw.line([(1040,100),(1040,50)],fill='black',width=3);draw.text((1037,33),'N',fill='black')
 im.save(OUT/f'phase-{phase}-overlay.png')
 source=Image.open(ROOT/f'data/kingswood-plans/phase-{phase}.png').convert('RGB').resize(tuple(annotation['canvas']))
 d=ImageDraw.Draw(source);xy=np.asarray(annotation['outline']);d.line([tuple(v) for v in np.vstack([xy,xy[0]])],fill='#ff6700',width=4)
 for flat,seg in annotation['facades'].items():
  d.line([tuple(v) for v in seg],fill='#00ffff',width=8);mid=np.mean(seg,axis=0);d.text(tuple(mid),flat,fill='#000000',stroke_width=1)
 source.save(OUT/f'phase-{phase}-traced-plan.png')

allresults=[]
for entry in manifest['phases']:
 if entry.get('residential') is False:continue
 phase=entry['phase'];annotation=annotations['phases'][str(phase)]
 file=entry.get('officialFootprintFile',f'data/kingswood-footprints/phase-{phase}-tower-1-official-footprint.json')
 official=json.loads((ROOT/file).read_text());ring=np.array(official['geometry']['rings'][0]);origin,factor,qpoly=en_frame(ring)
 poly=np.array(annotation['outline'],float)*[1,-1];p=sample(poly);q=sample(qpoly)
 if '--reuse-registration' in sys.argv:
  previous=json.loads((OUT/f'phase-{phase}.json').read_text());proper=previous['candidates'];mirror=previous['mirrorDiagnostic']
 else:
  proper=solve(p,q);mirror=solve(p,q,True)
 best=proper[0]
 # Each visually identified adjacent pair shares one straight diagonal glazed
 # facade. Fit that line to the four hand-picked endpoints to avoid turning
 # annotation noise at the partition into two different facade directions.
 annotation=json.loads(json.dumps(annotation))
 for pair in ['AB','CD','EF','GH']:
  points=np.concatenate([annotation['facades'][flat] for flat in pair]);centre=points.mean(0)
  _,_,vt=np.linalg.svd(points-centre);axis=vt[0]
  for flat in pair:
   seg=np.array(annotation['facades'][flat]);annotation['facades'][flat]=(centre+((seg-centre)@axis)[:,None]*axis).tolist()
 facades={}
 for flat,seg in annotation['facades'].items():
  f=apply(np.array(seg)*[1,-1],best);mid=f.mean(0);t=f[1]-f[0];normal=np.array([-t[1],t[0]])/np.linalg.norm(t)
  if np.dot(normal,mid-apply(np.mean(poly,axis=0)[None,:],best)[0])<0:normal=-normal
  nominal=mid+normal;offset=1.
  if inside(nominal,qpoly):
   exits=[]
   for a,b in zip(qpoly,np.roll(qpoly,-1,axis=0)):
    mat=np.column_stack([normal,a-b])
    if abs(np.linalg.det(mat))<1e-9:continue
    t,u=np.linalg.solve(mat,a-mid)
    if t>=1 and 0<=u<=1 and not inside(mid+(t+.5)*normal,qpoly):exits.append(t+.5)
   if not exits:raise ValueError(f'No safe outward clearance for phase {phase} {flat}')
   offset=min(exits)
  camera=mid+offset*normal;lng,lat=origin+camera/factor
  facades[flat]={'facadeLocalMetres':f.tolist(),'facadeMidpoint':{'lat':float((origin+mid/factor)[1]),'lng':float((origin+mid/factor)[0])},'cameraOffsetMetres':float(offset),'nominalOneMetreCameraLocal':nominal.tolist(),'clearanceNote':'Nominal 1 m from registered glazing. If enclosed by official generalized footprint, extend along the same normal to 0.5 m beyond its first exit; facade midpoint and heading are unchanged.','cameraLocalMetres':camera.tolist(),'lat':round(float(lat),6),'lng':round(float(lng),6),'heading':round(float(np.degrees(np.arctan2(normal[0],normal[1]))%360),1)}
 result={'phase':phase,'courtTC':entry['courtTC'],'courtEN':entry['courtEN'],'building':1,'attributes':official['attributes'],'originWGS84':origin.tolist(),'metresPerDegree':factor.tolist(),'planSource':entry['floorPlanUrl'],'estatePage':entry['estatePage'],'officialFile':file,'candidates':proper,'mirrorDiagnostic':mirror,'facadeExtraction':'Adjacent A/B, C/D, E/F, G/H living rooms share straight diagonal glazing envelopes in the inspected plans. Orthogonal least-squares line fit to the four traced endpoints suppresses partition-point annotation noise; individual segment midpoints remain separate.','facades':dict(sorted(facades.items()))}
 (OUT/f'phase-{phase}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 overlay(phase,annotation,poly,qpoly,best,facades);allresults.append(result)
 print(phase,'proper',[(round(c['rotationDegrees'],1),round(c['rmsMetres'],3)) for c in proper[:4]],'mirror',round(mirror[0]['rmsMetres'],3),'G',facades['G']['heading'],flush=True)
(OUT/'all-phases.json').write_text(json.dumps(allresults,ensure_ascii=False,indent=2)+'\n')
