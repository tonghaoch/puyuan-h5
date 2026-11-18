"""Preserve the provided map geometry and all visible building details.
Only crop/mask out-of-scope surroundings and color-grade the artwork.
The output remains image coordinates, never a georeferenced map.
Requires Pillow (PIL). Originals are never overwritten.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'src/data/reference-map.json').read_text())
source_path = ROOT / manifest['source']
source = Image.open(source_path).convert('RGB')
assert source.size == tuple(manifest['sourceSize'].values())
width, height = manifest['scene']['width'], manifest['scene']['height']
dx, dy = manifest['sourceOffset']['x'], manifest['sourceOffset']['y']
scene = Image.new('RGB', (width, height), '#efeede')
original = Image.new('RGB', (width, height), '#efeede')
raw = Image.new('RGB', (width, height), '#efeede')
raw.paste(source, (dx, dy))
mask = Image.new('L', (width, height), 0)
ImageDraw.Draw(mask).polygon([(x+dx,y+dy) for x,y in manifest['scope']], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(6))
original.paste(raw, (0,0), mask)
# Keep luminance and linework. Shift cyan rivers and bright vegetation into the app's jade palette.
pixels = raw.load()
for y in range(height):
    for x in range(width):
        r,g,b = pixels[x,y]
        if g > r*1.16 and b > r*1.18 and b > 110 and g > 110:
            luminance = .299*r+.587*g+.114*b
            pixels[x,y] = (int(.65*luminance+24), int(.78*luminance+35), int(.73*luminance+32))
        elif g > r*1.12 and g > b*1.08 and g > 75:
            luminance = .299*r+.587*g+.114*b
            pixels[x,y] = (min(255,int(.74*luminance+23)), min(255,int(.83*luminance+25)), min(255,int(.62*luminance+27)))
        elif max(r,g,b)<112:
            luminance=.299*r+.587*g+.114*b
            pixels[x,y]=(int(.68*luminance+25),int(.70*luminance+36),int(.66*luminance+31))
        else:
            pixels[x,y]=(int(r*.92+245*.08),int(g*.92+239*.08),int(b*.92+218*.08))
scene.paste(raw, (0,0), mask)
OUT=ROOT/'public/art'
OUT.mkdir(parents=True,exist_ok=True)
scene.save(OUT/'puyuan-reference-aligned.webp', quality=94, method=6)
original.save(OUT/'puyuan-original-scope.webp', quality=94, method=6)
# Water mask keeps animated highlights inside actual blue waterways from the source image.
water = Image.new('L', (width,height), 0)
wp=water.load(); src=source.load(); mp=mask.load()
for y in range(height):
    sy=y-dy
    if not 0 <= sy < source.height: continue
    for x in range(width):
        sx=x-dx
        if 0 <= sx < source.width and mp[x,y] > 128:
            r,g,b=src[sx,sy]
            if g > r*1.16 and b > r*1.18 and b > 110 and g > 110: wp[x,y]=255
water=water.filter(ImageFilter.GaussianBlur(.6))
# Convert mask into alpha. White pixels describe water, transparent pixels are everything else.
water_rgba=Image.new('RGBA',(width,height),(255,255,255,0));water_rgba.putalpha(water)
water_rgba.save(OUT/'puyuan-water-mask.png',optimize=True)
(ROOT/'docs/map-asset-manifest.json').write_text(json.dumps({
    'source':manifest['source'], 'source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
    'version':manifest['version'],'scene':manifest['scene'],'translation':manifest['sourceOffset'],
    'geometry_operation':'translation only; no warp, rotation, or invented building placement',
    'landmark_count':len(manifest['landmarks']),'georeferenced':False,
},indent=2,ensure_ascii=False)+'\n')
print(f'Prepared faithful source-derived map: {width}×{height}, {len(manifest["landmarks"])} reference landmarks.')
