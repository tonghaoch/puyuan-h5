"""Propose small adjustments to hand-measured eaves using only visible roof and timber evidence."""
import argparse, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from art.atlas_layout import PRINT_EXCLUSIONS
from art.street_houses import street_areas

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output',type=Path,help='A separate candidate JSON file for review; does not replace the authored data')
parser.add_argument('--site',action='append',default=[],help='Only propose changes for this site; repeat to select multiple sites')
args=parser.parse_args();source=ROOT/'src/data/street-houses.json'
if args.output.resolve()==source.resolve():parser.error('Use a separate proposal file')
data=json.loads(source.read_text());rgb=np.array(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB'))
areas=street_areas(data)
if set(args.site)-areas.keys():parser.error('Unknown site: '+', '.join(sorted(set(args.site)-areas.keys())))
gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);sat=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)[:,:,1]
red,green,blue=np.moveaxis(rgb.astype(np.int16),-1,0)
wood=(red-green>=12)&(red-blue>=16)&(gray<155)
tile=(gray<138)&(sat<96)&~wood
valid=np.full(gray.shape,255,np.uint8)
for ring in PRINT_EXCLUSIONS:cv2.fillPoly(valid,[np.int32(ring)],0)


def project(values,kind):
    start,end=values[:2],values[2:4];rear=values[4:6];rise,height=values[6:];up=np.array([0.,-rise]);down=np.array([0.,height]);axis=end-start
    inset=.19 if kind in ('canopy','hall') else .13 if kind=='temple' else .025
    ridge=start+axis*inset+rear/2+up;ridge_end=end-axis*inset+rear/2+up
    close_end=end-axis*.035 if rear[0]>=0 else start+axis*.035
    roof=np.array([start,end,end+rear,ridge_end,ridge,start+rear]);roof=cv2.convexHull(roof.astype(np.float32)).reshape(-1,2)
    front=np.array([start+axis*.035,end-axis*.035,end-axis*.035+down,start+axis*.035+down])
    gable=np.array([close_end,close_end+rear/2+up,close_end+rear,close_end+rear+down,close_end+down])
    return roof,front,gable


def fit(model):
    kind=model[-1];seed=np.array(model[:8],np.float64)
    if kind in ('temple','temple-portico','canopy'):return model
    geometry=np.vstack(project(seed,kind));origin=np.floor(geometry.min(axis=0)).astype(int)-7
    cols,rows=(np.ceil(geometry.max(axis=0)).astype(int)-origin+8)
    x,y=origin;area=np.s_[y:y+rows,x:x+cols];usable=valid[area]>0;slate=tile[area];timber=wood[area]
    def masks(values):
        state=np.zeros((rows,cols),np.uint8);roof,front,gable=project(values,kind)
        for points,material in [(gable,1),(front,1 if kind in ('plaster','gable','blind-wall') else 2),(roof,3)]:
            cv2.fillPoly(state,[np.int32(np.rint((points-origin)*16))],material,shift=4)
        return state
    first=masks(seed);occupied=first>0
    if np.count_nonzero(usable&occupied)<.72*occupied.sum():return model
    zone=usable&(cv2.dilate(occupied.astype(np.uint8),np.ones((7,7),np.uint8))>0)
    def overlap(first,second):
        return np.count_nonzero(zone&first&second)/max(1,np.count_nonzero(zone&(first|second)))
    def score(values):
        state=masks(values);dark=(state>=2);facade=state==2
        delta=values-seed
        penalty=.002*np.sum(delta[:6]**2)+.003*np.sum(delta[6:]**2)
        result=.54*overlap(state==3,slate)+.4*overlap(dark,slate|timber)
        if kind not in ('plaster','gable','blind-wall'):result+=.18*overlap(facade,timber)
        return result-penalty
    basis=np.eye(8);moves=[basis[0]+basis[2],basis[1]+basis[3],basis[0],basis[1],basis[2],basis[3],basis[4],basis[5],basis[6],basis[7]]
    best=seed.copy();value=score(best);initial=value
    for step in (1.5,.75,.4):
        for cycle in range(3):
            previous=value
            for move in moves:
                candidate=best.copy()
                for sign in (-1,1):
                    trial=best+move*step*sign
                    if np.any(np.abs(trial-seed)>3.1) or trial[6]<1 or trial[7]<2:continue
                    if np.dot(trial[4:6],seed[4:6])<=0:continue
                    merit=score(trial)
                    if merit>value+.0002:value=merit;candidate=trial
                best=candidate
            if previous==value:break
    return [*np.round(best,2).tolist(),kind] if value>initial+.025 else model


count=0
for site,groups in areas.items():
    if args.site and site not in args.site:continue
    for group in groups:
        if group.get('visibleOnly'):continue
        previous=group['houses'];group['houses']=[model if str(index) in group.get('roofForms',{}) else fit(model) for index,model in enumerate(previous)]
        count+=sum(old!=new for old,new in zip(previous,group['houses']))
args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('Proposed bounded eave adjustments for',count,'house records; inspect against the visible reference before adopting.')
