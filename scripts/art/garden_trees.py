"""Pruned garden trees and pendant willows, in a 32 by 40 crown frame."""
import math

from .crowns import curve
from .landscape import ellipse, number, path


def shoot(start, control, end, pigment, wide):
    coords=' '.join(f'{number(x)},{number(y)}' for x,y in (start,control,end))
    return path('M'+coords.replace(' ','Q',1),stroke=pigment,width=wide)


def spreading_crown(rng,stem,key):
    gold=stem['paint']=='ochre';bark='#66502c' if gold else '#474732'
    palette=('#66461b','#b58129','#dfaf45','#edc257','#f4d57d') if gold else ('#243e21','#437442','#619653','#77a963','#93bd76')
    parts=[shoot((-.4,.2),(-.7,-8),(.6,-21),bark,2.4),shoot((.6,-.5),(.25,-9),(1.2,-17),'#aa8450' if gold else '#797658',.63)]
    for index,(cross,level,radius,depth,stem_height) in enumerate(stem['tiers']):
        joint=(0,stem_height);branch_end=(cross,level+depth*.45)
        parts.append(shoot(joint,(cross*.76,stem_height+.85),branch_end,bark,1.8))
        rim=[(cross+radius*across,level+depth*down) for across,down in [(-1,.11),(-.90,-.34),(-.51,-.72),(-.16,-1.0),(.16,-.95),(.45,-.74),(.63,-.44),(.86,-.30),(1,.05),(.91,.42),(.62,.64),(.18,.75),(-.09,.61),(-.53,.81),(-.83,.56)]]
        parts.append(leaf_pad(rng,rim,palette,f'{key}-tier-{index}',.85));parts.append(shoot((cross-radius*.26,level+depth*.71),(cross+radius*.12,level+depth*.75),(cross+radius*.32,level+depth*.53),palette[0],.92))
    return ''.join(parts)


def leaf_pad(rng, rim, palette, key, grain=1):
    ink,shade,ground,leaf,light=palette
    left=min(point[0] for point in rim);right=max(point[0] for point in rim)
    top=min(point[1] for point in rim);foot=max(point[1] for point in rim)
    wide=right-left;high=foot-top;body=curve(rim);clip='pad-'+key
    parts=[f'<g data-foliage-pad="{key}"><defs><clipPath id="{clip}">'+path(body,'white')+'</clipPath></defs>',path(body,ground),f'<g clip-path="url(#{clip})">']
    for index in range(round(wide*high*.23*grain)):
        across=rng.uniform(left,right);down=rng.uniform(top,foot);level=(down-top)/high
        radius=rng.uniform(.65,1.7);pigment=rng.choice((leaf,light,ground)) if rng.random()>.14+level*.48 else shade
        parts.append(ellipse(across,down,radius*1.12,radius*.84,pigment,f'opacity="{rng.uniform(.57,.91):.2f}"'))
    parts.append('</g>')
    for index,start in enumerate(rim):
        end=rim[(index+1)%len(rim)];length=math.dist(start,end);count=max(1,round(length/2.5))
        for segment in range(count):
            if rng.random()<.23:continue
            begin=(segment+rng.uniform(.02,.34))/count;stop=(segment+rng.uniform(.46,.93))/count
            pair=[tuple(near+(far-near)*at for near,far in zip(start,end)) for at in (begin,stop)]
            between=((pair[0][0]+pair[1][0])*.5,(pair[0][1]+pair[1][1])*.5+rng.uniform(-.26,.28))
            parts.append(shoot(pair[0],between,pair[1],ink if rng.random()<.72 else shade,rng.uniform(1.0,1.83)))
    return ''.join(parts)+'</g>'


def trained_pine(rng,key):
    shades=('#142c14','#3b7133','#72a55c','#7fb56c','#9dc386')
    parts=[ellipse(.7,.5,6.0,1.25,'#68794e','opacity=".62"'),
           path('M-3.3-.2Q-3.2-5.8-2.0-10.2Q-.5-16.5-.7-21.7L-.9-30.8L2.0-31.3Q3.1-20.5 2.0-15.0Q.9-9.2 1.5-2.1L3.1-.1L.4-.7Z','#47432c','#343a23',.56),
           shoot((-1.4,-2.5),(-1.7,-9.6),(.2,-16.3),'#766846',1.25),
           shoot((.3,-9.6),(-2.2,-17.4),(-10.2,-17.5),'#3a3b24',2.08),
           shoot((.4,-12.1),(2.4,-18.7),(10.2,-19.8),'#343a20',2.3),
           shoot((.9,-19.1),(3.1,-25.1),(7.7,-29.3),'#443e27',1.7)]
    for suffix,rim in [('west',[(-14,-18.1),(-12.4,-20.4),(-7.3,-21),(-3.8,-19.7),(-1.7,-17.4),(-2.8,-15.0),(-8.1,-14.5),(-12.8,-15.4)]),('east',[(1.0,-20.7),(5.4,-23.9),(9.0,-24.4),(12.4,-23.4),(16.3,-20.4),(16.8,-18.7),(14.6,-17.9),(9.1,-17.7),(5.5,-17.2),(1.2,-18.1)]),('leader',[(-13.1,-25.0),(-11.6,-28.9),(-8.0,-32.8),(-4.3,-36.0),(.5,-38.7),(3.2,-39.2),(7.2,-37.9),(9.3,-35.8),(12.0,-33.5),(13.5,-30.6),(12.9,-27.9),(8.3,-27.0),(3.2,-27.3),(-1.5,-25.8),(-6.3,-24.6)])]:
        parts.append(leaf_pad(rng,rim,shades,key+'-'+suffix))
    for start,elbow,tip in [((1,-22.3),(.1,-25.6),(-1.1,-28.6)),((-.5,-23.0),(1.1,-27.6),(4.5,-28.4)),((2.3,-15.6),(4,-17.1),(7.1,-17.9))]:
        parts.append(shoot(start,elbow,tip,'#344323',1.25))
    for start,elbow,tip in [((-.3,-13),(-4.3,-15.0),(-9.7,-14.5)),((-.1,-20.3),(2.3,-22.5),(1.4,-25.6)),((1.1,-23.1),(6.3,-25.7),(9.3,-27.1)),((-.2,-24.3),(-4.4,-23.7),(-8.1,-24.7)),((-.5,-26.4),(-1.2,-28.6),(-.7,-30.7))]:
        parts.append(shoot(start,elbow,tip,'#28381b',1.43))
    for across,level in [(-9.4,-32.2),(-12.4,-28.7),(-5.3,-34.9),(5.4,-36.8),(9.1,-32.9),(11.3,-30.3),(-8.2,-17.1),(7.7,-19.2)]:
        parts.append(shoot((across-1.6,level+1.1),(across,level+.6),(across+.5,level-.93),'#365e31',1.36))
    parts.append(shoot((-6.1,.5),(-3.9,-1.7),(-1.6,-1.1),'#40502e',1.4))
    return ''.join(parts)


def forked_dome(rng,palette,key):
    lime=palette=='lime';shades=('#293e17','#60893d','#91b949','#a2c65c','#bed178') if lime else ('#284b22','#598d46','#7eb865','#8dc473','#a0cf86')
    parts=[path('M.8 .2L.3-2.8Q-1.3-4.7-5.4-5.1L-8.4-8.7L-8.0-10.1Q-5.8-6.5-3.2-6.4L-4.6-11.3L-3.7-11.8Q-3-7.9-1.4-6.4Q1-7.3 2.6-12.4L4-12.3Q3.5-8.4 1.7-5.4L1.8-1.7L3 .2Z','#544831','#423d2b',.45),
           shoot((-4,-5.8),(-7.3,-5.9),(-10.2,-9.9),'#534a2e',.86),shoot((-4,-5.9),(-3.5,-7.3),(-2.8,-10.9),'#483e29',.83)]
    rim=[(-17.7,-12.1),(-18.1,-15.8),(-16.4,-18.1),(-17.2,-21.5),(-16.7,-24.7),(-18.9,-26.5),(-15.6,-27.8),(-13.6,-31.2),(-10.0,-33.1),(-9.0,-35.7),(-6.0,-37.4),(-4.8,-39.3),(-2.4,-38.9),(.1,-40.0),(3.5,-38.1),(6.1,-37.6),(7.9,-35.3),(11.0,-34.2),(11.1,-31.8),(13.8,-30.0),(13.0,-27.2),(14.1,-25.1),(12.7,-21.7),(13.6,-19.9),(13.1,-17.6),(15.1,-15.2),(14.1,-13.6),(10.2,-14.4),(7.4,-13.0),(4.9,-10.7),(1.8,-10.1),(-1.0,-8.7),(-5.1,-8.5),(-9.5,-9.7),(-13.8,-9.9)]
    parts.append(leaf_pad(rng,rim,shades,key+'-shade',.54));parts.append(path('M-16.2-13.6Q-12.1-14.0-10.6-19.8Q-9.5-20.6-10.1-17.5Q-10.7-12.9-14.5-12.2Z',shades[1],extra='opacity=".57"'))
    for start,mid,tip in [((-6.1,-34.9),(-3.2,-32.8),(-1.6,-33.1)),((1.2,-31.2),(3.6,-30.8),(4.5,-29.4)),((7.0,-25.7),(9.5,-24.7),(9.3,-22.1)),((-14.4,-22.5),(-12.4,-23.5),(-10.6,-22.8)),((-7.6,-15.9),(-3.1,-15.4),(-1.4,-14.3)),((-.7,-14.4),(1.9,-13.4),(3.1,-14.6))]:
        parts.append(shoot(start,mid,tip,shades[1],1.27));parts.append(shoot(mid,((mid[0]+tip[0])/2,(mid[1]+tip[1])/2),tip,shades[0],.78))
    return ''.join(parts)


def pendant_willow(rng,key):
    shades=('#354c20','#5e8a34','#8cb94e','#9ac75a','#bcdb81');parts=[path('M-1.9 .1L-1.7-4.4Q-1.8-11.7-7.5-16.4L-6.9-18.1Q-3.0-15.8-.6-13.9L-1.5-24.8L.0-24.4L1.8-14.9Q5.4-17.4 8.3-24.8L9.1-23.9Q8.9-17.2 3.2-11.5Q-.2-7.3 1.7-1.0L3.1-.1L.1-.8Z','#585633','#484a29',.55)]
    boughs=[(-11.6,-30.2,-7.2,3.8),(-7.1,-35.2,-6.2,5.3),(-1.4,-38.0,-10.4,5.0),(5.0,-36.0,-9.4,5.6),(10.5,-30.7,-6.0,5.1)]
    for idx,(cross,head,toe,span) in enumerate(boughs):
        lean=cross*.12;crest=(cross,head);left=cross-span;right=cross+span
        rim=[(cross-span*.21,head-.7),(cross+span*.49,head+.5),(right-.45,head+3.1),(right,head+6.6),(right+lean,toe-2.3),(right+lean-.7,toe),(cross+lean+.5,toe-.3),(left+lean+1.6,toe+1),(left+lean+.45,toe-.85),(left,head+9.3),(left+.25,head+5.0),(cross-span*.65,head+1.6)]
        wash=f'willow-{key}-{idx}'
        parts.append(f'<defs><linearGradient id="{wash}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="{shades[2]}"/><stop offset=".62" stop-color="{shades[idx%2+2]}"/><stop offset="1" stop-color="{shades[3]}" stop-opacity=".68"/></linearGradient></defs>')
        parts.append(path(curve(rim),f'url(#{wash})'))
        for spray in range(12):
            side=rng.uniform(-.89,.89);tip=(cross+side*span+lean,toe+rng.uniform(-2.1,1.1));bud=(cross+side*span*.4,head+abs(side)*3.1+rng.uniform(.1,2.0));elbow=(cross+side*span*1.16,head+7.0);color=rng.choice(shades[1:]);parts.append(shoot(bud,elbow,tip,color,rng.uniform(.47,.86)))
            for step in (1,2,3,4,5):
                level=(step+rng.uniform(-.25,.25))/6;px,py=(a*(1-level)**2+2*b*(1-level)*level+c*level**2 for a,b,c in zip(bud,elbow,tip));swing=rng.choice((-1,1))*rng.uniform(.4,1.1);parts.append(shoot((px,py),(px+swing,py+.7),(px+swing*.55,py+rng.uniform(1.3,2.5)),color,.56))
        parts.append(shoot((left+.4,head+6.1),(left+.2,head+3),(cross-1,head+.1),shades[0],.84));parts.append(shoot(crest,(cross+span*.6,head+.6),(right-.6,head+4),shades[1],.81))
    parts.append(shoot((.3,-4.1),(1.6,-11.2),(-2.2,-13.7),'#665e35',1.8))
    for start,elbow,tip in [((.9,-11.7),(-5.4,-12.1),(-7.3,-18.5)),((-.2,-15.0),(-3.1,-19.5),(-1.6,-23.4)),((.9,-12.3),(5.5,-13.6),(8.2,-20.3))]:
        parts.append(shoot(start,elbow,tip,'#45512b',1.23))
    return '<g data-habit="pendant-curtains">'+''.join(parts)+'</g>'


def leafy_sprays(rng,leaders,pendant):
    parts=[]
    for head_x,head_y,tip_x,tip_y in leaders:
        parts.append(f'<g data-spray="{number(head_x)} {number(head_y)}">')
        shoulder=(head_x*.54,head_y*.49)
        parts.append(shoot((0,0),shoulder,(head_x,head_y),'#8c994e' if pendant else '#718c37',1.25))
        if not pendant:
            for joint in (1,2,3):
                at=.31+joint*.14;cross=head_x*at;level=head_y*at
                for side in (-1,1):
                    fan=side*rng.uniform(6.6,10.8);lift=rng.uniform(4.0,7.3);tip=(cross+fan,level-lift)
                    parts.append(shoot((cross,level),(cross+fan*.62,level-lift*1.24),tip,'#628b2e',.83))
                    for leaf in range(7):
                        along=(leaf+.35)/7;bud=(cross+fan*along,level-lift*along*(1.9-along));spread=side*rng.uniform(.8,2.4);rise=rng.uniform(1.7,3.8)*(-1 if leaf%2 else .8)
                        parts.append(shoot(bud,(bud[0]+spread*.7,bud[1]+rise*.35),(bud[0]+spread,bud[1]+rise),rng.choice(('#3d7027','#579320','#77aa2c','#91bf39','#aac94b')),rng.uniform(.86,1.65)))
        bend=(tip_x+.18*(tip_x-head_x),head_y+(tip_y-head_y)*.27)
        parts.append(shoot((head_x,head_y),bend,(tip_x,tip_y),'#9bb647',1.1))
        for index in range(19):
            at=(index+rng.uniform(.1,.8))/19
            cross,level=(a*(1-at)**2+2*b*(1-at)*at+c*at**2 for a,b,c in zip((head_x,head_y),bend,(tip_x,tip_y)))
            reach=(2.0+2.2*math.sin(at*math.pi))*(1-at*.48)*rng.uniform(.73,1.1);side=(-1 if index%2 else 1);length=(5.4 if pendant else 3.2)*rng.uniform(.73,1.19)
            tone=rng.choice(('#426925','#598c29','#699f2d','#78af34','#92c048') if at<.52 or not pendant else ('#85a93c','#9cbe47','#afcb51','#b9ce65'))
            parts.append(path(f'M{number(cross)},{number(level)}q{number(side*reach*.33)},{number(-.7)} {number(side*reach)},{number(length*.46)}q{number(-side*reach*.24)},{number(length*.19)} {number(-side*reach*.18)},{number(length*.55)}Q{number(cross)},{number(level+length*.43)} {number(cross)},{number(level)}Z',tone))
        parts.append('</g>')
    return ''.join(parts)
