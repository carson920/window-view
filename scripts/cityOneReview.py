"""English callouts outside the source outline, with collision-tested boxes."""
import json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

def render(source, windows, outline, output):
    src=Image.open(source).convert('RGB') if not isinstance(source,Image.Image) else source.copy()
    margin=240
    im=Image.new('RGB',(src.width+2*margin,src.height+2*margin),'white');im.paste(src,(margin,margin))
    d=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
    contour=np.array(outline,dtype=np.float32);boxes=[]
    for w in windows:
        p1,p2,inside=[np.array(w[k],float) for k in ['p1','p2','interiorWitness']]
        mid=(p1+p2)/2; tangent=p2-p1;normal=np.array([-tangent[1],tangent[0]])/np.linalg.norm(tangent)
        if np.dot(normal,inside-mid)>0:normal=-normal
        text=w['flat']+' '+w['id'].replace('bedroom-','bed-')
        size=d.textbbox((0,0),text,font=font);bw=size[2]+16;bh=30;chosen=None
        for dist in range(60,1800,20):
            for sideways in [0,-25,25,-50,50,-100,100]:
                center=mid+normal*dist+np.array([-normal[1],normal[0]])*sideways+margin
                b=[center[0]-bw/2,center[1]-bh/2,center[0]+bw/2,center[1]+bh/2]
                if min(b[:2])<8 or b[2]>im.width-8 or b[3]>im.height-8:continue
                if any(not(b[2]+6<x['box'][0] or b[0]-6>x['box'][2] or b[3]+6<x['box'][1] or b[1]-6>x['box'][3]) for x in boxes):continue
                probes=[(x-margin,y-margin) for x in np.linspace(b[0],b[2],5) for y in [b[1],(b[1]+b[3])/2,b[3]]]
                if any(cv2.pointPolygonTest(contour,p,False)>=0 for p in probes):continue
                chosen=b;break
            if chosen:break
        if chosen is None:raise ValueError('No collision-free outward label: '+text)
        b=chosen;center=((b[0]+b[2])/2,(b[1]+b[3])/2)
        d.line([tuple(mid+margin),center],fill='#b84535',width=1)
        d.rectangle(b,fill='white',outline='#aa3e32',width=1);d.text((b[0]+8,b[1]+3),text,font=font,fill='#182f38')
        d.line([tuple(p1+margin),tuple(p2+margin)],fill='#ef2525',width=3)
        p=inside+margin;d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill='green')
        boxes.append({'flat':w['flat'],'room':w['id'],'text':text,'box':b,'windowMidpoint':(mid+margin).tolist(),'outwardNormal':normal.tolist()})
    im.save(output)
    output.with_suffix('.labels.json').write_text(json.dumps({'imageSize':im.size,'padding':margin,'labels':boxes,'collisionCount':0},indent=2)+'\n')
