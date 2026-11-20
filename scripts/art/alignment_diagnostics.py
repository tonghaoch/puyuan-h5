"""Offline aggregate diagnostics; these counts do not award any alignment credit."""
import cv2
import json
import numpy as np
from PIL import Image

from .scene import scene_layers


CONTEXTS = ('green', 'blue-green', 'warm', 'dark-neutral', 'pale-neutral', 'mixed')
LAYER_NAMES = ('land', 'water', 'waterfront', 'street', 'landmark', 'plant')


def assign_layer(owners, alpha, left, top, value):
    height,width=alpha.shape
    west,north=max(0,left),max(0,top)
    east,south=min(owners.shape[1],left+width),min(owners.shape[0],top+height)
    if west<east and north<south:
        visible=alpha[north-top:south-top,west-left:east-left]>=128
        owners[north:south,west:east][visible]=value


def layer_owners(root):
    (width,height),layers=scene_layers(root)
    owners=np.zeros((height,width),np.uint8)
    town=json.loads((root/'src/data/town-landscape.json').read_text())
    offset=np.array([town['offset']['x'],town['offset']['y']])
    for water in town['water']:
        wet=np.zeros_like(owners)
        rings=[np.rint(np.array(ring)+offset).astype(np.int32) for ring in [water['points'],*water['holes']]]
        cv2.fillPoly(wet,rings,1);owners[wet!=0]=LAYER_NAMES.index('water')
    for name,asset,(left,top,wide,tall) in layers:
        if name=='land':continue
        with Image.open(root/'public'/asset.lstrip('/')) as image:
            alpha=np.asarray(image.convert('RGBA').getchannel('A').resize((wide,tall),Image.Resampling.LANCZOS))
        assign_layer(owners,alpha,left,top,LAYER_NAMES.index(name))
    return owners


def reference_contexts(rgb, valid):
    red, green, blue = np.moveaxis(rgb.astype(np.int16), -1, 0)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    chroma = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    signals = [(green > red+6) & (green > blue+17),
               (green > red+19) & (blue > red+23) & (blue >= green-6),
               (red > green+12) & (red > blue+18),
               (chroma <= 20) & (gray < 145), (chroma <= 22) & (gray >= 175)]
    def area(mask):
        return cv2.boxFilter(mask.astype(np.float32), -1, (7,7), normalize=False,
                             borderType=cv2.BORDER_CONSTANT)
    votes = np.stack([area(signal & valid) for signal in signals]); order = np.sort(votes, axis=0)
    size = area(valid); dominant = (size >= 20) & (order[-1] >= size*.36) & (order[-1]-order[-2] >= size*.12)
    return np.where(dominant, np.argmax(votes, axis=0), len(CONTEXTS)-1)


def error_distance(ink, valid):
    if not (ink & valid).any():return np.full(ink.shape, np.inf, np.float32)
    return cv2.distanceTransform((~(ink & valid)).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def diagnose(rgb, reference, drawing, valid, source_box):
    contexts = reference_contexts(rgb, valid); west,north = source_box[:2]; height,width = valid.shape
    result = {'note':'Diagnostic only. Euclidean distances use only valid ink in the opposite drawing. '
              'Contexts are the dominant reference colour in a 7x7 valid neighbourhood, not object labels. '
              '64px cells are ranked by unmatched pixels farther than 3px. No coordinates of individual pixels are stored.'}
    for key,source,opposite in [('missed',reference,drawing),('extra',drawing,reference)]:
        error = valid & source & ~opposite; distance = error_distance(opposite, valid)
        bands = [error & (distance <= 1.5), error & (distance > 1.5) & (distance <= 3), error & (distance > 3)]
        def summarize(region):
            return {name:int(np.count_nonzero(region & band)) for name,band in zip(('upTo1.5','over1.5To3','over3'),bands)}
        by_context = {name:summarize(contexts==index) for index,name in enumerate(CONTEXTS)}
        cells = []
        for top in range(0,height,64):
            for left in range(0,width,64):
                cut = np.s_[top:top+64,left:left+64]; scores = np.bincount(contexts[cut][bands[-1][cut]],minlength=len(CONTEXTS))
                if scores.sum():cells.append({'sourceBox':[west+left,north+top,west+min(left+64,width),north+min(top+64,height)],
                    'over3':int(scores.sum()),'contexts':dict(zip(CONTEXTS,map(int,scores)))})
        result[key] = {'total':int(error.sum()),'bands':summarize(valid),'byReferenceContext':by_context,
                       'largestDistantCells':sorted(cells,key=lambda cell:-cell['over3'])[:16]}
    return result
