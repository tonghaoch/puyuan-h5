"""Flowering street trees: one grounded trunk, scaffold forks and terminal short shoots."""
import json
import math
import random

from .landscape import ellipse, number, path
from .surface_finishes import sampled_shape


PAINT = {
    'pink': ('#65433e', '#945e60', '#b7717b', '#d999a1', '#edb4bc', '#f7d1d1', '#939454'),
    'apricot': ('#66483c', '#906352', '#b57668', '#dea296', '#eebaae', '#f5d2bd', '#909453'),
}


def point(pair):
    return ' '.join(number(component) for component in pair)


def part(name, body):
    return f'<g data-flower-part="{name}">{body}</g>'


def joint(start, elbow, tip, station):
    return tuple((1-station)**2*first+2*(1-station)*station*bend+station**2*last for first,bend,last in zip(start,elbow,tip))


def shoot(start, elbow, tip, ink, weight):
    return path('M'+point(start)+'Q'+point(elbow)+' '+point(tip),stroke=ink,width=weight)


def rosette(center, width, angle, paints, rng):
    _,_,calyx,shadow,petal,light,_=paints
    body=path('M-1.08 .15Q-1.43-.45-.79-.70Q-.90-1.35-.20-1.11Q.31-1.39.62-.83Q1.32-.97 1.12-.32Q1.63.14.96.59Q1.06 1.15.41.99Q.06 1.40-.37.92Q-1.10 1.04-1.04.52Z',shadow)
    body+=path('M-1.07-.02Q-1.33-.56-.74-.65Q-.75-1.31-.16-1.01Q.29-1.31.60-.76Q1.28-.85 1.08-.33Q.69.06.27.05Q.10.53-.26.22Q-.75.42-1.07-.02Z',rng.choice((petal,petal,light)))
    body+=path('M-.34 .18Q-.01-.11.44.02Q.36.45.04.52Z',calyx)
    return f'<g transform="translate({point(center)}) rotate({number(angle)}) scale({number(width)})">'+body+'</g>'


def short_shoot(socket, tip, radius, side, paints, rng, terminal):
    bark,twig,calyx,_,_,_,green=paints
    elbow=(socket[0]+(tip[0]-socket[0])*.77,socket[1]-.12*radius)
    wood=[shoot(socket,elbow,tip,twig,.34+.06*radius)];flowers=[];leaves=[]
    rosettes=((.57,-.41,.10,.48),(.82,.48,.36,.63),(1,-.21,.41,.58)) if not terminal else ((.61,-.31,-.13,.40),(.91,.26,.23,.47))
    for rank,(station,reach,lift,weight) in enumerate(rosettes):
        neck=joint(socket,elbow,tip,station);head=(neck[0]+side*(reach+rng.uniform(-.13,.13))*radius,neck[1]-(lift+rng.uniform(-.07,.08))*radius)
        wood.append(shoot(neck,(head[0],neck[1]-.16),head,calyx,.19+.035*radius))
        flowers.append(rosette(head,radius*weight*rng.uniform(.78,1.08),rng.uniform(-65,65),paints,rng))
        if rank==0 and (terminal or rng.random()<.50):
            leaves.append(f'<g transform="translate({point(neck)}) rotate({-42*side})">'+path('M0 0Q-.5-.9-.28-1.65Q.73-1.31.55-.69Z',green)+'</g>')
    bud=(tip[0]+radius*.42*side,tip[1]-radius*(.29 if terminal else .18));spur=shoot(joint(socket,elbow,tip,.71),(bud[0]-.21*side,bud[1]+.58),bud,twig,.34);flowers.append(ellipse(bud[0],bud[1]-.17,radius*.23,radius*.29,calyx));return part('wood',''.join(wood))+part('leaf',''.join(leaves))+part('bloom',''.join(flowers))+part('wood',spur)


def scaffold(design, index, spec, tone, rng):
    station,bend,tip,load=spec;lean,shoulder,neck,cleft=design['stem'];foot=(0,0);fork=joint(foot,(lean,shoulder),(neck,cleft),station)
    side=1 if tip[0]>fork[0] else -1;paints=PAINT[tone];length=math.dist(fork,tip);limb=shoot(fork,bend,tip,paints[0],max(.57,min(1.13,length*.068)))
    limb+=shoot(joint(fork,bend,tip,.05),joint(fork,bend,tip,.29),joint(fork,bend,tip,.52),paints[1],.32)
    sprays=[]
    for rank,along in enumerate((.22,.48,.77,.96)):
        socket=joint(fork,bend,tip,along);direction=side if (rank+index)%2==0 else -side
        for stagger in range(2 if rank==2 or (rank==1 and index%2==0) else 1):
            bearing=direction if not stagger else -direction;reach=rng.uniform(.64,1.08)*load*(.48 if rank==3 else 1);rise=rng.uniform(.01,.35)*load if rank else -rng.uniform(.24,.57)*load
            takeoff=socket if not stagger else joint(fork,bend,tip,along+.055);end=(takeoff[0]+bearing*reach,takeoff[1]-rise)
            sprays.append(short_shoot(takeoff,end,load*rng.uniform(.82,1.09),bearing,paints,rng,rank==3))
    if index==len(design['limbs'])-1:
        heel=joint((0,0),(lean,shoulder),(neck,cleft),.56);droop=(heel[0]+side*load*1.13,heel[1]+.24*load);sprays.insert(0,short_shoot(heel,droop,load*.88,side,paints,rng,False))
    return f'<g data-flower-scaffold="{index}">'+part('wood',limb)+''.join(sprays)+'</g>'


def rooted_flower(model, design, front_roofs):
    stem,=model['stems'];root=[round(model[coord]+shift,3) for coord,shift in zip(('x','y'),stem['root'])]
    if root!=design['root'] or stem['species']!='blooming-bough' or stem['bloom']!=design['bloom']:
        raise ValueError('Flowering root, family or stock changed: '+model['id'])
    key=model['id'];lean,shoulder,neck,cleft=design['stem'];paints=PAINT[design['bloom']]
    bole=path(f'M-1.12 .22Q{number(lean-.50)} {number(shoulder)} {number(neck-.47)} {number(cleft)}L{number(neck+.51)} {number(cleft-.28)}Q{number(lean+.79)} {number(shoulder+.42)} .73 .1L.05-.35Z',paints[0]);bole+=shoot((-.46,-.5),(lean-.27,shoulder),(neck-.17,cleft),paints[1],.28)
    branches=[scaffold(design,index,limb,design['bloom'],random.Random(f'{key}:scaffold:{index}')) for index,limb in enumerate(design['limbs'])]
    body=part('ground',ellipse(.36,-.10,1.55,.43,'#786e52','opacity=".31"'))+part('wood',bole)+''.join(branches)
    body=f'<g transform="translate({point(root)})">{body}</g>'
    if 'frontRoof' in design:
        face=front_roofs[design['frontRoof']];left,top,wide,high=face['bounds'];mask='flower-behind-'+key
        area=f'x="{left-70}" y="{top-70}" width="{wide+140}" height="{high+140}"';body=f'<defs><mask id="{mask}" maskUnits="userSpaceOnUse" {area}><rect {area} fill="white"/>'+sampled_shape(face,'black')+f'</mask></defs><g mask="url(#{mask})">{body}</g>'
    return f'<g data-rooted-flower="{key}">{body}</g>'


def load_family(root):
    designs=json.loads((root/'src/data/se-flowering-scaffolds.json').read_bytes())['trees'];needed={row['frontRoof'] for row in designs.values() if 'frontRoof' in row};faces={feature['id']:feature for feature in json.loads((root/'src/data/town-architecture.json').read_bytes())['features'] if feature['id'] in needed and feature['kind']=='roof'}
    if set(faces)!=needed:raise ValueError('Missing foreground eave')
    return designs,faces
