"""Offline observation of visible masonry courses along already authored water outlines."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from art.atlas_layout import PRINT_EXCLUSIONS
from art.landscape import quay_edge

ROOT = Path(__file__).resolve().parents[1]


def bank_courses(town, rgb):
    colors = rgb.astype(np.int16)
    red, green, blue = np.moveaxis(colors, -1, 0)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    ink = (gray < 146) & (red >= green-26) & (red+24 >= blue) & (blue < green+18)
    wet = (blue > red+22) & (green > red+21) & (blue >= green-7) & (blue>114)
    reserved = np.zeros(ink.shape, np.uint8)
    for outline in PRINT_EXCLUSIONS:
        cv2.fillPoly(reserved, [np.int32(outline)], 1)
    for model in town['bridges']:
        bounds = ((model['x'],model['y']), (model['length']+4,model['width']+7), model['angle'])
        cv2.fillPoly(reserved,[np.int32(cv2.boxPoints(bounds))],1)
    for region in town['water']:
        for key in ('bankFaces','islandQuays'):
            for existing in region.get(key,[]):
                cv2.polylines(reserved,[np.int32(quay_edge(region,existing))],False,1,7)
    def simplify(points):
        fitted = cv2.approxPolyDP(np.float32(points), .68, False).reshape(-1,2)
        return np.round(fitted.astype(float),1).tolist()
    def collect(samples):
        for index in range(1,len(samples)-1):
            if samples[index] is not None or samples[index-1] is None or samples[index+1] is None:continue
            previous,following=np.array(samples[index-1]),np.array(samples[index+1]); middle=(previous+following)*.5
            if np.linalg.norm(previous-following,axis=1).max()>6.2:continue
            horizontal,vertical=np.rint(middle.mean(axis=0)).astype(int)
            if reserved[vertical,horizontal] or not ink[vertical,horizontal]:continue
            samples[index]=tuple(middle)
        runs = []; run = []
        for pair in [*samples,None]:
            if pair is not None:
                run.append(pair)
            else:
                if len(run) >= 3:
                    toe, cap = zip(*run)
                    centers=np.int32(np.rint((np.array(toe)+np.array(cap))/2))
                    pigment=np.median(colors[centers[:,1],centers[:,0]],axis=0)
                    tone='moss' if pigment[1]>pigment[0]+3 else 'granite' if np.max(pigment)-np.min(pigment)<16 else 'umber'
                    runs.append({'toe':simplify(np.array(toe)+.5), 'cap':simplify(np.array(cap)+.5),'tone':tone})
                run = []
        return runs
    result = []
    for region_index, region in enumerate(town['water']):
        for index, outline in enumerate([region['points'],*region['holes']]):
            ring = np.array([*outline,outline[0]],float)
            delta = np.diff(ring,axis=0); distance = np.r_[0,np.cumsum(np.linalg.norm(delta,axis=1))]
            length = distance[-1]
            if length < 20: continue
            def at(position):
                return np.array([np.interp(position%length,distance,ring[:,axis]) for axis in (0,1)])
            sign = np.sign(cv2.contourArea(np.float32(ring),oriented=True)) * (1 if index==0 else -1)
            samples = []
            for position in np.arange(0,length,2.4):
                point = at(position); tangent = at(position+1.5)-at(position-1.5)
                tangent /= max(.001,np.linalg.norm(tangent)); normal = np.array([tangent[1],-tangent[0]])*sign
                def probe(mask, depths):
                    coords = point + np.array(depths)[:,None,None]*normal + np.array([-.8,0,.8])[None,:,None]*tangent
                    horizontal,vertical = np.moveaxis(np.rint(coords).astype(int),-1,0)
                    return mask[vertical,horizontal].sum(axis=1)>=2
                depths = np.arange(-5,16,.5)
                course = probe(ink,depths); spans = np.flatnonzero(np.diff(np.r_[False,course,False])).reshape(-1,2)
                usable = []
                for start,end in spans:
                    if start==0 or end==len(depths) or depths[start]>6.5 or not 3<=end-start<=22:continue
                    low,high=depths[start]-.24,depths[end-1]+.24
                    touching=probe(wet,low+np.array([-5.0,-3.3,-1.7,-.85]))
                    if not touching.any() or probe(wet,high+np.array([1.2,2.2,3.8])).sum()>1:continue
                    if probe(reserved,[low,(low+high)*.5,high]).any():continue
                    usable.append((abs(low)-.4*touching.sum(),low,high))
                if not usable or probe(reserved,[0,2]).any():
                    samples.append(None); continue
                _,low,high = min(usable)
                samples.append((point+normal*low,point+normal*high))
            start = next((idx for idx,sample in enumerate(samples) if sample is None),0)
            for course in collect(samples[start:] + samples[:start]):
                result.append({'water': region_index, 'ring':index, **course})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path,help='Separate editable proposal; not consumed by the release build')
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(ROOT/'src/data'):
        parser.error('Write the proposal outside src/data for review')
    town = json.loads((ROOT/'src/data/town-landscape.json').read_bytes())
    courses = bank_courses(town,np.asarray(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB')))
    args.out.write_text(json.dumps({'courses':courses},separators=(',',':'))+'\n')
    print(f'{len(courses)} visible bank courses')
