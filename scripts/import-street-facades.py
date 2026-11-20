"""One-time authoring aid: observe plaster panels below native eaves. Not used by art:generate."""
import argparse, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from art.atlas_layout import PRINT_EXCLUSIONS
from art.contour_registration import matches_archived_contour

ROOT=Path(__file__).resolve().parents[1]
rgb=np.array(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB'))
gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
saturation=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)[:,:,1]
allowed=np.full(gray.shape,255,np.uint8)
for ring in PRINT_EXCLUSIONS:cv2.fillPoly(allowed,[np.array(ring,np.int32)],0)
atlas=json.loads((ROOT/'src/data/town-architecture.json').read_text())['features']
archive=json.loads((ROOT/'references/architecture/visible-surfaces.json').read_text())
study={record['id']:record for record in archive['features']}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,default=ROOT/'src/data/street-observations.json')
args=parser.parse_args()


def plaster_panels(feature):
    left,top,width,height=feature['bounds'];reach=min(12,max(4,round(width*.22)))
    region=np.zeros((height+reach,width),np.uint8)
    origin=np.array([left,top],np.int32)
    cv2.fillPoly(region,[np.array(feature['points'],np.int32)-origin],255)
    for hole in feature['holes']:cv2.fillPoly(region,[np.array(hole,np.int32)-origin],0)
    projected=np.zeros_like(region)
    for distance in range(1,reach+1):projected[distance:]|=region[:-distance]
    crop=np.s_[top:top+height+reach,left:left+width];intensity=gray[crop]
    light=(intensity>174)&(saturation[crop]<46)&(allowed[crop]>0)&(projected>0)&(region==0)
    contours,hierarchy=cv2.findContours(light.astype(np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    result=[]
    if hierarchy is None:return result
    for index,contour in enumerate(contours):
        if hierarchy[0,index,3]>=0 or cv2.contourArea(contour)<13:continue
        px,py,pw,ph=cv2.boundingRect(contour)
        if pw<4 or ph<3 or cv2.contourArea(contour)/(pw*ph)<.34:continue
        face=np.zeros_like(region);cv2.drawContours(face,[contour],0,255,-1)
        columns=np.where(face.any(axis=0))[0];bottom=len(face)-1-np.argmax(face[::-1,columns],axis=0)
        edge=bottom<len(face)-2
        if np.count_nonzero(edge)<2:continue
        ink=intensity[bottom[edge]+1,columns[edge]]<155
        if np.count_nonzero(ink)<max(2,len(columns)*.23):continue
        def polygon(curve):return (cv2.approxPolyDP(curve,.75,True).reshape(-1,2)+origin).tolist()
        outer=polygon(contour)
        if len(outer)<3:continue
        holes=[];child=hierarchy[0,index,2]
        while child>=0:
            if cv2.contourArea(contours[child])>=2.5:
                opening=polygon(contours[child])
                if len(opening)>=3:holes.append(opening)
            child=hierarchy[0,child,0]
        result.append({'points':outer,'holes':holes})
    return result


def timber_facings(feature):
    left,top,width,height=feature['bounds'];origin=np.array([left,top],np.int32)
    region=np.zeros((height,width),np.uint8)
    cv2.fillPoly(region,[np.array(feature['points'],np.int32)-origin],255)
    for hole in feature['holes']:cv2.fillPoly(region,[np.array(hole,np.int32)-origin],0)
    crop=np.s_[top:top+height,left:left+width]
    red,green,blue=np.moveaxis(rgb[crop].astype(np.int16),-1,0)
    timber=(red-green>=12)&(red-blue>=16)&(gray[crop]<156)&(allowed[crop]>0)&(region>0)
    contours,hierarchy=cv2.findContours(timber.astype(np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:return []
    result=[]
    for index,contour in enumerate(contours):
        if hierarchy[0,index,3]>=0 or cv2.contourArea(contour)<6:continue
        points=(cv2.approxPolyDP(contour,.55,True).reshape(-1,2)+origin).tolist()
        if len(points)<3:continue
        holes=[];child=hierarchy[0,index,2]
        while child>=0:
            if cv2.contourArea(contours[child])>=2:
                opening=(cv2.approxPolyDP(contours[child],.5,True).reshape(-1,2)+origin).tolist()
                if len(opening)>=3:holes.append(opening)
            child=hierarchy[0,child,0]
        result.append({'points':points,'holes':holes})
    return result


observations={}
for feature in atlas:
    if feature['kind'] not in ('roof','wood'):continue
    original=study[feature['id']]
    if not matches_archived_contour(feature,original,'roofClosing' not in archive):
        raise ValueError(f'Archived geometry does not match {feature["id"]}')
    finish=original['finishing'];entry={}
    if feature['kind']=='roof':
        brightness=np.mean(original['sourceColor'])
        entry['slate']=min(5,max(0,round((brightness-64)/9)))
        shadows=[ring for ring in finish['sourceShadePatches'] if cv2.contourArea(np.array(ring,np.int32))>=8]
        if shadows:entry['shade']=shadows
        panels=plaster_panels(feature)
        if panels:entry['plaster']=panels
        timber=timber_facings(feature)
        if timber:entry['timber']=timber
    seams=finish['sourceRelief']['seams']
    if seams:entry['ink']=seams
    if entry:observations[feature['id']]=entry
output={'coordinateSpace':'illustration-plane','surfaces':observations}
args.out.write_text(json.dumps(output,separators=(',',':'))+'\n')
print('Observed',len(observations),'surfaces;',sum(len(entry.get('plaster',[])) for entry in observations.values()),'plaster panels with an independently visible lower edge.')
