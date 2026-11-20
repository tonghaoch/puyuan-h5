"""Describe visible crown volumes at known planting positions. Offline authoring only."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from art.atlas_layout import PRINT_EXCLUSIONS

ROOT = Path(__file__).resolve().parents[1]


def crown_volume(points, tree, brightness):
    bottom,top=np.quantile(points[:,1],[.985,.015]); height=bottom-top
    if height<8 or len(points)<55:return None
    levels=np.linspace(top,bottom,6); stations=[]
    for level in levels:
        across=points[np.abs(points[:,1]-level)<=max(1.0,height*.113),0]
        if len(across)<3:return None
        left,right=np.quantile(across,[.055,.945]);middle=(left+right)*.5
        radius=max(.8,(right-left)*.5)
        if level in (levels[0],levels[-1]):radius*=.69
        stations.append([round(level-tree['y'],1),round(middle-tree['x'],1),round(radius,1)])
    area=sum((end[0]-start[0])*(start[2]+end[2]) for start,end in zip(stations,stations[1:]))
    if area<26 or len(points)/area<.60:return None
    quantiles=np.quantile(brightness,[.12,.50,.84]);steps=[83,110,137,162,183,204]
    return {'stations':stations,'wash':int(np.searchsorted(steps,quantiles[1])),
            'grain':int(np.searchsorted([44,68,93],quantiles[2]-quantiles[0]))}


def flowering_sites(town,rgb):
    hue,sat,value = np.moveaxis(cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV),-1,0)
    petal = ((hue<12)|(hue>164))&(sat>38)&(sat<171)&(value>154)
    bright = ((hue<10)|(hue>165))&(sat>38)&(value>189)
    allowed = np.zeros(hue.shape,np.uint8);cv2.fillPoly(allowed,[np.int32(town['scope'])],1)
    for outline in PRINT_EXCLUSIONS:cv2.fillPoly(allowed,[np.int32(outline)],0)
    trees = [tree for tree in town['trees'] if not tree['id'].startswith('flowering-')]
    for tree in trees:
        if tree['kind']=='blossom':
            cv2.ellipse(allowed,(round(tree['x']),round(tree['crownY'])),(round(13*tree['scale']),round(16*tree['scale'])),0,0,360,0,-1)
    density = cv2.GaussianBlur((petal&allowed.astype(bool)).astype(np.float32),(0,0),2.65)
    interior = ((density>.32)&allowed.astype(bool)).astype(np.uint8)
    radius = cv2.distanceTransform(interior,cv2.DIST_L2,5)
    peaks = (radius >= cv2.dilate(radius,np.ones((13,13),np.uint8))-.01)&(radius>2.65)
    _,_,_,centers = cv2.connectedComponentsWithStats(peaks.astype(np.uint8));proposals=[]
    for horizontal,vertical in sorted(centers[1:],key=lambda point:-radius[round(point[1]),round(point[0])]):
        left,top=round(horizontal),round(vertical);size=radius[top,left]
        if any(np.hypot(left-tree['x'],top-tree['crownY'])<max(11,15*tree['scale']) for tree in proposals):continue
        patch=np.s_[top-7:top+8,left-7:left+8]
        if (bright[patch]&allowed[patch].astype(bool)).sum()<32:continue
        scale=round(float(np.clip((size+2.8)/10,.48,1.35)),2)
        proposals.append({'id':f'flowering-{left}-{top}','kind':'blossom','x':left,'crownY':top,'y':round(top+14*scale,1),'scale':scale})
    return proposals


def observe(trees, rgb):
    hue, sat, value = np.moveaxis(cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV), -1, 0)
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.float32)
    local_variance=cv2.GaussianBlur(gray*gray,(0,0),1.6)-cv2.GaussianBlur(gray,(0,0),1.6)**2
    visible = np.ones(hue.shape,np.uint8)
    for outline in PRINT_EXCLUSIONS:cv2.fillPoly(visible,[np.int32(outline)],0)
    masks = {'pink': ((hue>153)|(hue<13)) & (sat>32) & (value>120),
             'gold': (hue>=8) & (hue<34) & (sat>90) & (value>112),
             'leaf': (hue>=29) & (hue<82) & (sat>62) & (value>52)}
    def family(tree):
        return {'blossom':'pink','ginkgo':'gold'}.get(tree['kind'],'leaf')
    observed = {}
    for tree in trees:
        if not tree['id'].startswith(('tree-','flowering-')) or 'form' in tree or 'foliage' in tree:continue
        center = np.array([tree['x'], tree['crownY']]); scale = tree['scale']; tone = family(tree)
        left,top = np.floor(center-[16*scale+3,19*scale+3]).astype(int)
        right,bottom = np.ceil(center+[16*scale+3,19*scale+3]).astype(int)+1
        window = np.s_[top:bottom,left:right]; points = np.argwhere(masks[tone][window] & visible[window])[:,::-1] + [left,top]
        if len(points)<20:continue
        distance = np.sum(((points-center)/[16*scale+2,18*scale+2])**2,axis=1)
        allowed = distance<1
        for other in trees:
            if other is tree or family(other)!=tone:continue
            offset = np.array([other['x'],other['crownY']])-center
            if np.max(np.abs(offset))>48:continue
            rival = np.sum(((points-center-offset)/[16*other['scale']+2,18*other['scale']+2])**2,axis=1)
            allowed &= distance<rival*1.08
        points = points[allowed]
        if len(points)<22:continue
        occupied = np.zeros(visible[window].shape,np.uint8); occupied[points[:,1]-top,points[:,0]-left]=1
        count, regions = cv2.connectedComponents(cv2.dilate(occupied,np.ones((3,3),np.uint8)))
        if count<=1:continue
        labels = regions[points[:,1]-top,points[:,0]-left];nearest = np.argmin(np.sum((points-center)**2,axis=1))
        points = points[labels==labels[nearest]]
        if len(points)<22:continue
        textured=points[local_variance[points[:,1],points[:,0]]>100]
        if len(textured)>=max(40,len(points)*.52):points=textured
        narrow,wide = np.quantile(points,[.04,.96],axis=0); extent = wide-narrow
        if np.min(extent)<3 or len(points)<extent.prod()*.34:continue
        colors = rgb[points[:,1],points[:,0]].astype(float)
        lightness = colors @ [.299,.587,.114]
        features = np.c_[(points-center)/np.maximum(extent,4), (lightness-np.median(lightness))*.0018]
        parts = 4 if max(extent)>13 else 3
        cv2.setRNGSeed(1729)
        _, labels, _ = cv2.kmeans(np.float32(features),parts,None,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_MAX_ITER,40,.002),3,cv2.KMEANS_PP_CENTERS)
        lobes = []
        for label in range(parts):
            subset = points[labels.ravel()==label]
            if len(subset)<5:continue
            lower,upper = np.quantile(subset,[.04,.96],axis=0);radius = np.maximum(1.3,(upper-lower)*.56)
            offset = (lower+upper)/2-[tree['x'],tree['y']]
            local = lightness[labels.ravel()==label];median = np.median(local)
            band = int(np.searchsorted([110,144,167,191],median))
            shade = int(np.searchsorted([.17,.34],np.mean(local < median-25)))
            contrast = (subset-subset.mean(axis=0)).T @ (local-local.mean())
            light = int(round(np.arctan2(contrast[1],contrast[0])*4/np.pi))%8
            lobes.append([*np.round(offset,1).tolist(),*np.round(radius,1).tolist(),band,shade,light])
        if len(lobes)>=2:
            sample_y,sample_x=points[:,1],points[:,0]
            tint = 'spring' if tone=='leaf' and np.median(sat[sample_y,sample_x])>141 and np.median(hue[sample_y,sample_x])<49 else tone
            observed[tree['id']] = {'tone':tint,'lobes':sorted(lobes,key=lambda lobe:lobe[1])}
            volume=crown_volume(points,tree,lightness)
            if volume:observed[tree['id']]['volume']=volume
    return observed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path)
    parser.add_argument('--flowers',action='store_true',help='Propose additional flowering trees for visual review');args = parser.parse_args()
    if args.out.resolve().is_relative_to(ROOT/'src/data'):
        parser.error('Write the proposal outside src/data for review')
    town = json.loads((ROOT/'src/data/town-landscape.json').read_text());trees=town['trees']
    rgb=np.asarray(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB'))
    if args.flowers:
        trees=[tree for tree in trees if not tree['id'].startswith('flowering-')]+flowering_sites(town,rgb)
    observed = observe(trees,rgb)
    if args.flowers:observed=[{**tree,'crown':observed[tree['id']]} for tree in trees if tree['id'].startswith('flowering-') and tree['id'] in observed]
    args.out.write_text(json.dumps(observed,separators=(',',':'))+'\n')
    print(f'{len(observed)} proposed crown profiles')
