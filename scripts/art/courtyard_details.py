"""Native courtyard surfaces, garden furniture and enclosing walls in illustration coordinates."""
import json, math
from pathlib import Path
from .landscape import path, poly, ellipse, shape

def bench(x,y):
    p=[poly([(x-5,y),(x+5,y),(x+6,y+2),(x-4,y+2)],'#6a7051')]
    p.append(poly([(x-5,y-2),(x+5,y-2),(x+5,y),(x-5,y)],'#b6ac85','#687454',.3))
    for xx in [x-3.5,x+3.5]:p.append(path(f'M{xx} {y}v2.8',stroke='#8d9878',width=1))
    p.append(path(f'M{x-4.5} {y-1.6}h9',stroke='#e3d8b7',width=.35))
    return ''.join(p)

def planter(x,y,bamboo=False):
    p=[ellipse(x+1,y+1.5,3.8,1.3,'#526e4a','opacity=".16"'),
       poly([(x-2.8,y-3),(x+2.8,y-3),(x+2,y+1),(x-2,y+1)],'#9e8e65','#6e7755',.25),
       ellipse(x,y-3,3,1.2,'#d0c59d'),ellipse(x,y-3,2.4,.8,'#626b49')]
    if bamboo:
        for i in [-1,0,1]:
            xx=x+i*1.1;top=y-10-abs(i)*1.5
            p.append(path(f'M{xx} {y-3}Q{xx-1} {y-6} {xx+.7} {top}',stroke='#718455',width=.45))
            for j in range(3):
                yy=top+j*2
                p.append(path(f'M{xx} {yy}q-3-3-4-.8q.4 2.2 4 .8m0 1q2-3 3.8-1.3q-.2 1.8-3.8 1.3',fill='#7f9a5c',stroke='#536f44',width=.13))
    else:
        for i in range(9):
            a=i*math.tau/9;xx=x+math.cos(a)*2.1;yy=y-4+math.sin(a)*1.3
            p.append(path(f'M{x} {y-3}L{xx} {yy-2}',stroke='#789450',width=.4))
            p.append(ellipse(xx,yy-2,.8,.55,['#dab0a6','#a8b77c','#ebc4ac'][i%3]))
    return ''.join(p)

def rock(x,y):
    return (ellipse(x+1,y+.5,4.3,1.3,'#4e684b','opacity=".15"')+
            poly([(x-3,y),(x-2,y-3),(x-3,y-5),(x,y-8),(x+2,y-7),(x+1,y-4),(x+3,y-2),(x+2,y)],'#b7bea4','#7b8e76',.3)+
            path(f'M{x} {y-7}l-1 3 2 2-1 2',stroke='#e1ddc2',width=.45)+
            ellipse(x,y-4.3,.7,1.1,'#667d63'))

def table(x,y):
    p=[ellipse(x+.8,y+1.5,3.6,1.5,'#546d48','opacity=".13"'),path(f'M{x} {y-2}v3',stroke='#76684a',width=1),
       ellipse(x,y-2,3.5,1.8,'#a78d60'),ellipse(x,y-2.3,3.4,1.6,'#d1b987')]
    for dx,dy in [(-4,1),(4,1),(0,-5)]:
        p.append(path(f'M{x+dx} {y+dy}v1.5',stroke='#7a7453',width=.8))
        p.append(ellipse(x+dx,y+dy,1.1,.65,'#bfac7e'))
    p.append(ellipse(x-.6,y-2.5,.65,.32,'#eee1b6'))
    p.append(ellipse(x+1,y-2.4,.45,.25,'#80956a'))
    return ''.join(p)

def lantern(x,y):
    return (path(f'M{x} {y}v-11m-2 0h4',stroke='#766a4a',width=.65)+
            ellipse(x,y-8.5,1.35,2,'#c59b57')+ellipse(x-.3,y-8.8,.55,1.5,'#ead18c')+
            path(f'M{x-1} {y-10.4}h2m-2 3.9h2m-1 0v1.5',stroke='#e9cd83',width=.3))

def trellis(x,y):
    p=[]
    for xx in [x-4,x+4]:p.append(path(f'M{xx} {y}v-9',stroke='#8d7955',width=.7))
    for yy in [y-9,y-7,y-5]:p.append(path(f'M{x-5} {yy}h10',stroke='#a39267',width=.6))
    for i in range(8):
        xx=x-4+i;yy=y-8.5+(i%3)*1.6
        p.append(ellipse(xx,yy,1.1,.65,'#8da56a'))
    return ''.join(p)

def well(x,y):
    p=[ellipse(x+1,y+.5,3.3,1.4,'#526e4a','opacity=".16"')]
    p.append(poly([(x-3,y-2),(x,y-3),(x+3,y-2),(x+3,y),(x,y+1),(x-3,y)],'#b4b99e','#7c8e72',.3))
    p.append(ellipse(x,y-2.3,3,1.4,'#dfd9b8'));p.append(ellipse(x,y-2.3,1.8,.7,'#5d7660'))
    p.append(path(f'M{x-2.5} {y-2}v-5m5 5v-5m-5-1h5',stroke='#917d56',width=.55))
    return ''.join(p)

def urn(x,y):
    return (poly([(x-2.5,y-3),(x+2.5,y-3),(x+1.7,y),(x-1.7,y)],'#89906c','#5c7053',.25)+
            ellipse(x,y-3,2.8,1,'#b3b58a')+path(f'M{x-1.4} {y}v1.7m2.8-1.7v1.7m-1.4-5.3v-2',stroke='#627351',width=.5)+
            path(f'M{x-2.5} {y-2.6}q-2-2-2.5.2m7.5-.2q2-2 2.5.2',stroke='#8f9b72',width=.45))

def stage(x,y):
    p=[poly([(x-8,y-4),(x+8,y-4),(x+8,y+1),(x-8,y+1)],'#8b7752','#5e6648',.4)]
    p.append(poly([(x-9,y+1),(x+9,y+1),(x+10,y+3),(x-10,y+3)],'#d6cfad','#a4ad8e',.25))
    for xx in range(-7,8,2):p.append(path(f'M{x+xx} {y-4}v5',stroke='#bdac7d',width=.25))
    return ''.join(p)

ITEMS={'bench':bench,'planter':planter,'bamboo':lambda x,y:planter(x,y,True),'rock':rock,'table':table,
       'lantern':lantern,'trellis':trellis,'well':well,'urn':urn,'stage':stage}

def wall_segment(x,y,w):
    if w<2:return ''
    p=[poly([(x,y),(x+w,y),(x+w,y-4),(x,y-4)],'#e5e0c8','#a7b091',.3)]
    p.append(path(f'M{x} {y}h{w}',stroke='#879a7b',width=.8))
    p.append(path(f'M{x-.5} {y-4.4}h{w+1}',stroke='#61795b',width=.9))
    for i in range(2,int(w),3):p.append(path(f'M{x+i} {y-4.6}v.6',stroke='#a5b08b',width=.25))
    if w>16:
        cx=x+w/2;p.append(ellipse(cx,y-2.2,2.7,1.2,'#869777'))
        p.append(path(f'M{cx-2} {y-2.2}h4m-2-1v2',stroke='#d9d7b6',width=.25))
    return ''.join(p)

def ground(site):
    p=[]
    for index,c in enumerate(site.get('courts',[])):
        x,y,w,h=c['bounds'];key=f'court-{x}-{y}-{index}'
        if c.get('surface','paving')=='none':continue
        warm=c.get('surface')=='brick';base='#cec5a5' if warm else '#d6d5bd';line='#a7ab8e'
        p.append(f'<defs><pattern id="{key}" width="8" height="5" patternUnits="userSpaceOnUse"><rect width="8" height="5" fill="{base}"/><path d="M0 0h8M0 2.5h8M4 0v2.5M2 2.5V5" stroke="{line}" stroke-width=".22"/><path d="M.5 .5h3m1 2.5h3" stroke="#ece5c8" stroke-width=".25"/></pattern></defs>')
        p.append(poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],f'url(#{key})','#b6bc9d',.5))
        p.append(path(f'M{x+2} {y+2}h{w-4}v{h-4}H{x+2}Z',stroke='#ece4c4',width=.45))
        cx=x+w/2
        p.append(path(f'M{cx} {y+h}V{y+h-10}',stroke='#aaa98a',width=4))
        p.append(path(f'M{cx} {y+h}V{y+h-10}',stroke='#e4dcc0',width=3))
    if not p:return ''
    landscape=json.loads((Path(__file__).resolve().parents[2]/'src/data/town-landscape.json').read_text())
    blockers=''.join(path(shape(water),'black',extra='fill-rule="evenodd"') for water in landscape['water'])
    architecture=json.loads((Path(__file__).resolve().parents[2]/'src/data/town-architecture.json').read_text())['features']
    for f in architecture:
        if f['owner'] is not None:continue
        bx,by,bw,bh=f['bounds']
        if not any(bx+bw>=c['bounds'][0] and bx<=c['bounds'][0]+c['bounds'][2] and by+bh+7>=c['bounds'][1] and by<=c['bounds'][1]+c['bounds'][3] for c in site.get('courts',[])):continue
        blockers+=path(shape(f),'black',extra='fill-rule="evenodd"')
        if f['kind'] in ['roof','gold']:blockers+=path(shape(f),'black',extra='fill-rule="evenodd" transform="translate(0 6)"')
    mask='<defs><mask id="courtyard-land" maskUnits="userSpaceOnUse" x="0" y="0" width="2363" height="1672"><rect width="2363" height="1672" fill="white"/>'+blockers+'</mask></defs>'
    return mask+'<g mask="url(#courtyard-land)">'+''.join(p)+'</g>'

def details(site):
    p=[]
    for c in site.get('courts',[]):
        x,y,w,h=c['bounds']
        for item,ix,iy in c.get('items',[]):p.append(ITEMS[item](x+ix,y+iy))
        if c.get('wall'):
            gap=8;half=(w-8-gap)/2
            p.append(wall_segment(x+4,y+h,half));p.append(wall_segment(x+4+half+gap,y+h,half))
            for xx in [x+w/2-gap/2,x+w/2+gap/2]:
                p.append(poly([(xx-.8,y+h),(xx+.8,y+h),(xx+.8,y+h-6),(xx-.8,y+h-6)],'#e2dcc3','#a0ab8e',.25))
            p.append(path(f'M{x+w/2-5} {y+h-6.4}h10',stroke='#657d60',width=1.3))
    return ''.join(p)
