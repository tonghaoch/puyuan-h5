"""Build native ground, water mask and tiled vegetation from editable geometry; no reference image."""
from pathlib import Path
import json, math, random
from art.landscape import number, path, poly, ellipse, shape, tree, bridge, landing, island_quay, quay_edge, quay_face, bank_course, street_bed, ground_bed, stone_lip, crown_extent, MATERIALS
from art.waterfront import boat, projected_span
from art.completions import footprint
from art.street_houses import street_areas, tree_blockers
from art.stage import roof_outline
from art.sw_street_banks import dry_shoulders, bank_returns
from art.northeast_quay_steps import quay_steps
from art.sw_quay_tables import bank_with_tables, joined_faces, table_tops
from art.ne_root_order import contact_order
from art.plantings import planting
from art.se_flowering_scaffolds import load_family, rooted_flower

ROOT=Path(__file__).resolve().parents[1]
street_flowers,flower_roofs=load_family(ROOT)
data=json.loads((ROOT/'src/data/town-landscape.json').read_text())
sites=json.loads((ROOT/'src/data/town-completions.json').read_text())['sites']
building_outlines=[footprint(house) for site in sites.values() for house in site.get('houses',[])]
street_sites=street_areas(json.loads((ROOT/'src/data/street-houses.json').read_text()))
foreground_roofs={}
stage_canopy=json.loads((ROOT/'src/data/landmark-structures.json').read_text())['sites']['waterside-stage']['canopy']
for tree_id in stage_canopy['rearTrees']:foreground_roofs[tree_id]=[roof_outline(stage_canopy)]
for groups in street_sites.values():
    for group in groups:
        for tree_id,indices in group.get('behindEaves',{}).items():
            for index in indices:foreground_roofs.setdefault(tree_id,[]).extend(tree_blockers(group['houses'][index],group.get('roofForms',{}).get(str(index))))

def inside(points,x,y):
    result=False
    for a,b in zip(points,points[1:]+points[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result

def planted_tree(model,stem_index=None,define_mask=True,leader_range=None):
    occluders=[points for points in building_outlines if inside(points,model['x'],model['y'])]+foreground_roofs.get(model['id'],[])
    if model['id'] in street_flowers:
        if stem_index is not None or leader_range is not None:raise ValueError('Registered single tree unexpectedly shares a contact-order station')
        svg=rooted_flower(model,street_flowers[model['id']],flower_roofs)
    else:svg=tree(model) if stem_index is None else planting(model,stem_index,leader_range)
    if not occluders:return svg
    key='tree-depth-'+model['id']
    mask=f'<defs><mask id="{key}" maskUnits="userSpaceOnUse" x="0" y="0" width="2363" height="1672"><rect width="2363" height="1672" fill="white"/>'+''.join(poly(points,'black') for points in occluders)+'</mask></defs>'
    return (mask if define_mask else '')+f'<g mask="url(#{key})">{svg}</g>'
out=ROOT/'public/art/native';out.mkdir(parents=True,exist_ok=True)
width,height=data['scene']['width'],data['scene']['height'];dx,dy=data['offset']['x'],data['offset']['y']
scope=shape({'points':data['scope']});water=''.join(shape(p) for p in data['water'])
connections=''.join(path(c['d'],'none','#fff',c['width']) for c in data['waterConnections'])
defs=MATERIALS+f'<defs><clipPath id="scope"><path d="{scope}"/></clipPath><clipPath id="water-region"><path d="{water}" fill-rule="evenodd"/>{connections}</clipPath></defs>'
p=[defs,f'<g transform="translate({dx} {dy})">',path(scope,'url(#sand)','#b9c5a1',3)]
p.append(f'<g clip-path="url(#scope)">')
for region in data['paving']:p.append(path(shape(region),f'url(#{region.get("material","pavers")})','#dfe0c8',.55,'fill-rule="evenodd"'))
for bed in data['groundBeds']:
    paint=ground_bed(bed)
    if bed['id']=='southwest-avenue-verge':
        from art.sw_street_floors import floor_bed
        floors=[json.loads(file.read_bytes()) for file in sorted((ROOT/'src/data').glob('sw34-floor-*.json'))]
        if not all(unit['bed']==bed['id'] for unit in floors):raise ValueError('Unregistered street floor')
        paint=floor_bed(bed,floors,paint)
    p.append(paint)
p.append(dry_shoulders())
p.append(table_tops())
for walk in data['walks']:p.append(street_bed(walk))
for plaza in data['plazas']:
    p.append(f'<g id="{plaza["id"]}">'+path(shape(plaza),plaza.get('fill','#dbdedb'),plaza.get('edge','#c4c6bc'),.5))
    for seam in plaza['seams']:
        if 'jointWidth' in plaza:
            p.append(path('M'+'L'.join(f'{x},{number(y+.55)}' for x,y in seam),stroke='#eef1eb',width=.68))
        p.append(path('M'+'L'.join(f'{x},{y}' for x,y in seam),stroke=plaza.get('joint','#b9bcb7'),width=plaza.get('jointWidth',.53)))
    if plaza.get('flagCuts'):
        from art.landscape import flag_cut
        p.extend(flag_cut(cut,plaza['joint']) for cut in plaza['flagCuts'])
    for lip in plaza.get('stoneLips',[]):p.append(stone_lip(lip))
    p.append('</g>')
for garden in data.get('gardens',[]):
    if garden['kind']=='water-garden':
        p.append(f'<g id="{garden["id"]}">'+path(garden['d'],'url(#spring-turf)'))
        p.append(path(garden['walk'],stroke='#cdbea5',width=2.1))
        p.append(path(garden['walk'],stroke='#e1d6ba',width=1.35)+'</g>')
        continue
    if 'trackApron' in garden:
        p.append(f'<g id="{garden["id"]}">'+path(garden['trackApron'],'url(#cinder-clay)','#d6c9bf',.56))
        p.append(path(garden['trackApron'],'url(#track-grit)'))
        p.append(path(garden['d'],'#8aa584','#999c81',1.25)+'</g>')
        continue
    p.append(path(garden['d'],'#abbc8c','#d7d1b3',7))
    p.append(path(garden['d'],'none','#899f78',.7))
# Quay, submerged shelf, ripples and soft reflected highlights share the same water geometry.
p.append(bank_returns())
for region in data['water']:
    d=shape(region)
    p.append(path(d,'url(#water)','url(#quay)',2.8,'fill-rule="evenodd" paint-order="stroke fill"'))
    p.append(path(d,'url(#ripples)',extra='fill-rule="evenodd"'))
    for quay in region.get('islandQuays',[]):p.append(island_quay(region,quay))
    for quay in region.get('bankFaces',[]):
        edge=[(horizontal,vertical-quay.get('toeLift',0)) for horizontal,vertical in quay_edge(region,quay)]
        p.append(f'<g id="{quay["id"]}">'+quay_face(edge,quay['height'],quay.get('stone','#736554'))+'</g>')
for c in data['waterConnections']:
    p.append(path(c['d'],'none','#bdc6a7',c['width']+3))
    p.append(path(c['d'],'none','#7aac9f',c['width']))
p.append(quay_steps())
p.append('<g id="visible-canal-banks">'+''.join(bank_with_tables(course) for course in data['visibleBankCourses'])+joined_faces()+'</g>')
p.append('<g id="canal-currents" clip-path="url(#water-region)">'+''.join(path(curve,stroke=tone,width=width) for curve,tone,width in data['canalCurrents'])+'</g>')
p.append('</g>')
p.append('</g>')
def wrap(body,w=width,h=height,view=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{view or f"0 0 {w} {h}"}"><title>濮院原生手绘景观</title>{body}</svg>'
(out/'ground.svg').write_text(wrap(''.join(p)))
objects=[MATERIALS,f'<g transform="translate({dx} {dy})">']
for model in data['bridges']:objects.append(projected_span(model) if model.get('form')=='projected-span' else bridge(model))
for model in data['landings']:objects.append(landing(model))
for model in data['boats']:objects.append(boat(model))
objects.append('</g>')
(out/'waterfronts.svg').write_text(wrap(''.join(objects)))
mask=f'<g transform="translate({dx} {dy})">'+path(water,'white',extra='fill-rule="evenodd"')+connections+'</g>'
(out/'water-mask.svg').write_text(wrap(mask))

# Foreground vegetation is split into viewport-sized vector tiles, painted in ground-depth order.
tiles=[];size=384
extents={entry['id']:crown_extent(entry) for entry in data['trees']}
for row in range(4):
    for col in range(4):
        x,y=col*size,row*size
        visible=[t for t in data['trees'] if t['x']+dx+extents[t['id']][2]>x and t['x']+dx+extents[t['id']][0]<x+size and t['y']+dy+extents[t['id']][3]>y and t['y']+dy+extents[t['id']][1]<y+size]
        if not visible:continue
        key=f'canopy-{col}-{row}';body=f'<g transform="translate({dx} {dy})">'+contact_order(visible,planted_tree)+'</g>'
        (out/f'{key}.svg').write_text(wrap(body,size,size,f'{x} {y} {size} {size}'))
        tiles.append({'id':key,'x':x,'y':y,'width':size,'height':size,'asset':f'/art/native/{key}.webp','overviewAsset':f'/art/native/{key}.preview.webp','sourceAsset':f'/art/native/{key}.svg'})
(ROOT/'src/data/native-landscape.json').write_text(json.dumps({'ground':'/art/native/ground.svg','waterMask':'/art/native/water-mask.svg','waterfronts':'/art/native/waterfronts.svg','tiles':tiles,'treeCount':len(data['trees']),'bridgeCount':len(data['bridges']),'landingCount':len(data['landings'])},indent=2)+'\n')
print(f'Generated native ground, vector water mask, {len(tiles)} botanical tiles, {len(data["trees"])} trees and {len(data["bridges"])} bridges.')
