"""Optional comparison view only. Native artwork is generated without the reference image."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFilter

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
original.save(ROOT/'public/art/puyuan-original-scope.webp',quality=94,method=6)
print('Prepared optional original comparison. Native assets are untouched.')
