"""Source-matched architecture atlas: all named groups and every remaining visible surface."""
from pathlib import Path
import json, math
from xml.sax.saxutils import escape
from art.atlas_layout import ZONES, LABELS
from art.site_details import DETAILS
from art.secondary_details import SECONDARY_DETAILS
from art.surface_finishes import render_surface, PROFILES
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/art/landmarks';OUT.mkdir(parents=True,exist_ok=True)
CONTEXT=ROOT/'public/art/architecture';CONTEXT.mkdir(parents=True,exist_ok=True)
features=json.loads((ROOT/'references/architecture/visible-surfaces.json').read_text())['features']
reference=json.loads((ROOT/'src/data/reference-map.json').read_text())
dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']

def poly(points,fill,stroke='none',sw=.3):
    return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
def line(points,color,sw=.3,extra=''):
    return '<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{sw}" {extra}/>'
def path(points): return 'M'+'L'.join(f'{x},{y}' for x,y in points)+'Z'
def hexcolor(rgb): return '#'+''.join(f'{int(max(0,min(255,c))):02x}' for c in rgb)



def stone_pagoda():
    # Stone material and closely spaced cornices checked against the scenic area's own photograph.
    # This is a visual approximation; the illustration's ambiguous dark crown is retained in reference view.
    p=[];cx=915
    for level in range(4):
        y=592-level*1.6;r=23-level*1.2
        p.append(poly([(cx+math.cos(i*math.pi/4)*r,y+math.sin(i*math.pi/4)*r*.30) for i in range(8)],'#d9d4bf','#a6a48c',.4))
    p.append(poly([(900,581),(907,586),(923,586),(931,580),(930,561),(922,555),(907,556),(900,562)],'#d6cdb5','#9d9882',.4))
    for x in [904,911,920,927]:
        p.append(f'<path d="M{x-1.6} 579v-9q1.6-4 3.2 0v9Z" fill="#777768" stroke="#b4aa8e" stroke-width=".4"/>')
    for j in range(12):
        y=560-j*7.1;r=17-j*.35
        p.append(poly([(cx-r+2,y+2),(cx-6,y+5),(cx+7,y+5),(cx+r-2,y),(cx+r-2,y-5),(cx-6,y-8),(cx-r+2,y-5)],'#d9d1b9','#aaa28a',.26))
        p.append(poly([(cx-r+2,y-5),(cx-6,y-2),(cx-6,y+5),(cx-r+2,y+2)],'#c4c4ac','none'))
        p.append(poly([(cx+7,y-2),(cx+r-2,y-5),(cx+r-2,y),(cx+7,y+5)],'#a5af9c','none'))
        for sy in [y+.8,y+3]:
            p.append(line([(cx-r+3,sy-2),(cx-6,sy+1),(cx+7,sy+1),(cx+r-3,sy-3)],'#b2b59b',.18))
        for frac in [-.7,-.35,0,.35,.7]:
            x=cx+r*frac
            p.append(line([(x,y-3),(x,y+1)],'#777b69',.65))
        p.append(poly([(cx-r-2,y-4),(cx-7,y-8),(cx+7,y-8),(cx+r+2,y-4),(cx+r+3,y-1),(cx,y+4),(cx-r-3,y-1)],'#8d9686','#68766b',.3))
        p.append(poly([(cx-7,y-8),(cx,y-6),(cx,y+2),(cx-r-3,y-1),(cx-r-2,y-4)],'#a7af99','none'))
        p.append(poly([(cx,y-6),(cx+7,y-8),(cx+r+2,y-4),(cx+r+3,y-1),(cx,y+2)],'#768876','none'))
        p.append(line([(cx-r+1,y+.8),(cx,y+4),(cx+r-1,y+.8)],'#516b59',.5))
        p.append(line([(cx-r-3,y-1),(cx,y+4),(cx+r+3,y-1)],'#ded8bd',.65))
        for frac in [-.75,-.4,0,.4,.75]:
            x=cx+r*frac
            p.append(line([(x,y),(x,y+3)],'#d6cbb0',.32))
    p.append(poly([(901,477),(914,468),(928,477),(931,479),(915,483),(899,479)],'#7e8d80','#bdbaa0',.4))
    p.append(line([(915,469),(915,457)],'#b9a064',.7))
    for y,r in [(466,1.3),(463,1),(460,.7)]: p.append(f'<ellipse cx="915" cy="{y}" rx="{r}" ry=".8" fill="#ccb476"/>')
    return ''.join(p)




def wrap(box,body,title):
    x,y,r,b=box;w,h=r-x,b-y
    blocked=''.join(poly(points,'#000','none',0) for points in LABELS)
    blocked+=poly([(1012,584),(1107,584),(1107,850),(1012,850)],'#000','none',0)
    clipping=f'<defs><mask id="source-label-mask" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>{blocked}</mask></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}" role="img"><title>{escape(title)}</title>{clipping}<g mask="url(#source-label-mask)">{body}</g></svg>'

models=[]
for key,place,name,box in ZONES:
    owned=[f for f in features if f['owner']==key]
    if owned:
        box=(min(box[0],min(f['bounds'][0] for f in owned)-1),min(box[1],min(f['bounds'][1] for f in owned)-1),max(box[2],max(f['bounds'][0]+f['bounds'][2] for f in owned)+1),max(box[3],max(f['bounds'][1]+f['bounds'][3] for f in owned)+1))
    body=stone_pagoda() if key=='temple-pagoda' else ''.join(render_surface(f) for f in owned)+(DETAILS[key]() if key in DETAILS else '')+(SECONDARY_DETAILS[key]() if key in SECONDARY_DETAILS else '')
    (OUT/f'{key}.svg').write_text(wrap(box,body,name+' · 按原图可见轮廓描摹'))
    x,y,r,b=box
    models.append({'id':key,'placeId':place,'name':name,'sourceBounds':[x,y,r-x,b-y],'focus':[(x+r)/2,(y+b)/2],'erase':[],'ground':'source-preserved','asset':f'/art/landmarks/{key}.webp','overviewAsset':f'/art/landmarks/{key}.preview.webp','heroAsset':f'/art/landmarks/{key}.scene.webp','sourceAsset':f'/art/landmarks/{key}.svg','lights':[[round((f['bounds'][0]+f['bounds'][2]*.5-x)/(r-x),4),round((f['bounds'][1]+f['bounds'][3]*.5-y)/(b-y),4)] for f in sorted([q for q in owned if q['kind']=='wood'],key=lambda q:q['area'],reverse=True)[:3]],'surfaceCount':len(owned),'evidence':'official-photo-and-source-layout' if key=='temple-pagoda' else 'source-visible-contours','kinds':sorted(set(f['kind'] for f in owned)),'finishLabel':PROFILES[key][0] if key in PROFILES else '地标屋面与木构细节'})
# Background architecture is partitioned rather than left on the old low-resolution raster.
unassigned=[f for f in features if f['owner'] is None]
tiles=[]
for row in range(5):
    for col in range(6):
        sx=col*256-dx;sy=row*256-dy
        visible=[f for f in unassigned if f['bounds'][0]+f['bounds'][2]>sx and f['bounds'][0]<sx+256 and f['bounds'][1]+f['bounds'][3]>sy and f['bounds'][1]<sy+256]
        if not visible: continue
        key=f'block-{col}-{row}'
        (CONTEXT/f'{key}.svg').write_text(wrap((sx,sy,sx+256,sy+256),''.join(render_surface(f) for f in visible),'古镇街巷建筑 · 原图轮廓'))
        tiles.append({'id':key,'x':col*256,'y':row*256,'width':256,'height':256,'asset':f'/art/architecture/{key}.webp','overviewAsset':f'/art/architecture/{key}.preview.webp','sourceAsset':f'/art/architecture/{key}.svg','surfaceCount':len(visible)})
(ROOT/'src/data/landmark-models.json').write_text(json.dumps({'version':'source-traced-relief-2026-11-18','coordinateSpace':'reference-image-pixels','models':models},ensure_ascii=False,indent=2)+'\n')
(ROOT/'src/data/architecture-tiles.json').write_text(json.dumps({'tiles':tiles,'surfaceCount':len(unassigned)},ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(models)} landmark groups and {len(tiles)} background architecture tiles; {len(features)} traced surfaces.')
