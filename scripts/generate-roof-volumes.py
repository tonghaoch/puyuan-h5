"""Compile editable roof planes from native polygons, without reading any reference imagery.

Run after editing town-architecture.json. The saved vector volume data is consumed by
ordinary art generation, so daily rendering needs no geometry-processing dependencies.
"""
from pathlib import Path
import hashlib, json, math
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'src/data/town-architecture.json'
features=json.loads(source.read_text())['features']
guide_path=ROOT/'src/data/roof-guides.json'
guides=json.loads(guide_path.read_text())['roofs']
SCALE=3

def compile_volume(f):
    x,y,w,h=f['bounds']
    mask=np.zeros((h*SCALE+3,w*SCALE+3),np.uint8)
    def ring(points):return np.rint((np.array(points)-[x,y])*SCALE).astype(np.int32)
    cv2.fillPoly(mask,[ring(f['points'])],255)
    for hole in f['holes']:cv2.fillPoly(mask,[ring(hole)],0)
    yy,xx=np.where(mask>0)
    if not len(xx):return []
    px=xx.astype(np.float32)/SCALE+x;py=yy.astype(np.float32)/SCALE+y
    best=np.full(px.shape,np.inf,np.float32);owners=np.zeros(px.shape,np.int16)
    edges=[]
    outlines=guides.get(f['id'])
    if outlines is None:
        outlines=[cv2.approxPolyDP(np.array(f['points'],np.int32),min(1.9,max(.65,min(w,h)*.07)),True).reshape(-1,2).tolist()]
        outlines += [cv2.approxPolyDP(np.array(hole,np.int32),1,True).reshape(-1,2).tolist() for hole in f['holes'] if cv2.contourArea(np.array(hole,np.int32))>=50]
    for points in outlines:
        for a,b in zip(points,points[1:]+points[:1]):
            length=math.dist(a,b)
            if length<min(6,max(1.7,min(w,h)*.26)):continue
            ax,ay=a;bx,by=b;nx,ny=-(by-ay)/length,(bx-ax)/length
            mx,my=(ax+bx)/2,(ay+by)/2
            sx,sy=round((mx+nx*.8-x)*SCALE),round((my+ny*.8-y)*SCALE)
            if not (0<=sx<mask.shape[1] and 0<=sy<mask.shape[0] and mask[sy,sx]):nx,ny=-nx,-ny
            edges.append((length,a,b,nx,ny))
    if len(edges)<2:return []
    # Longer eaves get precedence at ties. The Voronoi split follows every courtyard
    # and return wing rather than treating an entire concave block as one gable.
    edges=sorted(edges,reverse=True)[:110]
    for index,(_,a,b,nx,ny) in enumerate(edges):
        ax,ay=a;bx,by=b;vx,vy=bx-ax,by-ay
        t=np.clip(((px-ax)*vx+(py-ay)*vy)/(vx*vx+vy*vy),0,1)
        distance=(px-ax-vx*t)**2+(py-ay-vy*t)**2
        update=distance<best
        best[update]=distance[update];owners[update]=index+1
    labels=np.zeros(mask.shape,np.int16);labels[yy,xx]=owners
    faces=[]
    for index,(_,a,b,nx,ny) in enumerate(edges):
        region=(labels==index+1).astype(np.uint8)
        contours,hierarchy=cv2.findContours(region,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:continue
        for ci,contour in enumerate(contours):
            area=cv2.contourArea(contour)/(SCALE*SCALE)
            if hierarchy[0,ci,3]>=0 or area<2:continue
            points=cv2.approxPolyDP(contour,.8,True).reshape(-1,2)
            if len(points)<3:continue
            holes=[];child=hierarchy[0,ci,2]
            while child>=0:
                if cv2.contourArea(contours[child])>SCALE*SCALE:
                    hole=cv2.approxPolyDP(contours[child],.8,True).reshape(-1,2)
                    if len(hole)>=3:holes.append(np.round(hole/SCALE+[x,y],2).tolist())
                child=hierarchy[0,child,0]
            faces.append({'points':np.round(points/SCALE+[x,y],2).tolist(),'holes':holes,
                          'shade':round(-nx*.62-ny*.78,3),'angle':round(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])),2)})
    return faces

volumes={}
for f in features:
    if f['kind'] not in ['roof','gold'] or f['area']<28:continue
    faces=compile_volume(f)
    if faces:volumes[f['id']]={'faces':faces}
target=ROOT/'src/data/roof-volumes.json'
target.write_text(json.dumps({'version':'native-eave-volumes-1','geometrySha256':hashlib.sha256(source.read_bytes()).hexdigest(),'guideSha256':hashlib.sha256(guide_path.read_bytes()).hexdigest(),'roofs':volumes},ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Compiled {sum(len(v["faces"]) for v in volumes.values())} native planes across {len(volumes)} roof footprints, retaining courtyards and holes.')
