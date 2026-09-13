"""Visually transcribed main glazing lines on each independent approved crop.
Coordinates reference plan-crop.png pixels; no official-polygon window inference.
"""
from registerSouthHorizons import ROOT,JOB,read,save
import numpy as np
# Four continuous living-room window runs, each with the separating flat wall.
# Orders: A/B, C/D, E/F, H/G. Bedroom segments have an interior-side witness.
traces=read(JOB/'window-traces.json')

def build(t,record):
 out=ROOT/f'data/south-horizons-tower-{t.lower()}';a=read(out/'annotations.json');rooms={f:[] for f in 'ABCDEFGH'}
 for flats,d in zip(['AB','CD','EF','HG'],record['diagonals']):
  p1=np.array(d[:2],float);m=np.array(d[2:4],float);p2=np.array(d[4:],float)
  for f,l,r in [(flats[0],p1,m),(flats[1],m,p2)]:
   # Camera proxy only: 6% is heuristic, not measured physical glazing extents.
   # Original untrimmed endpoints remain in window-traces.json.
   delta=r-l;l=l+delta*.06;r=r-delta*.06;mid=(l+r)/2;core=np.array(a['canvas'])/2;interior=mid+(core-mid)*.25
   rooms[f].append(['living',l.tolist(),r.tolist(),interior.tolist()])
 for f,rows in record['beds'].items():
  for kind,x1,y1,x2,y2,side in rows:
   interior=(np.array([x1+x2,y1+y2])/2+np.array({'E':[22,0],'W':[-22,0],'N':[0,-22],'S':[0,22]}[side])).tolist();rooms[f].append([kind,[x1,y1],[x2,y2],interior])
 a.update(rooms=rooms,extractionMethod='Independent visual tracing of close parallel glazing/sill lines on approved tower-specific crop; living glazing excludes party-wall ends; bedroom interior witness selects outward normal',planInterpretation='visually-reviewed-main-window-segments',geometryFamily='independent-'+a['sourceId'],core=(np.array(a['canvas'])/2).tolist());save(out/'annotations.json',a)
 from PIL import Image,ImageDraw
 im=Image.open(out/'plan-crop.png');d=ImageDraw.Draw(im)
 for f,rows in rooms.items():
  for kind,p,q,witness in rows:d.line([tuple(p),tuple(q)],fill='red',width=3);d.text(tuple(witness),f+'/'+kind,fill='red')
 im.save(out/'window-review.png')
if __name__=='__main__':
 for t,r in traces.items():build(t,r)
