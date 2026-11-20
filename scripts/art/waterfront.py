"""Projected canal crossings and covered skiffs in illustration coordinates."""
import math
import random

from .landscape import ellipse, number, path, poly


def between(first,last,fraction):
    return tuple(start+(end-start)*fraction for start,end in zip(first,last))


def lift(point,amount):
    return point[0],point[1]-amount


def stroke(points,color,width,extra=''):
    return path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in points),stroke=color,width=width,extra=extra)


def pile_bridge(model,at,edge):
    parts=[];height=model['railLift']
    for along,width,drop,lean in model['bents']:
        parts.append('<g data-trestle-bent="timber">')
        for side in (.16,.94):
            cross,top=at(along,side);left=(cross-width/2,top);right=(cross+width/2,top)
            foot=(left[0]+lean,top+drop);toe=(right[0]+lean,top+drop-.30)
            parts.extend([poly([left,right,toe,foot],'#936d43','#403a2c',.60),stroke([lift(foot,.90),lift(toe,.9)],'#665740',1.0),stroke([lift(right,-1.2),lift(toe,.92)],'#bd9c66',.55)])
        parts.append(poly([at(along-.026,.15,-1.1),at(along+.039,.15,-1.1),at(along+.04,1,-1.6),at(along-.032,1,-1.4)],'#75573a','#564830',.48));parts.append('</g>')
    rear,front=edge(0),edge(1);parts.extend([poly(front+edge(1,-1.05)[::-1],'#6b4e34','#463c2a',.54),poly(rear+front[::-1],'#d2ad79','#594a32',.53)])
    for index in range(1,model['planks']):
        station=index/model['planks'];parts.append(stroke([at(station,.06),at(station,.91)],'#987550',.45));parts.append(stroke([at(station+.012,.14),at(station+.012,.74)],'#e5c597',.35))
    for side in (.02,.98):
        for along in model['stanchions']:
            base=at(along,side,-.26);head=at(along,side,height)
            parts.extend([stroke([base,head],'#654a32',.94),stroke([lift(base,.19),lift(head,-.33)],'#b1905b',.40)])
        parts.extend([stroke(edge(side,height),'#574a30',1.0),stroke(edge(side,height+.35),'#d0b181',.42)])
    return ''.join(parts)


def projected_span(model):
    stations=model['sections'];centers=[between(*pair,.5) for pair in stations];lengths=[0]
    for first,last in zip(centers,centers[1:]):lengths.append(lengths[-1]+math.dist(first,last))
    def at(fraction,side,up=0):
        distance=fraction*lengths[-1]
        index=next((ix for ix,total in enumerate(lengths[1:]) if total>=distance),len(stations)-2)
        along=(distance-lengths[index])/(lengths[index+1]-lengths[index]);near,far=stations[index:index+2]
        return lift(between(between(*near,side),between(*far,side),along),up)
    def edge(side,up=0):return [lift(between(*row,side),up) for row in stations]
    wood=model['material']=='timber';key=model['id'];lift_rail=model['railLift'];depth=model['apron'];rng=random.Random(key)
    face,shadow,cap,deck={
        'chalk':('#9c9891','#494642','#e3ded2','#d3cfc5'),
        'rose':('#a18991','#4f414b','#e6c6d6','#d9b8cb'),
        'shell-stone':('#968882','#514a46','#ded5d2','#c9bcb7'),
        'granite':('#81898d','#464a4d','#d5d9d7','#b8bec0'),
        'timber':('#916a46','#493e32','#c8ab83','#c6a579'),
    }[model['stone']]
    parts=[f'<g id="{key}" data-bridge-form="{model["stone"]}">'];front=edge(1);rear=edge(0)
    if model.get('construction')=='pile-bents':
        return ''.join(parts)+pile_bridge(model,at,edge)+'</g>'
    if model.get('construction')=='kerbed-slab':
        parts.append(poly(front+edge(1,-depth)[::-1],face,shadow,.53))
        parts.append(poly(rear+front[::-1],deck,shadow,.61))
        for index in range(1,5):
            fraction=index/5;parts.append(stroke([at(fraction,.15),at(fraction+.02,.70)],face,.52))
        for side,inside in [(0,.21),(1,.81)]:
            shoulder=edge(inside);raised=edge(side,lift_rail)
            parts.append(poly(shoulder+raised[::-1],cap,face,.35))
            for index in range(5):
                start=index/5;end=(index+1)/5
                parts.append(poly([at(start,side,lift_rail),at(end,side,lift_rail),at(end,inside),at(start,inside)],(cap,face,cap,deck,face)[(index+side)%5]))
                if (index+side)%3!=1:
                    parts.append(stroke([at(start+.02,side,lift_rail),at(end-.03,side,lift_rail)],shadow,.84))
        return ''.join(parts)+'</g>'
    if model.get('construction')=='flat-slab':
        parts.append(poly(front+edge(1,-depth)[::-1],face,shadow,.4))
        parts.append(poly(rear+front[::-1],deck,shadow,.45))
        for across in (.04,.97):parts.append(stroke(edge(across),cap,.36))
        for along in (.12,.54,.88):parts.append(stroke([at(along,.03),at(along,.95)],face,.38))
        for along in model.get('edgeStones',[]):
            for across in (.04,.96):
                foot=at(along,across);parts.append(stroke([foot,lift(foot,.65)],shadow,.91))
                parts.append(ellipse(foot[0],foot[1]-.65,.53,.27,face))
        return ''.join(parts)+'</g>'
    if wood:
        for index in range(max(2,round(lengths[-1]/9))):
            pos=(index+.42)/max(2,round(lengths[-1]/9))
            for across in (.17,.88):
                post=at(pos,across);foot=lift(post,-depth-1.6)
                parts.append(stroke([post,foot],shadow,1.15));parts.append(stroke([lift(post,-depth),at(min(1,pos+.07),across,-.8)],face,.63))
        parts.append(poly(front+[lift(p,-1.2) for p in front[::-1]],shadow))
    else:
        intervals=24;soffit=[]
        for index in range(intervals+1):
            pos=index/intervals;bow=math.sqrt(max(0,1-((pos-.5)/.37)**2))
            soffit.append(at(pos,1,-max(.62,depth*(1-bow)+.45)))
        parts.append(poly(front+soffit[::-1],face,shadow,.39))
        parts.append(stroke(soffit,shadow,.45))
    parts.append(poly(rear+front[::-1],deck,shadow,.43))
    count=max(4,round(lengths[-1]/(1.7 if wood else 2.25)))
    for index in range(count):
        pos=index/count;end=(index+1)/count;seam=rng.uniform(.31,.77)
        if not wood and index%3!=1:
            low,high=(.09,seam) if index%2 else (seam,.91)
            parts.append(poly([at(pos,low),at(pos,high),at(end,high),at(end,low)],rng.choice([cap,deck])))
        parts.append(stroke([at(pos,.09),at(pos,.91)],face,.35 if wood else .32))
        if wood:parts.append(stroke([at(pos,.18),at(pos,.68)],cap,.32))
    for side in (.03,.98):
        posts=max(3,round(lengths[-1]/4.2));parts.append(stroke(edge(side),shadow,.65))
        if wood:parts.append(stroke(edge(side,lift_rail*.57),face,.49))
        parts.append(stroke(edge(side,lift_rail),shadow,.83 if wood else .72))
        parts.append(stroke(edge(side,lift_rail+.25),cap,.37))
        for index in range(posts+1):
            ratio=index/posts;foot=at(ratio,side);head=lift(foot,lift_rail+.65)
            parts.append(stroke([foot,head],shadow,.95 if wood else .8))
            parts.append(ellipse(head[0],head[1],.58,.33,face if wood else cap))
    return ''.join(parts)+'</g>'


def boat(model):
    reed=model['canopy'] in ('bamboo','woven-hood');key=model['id'];rng=random.Random(key)
    def rib(x,width,height):return f'M{number(x-width)},-2.7q-.2,-{number(height)} {number(width)},-{number(height)}q{number(width)},.1 {number(width+.65)},{number(height-.1)}'
    facing=' scale(-1 1)' if model.get('bow')=='west' else ''
    parts=[f'<g id="{key}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]}) scale({model["scale"]}){facing}">',
           path('M-16 2.1Q-13 7.6 1 7.7Q12.4 7.1 16.8 2.1',stroke='#c9e8e4',width=1.1),
           path('M-15.6 -.7Q-12 2.7 .6 3.3Q11.4 3.1 16.4-.7L15.6 2.3Q11.2 6.7 2.1 6.4Q-9.4 6.6-14.5 2.8Z','#82533c','#4f4938',.59),
           path('M-14.8-.2Q-13-4.9-4-5.3L6.7-5Q13.9-4.7 16.4-.7Q10.5 3.5 1.5 3.25Q-9.2 3.0-14.8-.2Z','#d4ad81','#78573f',.49),
           path('M-12.6 2.4Q-1.8 7.0 12.7 3.15',stroke='#aa714f',width=.62)]
    stern=-12.3;end=3.0 if reed else 11.6;posts=4 if reed else 5
    for index in range(posts):
        x=stern+(end-stern)*index/(posts-1);up=4.2 if reed else 5.2+.65*abs(index-(posts-1)/2)
        parts.append(path(f'M{number(x)} 1.1v-{number(up)}',stroke='#4d352a',width=1.02))
        if index+1<posts:
            other=stern+(end-stern)*(index+1)/(posts-1)
            parts.append(poly([(x+.6,1),(other-.5,1.45),(other-.5,1.45-up),(x+.6,1-up)],'#e5c193' if reed else '#ebcfab','#ad8969',.23))
            parts.append(path(f'M{number(x+1)} .43v-{number(up*.68)}',stroke='#e9d8b6',width=.44))
    if reed:
        if model['canopy']=='woven-hood':
            parts.append(path('M-13.6-.9Q-14.7-8.6-10.2-11.3Q-4.1-14 1.1-10.9Q4.2-8.5 4.7-4.3L2.8-1.6Q-3.1-3.2-6.2-2.8L-11.8.25Z','#bb9363','#72583d',.54))
            for across in (-10,-7.4,-5.1,-2.8):
                parts.append(path(f'M{number(across)} -2.4q.6-2.8-.45-5.3',stroke='#a98352',width=.62))
        roof='M-14.4-3.1Q-14.4-9.4-10.4-11.7Q-4.2-15 1.2-11.3Q5.0-9.6 5.3-3.0L3.8-2.1Q-.4-7.9-3.4-7.9Q-8.3-7.6-12.4-2.3Z'
        parts.append(path(roof,'#c6a379','#745e43',.64))
        for index in range(10):
            x=-12.3+index*1.53;level=-6.2-3.1*math.sin(math.pi*index/10)
            parts.append(path(f'M{number(x)} {number(level)}q1.05 -1.6 2.4 -1.8',stroke=rng.choice(['#a98158','#ddc09a','#b7966d']),width=.44))
        for x in (-11,-4,2.1):parts.append(path(rib(x,.85,4.6),stroke='#826343',width=.55))
        for x in (7.4,11.4):parts.append(path(f'M{x} -2.25l.45 3.32',stroke='#9a724d',width=.78))
    else:
        roof='M-14.2-3Q-14.2-8.7-11.2-9.05Q-4.9-9.55 0-7.25Q5.8-5.55 10.1-9.5Q12.3-10.5 13.2-6.3L12.5-2.95Q10.3-6.25 8.9-5.05Q4.1-1.15-1.7-3.35Q-8.7-6.4-11.3-5.5L-13.6-1.7Z'
        parts.append(path(roof,'#526467','#383d3b',.59))
        for index in range(13):
            x=-11.6+index*1.85;level=-7.55+1.6*math.sin((index-2)*math.pi/10)
            parts.append(path(f'M{number(x)} {number(level)}q.9 .25 1.28 2.6',stroke=rng.choice(['#718180','#48585b','#89938d']),width=.64))
    parts.append(path('M-14.8 -.1Q-9.7 2.95.8 3.2Q11 3.25 15.9-.45',stroke='#65472f',width=.65))
    return ''.join(parts)+'</g>'
