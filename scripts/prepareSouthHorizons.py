"""Cache inventory and independent raster outlines from approved tower sheets."""
import json,time,hashlib,copy
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];JOB=ROOT/'data/south-horizons-approved-job'
def save(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
job=read(JOB/'approved-job.json')
names=['Hoi Sing','Hoi Fai','Hoi Ngar','Hoi Wan','Hoi Ning','Hoi Yat','Yee Mei','Yee King','Yee Ngar','Yee Lai','Yee Fung','Yee Moon','Yee Lok','Yee Fai','Yee Wan','Yee Tsui','Mei Fai','Mei Hay','Mei Hong','Mei Cheung','Mei Chun','Mei Wah','Mei Hin','Mei Ka','Dover','Eaton','Fenton','Grosvenor','Fung King','Wai King','Pak King','Albany','Berkeley','Cambridge']
# ROIs transcribed on 490x555 thumbnails, removing header/footer, insets and site plans.
rois=[[25,50,320,355],[35,50,317,345],[40,35,442,450],[50,43,434,440],[50,43,438,440],[48,43,430,440],[22,60,315,335],[22,50,315,326],[24,56,309,329],[40,52,334,333],[20,28,247,250],[29,45,325,329],[12,28,247,257],[30,62,319,338],[25,62,320,340],[29,56,316,334],[12,27,480,447],[24,34,444,464],[29,30,429,437],[21,30,474,463],[18,20,480,465],[28,31,456,464],[31,30,449,466],[29,31,455,467],[45,110,385,445],[47,100,390,440],[49,99,394,440],[45,107,398,433],[43,58,435,436],[41,57,430,428],[43,67,421,426],[30,107,377,442],[48,101,388,423],[47,101,375,419]]
raw=read(JOB/'neighborhood-query.raw.json')
query='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query?where=1%3D1&geometry=%7B%22xmin%22%3A114.143%2C%22ymin%22%3A22.238%2C%22xmax%22%3A114.152%2C%22ymax%22%3A22.247%7D&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&outSR=4326&f=json'
summary=[]
for tower,name,roi in zip(job['estate']['blockIds'],names,rois):
 start=time.perf_counter();it=next(i for i in job['primaryFloorPlanSource']['items'] if i['blocks']==[tower] and i['planRole']=='typical');p=JOB/'floorplans/primary'/f'{it["id"]}.jpg';im=Image.open(p).convert('RGB');thumb=min(490/im.width,555/im.height)
 box=tuple(round(v/thumb) for v in roi);crop=im.crop(box);crop.thumbnail((1000,1000));out=ROOT/f'data/south-horizons-tower-{tower.lower()}';out.mkdir(exist_ok=True)
 crop.save(out/'plan-crop.png');rgb=np.array(crop);hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
 mask=((hsv[:,:,1]>20)&(hsv[:,:,2]>65)&(hsv[:,:,0]>17)&(hsv[:,:,0]<120)).astype('uint8')*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
 cv2.rectangle(mask,(int(crop.width*.36),int(crop.height*.33)),(int(crop.width*.67),int(crop.height*.68)),255,-1)
 contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);contour=max(contours,key=cv2.contourArea);outline=cv2.approxPolyDP(contour,2.5,True).reshape(-1,2).tolist()
 a={'tower':tower,'canvas':list(crop.size),'source':it['previewUrl'],'sourcePage':job['primaryFloorPlanSource']['sourcePage'],'floorCoverage':it['floorCoverage'],'sourceId':it['id'],'cropInSourcePixels':box,'sourceImageSize':list(im.size),'outline':outline,'outlineMethod':'Independent colour-fill contour, morphology closing and 2.5px simplification; review overlay before publication','rooms':{},'templateId':it['id'],'reflected':False}
 save(out/'annotations.json',a)
 d=ImageDraw.Draw(crop);d.line([tuple(p) for p in outline+[outline[0]]],fill='red',width=2);crop.save(out/'outline-check.png')
 matches=[f for f in raw['features'] if f['attributes'].get('BuildingNameEN')==name+' Court'];assert len(matches)==1,(tower,name,len(matches));o=copy.deepcopy(matches[0]);o['provenance']={'source':'LandsD CSDI Building FSDT','queryUrl':query,'rawFile':str((JOB/'neighborhood-query.raw.json').relative_to(ROOT)),'rawSha256':hashlib.sha256((JOB/'neighborhood-query.raw.json').read_bytes()).hexdigest(),'selectionRule':'Exact individual court name from approved labelled estate screenshots','outputCRS':'EPSG:4326'};save(out/'official-footprint.json',o)
 summary.append({'tower':tower,'name':name+' Court','csuid':o['attributes']['BuildingCSUID'],'sourceId':it['id'],'floorCoverage':it['floorCoverage'],'plan-parse':time.perf_counter()-start})
save(JOB/'preparation.json',summary)
