"""Locate unreviewed building clusters on the full map; only for offline visual comparison."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from art.atlas_layout import PRINT_EXCLUSIONS, ZONES
from art.scene import compose_scene
from art.street_houses import street_areas

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,default=ROOT/'artifacts/remaining-streets')
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)


def read(name):
    return json.loads((ROOT/'src/data'/name).read_text())


frame=read('reference-map.json');offset=frame['sourceOffset'];extent=frame['scene']
origin=np.array([-offset['x'],-offset['y']]);size=(extent['width'],extent['height'])
original=Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB').crop((*origin,*(origin+size)))
native=compose_scene().convert('RGB');scale=native.width//size[0]
mask=np.zeros(size[::-1],np.uint8)
for feature in read('town-architecture.json')['features']:
    if feature['kind'] not in ('roof','wood','gold'):continue
    rings=[feature['points'],*feature['holes']]
    cv2.fillPoly(mask,[np.int32(ring-origin) for ring in rings],1)
mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
park=np.zeros_like(mask);cv2.fillPoly(park,[np.int32(frame['scope']-origin)],1)
for ring in PRINT_EXCLUSIONS:cv2.fillPoly(park,[np.int32(ring-origin)],0)
for groups in street_areas(read('street-houses.json')).values():
    for group in groups:
        for ring in group['replace']:cv2.fillPoly(park,[np.int32(ring-origin)],0)
mask&=park


def dark(image):
    return np.array(image.convert('L').resize(size,Image.Resampling.LANCZOS))<145


source=dark(original);current=dark(native);rows=[];missing=[];step=64
red,green,blue=np.moveaxis(np.array(original,dtype=np.int16),-1,0)
wood=(red-green>=12)&(red-blue>=16)&source&(park>0)
near_wood=cv2.dilate(wood.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(17,17)))>0
slate=(np.maximum.reduce([red,green,blue])-np.minimum.reduce([red,green,blue])<38)&(green<=red+5)&(green<=blue+6)&source&near_wood&(park>0)
coherent=cv2.morphologyEx(slate.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))>0
absent=coherent&(cv2.dilate(current.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))==0)
for top in range(0,size[1],step):
    for left in range(0,size[0],step):
        right=min(left+step,size[0]);bottom=min(top+step,size[1]);window=np.s_[top:bottom,left:right]
        usable=mask[window]>0;before=source[window]&usable;after=current[window]&usable
        x,y=(origin+[left,top]).tolist();width,height=right-left,bottom-top
        site=next((key for key,_,_,(xmin,ymin,xmax,ymax) in ZONES if xmin<=x+width/2<xmax and ymin<=y+height/2<ymax),'street')
        entry={'bounds':[x,y,width,height],'zone':site}
        if absent[window].sum()>=25:missing.append({**entry,'unmatchedPixels':int(absent[window].sum())})
        if before.sum()>=150:rows.append({**entry,'evidencePixels':int(before.sum()),'iou':round(float((before&after).sum()/(before|after).sum()),3)})
rows.sort(key=lambda row:(row['iou'],-row['evidencePixels']))
missing.sort(key=lambda row:-row['unmatchedPixels'])


def separated(ranking):
    selected=[]
    for row in ranking:
        x,y,*_=row['bounds']
        if any(max(abs(x-other['bounds'][0]),abs(y-other['bounds'][1]))<=step for other in selected):continue
        selected.append(row)
        if len(selected)==8:break
    return selected


shortlist=separated(rows);omissions=separated(missing)
report={'cellSize':step,'minimumEvidencePixels':150,'evaluatedCells':len(rows),'shortlist':shortlist,'cells':rows,'possibleOmissions':omissions}
(args.out/'survey.json').write_text(json.dumps(report,indent=2)+'\n')
for stem,selected in [('shortlist',shortlist),('possible-omissions',omissions)]:
    if not selected:continue
    sheet=Image.new('RGB',(800,187*((len(selected)+1)//2)),'#edeadd');draw=ImageDraw.Draw(sheet)
    locator=original.copy();markers=ImageDraw.Draw(locator)
    for index,row in enumerate(selected):
        x,y,width,height=row['bounds'];left,top=(np.array([x,y])-origin).tolist();box=(left,top,left+width,top+height)
        col=index%2*400;band=index//2*187
        draw.text((col+4,band+2),f"{index+1}. {row['zone']} ({x},{y})   Reference / Native",fill='#3e3936')
        for side,crop in enumerate([original.crop(box),native.crop(tuple(value*scale for value in box))]):
            sheet.paste(crop.resize((165,165),Image.Resampling.LANCZOS),(col+side*174+6,band+18))
        markers.rectangle(box,outline='#c43f30',width=3);markers.text((left+3,top+3),str(index+1),fill='#fff',stroke_width=2,stroke_fill='#7d2827')
    sheet.save(args.out/(stem+'.jpg'),quality=94);locator.thumbnail((950,775));locator.save(args.out/(stem+'-locations.jpg'),quality=92)

authored=set(read('street-houses.json')['sites'])|set(read('landmark-structures.json')['sites'])
remaining=[model for model in read('landmark-models.json')['models'] if model['id'] not in authored]
if remaining:
    sheet=Image.new('RGB',(800,len(remaining)*280),'#edeadd');draw=ImageDraw.Draw(sheet)
    for index,model in enumerate(remaining):
        left,top,width,height=model['sourceBounds'];left-=origin[0];top-=origin[1];box=(left,top,left+width,top+height)
        band=index*280;draw.text((6,band+3),model['id']+'   Reference / Native',fill='#3e3936')
        zoom=min(390/width,250/height);size=(round(width*zoom),round(height*zoom))
        for side,crop in enumerate([original.crop(box),native.crop(tuple(value*scale for value in box))]):
            sheet.paste(crop.resize(size,Image.Resampling.LANCZOS),(side*400+(400-size[0])//2,band+20))
    sheet.save(args.out/'remaining-landmarks.jpg',quality=94)
print(f'{len(rows)} cells with remaining roof/timber evidence; {len(shortlist)} alignment and {len(omissions)} omission candidates saved to {args.out}')
