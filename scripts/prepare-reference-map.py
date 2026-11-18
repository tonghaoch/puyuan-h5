"""Ground and reference assets. Keep the original intact; architecture is reconstructed in separate layers."""
from pathlib import Path
import hashlib, json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'src/data/reference-map.json').read_text())
models=json.loads((ROOT/'src/data/landmark-models.json').read_text())
source_path=ROOT/manifest['source'];source=Image.open(source_path).convert('RGB')
w,h=manifest['scene']['width'],manifest['scene']['height'];dx,dy=manifest['sourceOffset']['x'],manifest['sourceOffset']['y']
OUT=ROOT/'public/art';OUT.mkdir(exist_ok=True)
scope=Image.new('L',(w,h));ImageDraw.Draw(scope).polygon([(x+dx,y+dy) for x,y in manifest['scope']],fill=255)
original_raw=Image.new('RGB',(w,h),'#efeede');original_raw.paste(source,(dx,dy))
original=Image.new('RGB',(w,h),'#efeede');original.paste(original_raw,(0,0),scope.filter(ImageFilter.GaussianBlur(6)))
original.save(OUT/'puyuan-original-scope.webp',quality=94,method=6)

def grade(image):
    arr=np.array(image).astype(float);r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2];lum=.299*r+.587*g+.114*b
    water=(g>r*1.16)&(b>r*1.18)&(b>110)&(g>110)
    green=(g>r*1.12)&(g>b*1.08)&(g>75)&~water
    dark=(np.max(arr,axis=2)<112)&~water&~green
    out=arr*.92+np.array([245,239,218])*.08
    out[water]=np.stack([lum*.65+24,lum*.78+35,lum*.73+32],axis=2)[water]
    out[green]=np.stack([lum*.74+23,lum*.83+25,lum*.62+27],axis=2)[green]
    out[dark]=np.stack([lum*.55+24,lum*.56+31,lum*.54+29],axis=2)[dark]
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
colored=grade(original_raw)
aligned=Image.new('RGB',(w,h),'#efeede');aligned.paste(colored,(0,0),scope.filter(ImageFilter.GaussianBlur(6)))
aligned.save(OUT/'puyuan-reference-aligned.webp',quality=94,method=6)
# Preserve printed labels: obscured architecture cannot be reliably recovered from this image.
label_mask=np.zeros((source.height,source.width),np.uint8)
# Replace the ambiguous dark tower illustration with the official-photo-based stone pagoda.
cv2.fillPoly(label_mask,[np.array([[899,475],[928,473],[934,520],[932,545],[939,575],[931,588],[898,587],[892,570],[897,541]],np.int32)],255)
cleaned=cv2.inpaint(cv2.cvtColor(np.array(source),cv2.COLOR_RGB2BGR),label_mask,5,cv2.INPAINT_TELEA)
cleaned=Image.fromarray(cv2.cvtColor(cleaned,cv2.COLOR_BGR2RGB))
ground=Image.new('RGB',(w,h),'#e4e6cc');ground.paste(cleaned,(dx,dy));ground=grade(ground).convert('RGBA')
edge=scope.filter(ImageFilter.GaussianBlur(23)).point(lambda value:max(0,min(255,(value-128)*2)))
ground.putalpha(edge);ground.save(OUT/'puyuan-layered-ground.webp',quality=94,method=6)
arr=np.array(original_raw);r,g,b=arr[:,:,0].astype(float),arr[:,:,1].astype(float),arr[:,:,2].astype(float)
water=((g>r*1.16)&(b>r*1.18)&(b>110)&(g>110)&(np.array(scope)>0)).astype(np.uint8)*255
water_image=Image.new('RGBA',(w,h),(255,255,255,0));water_image.putalpha(Image.fromarray(water).filter(ImageFilter.GaussianBlur(.6)));water_image.save(OUT/'puyuan-water-mask.png',optimize=True)
summary=json.loads((ROOT/'references/architecture/coverage-summary.json').read_text())
(ROOT/'docs/map-asset-manifest.json').write_text(json.dumps({'source':manifest['source'],'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'version':'whole-town-visible-architecture-2026-11-18','scene':manifest['scene'],'translation':manifest['sourceOffset'],'geometry_operation':'Source-visible contours remain in their original pixel locations. Original printed labels are preserved; the ambiguous tower silhouette is replaced using first-party photo evidence. No georeferencing inferred.','landmark_count':len(manifest['landmarks']),'independent_model_sites':[m['id'] for m in models['models']],'traced_surfaces':summary['surfaces'],'georeferenced':False},ensure_ascii=False,indent=2)+'\n')
print('Prepared presentation ground and unchanged original comparison.')
