"""Authored courtyard/house completions where printed reference labels hid the scene.

These are native art designs, not claims about measured or previously hidden architecture.
"""
import math
import random
from .landscape import path, poly, ellipse
from .courtyard_details import details

def footprint(model):
    x,y,w,d,h=model[:5];a=math.radians(model[6] if len(model)>6 else 0)
    points=[(0,0),(w,0),(w,d-3),(w+2,d-3),(w+2,d+h-2),(w-2,d+h),(2,d+h),(2,d),(0,d)]
    return [(x+px*math.cos(a)-py*math.sin(a),y+px*math.sin(a)+py*math.cos(a)) for px,py in points]

def house(x,y,w,d,h,kind='residence',angle=0):
    p=[f'<g transform="translate({x} {y}) rotate({angle})">']
    timber=kind in ['shop','gallery','hall','shrine'];gold=kind=='gold-hall'
    wall='#996d49' if timber else '#e6e1ca';shade='#6e674f' if timber else '#bcc5a7'
    roof='#a99051' if gold else '#59565a';roof_dark='#7e6a3d' if gold else '#39373c';roof_light='#d7c08a' if gold else '#a49f97'
    p.append(poly([(1,d+h),(w-1,d+h),(w+3,d+h+3),(5,d+h+3)],'#4e6848'))
    p.append(poly([(2,d-1),(w-2,d-1),(w-2,d+h),(2,d+h)],wall,'#65785b',.4))
    p.append(poly([(w-2,d-1),(w+2,d-3),(w+2,d+h-2),(w-2,d+h)],shade,'#65785b',.3))
    bays=max(2,int(w/6))
    for i in range(bays):
        xx=3+i*(w-6)/bays;ww=(w-6)/bays-1
        p.append(poly([(xx,d+1),(xx+ww,d+1),(xx+ww,d+h-1.6),(xx,d+h-1.6)],'#59694e','#a28f64',.23))
        for n in [1,2]:p.append(path(f'M{xx+ww*n/3:.2f} {d+1}v{h-2.6}',stroke='#c0b68a',width=.17))
        p.append(path(f'M{xx} {d+h*.45}h{ww}',stroke='#c0b68a',width=.18))
        p.append(path(f'M{xx-.5} {d}v{h}',stroke='#514f39',width=.65))
        p.append(path(f'M{xx-.7} {d-.2}h2m-1.6 .8h1.2',stroke='#c1ac77',width=.3))
    p.append(path(f'M1 {d+h}H{w-1}',stroke='#d2c7a2',width=.9))
    a=(w*.18,d*.22-2);b=(w*.81,d*.22-2)
    p.append(poly([(0,0),(w,0),b,a],roof_light,roof_dark,.3))
    p.append(poly([(0,0),a,(0,d)],roof,roof_dark,.3))
    p.append(poly([(w,0),(w,d),b],roof_dark,roof_dark,.3))
    p.append(poly([(0,d),(w,d),b,a],roof,roof_dark,.35))
    # Tile channels follow each roof plane rather than a screen-space grid.
    for i in range(1,max(10,int(w/.9))):
        t=i/max(10,int(w/.9));sx=a[0]+(b[0]-a[0])*t
        p.append(path(f'M{sx:.2f} {a[1]}L{w*t:.2f} {d}',stroke=roof_light,width=.18,extra='opacity=".62"'))
    for j in range(1,5):
        t=j/5;left=(a[0]*(1-t),a[1]*(1-t)+d*t);right=(b[0]*(1-t)+w*t,b[1]*(1-t)+d*t)
        p.append(path(f'M{left[0]:.2f} {left[1]:.2f}L{right[0]:.2f} {right[1]:.2f}',stroke=roof_dark,width=.22,extra='opacity=".7"'))
    p.append(path(f'M{a[0]-1} {a[1]-1}Q{a[0]} {a[1]} {a[0]+2} {a[1]}H{b[0]-2}Q{b[0]} {b[1]} {b[0]+1} {b[1]-1}',stroke=roof_light,width=.75))
    p.append(path(f'M-1 {d-1.5}Q0 {d+.8} 3 {d+.8}H{w-3}Q{w} {d+.8} {w+1} {d-1.5}',stroke=roof_light,width=.6))
    p.append(path(f'M0 {d+1.4}H{w}',stroke=roof_dark,width=.5))
    if kind=='shop':
        for xx in [w*.2,w*.8]:
            p.append(path(f'M{xx} {d+.6}v2',stroke='#8b7752',width=.3))
            p.append(ellipse(xx,d+3,.85,1.3,'#c99757'))
            p.append(path(f'M{xx} {d+4.3}v1.1',stroke='#dab674',width=.25))
    return ''.join(p)+'</g>'

def completion(site):
    p=[]
    for house_data in site.get('houses',[]):p.append(house(*house_data))
    p.append(details(site))
    return ''.join(p)


def stone_arris(edge, seed):
    rng=random.Random(seed)
    parts=[]
    for start,end in zip(edge,edge[1:]):
        length=math.dist(start,end)
        if length==0:continue
        def station(distance):
            return tuple(first+(last-first)*distance/length for first,last in zip(start,end))
        def mark(low,high,color,width):
            first,last=station(low),station(high)
            return path(f'M{first[0]:.2f},{first[1]:.2f}L{last[0]:.2f},{last[1]:.2f}',stroke=color,width=width)
        parts.append(mark(0,length,'#d7d9ce',.40))
        low=0
        while low<length:
            high=min(length,low+rng.uniform(3.4,4.8))
            parts.append(mark(low,low+(high-low)*rng.uniform(.12,.27),rng.choice(('#34382f','#43483b','#515646')),rng.uniform(.79,1.04)))
            low=high
    return ''.join(parts)


def pale_block(block):
    def trace(points):
        return 'M'+'L'.join(f'{horizontal:.2f},{vertical:.2f}' for horizontal,vertical in points)
    parts=[f'<g id="{block["id"]}">']
    for index,unit in enumerate(block['units']):
        top,lip,rise=unit['top'],unit['lip'],unit['rise']
        bottom=[(horizontal,vertical+rise) for horizontal,vertical in lip]
        parts.append(poly(lip+bottom[::-1],['#cccbbc','#d5d4c9','#c5c6b8'][index%3]))
        parts.append(path(trace(bottom),stroke='#8f9083',width=.43))
        if 'shadedReturn' in unit:
            side=unit['shadedReturn'];edge=side['edge'];foot=side['foot']
            parts.append(poly(edge+foot[::-1],'#54534e','#64655c',.4))
            parts.append(path(trace(foot),stroke='#a8a299',width=.63))
        parts.append(poly(top,['#ebeee8','#ecefe9','#e9ede6'][index%3],'#b9bdb2',.38))
        parts.append(path(trace([(horizontal-.12,vertical+.85) for horizontal,vertical in lip]),stroke='#f2f2e7',width=.46))
    for opening in block.get('openings',[]):
        back_left,back_right,front_right,front_left=opening['rim'];left_foot,right_foot=opening['wallFoot']
        parts.append(poly(opening['rim'],'#c4c3a6'))
        parts.append(poly([back_left,back_right,right_foot,left_foot],'#dddccf'))
        parts.append(poly([back_left,left_foot,front_left],'#ceccbb'))
        parts.append(poly([left_foot,right_foot,front_right,front_left],'#bfbea2'))
        parts.append(stone_arris(opening['wallFoot'],'recess-foot'))
        parts.append(stone_arris(opening['rim']+[back_left],'recess-rim'))
    for index,edge in enumerate(block['copings']):
        parts.append(stone_arris(edge,f'{block["id"]}-{index}'))
    return ''.join(parts)+'</g>'
