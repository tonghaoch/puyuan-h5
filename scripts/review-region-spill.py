"""Check whether published off-region drift exists in the native pre-encoding art as well."""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from art.region_review import REGIONS, region_map


def manifest(root):
    def data(key):return json.loads((root/'src/data'/f'{key}.json').read_bytes())
    reference = data('reference-map'); landscape = data('native-landscape')
    left,top = [-reference['sourceOffset'][key] for key in ('x','y')]
    width,height = [reference['scene'][key] for key in ('width','height')]
    rows = {model['id']:(model['sourceAsset'],model['asset'],model['sourceBounds']) for model in data('landmark-models')['models']}
    for tile in [*data('architecture-tiles')['tiles'],*landscape['tiles']]:
        rows[tile['id']] = (tile['sourceAsset'],tile['asset'],[left+tile['x'],top+tile['y'],tile['width'],tile['height']])
    for key in ('ground','waterfronts'):
        svg = landscape[key]; rows['native-'+key] = (svg,svg.replace('.svg','.webp'),[left,top,width,height])
    return rows


def raw_counts(before, after, box):
    left,top,width,height = box; factor = before.shape[1]//width
    if before.shape != after.shape or before.shape != (height*factor,width*factor,4):
        raise ValueError(f'Raw dimensions differ from published bounds: {box}')
    changes = np.any(before!=after,axis=2).reshape(height,factor,width,factor).sum(axis=(1,3))
    owners = region_map([left,top,left+width,top+height])
    return factor,{name:int(changes[owners==index].sum()) for index,name in enumerate(REGIONS)}


def raster(source_root, cache_root, key, svg, webp):
    if (source_root/svg).read_bytes() != (cache_root/svg).read_bytes():raise ValueError(f'Stale SVG in raster cache: {key}')
    with Image.open(cache_root/'artifacts/architecture-renders'/f'{key}.png') as raw:
        stream = io.BytesIO(); raw.save(stream,format='WEBP',method=4,quality=92)
        if stream.getvalue() != (source_root/webp).read_bytes():raise ValueError(f'PNG does not encode to the published asset: {key}')
        return np.asarray(raw.convert('RGBA'))


def review(base, candidate, base_cache, candidate_cache, region):
    assets = manifest(base); totals = dict.fromkeys(REGIONS,0); changed = {}
    if assets != manifest(candidate):raise ValueError('Asset registration changed; inspect placement separately')
    for key,(source,asset,box) in assets.items():
        svg = Path('public')/source.lstrip('/'); webp = Path('public')/asset.lstrip('/')
        if (base/svg).read_bytes()==(candidate/svg).read_bytes() and (base/webp).read_bytes()==(candidate/webp).read_bytes():continue
        before = raster(base,base_cache,key,svg,webp); after = raster(candidate,candidate_cache,key,svg,webp)
        factor,counts = raw_counts(before,after,box); changed[key] = {'scale':factor,'changedSubpixels':counts}
        for name,count in counts.items():totals[name]+=count
    return {'region':region,'note':'Counts raw RGBA changes at rasterizer resolution, including outside the park mask. Both PNGs must re-encode to their published map assets. The strict acceptance report still counts every published WebP drift.', 'assets':changed,'total':totals}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('base','candidate','out'):parser.add_argument('--'+key,type=Path,required=True)
    for key in ('base-cache','candidate-cache'):parser.add_argument('--'+key,type=Path)
    parser.add_argument('--region',choices=REGIONS,required=True); args=parser.parse_args()
    report=review(args.base,args.candidate,args.base_cache or args.base,args.candidate_cache or args.candidate,args.region)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n');print(report['total'])
