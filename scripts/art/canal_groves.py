import json
from functools import lru_cache
from pathlib import Path

from .landscape import number, path
from .plantings import PAINT, planting
from .surface_finishes import sampled_shape


@lru_cache(maxsize=1)
def roof_shapes():
    data=Path(__file__).resolve().parents[2]/'src/data/town-architecture.json'
    return {feature['id']:feature for feature in json.loads(data.read_bytes())['features'] if feature['kind']=='roof'}


def arch_leader(across,up,span,height,tones):
    transform=f'translate({number(across)} {number(up)}) scale({number(span)} {number(height)})'
    return (f'<g data-outer-shoulder="raised" transform="{transform}">'+
            path('M-.38-.11Q-.52-.18-.47-.32Q-.58-.37-.43-.49Q-.49-.59-.34-.67Q-.37-.76-.25-.8Q-.19-.94-.04-1Q.06-.96.11-.86Q.24-.87.25-.77Q.42-.72.34-.62Q.5-.56.41-.46Q.56-.34.43-.23Q.44-.13.2-.08Q.03 .02-.15-.03Z',tones[1])+
            path('M-.39-.26Q-.47-.48-.34-.63Q-.27-.84-.05-.95Q.06-.86.02-.73Q-.15-.57-.12-.45Q-.26-.4-.26-.28Z',tones[2])+
            path('M.13-.8Q.27-.77.31-.60Q.48-.45.4-.31L.27-.17L.05-.1Q.14-.41.11-.48Z',tones[0])+
            path('M-.04-.07Q.005-.33-.025-.55M-.025-.35Q-.19-.44-.22-.55M-.02-.44Q.14-.52.19-.65',stroke=tones[0],width=.035)+
            path('M-.27-.56Q-.42-.56-.43-.47Q-.29-.46-.19-.54Q-.13-.64-.18-.69Q-.26-.68-.27-.56Z',tones[1])+
            path('M.12-.56Q.16-.72.24-.73Q.29-.62.2-.57Q.3-.59.39-.56Q.32-.46.15-.49Z',tones[1])+'</g>')


def forefan(across,span,height):
    transform=f'translate({number(across)} -.09) scale({number(span)} {number(height)})'
    return (f'<g data-front-crown="low" transform="{transform}">'+
            path('M-.49-.24Q-.51-.45-.32-.53Q-.33-.74-.15-.77Q-.04-.99.09-.91Q.22-.92.27-.72Q.45-.67.41-.51Q.56-.42.49-.25Q.48-.14.29-.1Q.12-.015-.05-.07Q-.29-.015-.4-.15Z','#a0b95d')+
            path('M-.4-.32Q-.36-.51-.23-.56Q-.24-.69-.11-.73Q.01-.85.06-.84Q.06-.72-.04-.62Q-.08-.48-.25-.44Z','#bed27d')+
            path('M-.02-.07Q-.04-.33.03-.57M-.02-.24Q-.17-.34-.25-.48M-.005-.29Q.18-.38.24-.59',stroke='#68873d',width=.043)+'</g>')


def eave_thicket(model,design):
    stations=model['crown']['volume']['stations'];height=-stations[0][0]*.91
    width=max(center+radius for _,center,radius in stations)-min(center-radius for _,center,radius in stations)
    key=model['id']+'-grove-eave';area=f'x="{number(model["x"]-width)}" y="{number(model["y"]-height-3)}" width="{number(width*2)}" height="{number(height+6)}"'
    protected=sampled_shape(roof_shapes()[design['behind']],'black')
    mask=f'<defs><mask id="{key}" maskUnits="userSpaceOnUse" {area}><rect {area} fill="white"/>{protected}</mask></defs>'
    shoulders=design['shoulders'];front=design['front'];root=f'translate({model["x"]} {model["y"]}) scale({number(width)} {number(height)})'
    parts=[mask,f'<g data-crown="{model["id"]}" data-eave-thicket="true" mask="url(#{key})"><g transform="{root}">',
           path('M0-.19Q-.08-.32-.22-.5M-.04-.29Q.09-.38.23-.63',stroke='#53623a',width=.072)]
    for shoulder,tones in zip(shoulders,[('#4d773a','#85ac60','#acc681'),('#467548','#74a767','#a2c383')]):
        across,span,tall=shoulder;parts.append(arch_leader(across,-.13,span,tall,tones))
    parts.extend([forefan(*front),'</g></g>'])
    return ''.join(parts)


def bed_crown(stem,design):
    ink,shadow,leaf,light,pale=PAINT[stem['paint']];across,up=design['leader'];bend,reach=design['shoulder']
    parts=['<g data-open-bed-crown="rooted">',
           path(f'M-1.6 .1Q-1.25-9 {number(across)} {number(up)}Q2-12 1.7-.35Z',ink),
           path('M-.7-6Q-4.9-10-8.8-17M.1-9Q6.5-13 9.5-23',stroke=shadow,width=1.35),
           arch_leader(across,up+13,bend*.77,14,(shadow,leaf,light)),
           arch_leader(-bend*.41,-7.4,bend*.85,reach*.92,(shadow,leaf,light)),
           arch_leader(bend*.37,-8.6,bend*.79,reach*.84,(shadow,light,pale)),
           arch_leader(-.8,-5.7,bend*.86,reach*.67,(shadow,leaf,light)),
           path('M-.65-.45Q-.5-4.9-.76-8.9',stroke='#87794c',width=.8),'</g>']
    return ''.join(parts)


def open_bed(model,design):
    ordered=sorted(enumerate(model['stems']),key=lambda item:item[1]['root'][1]);selected=set(design['stems'])
    original=planting(model);marker='<g data-species="';head,*children=original[:-4].split(marker)
    if len(ordered)!=len(children) or not selected<=set(range(len(ordered))):raise ValueError('Invalid open-bed stem registration')
    parts=[head]
    for (index,stem),child in zip(ordered,children):
        if index in selected and stem['species']!='spire':raise ValueError('Unregistered open-bed species')
        if index in selected and stem.get('habit')=='open-spire':
            placement,separator,_=child.partition('>');child=placement+separator+bed_crown(stem,design)+'</g>'
        parts.append(marker+child)
    return ''.join(parts)+'</g>'


def canal_grove(model):
    design=model['canalGrove']
    return {'eave-thicket':eave_thicket,'open-bed':open_bed}[design['form']](model,design)
