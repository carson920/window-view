"""v4 source-image transcription. No government geometry is used here.
Reference canvases match the visually inspected images; original pixel endpoints are retained.
Only clearly separated thin glazing runs are accepted. Bay outlines stay unresolved.
"""
from pathlib import Path
import json,hashlib,time,os
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];JOB=ROOT/os.environ.get('CITY_ONE_JOB','data/city-one-shatin-approved-job')
def read(p):return json.loads(p.read_text())
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Explicit reference canvases (not original source dimensions).
SIZES={1:(1280,1949),7:(1275,1952),4:(1215,1089),8:(1061,1345),16:(1280,1933),18:(1280,1950),19:(1061,1345),30:(1061,1345),25:(1114,1097),27:(1114,1097),37:(1114,1411),42:(1114,1411),34:(1114,1411),36:(1114,1411)}
ROI={1:[190,564,1080,1580],7:[123,595,1162,1510],4:[75,68,1140,760],8:[73,80,970,1124],16:[215,568,1080,1580],18:[124,625,1167,1540],19:[74,45,976,1080],30:[74,45,976,1080],25:[24,108,1085,777],27:[24,108,1085,777],37:[76,81,1020,1160],42:[76,81,1020,1160],34:[156,43,887,1129],36:[67,105,1033,1148]}
T={n:[] for n in SIZES}
def line(n,f,r,x1,y1,x2,y2,side):
 m=np.array([(x1+x2)/2,(y1+y2)/2]);w=m+np.array({'E':(22,0),'W':(-22,0),'N':(0,-22),'S':(0,22)}[side]);T[n].append(dict(flat=f,id=r,p1=[x1,y1],p2=[x2,y2],interiorWitness=w.tolist()))
def v(n,f,r,x,a,b,s):line(n,f,r,x,a,x,b,s)
def h(n,f,r,y,a,b,s):line(n,f,r,a,y,b,y,s)
# Tower 1: clear straight glazing, three-bedroom north/south wings and two-bedroom side wings.
for f,x,a,b,s in [('E',401,775,850,'E'),('F',861,775,850,'W'),('B',408,1291,1376,'E'),('A',864,1291,1376,'W')]:v(1,f,'living',x,a,b,s)
for f,y,a,b,s in [('D',868,320,386,'S'),('G',864,884,946,'S'),('C',1278,322,394,'N'),('H',1275,882,947,'N')]:h(1,f,'living',y,a,b,s)
for f,x,ys,s in [('E',366,[(587,628),(703,746)],'E'),('F',894,[(585,628),(703,746)],'W'),('B',375,[(1398,1446),(1495,1555)],'E'),('A',900,[(1398,1446),(1495,1555)],'W')]:
 for i,(a,b) in enumerate(ys):v(1,f,f'bedroom-{i+1}',x,a,b,s)
for f,y,a,b,s in [('E',574,493,528,'S'),('F',570,740,775,'S'),('B',1573,499,531,'N'),('A',1574,744,779,'N')]:h(1,f,'bedroom-3',y,a,b,s)
for f,y,a,b,s in [('D',849,214,261,'S'),('G',840,1000,1033,'S'),('C',1300,214,261,'N'),('H',1294,1000,1033,'N')]:h(1,f,'bedroom-1',y,a,b,s)
for f,y,a,b,s in [('D',1026,244,273,'N'),('G',1020,999,1031,'N'),('C',1124,244,270,'S'),('H',1115,999,1031,'S')]:h(1,f,'bedroom-2',y,a,b,s)
# Tower 7: six flats, source side glazing only.
for f,x,a,b,s in [('D',362,834,902,'E'),('E',912,834,902,'W'),('B',364,1215,1285,'E'),('A',918,1215,1285,'W')]:v(7,f,'living',x,a,b,s)
for f,x,ys,s in [('D',361,[(644,694),(711,754)],'E'),('E',912,[(644,694),(711,754)],'W'),('B',365,[(1348,1387),(1418,1477)],'E'),('A',916,[(1348,1387),(1418,1477)],'W')]:
 for i,(a,b) in enumerate(ys):v(7,f,f'bedroom-{i+1}',x,a,b,s)
for f,y,a,b,s in [('D',603,490,520,'S'),('E',602,755,786,'S')]:h(7,f,'bedroom-3',y,a,b,s)
v(7,'B','bedroom-3',576,1415,1475,'W');v(7,'A','bedroom-3',701,1415,1475,'E')
for f,y,a,b,side in [('C',1197,322,358,'N'),('F',1194,922,960,'N')]:h(7,f,'living',y,a,b,side)
for f,y,a,b,side in [('C',982,139,190,'S'),('F',977,1100,1148,'S')]:h(7,f,'bedroom-1',y,a,b,side)
for f,y,a,b,side in [('C',1198,185,223,'N'),('F',1194,1060,1095,'N')]:h(7,f,'bedroom-2',y,a,b,side)
for f,x,a,b,side in [('C',362,994,1018,'E'),('F',914,990,1014,'W')]:v(7,f,'bedroom-3',x,a,b,side)
# Four-flat family: do not turn polygonal bay outlines into windows.
for n,xl,xr,yt,yb in [(4,448,765,170,630),(25,410,696,210,632),(27,410,696,210,632)]:
 for f,x,y,s in [('C',xl,yt,'W'),('D',xr,yt,'E'),('B',xl,yb,'W'),('A',xr,yb,'E')]:v(n,f,'living-side',x,y,y+32,s)
for f,y,a,b,s in [('C',347,154,185,'N'),('D',347,1037,1067,'N'),('B',495,153,185,'S'),('A',495,1028,1057,'S')]:h(4,f,'bedroom-1',y,a,b,s)
# Tower 8 non-bay variant.
for f,x,a,b,s in [('E',282,306,373,'E'),('F',760,306,373,'W'),('B',282,834,905,'E'),('A',760,834,905,'W')]:v(8,f,'living',x,a,b,s)
for f,y,a,b,s in [('D',397,201,270,'S'),('G',397,772,842,'S'),('C',806,201,270,'N'),('H',807,772,842,'N')]:h(8,f,'living',y,a,b,s)
for f,x,ys,s in [('E',241,[(106,149),(222,275)],'E'),('F',802,[(106,149),(222,275)],'W'),('B',241,[(932,983),(1053,1096)],'E'),('A',802,[(932,983),(1053,1096)],'W')]:
 for i,(a,b) in enumerate(ys):v(8,f,f'bedroom-{i+1}',x,a,b,s)
for f,y,a,b,s in [('E',87,369,405,'S'),('F',87,637,672,'S'),('B',1117,369,405,'N'),('A',1117,637,672,'N')]:h(8,f,'bedroom-3',y,a,b,s)
for f,x,a,b,s in [('E',452,158,190,'W'),('F',589,158,190,'E'),('B',452,1016,1045,'W'),('A',589,1016,1045,'E')]:v(8,f,'bedroom-3-side',x,a,b,s)
for f,y,a,b,s in [('D',375,94,180,'S'),('G',375,863,946,'S'),('C',831,94,180,'N'),('H',831,863,946,'N')]:h(8,f,'bedroom-1',y,a,b,s)
for f,x,a,b,s in [('D',80,473,531,'E'),('G',962,473,531,'W'),('C',80,678,733,'E'),('H',962,678,733,'W')]:v(8,f,'bedroom-2',x,a,b,s)
for f,y,a,b,s in [('D',553,120,150,'N'),('G',553,893,919,'N'),('C',650,123,150,'S'),('H',650,893,919,'S')]:h(8,f,'bedroom-2-side',y,a,b,s)
# Tower 16 bay variant: main living and clear inner/side bedrooms.
for f,x,a,b,s in [('E',420,770,839,'E'),('F',873,770,839,'W'),('B',421,1285,1366,'E'),('A',873,1285,1366,'W')]:v(16,f,'living',x,a,b,s)
for f,y,a,b,s in [('D',865,336,398,'S'),('G',862,890,953,'S'),('C',1271,335,398,'N'),('H',1267,890,953,'N')]:h(16,f,'living',y,a,b,s)
for f,y,a,b,s in [('E',577,510,540,'S'),('F',576,752,782,'S')]:h(16,f,'bedroom-3',y,a,b,s)
for f,y,a,b,s in [('D',846,265,287,'S'),('G',841,1003,1025,'S'),('C',1291,265,287,'N'),('H',1287,1003,1025,'N')]:h(16,f,'bedroom-1',y,a,b,s)
for f,y,a,b,s in [('D',1018,265,287,'N'),('G',1016,1003,1025,'N'),('C',1117,265,287,'S'),('H',1115,1003,1025,'S')]:h(16,f,'bedroom-2',y,a,b,s)
# Tower 18: inner-room narrow glazing; bay outlines deliberately unresolved.
for f,x,a,b,s in [('D',575,694,723,'W'),('E',707,694,723,'E'),('B',581,1447,1468,'W'),('A',711,1447,1468,'E')]:v(18,f,'bedroom-3',x,a,b,s)
# Tower 19 / 30 sources were inspected separately: same walls, explicit different labels.
for n,mapping in [(19,dict(zip('EFDCGHBA','ABHGCDFE'))),(30,{f:f for f in 'ABCDEFGH'})]:
 def mf(f):return mapping[f]
 for f,x,a,b,s in [('E',285,253,344,'E'),('F',763,253,344,'W'),('B',289,796,868,'E'),('A',764,796,868,'W')]:v(n,mf(f),'living',x,a,b,s)
 for f,y,a,b,s in [('D',360,202,272,'S'),('G',359,773,845,'S'),('C',771,202,272,'N'),('H',770,773,845,'N')]:h(n,mf(f),'living',y,a,b,s)
 for f,y,a,b,s in [('E',56,380,425,'S'),('F',56,625,668,'S'),('B',1068,381,426,'N'),('A',1068,628,672,'N')]:h(n,mf(f),'bedroom-3',y,a,b,s)
 for f,x,a,b,s in [('E',455,121,145,'W'),('F',592,121,145,'E'),('B',456,993,1018,'W'),('A',593,993,1018,'E')]:v(n,mf(f),'bedroom-3-side',x,a,b,s)
 for f,y,a,b,s in [('D',337,94,180,'S'),('G',337,867,951,'S'),('C',794,94,180,'N'),('H',794,867,951,'N')]:h(n,mf(f),'bedroom-1',y,a,b,s)
 for f,x,a,b,s in [('D',81,429,460,'E'),('G',965,429,460,'W'),('C',81,672,701,'E'),('H',965,672,701,'W')]:v(n,mf(f),'bedroom-2',x,a,b,s)
 for f,y,a,b,s in [('D',517,123,149,'N'),('G',517,897,923,'N'),('C',614,123,150,'S'),('H',614,897,923,'S')]:h(n,mf(f),'bedroom-2-side',y,a,b,s)
# Tower 37 / 42: straight living side glazing; rectangular bay representation unresolved.
for n,fs in [(37,'GHDC'),(42,'CDHG')]:
 for f,x,a,b,s in zip(fs,[289,808,289,808],[242,242,892,892],[348,348,998,998],['E','W','E','W']):v(n,f,'living',x,a,b,s)
# Tower 34: two-sided inner bedrooms and secondary living glazing.
for f,y,a,b,s in [('B',445,269,304,'N'),('C',445,737,772,'N'),('A',727,269,304,'S'),('D',727,737,772,'S')]:h(34,f,'living-side',y,a,b,s)
for f,y,a,b,s in [('B',75,356,404,'S'),('C',75,640,686,'S'),('A',1097,356,404,'N'),('D',1097,640,686,'N')]:h(34,f,'bedroom-3',y,a,b,s)
for f,x,a,b,s in [('B',443,152,179,'W'),('C',598,152,179,'E'),('A',443,991,1019,'W'),('D',598,991,1019,'E')]:v(34,f,'bedroom-3-side',x,a,b,s)
# Tower 36: short living runs and inner bedrooms. Rectangular bay rooms unresolved.
for f,x,a,b,s in [('A',294,318,367,'E'),('B',803,318,367,'W'),('F',294,891,935,'E'),('E',803,891,935,'W')]:v(36,f,'living',x,a,b,s)
for f,y,a,b,s in [('H',384,214,253,'S'),('C',384,846,886,'S'),('G',868,214,253,'N'),('D',868,846,886,'N')]:h(36,f,'living',y,a,b,s)
for f,y,a,b,s in [('A',115,416,442,'S'),('B',115,651,679,'S'),('F',1140,416,442,'N'),('E',1140,651,679,'N')]:h(36,f,'bedroom-3',y,a,b,s)
for f,x,a,b,s in [('A',490,197,216,'W'),('B',607,197,216,'E'),('F',490,1053,1077,'W'),('E',607,1053,1077,'E')]:v(36,f,'bedroom-3-side',x,a,b,s)
# Source-overlay review corrections: actual jamb positions; no snapping to government edges.
for w in T[4]:
 if w['id']=='living-side' and w['flat'] in 'AB':
  dx=(762 if w['flat']=='A' else 453)-w['p1'][0]
  for k in ['p1','p2','interiorWitness']:w[k][0]+=dx
# North/south bedroom bay-base lines in 34 are a sill outline, not independently legible glazing.
T[34]=[w for w in T[34] if w['id']!='bedroom-3']
for f,x,a,b,side in [('E',571,637,667,'W'),('F',693,637,667,'E'),('B',577,1491,1514,'W'),('A',701,1491,1514,'E')]:v(1,f,'bedroom-3-side',x,a,b,side)
for f,x,a,b,side in [('D',572,668,692,'W'),('E',702,668,692,'E')]:v(7,f,'bedroom-3-side',x,a,b,side)
if __name__=='__main__':
 if (JOB/'manifest.json').exists():
  from cityOneBayWindows import extend_traces
  extend_traces(T)
 start=time.perf_counter();doc=read(JOB/'canonical-window-traces.json')
 for fam in doc['families']:
  n=int(fam['canonicalTower']);src=JOB/f'floorplans/H-{n}-typ.jpg';im=Image.open(src).convert('RGB');scale=np.array(im.size)/SIZES[n];windows=[]
  for w in T[n]:
   row={**w,**{k:(np.array(w[k])*scale).tolist() for k in ['p1','p2','interiorWitness']},'status':'source-traced','sourceExtentRole':w.get('sourceExtentRole','untrimmed visible straight glazing run'),'confidence':'visual-source-review'};windows.append(row)
  fam.update(traceStatus='source-glazing-and-approved-bay-faces-transcribed',sourceImageSize=list(im.size),sourceImageSha256=hashlib.sha256(src.read_bytes()).hexdigest(),referenceCanvas=SIZES[n],sourceRoi=(np.array(ROI[n])*np.tile(scale,2)).tolist(),windows=windows)
  d=ImageDraw.Draw(im)
  for w in windows:d.line([tuple(w['p1']),tuple(w['p2'])],fill='red',width=2);d.ellipse([w['interiorWitness'][0]-3,w['interiorWitness'][1]-3,w['interiorWitness'][0]+3,w['interiorWitness'][1]+3],fill='green')
  out=JOB/f'canonical/{fam["familyId"]}';out.mkdir(parents=True,exist_ok=True);im.save(out/'source-trace-overlay.png')
 doc.update(status='source-traced-awaiting-downstream-qa',tracedWindowCount=sum(len(f['windows']) for f in doc['families']));save(JOB/'canonical-window-traces.json',doc)
 save(JOB/'trace-timing.json',{'stage':'canonical-window-trace-output','seconds':time.perf_counter()-start,'note':'Measures artifact generation, not preceding visual inspection time.'})
 print(doc['tracedWindowCount'])
