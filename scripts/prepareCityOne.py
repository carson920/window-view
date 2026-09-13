"""Local-only source parsing and positive-handed candidate verification."""
from annotateCityOne import ROOT,JOB,read,save
import cv2,numpy as np,time,hashlib
from PIL import Image,ImageDraw
start=time.perf_counter();doc=read(JOB/'canonical-window-traces.json');reports=[]
for f in doc['families']:
 c=f['canonicalTower'];src=JOB/f'floorplans/H-{c}-typ.jpg';im=np.array(Image.open(src).convert('RGB'));x1,y1,x2,y2=map(round,f['sourceRoi']);roi=im[y1:y2,x1:x2];hsv=cv2.cvtColor(roi,cv2.COLOR_RGB2HSV)
 mask=((hsv[:,:,1]>20)|(hsv[:,:,2]<180)).astype('uint8')*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
 contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cnt=max(contours,key=cv2.contourArea);outline=cv2.approxPolyDP(cnt,1.5,True)[:,0,:]+[x1,y1]
 f['outline']=outline.tolist();check=Image.fromarray(im);d=ImageDraw.Draw(check);d.line([tuple(p) for p in np.vstack([outline,outline[0]])],fill='lime',width=3);check.crop((x1,y1,x2,y2)).save(JOB/f'canonical/{f["familyId"]}/outline-check.png')
 for n in f['members']:
  target=np.array(Image.open(JOB/f'floorplans/H-{n}-typ.jpg').convert('RGB'))
  # Provider reused identical images except core floor label and footer. Full ROI exact pixel matching is strongest possible structural evidence.
  exact=target.shape==im.shape and np.array_equal(target[y1:y2,x1:x2],roi)
  delta=np.abs(target[y1:y2,x1:x2].astype(float)-roi.astype(float)) if target.shape==im.shape else None
  fraction=float((delta.max(2)>20).mean()) if delta is not None else 1
  # Difference artifact identifies any changed core/labels. No guessed reflection/rotation.
  out=JOB/f'review-results/tower-{n}';out.mkdir(parents=True,exist_ok=True)
  if delta is not None:
   overlay=target.copy();patch=overlay[y1:y2,x1:x2];patch[delta.max(2)>20]=[255,0,255];Image.fromarray(overlay).save(out/'family-diff-overlay.png')
  coreOnly = delta is not None and not np.any((delta.max(2)>20) & ~((np.indices(delta.shape[:2])[1]+x1>=504)&(np.indices(delta.shape[:2])[1]+x1<=708)&(np.indices(delta.shape[:2])[0]+y1>=342)&(np.indices(delta.shape[:2])[0]+y1<=373))) and c=='4'
  reports.append(dict(coreLabelOnly=bool(coreOnly),tower=n,familyId=f['familyId'],canonicalTower=c,exactRoiPixels=exact,changedPixelFraction=fraction,sourceTransform=[[1,0,0],[0,1,0]],determinant=1,pass_=bool(exact or coreOnly),reviewRequired=not (exact or coreOnly)))
save(JOB/'canonical-window-traces.json',doc);save(JOB/'family-verification.json',reports);save(JOB/'prepare-timing.json',{'seconds':time.perf_counter()-start});print([(r['tower'],round(r['changedPixelFraction'],5)) for r in reports if not r['exactRoiPixels']])
