"""Optional comparison view only. Native artwork is generated without the reference image."""
from pathlib import Path
import argparse
import json
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'src/data/reference-map.json').read_text())
source=Image.open(ROOT/layout['source']).convert('RGB')
w,h=layout['scene']['width'],layout['scene']['height']
dx,dy=layout['sourceOffset']['x'],layout['sourceOffset']['y']
scope=Image.new('L',(w,h))
ImageDraw.Draw(scope).polygon([(x+dx,y+dy) for x,y in layout['scope']],fill=255)
raw=Image.new('RGB',(w,h),'#efeede');raw.paste(source,(dx,dy))
original=Image.new('RGB',(w,h),'#efeede')
original.paste(raw,(0,0),scope.filter(ImageFilter.GaussianBlur(6)))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ai-master',type=Path,help='Approved 4x AI image in cropped scene coordinates')
parser.add_argument('--lapsrn-x8',type=Path,help='LapSRN_x8.pb for the high-density close-up layer')
args=parser.parse_args()
directory=ROOT/'public/art/reference-tiles'
if args.ai_master:
    ai=Image.open(args.ai_master)
    if ai.size != (w*4,h*4):
        parser.error(f'Expected an AI master of {w*4} x {h*4} pixels')

def save_tiles(image,level):
    dest=directory/str(level)
    dest.mkdir(parents=True,exist_ok=True)
    for y in range(0,image.height,512):
        for x in range(0,image.width,512):
            tile=image.crop((x,y,min(x+512,image.width),min(y+512,image.height)))
            tile.save(dest/f'{x//512}-{y//512}.webp',lossless=True,method=4)

def clarify_lines(image, radius):
    # Work before tiling so a roof line crossing two tiles gets the same treatment.
    rgb=image.convert('RGB')
    luminance=rgb.convert('L')
    blurred=luminance.filter(ImageFilter.GaussianBlur(radius))
    detail=ImageChops.subtract(luminance,blurred,offset=128)
    # Ignore tiny fluctuations in paper/water and cap bright/dark halos.
    detail=detail.point(lambda v: 128 if abs(v-128)<=2 else 128+max(-16,min(16,round((v-128)*0.85))))
    return Image.merge('RGB',tuple(ImageChops.add(channel,detail,offset=-128) for channel in rgb.split()))

original.save(ROOT/'public/art/puyuan-original-scope.webp',quality=90,method=6)
save_tiles(clarify_lines(original.resize((w*2,h*2),Image.Resampling.LANCZOS),1.35),2)
if args.ai_master:
    save_tiles(clarify_lines(ai,2.4),4)
if args.lapsrn_x8:
    import cv2
    import numpy as np

    model=cv2.dnn_superres.DnnSuperResImpl_create()
    model.readModel(str(args.lapsrn_x8))
    model.setModel('lapsrn',8)
    cv2.setNumThreads(3)
    dest=directory/'8'
    dest.mkdir(parents=True,exist_ok=True)
    # Infer from original pixels, with neighboring context beyond the final tile.
    for y in range(0,h,128):
        for x in range(0,w,128):
            left,top=max(0,x-32),max(0,y-32)
            right,bottom=min(w,x+128),min(h,y+128)
            patch=original.crop((left,top,min(w,right+32),min(h,bottom+32)))
            result=model.upsample(cv2.cvtColor(np.asarray(patch),cv2.COLOR_RGB2BGR))
            result=clarify_lines(Image.fromarray(cv2.cvtColor(result,cv2.COLOR_BGR2RGB)),3)
            result.crop(((x-left)*8,(y-top)*8,(right-left)*8,(bottom-top)*8)).save(
                dest/f'{x//128}-{y//128}.webp',quality=95,method=4)
print('Prepared optional original comparison. Native assets are untouched.')
