"""Compare authored eave groups at the same illustration coordinates; never a release input."""
import argparse, json
from pathlib import Path
from contextlib import nullcontext
import cv2
import numpy as np
from PIL import Image, ImageDraw
from art.atlas_layout import PRINT_EXCLUSIONS
from art.scene import compose_scene
from art.street_houses import street_areas

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline',type=Path,help='Earlier checkout or asset build with landmark models and hero images')
parser.add_argument('--out',type=Path,default=ROOT/'artifacts/street-review')
parser.add_argument('--site',action='append',default=[],help='Review only this site; may be repeated')
parser.add_argument('--full-scene',action='store_true',help='Use complete native layers on both sides when streets extend past old detail cards')
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
reference=Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB')
streets=json.loads((ROOT/'src/data/street-houses.json').read_text())
if not args.full_scene and set(args.site)&streets['background'].keys():parser.error('Background streets have no detail card; use --full-scene')
sites=street_areas(streets) if args.full_scene else streets['sites']
structures=json.loads((ROOT/'src/data/landmark-structures.json').read_text())['sites']
sites={**sites,**{site:model['review'] for site,model in structures.items()}}
if set(args.site)-sites.keys():parser.error('Unknown site: '+', '.join(sorted(set(args.site)-sites.keys())))
if args.site:sites={site:groups for site,groups in sites.items() if site in args.site}


def collection(root):
    if args.full_scene:
        frame=json.loads((root/'src/data/reference-map.json').read_text())
        offset=frame['sourceOffset'];size=frame['scene'];image=compose_scene(root=root)
        return {site:(image,[-offset['x'],-offset['y'],size['width'],size['height']]) for site in sites}
    models=json.loads((root/'src/data/landmark-models.json').read_text())['models']
    return {model['id']:(root/'public'/model['heroAsset'].lstrip('/'),model['sourceBounds']) for model in models}


def crop_scene(entry,box):
    file,(left,top,width,height)=entry
    with (nullcontext(file) if isinstance(file,Image.Image) else Image.open(file)) as scene:
        sx,sy=scene.width/width,scene.height/height
        return scene.crop(tuple(round((value-origin)*scale) for value,origin,scale in zip(box,[left,top]*2,[sx,sy]*2))).convert('RGB')


def dark_shape(image,size):
    rgb=np.array(image.resize(size,Image.Resampling.LANCZOS))
    return cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)<145


def ochre_shape(image,size):
    rgb=np.array(image.resize(size,Image.Resampling.LANCZOS));hue,saturation,value=np.moveaxis(cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV),-1,0)
    return (hue>=6)&(hue<=29)&(saturation>=65)&(value>=118)


def material_shape(image,size,material):
    red,green,blue=np.moveaxis(np.array(image.resize(size,Image.Resampling.LANCZOS),dtype=np.int16),-1,0)
    if material=='glass':return (blue>red+9)&(blue>=green)&(green-red<55)&(red>108)&(green>120)
    if material=='timber':return (red>green+9)&(red<160)&(green<125)&(green-blue<22)
    raise ValueError(f'Unknown review material: {material}')


def alignment(original,native,mask):
    original=original&mask;native=native&mask
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    def nearby(shape):return cv2.dilate(shape.astype(np.uint8),kernel)>0
    precision=(native&nearby(original)).sum()/max(1,native.sum())
    recall=(original&nearby(native)).sum()/max(1,original.sum())
    return {'precision':round(float(precision),3),'recall':round(float(recall),3),'iou':round(float((original&native).sum()/max(1,(original|native).sum())),3)}


current=collection(ROOT);baseline=collection(args.baseline) if args.baseline else None
report={};materials={};finishes={};overview=[]
for site,groups in sites.items():
    bounds=[entry[site][1] for entry in (current,baseline) if entry is not None]
    def common_box(rings):
        points=np.array([point for ring in rings for point in ring]);low=np.floor(points.min(axis=0)).astype(int)-2;high=np.ceil(points.max(axis=0)).astype(int)+3
        for x,y,width,height in bounds:
            low=np.maximum(low,[x,y]);high=np.minimum(high,[x+width,y+height])
        if np.any(high<=low):raise ValueError(f'{site}: review region outside shared scene coverage')
        return (*low,*high)
    box=common_box([ring for group in groups for ring in group['replace']])
    strips=[('Reference',reference.crop(box))]
    if baseline:strips.append(('Before',crop_scene(baseline[site],box)))
    strips.append(('Native',crop_scene(current[site],box)))
    strip=Image.new('RGB',(440*len(strips),310),'#e9e7da');caption=ImageDraw.Draw(strip)
    for index,(label,image) in enumerate(strips):
        factor=min(430/image.width,280/image.height);scaled=image.resize((round(image.width*factor),round(image.height*factor)),Image.Resampling.LANCZOS)
        caption.text((index*440+5,4),site+' / '+label,fill='#383933');strip.paste(scaled,(index*440+(440-scaled.width)//2,22))
    overview.append(strip)
    for group in groups:
        box=common_box(group['replace']);left,top,right,bottom=box;size=(right-left,bottom-top)
        mask=np.zeros((size[1],size[0]),np.uint8);origin=np.array([left,top]);
        for ring in group['replace']:cv2.fillPoly(mask,[np.int32(ring-origin)],1)
        for ring in PRINT_EXCLUSIONS:cv2.fillPoly(mask,[np.int32(ring-origin)],0)
        original=reference.crop(box);target=dark_shape(original,size);images={'Reference':original}
        if baseline:images['Before']=crop_scene(baseline[site],box)
        images['Native']=crop_scene(current[site],box)
        name=site+'-'+group['id'];report[name]={label:alignment(target,dark_shape(image,size),mask>0) for label,image in images.items() if label!='Reference'}
        if 'material' in group:
            material=group['material'];target_material=material_shape(original,size,material)
            finishes[name]={'material':material,'visibleReferencePixels':int((target_material&(mask>0)).sum()),**{label:alignment(target_material,material_shape(image,size,material),mask>0) for label,image in images.items() if label!='Reference'}}
        if 'ochre-glaze' in group.get('roofTones',{}).values():
            target_glaze=ochre_shape(original,size)
            materials[name]={label:alignment(target_glaze,ochre_shape(image,size),mask>0) for label,image in images.items() if label!='Reference'}
        width=min(520,size[0]*4);height=round(size[1]*width/size[0]);sheet=Image.new('RGB',(width*len(images),height+24),'#e9e7da');draw=ImageDraw.Draw(sheet)
        for index,(label,image) in enumerate(images.items()):
            draw.text((index*width+5,5),label,fill='#383933');sheet.paste(image.resize((width,height),Image.Resampling.LANCZOS),(index*width,24))
        sheet.save(args.out/(name+'.jpg'),quality=94)
(args.out/'alignment.json').write_text(json.dumps(report,indent=2)+'\n')
if materials:(args.out/'ochre-alignment.json').write_text(json.dumps(materials,indent=2)+'\n')
if finishes:(args.out/'material-alignment.json').write_text(json.dumps(finishes,indent=2)+'\n')
sheet=Image.new('RGB',(overview[0].width,310*len(overview)))
for index,strip in enumerate(overview):sheet.paste(strip,(0,310*index))
sheet.save(args.out/'overview.jpg',quality=94)
print('Saved',len(report),'registered group comparisons to',args.out)
