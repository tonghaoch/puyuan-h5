"""A decorative, building-free meadow around the reference scene. Not geographic data."""
from pathlib import Path
import random, math, json
from art.architecture import path, ellipse, pine

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/art'
rng=random.Random(20261118)
manifest=json.loads((ROOT/'src/data/reference-map.json').read_text())
dx,dy=manifest['sourceOffset']['x'],manifest['sourceOffset']['y']
ring=[(x+dx,y+dy) for x,y in manifest['scope']]

def inside(x,y):
    result=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: result=not result
    return result

def distance(x,y):
    result=1e9
    for a,b in zip(ring,ring[1:]+ring[:1]):
        vx,vy=b[0]-a[0],b[1]-a[1]
        t=max(0,min(1,((x-a[0])*vx+(y-a[1])*vy)/(vx*vx+vy*vy)))
        result=min(result,math.hypot(x-a[0]-t*vx,y-a[1]-t*vy))
    return result

# Seamless tiny blades and pigment marks; edges contain no partial elements.
tile=['<svg xmlns="http://www.w3.org/2000/svg" width="384" height="384" viewBox="0 0 384 384">']
for _ in range(170):
    x=rng.randint(10,374); y=rng.randint(10,374)
    tile.append(path(f'M{x-2} {y}q-2-5-3-7m5 7q0-5 2-8m-2 8 4-4',stroke=rng.choice(['#aeb994','#b7bf9c','#c9ccaa']),width=.75,extra=f'opacity="{rng.uniform(.25,.55):.2f}"'))
for _ in range(85):
    x=rng.randint(5,379);y=rng.randint(5,379)
    tile.append(ellipse(x,y,rng.uniform(.6,1.4),rng.uniform(.4,.8),'#99a87e',extra='opacity=".23"'))
tile.append('</svg>')
(OUT/'meadow-tile.svg').write_text(''.join(tile))

# Irregular grassland, trees and small stones, only outside the existing town footprint.
defs='<defs><radialGradient id="grassPatch"><stop stop-color="#b9c597" stop-opacity=".36"/><stop offset="1" stop-color="#b9c597" stop-opacity="0"/></radialGradient><radialGradient id="warmPatch"><stop stop-color="#ecdfae" stop-opacity=".25"/><stop offset="1" stop-color="#ecdfae" stop-opacity="0"/></radialGradient></defs>'
patches=[]
for _ in range(100):
    x=rng.randint(-1400,2900); y=rng.randint(-1400,2600)
    if inside(x,y): continue
    rx,ry=rng.randint(75,230),rng.randint(40,150)
    patches.append((x,y,rx,ry,ellipse(x,y,rx,ry,rng.choice(['url(#grassPatch)','url(#warmPatch)']))))
objects=[]
for _ in range(700):
    x=rng.randint(-850,2370);y=rng.randint(-850,2090)
    if inside(x,y): continue
    dist=distance(x,y)
    if dist<32 or (dist>500 and rng.random()<.78): continue
    scale=rng.uniform(.45,.95)
    if rng.random()<.78:
        objects.append((y,x,22*scale,60*scale,pine(x,y,scale)))
    else:
        # Looser flowering canopies and little boulders.
        body=f'<g transform="translate({x} {y}) scale({scale})">'+ellipse(4,4,18,6,'#7c9164',extra='opacity=".13"')+path('M0 0v-30m0 16-10-10m10 3 10-9',stroke='#9b8960',width=2)
        for cx,cy,r in [(-9,-25,11),(9,-28,12),(0,-38,12),(-8,-39,8)]:
            body+=ellipse(cx,cy,r,r*.8,rng.choice(['#b9bf98','#c2c39e','#d1c5ad','#a8b68c']))
        objects.append((y,x,24*scale,55*scale,body+'</g>'))
for _ in range(120):
    x=rng.randint(-500,2020);y=rng.randint(-500,1740)
    if inside(x,y) or distance(x,y)<20: continue
    objects.append((y,x,10,10,ellipse(x,y,6,2.5,'#9b9d7f',extra='opacity=".18"')+path(f'M{x-5} {y}l2-5 7-2 3 6Z',fill='#c7c7a6',stroke='#afb696',width=.6)))
# 768-pixel transparent tiles: only visible ones are mounted by the map.
# Border-crossing shapes are painted in both neighboring tiles then clipped at identical coordinates.
folder=OUT/'meadow'
folder.mkdir(exist_ok=True)
manifest_tiles=[]
for row in range(-3,5):
    for col in range(-3,5):
        x,y=col*768,row*768
        visible_patches=[svg for px,py,rx,ry,svg in patches if px+rx>x and px-rx<x+768 and py+ry>y and py-ry<y+768]
        visible_objects=[svg for py,px,rx,ry,svg in sorted(objects) if px+rx>x and px-rx<x+768 and py+10>y and py-ry<y+768]
        if not visible_patches and not visible_objects: continue
        key=f'{col}_{row}'
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="768" height="768" viewBox="{x} {y} 768 768">'+defs+''.join(visible_patches+visible_objects)+'</svg>'
        (folder/f'{key}.svg').write_text(svg)
        manifest_tiles.append({'id':key,'x':x,'y':y,'width':768,'height':768,'src':f'/art/meadow/{key}.svg'})
(ROOT/'src/data/meadow-tiles.json').write_text(json.dumps({'tiles':manifest_tiles},indent=2)+'\n')
legacy=OUT/'meadow-landscape.svg'
if legacy.exists(): legacy.unlink()
print(f'Generated seamless meadow and {len(objects)} exterior trees/rocks in {len(manifest_tiles)} lightweight tiles, no buildings.')
