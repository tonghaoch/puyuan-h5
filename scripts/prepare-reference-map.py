"""Optional comparison view only. Native artwork is generated without the reference image."""
from pathlib import Path
import argparse
import json
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parents[1]
layout=json.loads((ROOT/'src/data/reference-map.json').read_text())
source=Image.open(ROOT/layout['source']).convert('RGB')
w,h=layout['scene']['width'],layout['scene']['height']
dx,dy=layout['sourceOffset']['x'],layout['sourceOffset']['y']
scope=Image.new('L',(w,h))
ImageDraw.Draw(scope).polygon([(x+dx,y+dy) for x,y in layout['scope']],fill=255)
raw=Image.new('RGB',(w,h),'#efeede');raw.paste(source,(dx,dy))
paint=Image.open(ROOT/'references/reference-outpaint.webp').convert('RGB')
if paint.size != (w,h):
    raise ValueError('AI outpaint must be registered to the reference scene')
# Sample open ground in the northwest of the painting, not a second illustration.
patch=paint.crop((round(w*.04),round(h*.05),round(w*.1663),round(h*.2048))).resize((192,192),Image.Resampling.LANCZOS)
strip=Image.new('RGB',(384,192))
strip.paste(patch);strip.paste(ImageOps.mirror(patch),(192,0))
grass=Image.new('RGB',(384,384))
grass.paste(strip);grass.paste(ImageOps.flip(strip),(0,192))
grass.save(ROOT/'public/art/reference-meadow.webp',lossless=True,method=4)
# Match the repeating backdrop's origin and period at all four scene edges.
field=Image.new('RGB',(w,h))
for y in range(0,h,grass.height):
    for x in range(0,w,grass.width):
        field.paste(grass,(x,y))
rim=Image.new('L',(w,h))
draw=ImageDraw.Draw(rim)
for inset in range(min(65,w//2,h//2)):
    t=inset/64
    draw.rectangle((inset,inset,w-1-inset,h-1-inset),fill=round(255*t*t*(3-2*t)))
paint=Image.composite(paint,field,rim)
# Keep source pixels inside the town. Only the outer lip transitions to the AI edit.
keep=ImageChops.lighter(scope,scope.filter(ImageFilter.GaussianBlur(4)).point(lambda p:min(255,p*2)))
original=Image.composite(raw,paint,keep)
repairs=Image.open(ROOT/'references/reference-label-repairs.webp').convert('RGBA')
if repairs.size != original.size:
    raise ValueError('Label repairs must be registered to the reference scene')
label_mask=repairs.getchannel('A')
original.paste(repairs,(0,0),label_mask)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ai-master',type=Path,help='Approved 4x AI image in cropped scene coordinates')
parser.add_argument('--fsrcnn-x4',type=Path,help='FSRCNN_x4.pb to enhance label repairs at the same density as the master')
parser.add_argument('--lapsrn-x8',type=Path,help='LapSRN_x8.pb for the high-density close-up layer')
args=parser.parse_args()
directory=ROOT/'public/art/reference-tiles'
if args.ai_master:
    if not args.fsrcnn_x4:
        parser.error('--ai-master requires --fsrcnn-x4 for the restored label regions')
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
    # The approved master has a cream matte at its edge. Keep its enhanced
    # interior, but derive the rim and exterior from the newly painted scene.
    interior=scope.filter(ImageFilter.GaussianBlur(6)).point(lambda p:max(0,(p-246)*255//9))
    detailed=Image.composite(ai,original.resize(ai.size,Image.Resampling.LANCZOS),
                             interior.resize(ai.size,Image.Resampling.BILINEAR))
    import cv2
    import numpy as np
    model=cv2.dnn_superres.DnnSuperResImpl_create()
    model.readModel(str(args.fsrcnn_x4))
    model.setModel('fsrcnn',4)
    # Include the receptive field on both sides of each repair; never interpolate
    # just the masked pixels against a sharper AI master.
    blend=label_mask.filter(ImageFilter.MaxFilter(9))
    x,y,r,b=blend.getbbox()
    box=(max(0,x-16),max(0,y-16),min(w,r+16),min(h,b+16))
    patch=model.upsample(cv2.cvtColor(np.asarray(original.crop(box)),cv2.COLOR_RGB2BGR))
    patch=Image.fromarray(cv2.cvtColor(patch,cv2.COLOR_BGR2RGB))
    detailed.paste(patch,(box[0]*4,box[1]*4),blend.crop(box).resize(patch.size,Image.Resampling.BILINEAR))
    save_tiles(clarify_lines(detailed,2.4),4)
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
