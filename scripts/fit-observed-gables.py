"""Propose small adjustments to explicit eaves and ridges; preserve each house and its supports."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from art.atlas_layout import PRINT_EXCLUSIONS
from art.street_houses import roof_frame, street_areas

ROOT = Path(__file__).resolve().parents[1]


def fit(house, form, slate, visible):
    seed = np.array(roof_frame(house, form), float)
    origin = np.floor(seed.min(axis=0)).astype(int) - 6
    width, height = np.ceil(seed.max(axis=0)).astype(int) - origin + 7
    left, top = origin
    source = slate[top:top+height,left:left+width]
    valid = visible[top:top+height,left:left+width].astype(bool)
    bend = np.linspace(0,1,7)[:,None]
    def slope(start, end):
        return start + (end-start)*bend + np.c_[np.zeros(7), 4*form.get('sag',0)*bend[:,0]*(1-bend[:,0])]
    def draw(points):
        mask = np.zeros((height*3,width*3),np.uint8)
        for upper, edge in ((points[2:4],points[4:6]),(points[4:6],points[:2])):
            outline = np.vstack([slope(upper[0],edge[0]),slope(upper[1],edge[1])[::-1]])
            cv2.fillPoly(mask,[np.int32(np.rint(((outline-origin+.5)*3-.5)*16))],255,shift=4)
        return cv2.resize(mask,(width,height),interpolation=cv2.INTER_AREA)>127
    original = draw(seed)
    if np.count_nonzero(original & valid) < max(14, original.sum()*.86):return None
    valid &= cv2.dilate(original.astype(np.uint8), np.ones((7,7),np.uint8)).astype(bool)
    target = source & valid
    def score(points):
        drawn = draw(points) & valid
        return ((drawn & target).sum()/max(1,(drawn | target).sum())
                - .0015*np.mean((points-seed)**2))
    def sound(points):
        if np.max(np.abs(points-seed))>3:return False
        if form.get('support')=='water-piers' and np.max(np.abs(points[:2]-seed[:2]))>.7:return False
        for start,end in ((0,1),(2,3),(4,5),(0,2),(1,3)):
            axis = seed[end]-seed[start]; drift = points[end]-points[start]
            if axis@drift < .69*(axis@axis):return False
        for front,back,ridge in ((0,2,4),(1,3,5)):
            across = points[back,0]-points[front,0]
            if abs(across)>5 and not .18 <= (points[ridge,0]-points[front,0])/across <= .82:return False
            old_rise = min(seed[front,1],seed[back,1])-seed[ridge,1]
            if old_rise>1 and min(points[front,1],points[back,1])-points[ridge,1]<.72*old_rise:return False
        return True
    best = seed.copy(); merit = score(best); initial = merit
    for step in (1.25,.65,.3):
        for _ in range(2):
            before = merit
            for vertices in ([0,1,2,3,4,5],[0,2,4],[1,3,5],[0,1],[2,3],[4,5],[0],[1],[2],[3],[4],[5]):
                for axis in (0,1):
                    anchor = best.copy()
                    for direction in (-1,1):
                        trial = anchor.copy(); trial[vertices,axis] += direction*step
                        if not sound(trial):continue
                        value = score(trial)
                        if value>merit+.0003:best,merit = trial,value
            if before==merit:break
    if merit-initial<.008:return None
    result = np.round(best,2)
    house[:4] = result[:2].reshape(-1).tolist()
    house[4:6] = np.round(np.mean(result[2:4]-result[:2],axis=0),2).tolist()
    form['rear'],form['ridge'] = result[2:4].tolist(),result[4:6].tolist()
    return round(initial,3),round(merit,3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path)
    parser.add_argument('--input',type=Path,default=ROOT/'src/data/street-houses.json')
    parser.add_argument('--group',action='append',required=True)
    args = parser.parse_args()
    if args.out.resolve()==args.input.resolve() or args.out.resolve().is_relative_to(ROOT/'src/data'):
        parser.error('Write proposals to a separate file for visual review')
    data = json.loads(args.input.read_text()); rgb = np.asarray(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB'))
    gray = cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY); hsv = cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    slate = (gray<143) & (hsv[:,:,1]<92); visible = np.ones(gray.shape,np.uint8)
    for ring in PRINT_EXCLUSIONS:cv2.fillPoly(visible,[np.int32(ring)],0)
    groups = {group['id']:group for group_list in street_areas(data).values() for group in group_list}
    if set(args.group)-groups.keys():parser.error('Unknown group')
    proposals = {}
    for key in args.group:
        group = groups[key]
        for index, house in enumerate(group['houses']):
            form = group.get('roofForms',{}).get(str(index),{})
            if house[-1] not in ('gable','blind-wall') or not {'rear','ridge'}<=form.keys():continue
            if (change:=fit(house,form,slate,visible)):proposals[f'{key}/{index}'] = change
    args.out.write_text(json.dumps(data,ensure_ascii=False)+'\n')
    print(json.dumps(proposals))
