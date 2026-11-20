"""Trace every source-visible architectural surface; never invent geographical coordinates.
The masks are an art-production aid, not a count of physical buildings or a survey.
"""
from pathlib import Path
import json, math, hashlib
import cv2
import numpy as np
from PIL import Image
from art.atlas_layout import ZONES, PRINT_EXCLUSIONS
from art.landscape import quay_edge
from art.contour_registration import close_roof_gaps
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'references/puyuan-reference.jpg'
rgb=np.array(Image.open(source).convert('RGB'))
hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
manifest=json.loads((ROOT/'src/data/reference-map.json').read_text())
scope=np.zeros(gray.shape,np.uint8);cv2.fillPoly(scope,[np.array(manifest['scope'],np.int32)],255)
labels=np.zeros_like(scope)
for polygon in PRINT_EXCLUSIONS: cv2.fillPoly(labels,[np.array(polygon,np.int32)],255)
town=json.loads((ROOT/'src/data/town-landscape.json').read_text())
for region in town['water']:
    for quay in region.get('bankFaces',[]):
        edge=quay_edge(region,quay);top=[(x,y-quay['height']-.6) for x,y in edge]
        cv2.fillPoly(labels,[np.int32(np.rint(edge+top[::-1]))],255)
allowed=(scope>0)&(labels==0)
r,g,b=rgb[:,:,0].astype(float),rgb[:,:,1].astype(float),rgb[:,:,2].astype(float)
roof=((gray<121)&(hsv[:,:,1]<92)&(g<r*1.17+2)&allowed).astype(np.uint8)*255
roof=close_roof_gaps(roof)
roof[~allowed]=0
# Gold roof in the temple. The constrained region prevents paths and tree trunks being treated as gold tile.
gold=np.zeros_like(roof)
gold_region=np.zeros_like(roof);cv2.rectangle(gold_region,(868,633),(979,691),255,-1)
gold[((r>g*1.12)&(g>b*1.15)&(r>125)&(gold_region>0)&allowed)]=255
gold=close_roof_gaps(gold);roof[gold>0]=0
near=cv2.dilate(roof|gold,np.ones((11,9),np.uint8))>0
wall=((gray>147)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<42)&near&allowed).astype(np.uint8)*255
wood=((r>g*1.18)&(g>b*.94)&(gray>35)&(gray<160)&near&allowed).astype(np.uint8)*255
# Glazed atria are explicitly bounded to the visitor-centre site.
glass_region=np.zeros_like(roof)
for box in [(684,350,766,413),(790,326,831,401)]: cv2.rectangle(glass_region,box[:2],box[2:],255,-1)
glass=((b>r*1.06)&(g>r*1.06)&(gray>85)&(glass_region>0)&allowed).astype(np.uint8)*255
# Keep the tower for the evidence-based custom silhouette; exclude it from automatic roof hatching.
for mask in [roof,wall,wood,gold,glass]: cv2.rectangle(mask,(878,450),(952,599),0,-1)
features=[]
coverage=np.zeros_like(roof)
for kind,mask,minimum in [('wall',wall,9),('wood',wood,8),('roof',roof,8),('gold',gold,5),('glass',glass,5)]:
    contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None: continue
    for index,contour in enumerate(contours):
        if hierarchy[0,index,3]>=0: continue
        area=cv2.contourArea(contour)
        if area<minimum: continue
        x,y,w,h=cv2.boundingRect(contour)
        if w<2 or h<2: continue
        perimeter=cv2.arcLength(contour,True)
        if area/(w*h)<.18 and area/max(1,perimeter)<1.6: continue
        if (w>h*12 and h<4) or (h>w*12 and w<4): continue
        outer=cv2.approxPolyDP(contour,.45,True).reshape(-1,2)
        if len(outer)<3: continue
        # Fine voids on roofs are tile marks; retain larger courtyard holes and wall windows.
        holes=[];child=hierarchy[0,index,2]
        while child>=0:
            if cv2.contourArea(contours[child])> (5 if kind=='wall' else 12):
                holes.append(cv2.approxPolyDP(contours[child],.4,True).reshape(-1,2).tolist())
            child=hierarchy[0,child,0]
        pixel_mask=np.zeros_like(mask);cv2.drawContours(pixel_mask,[contour],-1,255,-1)
        for hole in holes: cv2.fillPoly(pixel_mask,[np.array(hole,np.int32)],0)
        samples=rgb[pixel_mask>0]
        color=np.median(samples,axis=0).round().astype(int).tolist()
        center=[x+w/2,y+h/2]
        owner=None
        # Own each visible surface exactly once, even where group bounds overlap.
        candidates=[]
        for order,(key,place,name,box) in enumerate(ZONES):
            if key=='temple-pagoda': continue
            if box[0]<=center[0]<=box[2] and box[1]<=center[1]<=box[3] and x>=box[0]-8 and y>=box[1]-8 and x+w<=box[2]+8 and y+h<=box[3]+8:
                candidates.append(((box[2]-box[0])*(box[3]-box[1]),order,key))
        if candidates: owner=min(candidates)[2]
        rect=cv2.minAreaRect(contour);angle=float(rect[2])
        if rect[1][0]<rect[1][1]: angle+=90
        feature={'id':f'{kind}-{len(features)}','kind':kind,'points':outer.tolist(),'holes':holes,'bounds':[x,y,w,h],'area':round(area,2),'angle':round(angle,2),'sourceColor':color,'owner':owner}
        features.append(feature)
        coverage[pixel_mask>0]=255
# Save a geometry snapshot and a visual review overlay for auditability.
out=ROOT/'references/architecture';out.mkdir(exist_ok=True)
(out/'visible-surfaces.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'coordinateSpace':'reference-image-pixels','roofClosing':'balanced','features':features},ensure_ascii=False,separators=(',',':')))
overlay=rgb.copy();paint=overlay.astype(float)
paint[coverage>0]=paint[coverage>0]*.4+np.array([100,190,155])*.6
Image.fromarray(paint.astype(np.uint8)).crop((120,260,1460,1340)).save(out/'surface-coverage.jpg',quality=93)
Image.fromarray(labels).save(out/'annotation-mask.png')
counts={kind:sum(f['kind']==kind for f in features) for kind in ['roof','gold','wood','wall','glass']}
(out/'coverage-summary.json').write_text(json.dumps({'counts':counts,'surfaces':len(features),'visibleSurfacePixels':int((coverage>0).sum()),'namedGroups':len(ZONES),'unassignedSurfaces':sum(f['owner'] is None for f in features),'note':'Counts describe traced visible surfaces, not physical buildings. Hidden details are not measured.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(counts), 'total surfaces:',len(features))
