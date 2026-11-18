"""Read visible source marks to enrich roof/facade finishes, without changing any contour."""
from pathlib import Path
import hashlib, json, math
import cv2
import numpy as np
from PIL import Image
from art.source_relief import source_relief
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'references/architecture/visible-surfaces.json'
data=json.loads(path.read_text())
rgb=np.array(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB'))
gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
geometry_keys=['id','kind','points','holes','bounds','owner']
before=json.dumps([{key:f[key] for key in geometry_keys} for f in data['features']],sort_keys=True,separators=(',',':'))
counts={'observedRoofMarks':0,'roofShadePatches':0,'observedOpenings':0,'sourceTonePatches':0,'sourceInkLines':0}
for f in data['features']:
    x,y,w,h=f['bounds']
    polygon=np.array(f['points'],np.int32)-np.array([x,y])
    region=np.zeros((h,w),np.uint8);cv2.fillPoly(region,[polygon],255)
    for hole in f['holes']: cv2.fillPoly(region,[np.array(hole,np.int32)-np.array([x,y])],0)
    gray_crop=gray[y:y+h,x:x+w];hsv_crop=hsv[y:y+h,x:x+w]
    marks=[];shade=[];openings=[]
    if f['kind'] in ['roof','gold']:
        bright=((gray_crop>137)&(hsv_crop[:,:,1]<105)&(region>0)).astype(np.uint8)*255
        segments=cv2.HoughLinesP(bright,1,np.pi/180,threshold=5,minLineLength=5,maxLineGap=1)
        if segments is not None:
            candidates=[]
            for x1,y1,x2,y2 in np.asarray(segments).reshape(-1,4):
                length=math.hypot(int(x2)-int(x1),int(y2)-int(y1))
                if length>=5: candidates.append((length,[[int(x1)+x,int(y1)+y],[int(x2)+x,int(y2)+y]]))
            marks=[points for _,points in sorted(candidates,reverse=True)[:10]]
        samples=gray_crop[region>0]
        if samples.size:
            threshold=float(np.percentile(samples,35))
            shadow=((gray_crop<threshold)&(region>0)).astype(np.uint8)*255
            shadow=cv2.morphologyEx(shadow,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
            shadow[region==0]=0
            contours,_=cv2.findContours(shadow,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            for contour in sorted(contours,key=cv2.contourArea,reverse=True)[:6]:
                if cv2.contourArea(contour)<6: continue
                points=cv2.approxPolyDP(contour,.55,True).reshape(-1,2)
                if len(points)>=3:shade.append((points+np.array([x,y])).tolist())
    if f['kind'] in ['wall','wood'] and min(w,h)<25:
        for hole in f['holes']:
            points=np.array(hole,np.int32)
            hx,hy,hw,hh=cv2.boundingRect(points)
            area=cv2.contourArea(points)
            if not (2<=hw<=9 and 3<=hh<=13 and 3<=area<=65): continue
            hm=np.zeros((hh,hw),np.uint8);cv2.fillPoly(hm,[points-np.array([hx,hy])],255)
            brightness=gray[hy:hy+hh,hx:hx+hw][hm>0]
            saturation=hsv[hy:hy+hh,hx:hx+hw,1][hm>0]
            if brightness.size and np.median(brightness)<115 and np.median(saturation)<120:
                openings.append({'points':hole,'bounds':[hx,hy,hw,hh]})
    relief=source_relief(gray_crop,region,(x,y),f['kind'])
    f['finishing']={'observedRoofMarks':marks,'sourceShadePatches':shade,'observedOpenings':openings,'sourceRelief':relief}
    counts['sourceTonePatches']+=len(relief['tones']);counts['sourceInkLines']+=len(relief['seams'])
    counts['observedRoofMarks']+=len(marks);counts['roofShadePatches']+=len(shade);counts['observedOpenings']+=len(openings)
path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
geometry=[{key:f[key] for key in geometry_keys} for f in data['features']]
assert before==json.dumps(geometry,sort_keys=True,separators=(',',':')), 'Finishing must not alter source geometry'
(ROOT/'references/architecture/finishing-audit.json').write_text(json.dumps({'version':'source-relief-2026-11-18','source':data['source_sha256'],'surfaces':len(data['features']),'geometry_sha256':hashlib.sha256(json.dumps(geometry,sort_keys=True,separators=(',',':')).encode()).hexdigest(),**counts,'note':'Source tones and ink lines guide visual finishes inside existing surfaces. They are not new surveyed buildings, openings, or coordinates.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(counts))
