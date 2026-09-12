"""South Horizons: screenshot-fixed orientation, scale/translation only.
Never enumerate angles or reflect the approved tower drawing.
"""
import json,time,math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];JOB=ROOT/'data/south-horizons-approved-job'
scope={'__file__':str(ROOT/'scripts/registerKingswood.py')};exec((ROOT/'scripts/registerKingswood.py').read_text().split('allresults=[]')[0],scope)
sample,apply,en_frame,inside=[scope[k] for k in ['sample','apply','en_frame','inside']]
def read(p):return json.loads(p.read_text())
def save(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
# Angles transcribed from parallel edges in the approved NORTH-UP screenshots.
# Screenshot pixels establish orientation only, never scale or coordinates.
angles={'1':0,'2':0,**{str(n):3.5 for n in range(3,7)},**{str(n):-45 for n in range(7,11)},**{str(n):-12 for n in range(11,23)},'13A':-12,'23':20,'23A':20,**{str(n):37 for n in range(25,29)},**{str(n):-12 for n in range(29,34)},'33A':-12}
def fit(a,o,theta):
 ring=np.array(o['geometry']['rings'][0]);origin,factor,q=en_frame(ring);p=sample(np.array(a['outline'])*[1,-1]);dest=sample(q);ang=np.radians(theta);rot=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]]);p=p@rot.T
 s=np.sqrt(np.var(dest,axis=0).sum()/np.var(p,axis=0).sum());t=dest.mean(0)-s*p.mean(0);tree=cKDTree(dest)
 def loss(v):
  moved=p*np.exp(v[0])+v[1:];d=tree.query(moved)[0];r=cKDTree(moved).query(dest)[0];return np.mean(d*d)+np.mean(r*r)
 res=minimize(loss,[np.log(s),*t],method='Powell',options={'maxiter':400,'xtol':1e-8,'ftol':1e-9})
 sc=np.exp(res.x[0]);return dict(rotationDegrees=theta,reflected=False,scaleMetresPerCanvasPixel=float(sc),translationMetres=res.x[1:].tolist(),rmsMetres=float(np.sqrt(res.fun/2)),method='Single approved screenshot angle held constant; symmetric boundary distance optimizes uniform scale + east/north translation only'),origin,factor,q
if __name__=='__main__':
 from PIL import Image,ImageDraw
 reports=[]
 for item in read(JOB/'preparation.json'):
  tower=item['tower'];out=ROOT/f'data/south-horizons-tower-{tower.lower()}';start=time.perf_counter();a=read(out/'annotations.json');o=read(out/'official-footprint.json');s,origin,factor,q=fit(a,o,angles[tower]);save(out/'placement.json',dict(transform=s,origin=origin.tolist(),factor=factor.tolist()))
  p=apply(np.array(a['outline'])*[1,-1],s);both=np.vstack([p,q]);lo=both.min(0);hi=both.max(0);scale=700/max(hi-lo);xy=lambda v:tuple((np.array([v[0]-lo[0],hi[1]-v[1]])*scale+50).tolist());im=Image.new('RGB',(800,800),'white');d=ImageDraw.Draw(im);d.line([xy(v) for v in np.vstack([q,q[0]])],fill='blue',width=3);d.line([xy(v) for v in np.vstack([p,p[0]])],fill='red',width=2);d.text((10,10),f'{tower} fixed angle {angles[tower]} | RMSE {s["rmsMetres"]:.2f}m',fill='black');im.save(out/'placement-check.png');reports.append(dict(tower=tower,**s,seconds=time.perf_counter()-start));print(tower,round(s['rmsMetres'],2),flush=True)
 save(JOB/'placement-summary.json',reports)
