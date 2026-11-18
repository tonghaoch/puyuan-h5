"""One-time layout transcription. Saved town-landscape.json is the editable authoring source.

This command reads the reference; the native landscape generator never does.
"""
from pathlib import Path
import json, math
import cv2
import numpy as np
from PIL import Image
from art.atlas_layout import PRINT_EXCLUSIONS

ROOT = Path(__file__).resolve().parents[1]
layout = json.loads((ROOT/'src/data/reference-map.json').read_text())
rgb = np.array(Image.open(ROOT/layout['source']).convert('RGB'))
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
scope = np.zeros(gray.shape, np.uint8)
cv2.fillPoly(scope, [np.array(layout['scope'], np.int32)], 255)
r,g,b = [rgb[:,:,i].astype(float) for i in range(3)]

def polygons(mask, minimum=30, tolerance=1):
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    result=[]
    if hierarchy is None:return result
    for i,c in enumerate(contours):
        if hierarchy[0,i,3]>=0 or cv2.contourArea(c)<minimum:continue
        points=cv2.approxPolyDP(c,tolerance,True).reshape(-1,2)
        if len(points)<3:continue
        holes=[];child=hierarchy[0,i,2]
        while child>=0:
            if cv2.contourArea(contours[child])>=minimum:
                hole=cv2.approxPolyDP(contours[child],tolerance,True).reshape(-1,2)
                if len(hole)>=3:holes.append(hole.tolist())
            child=hierarchy[0,child,0]
        result.append({'points':points.tolist(),'holes':holes})
    return result

water = ((g>r*1.16)&(b>r*1.18)&(b>110)&(g>110)&(scope>0)).astype(np.uint8)*255
# Glazed atria are buildings, rather than ponds.
for box in [(684,350,766,413),(790,326,831,401)]:cv2.rectangle(water,box[:2],box[2:],0,-1)
water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
water[scope==0]=0
paving=((gray>140)&(gray<245)&(hsv[:,:,1]<48)&(scope>0)&(water==0)).astype(np.uint8)*255
paving=cv2.morphologyEx(paving,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
annotations=np.zeros_like(scope)
for points in PRINT_EXCLUSIONS:cv2.fillPoly(annotations,[np.array(points,np.int32)],255)
paving[annotations>0]=0

# Canopy centres and sizes are transcribed once; every branch and leaf is drawn natively.
tree_masks=[('willow',((hsv[:,:,0]>30)&(hsv[:,:,0]<86)&(hsv[:,:,1]>65)&(hsv[:,:,2]>85))),
            ('blossom',((r>g*1.09)&(b>g*1.04)&(r>145))),
            ('ginkgo',((hsv[:,:,0]>15)&(hsv[:,:,0]<31)&(hsv[:,:,1]>95)&(hsv[:,:,2]>130)))]
trees=[]
for kind,mask in tree_masks:
    mask=(mask&(scope>0)&(water==0)).astype(np.uint8)*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    distance=cv2.distanceTransform(mask,cv2.DIST_L2,5)
    peaks=(distance>=cv2.dilate(distance,np.ones((13,13),np.uint8))-.01)&(distance>2.8)
    _,_,stats,centres=cv2.connectedComponentsWithStats(peaks.astype(np.uint8))
    candidates=[]
    for i,(cx,cy) in enumerate(centres[1:],1):
        radius=float(distance[round(cy),round(cx)])
        candidates.append((radius,cx,cy))
    for radius,cx,cy in sorted(candidates,reverse=True):
        if any(math.hypot(cx-t['x'],cy-t['crownY'])<max(7,radius*.9) for t in trees):continue
        size=round(max(.35,min(1.35,radius/9)),2)
        trees.append({'id':f'tree-{len(trees)}','x':round(cx,1),'y':round(cy+17*size,1),'crownY':round(cy,1),'scale':size,'kind':kind})

# Ground paths and crossings are authored, with no pixels carried into the render.
walks=[
 {'id':'south-promenade','d':'M157 1298Q565 1308 838 1267T1292 1225','width':14},
 {'id':'west-quay','d':'M482 563Q449 739 490 884L503 987Q449 1045 333 1086Q265 1122 247 1236','width':10},
 {'id':'central-street','d':'M520 992Q694 975 840 927T1113 889L1232 862','width':12},
 {'id':'east-quay','d':'M1280 411Q1310 577 1285 690T1192 913Q1148 1091 1154 1224','width':9},
 {'id':'temple-court','d':'M914 705L930 821','width':11},
 {'id':'fuma-lane','d':'M581 718Q693 723 796 680','width':8},
 {'id':'south-lane','d':'M340 1199Q552 1223 776 1180L1001 1118','width':8},
]
crossings=[(1242,393,43,9,83),(1404,494,29,6,-6),(959,545,44,7,-24),
           (999,651,29,6,-37),(844,676,30,6,-13),(817,711,26,6,40),
           (590,690,20,5,-12),(603,823,24,6,-8),(825,878,42,8,-17),
           (1210,959,47,8,7),(1194,849,30,7,0),(1017,909,24,6,71),
           (628,1122,22,6,1),(555,1181,24,6,86),(270,1215,24,6,-4),
           (286,1280,23,6,-2),(734,1218,24,6,78)]
bridges=[{'id':f'bridge-{i}','x':x,'y':y,'length':length,'width':width,'angle':angle,'material':'stone' if i%4 else 'timber'} for i,(x,y,length,width,angle) in enumerate(crossings)]
gardens=[
 {'id':'oval-lawn','d':'M1126 699C1120 649 1185 641 1195 690L1202 738C1212 789 1142 796 1135 752Z','kind':'lawn'},
 {'id':'temple-east-garden','d':'M1037 606Q1083 601 1101 640L1090 754Q1102 800 1084 847L1031 834Q1060 782 1036 744Q1026 705 1041 670Z','kind':'garden'},
]
for i in range(38):
    # Designed park planting replaces typography in the central garden.
    rr=np.random.default_rng(20261118+i);cx=float(rr.uniform(1042,1092));cy=float(rr.uniform(630,832))
    trees.append({'id':f'park-tree-{i}','x':round(cx,1),'y':round(cy,1),'crownY':round(cy-13,1),'scale':round(float(rr.uniform(.48,.85)),2),'kind':'blossom' if i%4==0 else 'willow'})
data={'version':'native-landscape-1','coordinateSpace':'illustration-plane','scene':layout['scene'],'offset':layout['sourceOffset'],
      'scope':layout['scope'],'water':polygons(water,18,1.05),'paving':polygons(paving,65,1.1),
      'walks':walks,'bridges':bridges,'trees':trees,'gardens':gardens,
      'waterConnections':[],
      'note':'Editable illustration geometry. Reference transcribed once; rendering is independent. Ground connections and obscured areas are artistic completions, not surveyed geography.'}
target=ROOT/'src/data/town-landscape.json'
target.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Saved {len(data["water"])} water polygons, {len(data["paving"])} paving regions, {len(trees)} native tree instances and {len(bridges)} bridges.')
