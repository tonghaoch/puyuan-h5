"""Build native ground, water mask and tiled vegetation from editable geometry; no reference image."""
from pathlib import Path
import json, math, random
from art.landscape import path, poly, ellipse, shape, tree, bridge, boat, landing, island_quay, quay_edge, quay_face, MATERIALS
from art.completions import footprint
from art.street_houses import street_areas, tree_blockers
from art.stage import roof_outline

ROOT=Path(__file__).resolve().parents[1]
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

def planted_tree(model):
    occluders=[points for points in building_outlines if inside(points,model['x'],model['y'])]+foreground_roofs.get(model['id'],[])
    svg=tree(model)
    if not occluders:return svg
    key='tree-depth-'+model['id']
    mask=f'<defs><mask id="{key}" maskUnits="userSpaceOnUse" x="0" y="0" width="2363" height="1672"><rect width="2363" height="1672" fill="white"/>'+''.join(poly(points,'black') for points in occluders)+'</mask></defs>'
    return mask+f'<g mask="url(#{key})">{svg}</g>'
out=ROOT/'public/art/native';out.mkdir(parents=True,exist_ok=True)
width,height=data['scene']['width'],data['scene']['height'];dx,dy=data['offset']['x'],data['offset']['y']
scope=shape({'points':data['scope']});water=''.join(shape(p) for p in data['water'])
connections=''.join(path(c['d'],'none','#fff',c['width']) for c in data['waterConnections'])
defs=MATERIALS+f'<defs><clipPath id="scope"><path d="{scope}"/></clipPath><clipPath id="water-region"><path d="{water}" fill-rule="evenodd"/>{connections}</clipPath></defs>'
p=[defs,f'<g transform="translate({dx} {dy})">',path(scope,'url(#sand)','#b9c5a1',3)]
p.append(f'<g clip-path="url(#scope)">')
for region in data['paving']:p.append(path(shape(region),'url(#pavers)','#dfe0c8',.55,'fill-rule="evenodd"'))
for walk in data['walks']:
    p.append(path(walk['d'],'none','#b1b59a',walk['width']+2))
    p.append(path(walk['d'],'none','#e2dcc0',walk['width']))
    p.append(path(walk['d'],'none','#c2bea1',.4,'stroke-dasharray="1 4"'))
for plaza in data['plazas']:
    p.append(f'<g id="{plaza["id"]}">'+path(shape(plaza),plaza.get('fill','#dbdedb'),plaza.get('edge','#c4c6bc'),.5))
    for seam in plaza['seams']:
        p.append(path('M'+'L'.join(f'{x},{y}' for x,y in seam),stroke=plaza.get('joint','#b9bcb7'),width=.53))
    p.append('</g>')
for garden in data.get('gardens',[]):
    p.append(path(garden['d'],'#abbc8c','#d7d1b3',7))
    if garden.get('track'):p.append(path(garden['d'],'#9cb28c','#a7a48a',4))
    p.append(path(garden['d'],'none','#899f78',.7))
    if garden['kind']=='garden':
        p.append(path('M1068 614Q1039 655 1068 698T1060 775Q1052 810 1070 841','none','#ded7ba',3))
# Quay, submerged shelf, ripples and soft reflected highlights share the same water geometry.
for region in data['water']:
    d=shape(region)
    p.append(path(d,'url(#water)','url(#quay)',2.8,'fill-rule="evenodd"'))
    p.append(path(d,'url(#ripples)','#d7dac0',.45,'fill-rule="evenodd"'))
    for quay in region.get('islandQuays',[]):p.append(island_quay(region,quay))
    for quay in region.get('bankFaces',[]):
        p.append(f'<g id="{quay["id"]}">'+quay_face(quay_edge(region['points'],quay),quay['height'],quay.get('stone','#736554'))+'</g>')
for c in data['waterConnections']:
    p.append(path(c['d'],'none','#bdc6a7',c['width']+3))
    p.append(path(c['d'],'none','#7aac9f',c['width']))
p.append('</g>')
p.append('</g>')
def wrap(body,w=width,h=height,view=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{view or f"0 0 {w} {h}"}"><title>濮院原生手绘景观</title>{body}</svg>'
(out/'ground.svg').write_text(wrap(''.join(p)))
objects=[MATERIALS,f'<g transform="translate({dx} {dy})">']
for model in data['bridges']:objects.append(bridge(model))
for model in data['landings']:objects.append(landing(model))
for model in data['boats']:objects.append(boat(model))
objects.append('</g>')
(out/'waterfronts.svg').write_text(wrap(''.join(objects)))
mask=f'<g transform="translate({dx} {dy})">'+path(water,'white',extra='fill-rule="evenodd"')+connections+'</g>'
(out/'water-mask.svg').write_text(wrap(mask))

# Foreground vegetation is split into viewport-sized vector tiles, painted in ground-depth order.
tiles=[];size=384
for row in range(4):
    for col in range(4):
        x,y=col*size,row*size
        visible=[t for t in data['trees'] if t['x']+dx+22*t['scale']>x and t['x']+dx-22*t['scale']<x+size and t['y']+dy+5>y and t['y']+dy-44*t['scale']<y+size]
        if not visible:continue
        key=f'canopy-{col}-{row}';body=f'<g transform="translate({dx} {dy})">'+''.join(planted_tree(t) for t in sorted(visible,key=lambda t:t['y']))+'</g>'
        (out/f'{key}.svg').write_text(wrap(body,size,size,f'{x} {y} {size} {size}'))
        tiles.append({'id':key,'x':x,'y':y,'width':size,'height':size,'asset':f'/art/native/{key}.webp','overviewAsset':f'/art/native/{key}.preview.webp','sourceAsset':f'/art/native/{key}.svg'})
(ROOT/'src/data/native-landscape.json').write_text(json.dumps({'ground':'/art/native/ground.svg','waterMask':'/art/native/water-mask.svg','waterfronts':'/art/native/waterfronts.svg','tiles':tiles,'treeCount':len(data['trees']),'bridgeCount':len(data['bridges']),'landingCount':len(data['landings'])},indent=2)+'\n')
print(f'Generated native ground, vector water mask, {len(tiles)} botanical tiles, {len(data["trees"])} trees and {len(data["bridges"])} bridges.')
