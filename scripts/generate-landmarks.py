"""Source-matched architecture atlas: all named groups and every remaining visible surface."""
from pathlib import Path
import json, hashlib
from xml.sax.saxutils import escape
from art.atlas_layout import ZONES
from art.site_details import DETAILS
from art.stage import stage
from art.pagoda import pagoda
from art.surface_finishes import render_surface, sampled_shape, PROFILES
from art.completions import completion, pale_block
from art.courtyard_details import ground as courtyard_ground
from art.street_houses import colonnade, court_shadows, detail_body, eave_end, overlaps_box, replace_traces, street_areas
from art.sw_quay_tables import retired_traces
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/art/landmarks';OUT.mkdir(parents=True,exist_ok=True)
CONTEXT=ROOT/'public/art/architecture';CONTEXT.mkdir(parents=True,exist_ok=True)
features=json.loads((ROOT/'src/data/town-architecture.json').read_text())['features']
volume_data=json.loads((ROOT/'src/data/roof-volumes.json').read_text())
for path,key in [('src/data/town-architecture.json','geometrySha256'),('src/data/roof-guides.json','guideSha256')]:
    if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=volume_data[key]:
        raise SystemExit('Roof geometry changed. Run npm run art:geometry before rebuilding the artwork.')
volumes=volume_data['roofs']
observations=json.loads((ROOT/'src/data/street-observations.json').read_text())['surfaces']
for feature in features:
    feature['roofVolume']=volumes.get(feature['id'],{})
    feature['streetObservation']=observations.get(feature['id'],{})
reference=json.loads((ROOT/'src/data/reference-map.json').read_text())
completion_data=json.loads((ROOT/'src/data/town-completions.json').read_text())
completions=completion_data['sites']
streets=json.loads((ROOT/'src/data/street-houses.json').read_text())
structures=json.loads((ROOT/'src/data/landmark-structures.json').read_text())['sites']
street_sites=streets['sites']
background_groups=[group for groups in streets['background'].values() for group in groups]
street_groups=[group for groups in street_areas(streets).values() for group in groups]
superseded={surface for group in street_groups for surface in group.get('replacedSurfaces',[])} | retired_traces()
dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']

def poly(points,fill,stroke='none',sw=.3):
    return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'
def path(points): return 'M'+'L'.join(f'{x},{y}' for x,y in points)+'Z'
def hexcolor(rgb): return '#'+''.join(f'{int(max(0,min(255,c))):02x}' for c in rgb)

def surfaces_body(surfaces):
    surfaces=[surface for surface in surfaces if surface['id'] not in superseded and surface['owner']!='waterside-stage' and not (surface['owner']=='visitor-court' and surface['kind']=='glass')]
    from art.nw_market_ranges import market_layer
    old_timber,market=market_layer(surfaces)
    if old_timber:surfaces=[surface for surface in surfaces if surface['id'] not in old_timber]
    # Narrow timber elevations sit in front of their roof edge, so connected roof
    # footprints cannot erase upper-storey windows and gallery fronts.
    def elevation(f):
        _,_,w,h=f['bounds']
        return f['kind']=='wood' and h<=18 and w>=h*1.8
    cutouts=streets.get('partialTraceReplacements',{});defs=[]
    for surface in surfaces:
        key=surface['id']
        if key not in cutouts:continue
        extent='x="0" y="0" width="2363" height="1672"'
        defs.append(f'<mask id="clear-{key}" maskUnits="userSpaceOnUse" {extent}><rect {extent} fill="white"/>'+''.join(poly(ring,'black') for ring in cutouts[key])+'</mask>')
    def clipped(surface,body):
        key=surface['id']
        return f'<g mask="url(#clear-{key})">{body}</g>' if key in cutouts and body else body
    plaster=''.join(clipped(surface,''.join(sampled_shape(panel,'#eeebe2') for panel in surface['streetObservation'].get('plaster',[]))) for surface in surfaces)
    backings=[];joinery=[]
    for surface in surfaces:
        detail=streets.get('joinery',{}).get(surface['id'])
        if not detail:continue
        if detail.get('plasterReturns'):
            walls=''.join(poly(ring,'#eee8df') for ring in detail['plasterReturns'])
            backings.append(clipped(surface,f'<g id="{detail["id"]}-plaster">{walls}</g>'))
        pieces=''.join(colonnade(piece,piece['height']) if 'beam' in piece else eave_end(piece) for piece in detail['pieces'])
        joinery.append(clipped(surface,f'<g id="{detail["id"]}">{pieces}</g>'))
    return ('<defs>'+''.join(defs)+'</defs>' if defs else '')+plaster+''.join(backings)+''.join(clipped(f,render_surface(f)) for f in sorted(surfaces,key=elevation))+''.join(joinery)+market

def painted_bottom(feature):
    bottom=feature['bounds'][1]+feature['bounds'][3]+7
    return max([bottom]+[y+1 for panel in feature['streetObservation'].get('plaster',[]) for x,y in panel['points']])



def wrap(box,body,title):
    x,y,r,b=box;w,h=r-x,b-y
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} {y} {w} {h}" role="img"><title>{escape(title)}</title>{body}</svg>'

models=[]
for key,place,name,box in ZONES:
    owned=[f for f in features if f['owner']==key]
    if owned:
        box=(min(box[0],min(f['bounds'][0] for f in owned)-1),min(box[1],min(f['bounds'][1] for f in owned)-1),max(box[2],max(f['bounds'][0]+f['bounds'][2] for f in owned)+1),max(box[3],max(painted_bottom(f) for f in owned)))
    for court in completions.get(key,{}).get('courts',[]):
        cx,cy,cw,ch=court['bounds']
        box=(min(box[0],cx-2),min(box[1],cy-2),max(box[2],cx+cw+2),max(box[3],cy+ch+3))
    body=pagoda(structures[key]) if key=='temple-pagoda' else courtyard_ground(completions.get(key,{}))+surfaces_body(owned)+(DETAILS[key]() if key in DETAILS and key!='visitor-court' else '')+completion(completions.get(key,{}))
    own_groups=street_sites.get(key,[])
    for group in own_groups:
        for ring in group['replace']:
            box=(min(box[0],min(x for x,y in ring)-1),min(box[1],min(y for x,y in ring)-1),max(box[2],max(x for x,y in ring)+1),max(box[3],max(y for x,y in ring)+1))
    body=court_shadows(own_groups)+replace_traces(body,box,street_groups)+(DETAILS[key]() if key=='visitor-court' else '')+detail_body(own_groups,features)
    if key=='waterside-stage':body+=stage(structures[key])
    (OUT/f'{key}.svg').write_text(wrap(box,body,name+' · 原生手绘建筑'))
    x,y,r,b=box
    finish=structures.get(key,{}).get('finishLabel') or (PROFILES[key][0] if key in PROFILES else '地标屋面与木构细节')
    models.append({'id':key,'placeId':place,'name':name,'sourceBounds':[x,y,r-x,b-y],'focus':[(x+r)/2,(y+b)/2],'erase':[],'ground':'native-landscape','asset':f'/art/landmarks/{key}.webp','overviewAsset':f'/art/landmarks/{key}.preview.webp','heroAsset':f'/art/landmarks/{key}.scene.webp','sourceAsset':f'/art/landmarks/{key}.svg','lights':[[round((f['bounds'][0]+f['bounds'][2]*.5-x)/(r-x),4),round((f['bounds'][1]+f['bounds'][3]*.5-y)/(b-y),4)] for f in sorted([q for q in owned if q['kind']=='wood'],key=lambda q:q['area'],reverse=True)[:3]],'surfaceCount':len(owned),'evidence':'source-visible-contours','kinds':sorted(set(f['kind'] for f in owned)),'finishLabel':finish})
# Background architecture is partitioned rather than left on the old low-resolution raster.
unassigned=[f for f in features if f['owner'] is None]
tiles=[]
for row in range(5):
    for col in range(6):
        sx=col*256-dx;sy=row*256-dy
        visible=[f for f in unassigned if f['bounds'][0]+f['bounds'][2]>sx and f['bounds'][0]<sx+256 and painted_bottom(f)>sy and f['bounds'][1]<sy+256]
        key=f'block-{col}-{row}'
        box=(sx,sy,sx+256,sy+256)
        streets_here=[group for group in background_groups if any(overlaps_box(ring,box) for ring in group['replace'])]
        terraces=[block for block in completion_data['paleBlocks'] if any(overlaps_box(unit['top']+[(px,py+unit['rise']) for px,py in unit['lip']],box) for unit in block['units'])]
        if not visible and not streets_here and not terraces:continue
        court_underlays=[group for group in streets_here if group.get('swCourtUnderlay')]
        foreground_streets=[group for group in streets_here if not group.get('swCourtUnderlay')]
        body=''.join(pale_block(block) for block in terraces)+detail_body(court_underlays,features)+replace_traces(surfaces_body(visible),box,street_groups)+detail_body(foreground_streets,features)
        (CONTEXT/f'{key}.svg').write_text(wrap(box,body,'古镇街巷建筑 · 原生轮廓'))
        tiles.append({'id':key,'x':col*256,'y':row*256,'width':256,'height':256,'asset':f'/art/architecture/{key}.webp','overviewAsset':f'/art/architecture/{key}.preview.webp','sourceAsset':f'/art/architecture/{key}.svg','surfaceCount':len(visible)})
(ROOT/'src/data/landmark-models.json').write_text(json.dumps({'version':'native-architecture-2026-11-18','coordinateSpace':'reference-image-pixels','models':models},ensure_ascii=False,indent=2)+'\n')
(ROOT/'src/data/architecture-tiles.json').write_text(json.dumps({'tiles':tiles,'surfaceCount':len(unassigned)},ensure_ascii=False,indent=2)+'\n')
print(f'Generated {len(models)} landmark groups and {len(tiles)} background architecture tiles; {len(features)} traced surfaces.')
