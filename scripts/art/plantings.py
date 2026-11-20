"""Rooted plant groups in illustration space; each stem has its own species, spread and height."""
import math
import random

from .bank_evergreen import bank_evergreen
from .crowns import curve
from .garden_trees import forked_dome, leaf_pad, leafy_sprays, pendant_willow, spreading_crown, trained_pine
from .landscape import ellipse, number, path


PAINT = {
    'leaf': ('#263b20', '#58864c', '#80b46a', '#9dcb7c', '#c1dba0'),
    'pine': ('#243922', '#426b3e', '#639553', '#7fb269', '#b0cd8b'),
    'lime': ('#404c21', '#758b38', '#99bb4c', '#b9d36d', '#d4e698'),
    'ochre': ('#705226', '#ae782c', '#d9a43c', '#ebc45b', '#f6df92'),
    'citron': ('#3e431f', '#8d9149', '#c4c871', '#dadd91', '#eeeab0'),
    'straw': ('#38361b', '#a0984e', '#e3d88c', '#eddf9c', '#f4ebbc'),
    'sage': ('#314322', '#689255', '#9ebd79', '#b6d399', '#d0e1ad'),
}


def point(horizontal, vertical):
    return f'{number(horizontal)} {number(vertical)}'


def bough(start, elbow, tip, pigment, width):
    return path('M'+point(*start)+'Q'+point(*elbow)+' '+point(*tip), stroke=pigment, width=width)


def foliage(rng, horizontal, vertical, wide, tall, palette):
    rim = []
    for index in range(25):
        angle = math.tau*index/25
        radius = rng.uniform(.87, 1.03)
        rim.append((horizontal+wide*math.cos(angle)*radius, vertical+tall*math.sin(angle)*radius))
    parts = [path(curve(rim), palette[2], palette[1], .45)]
    for tuft in range(max(4,round(wide*tall*.18))):
        angle=rng.random()*math.tau; radius=rng.random()**.48*.76
        across=horizontal+wide*math.cos(angle)*radius; down=vertical+tall*math.sin(angle)*radius
        brush=rng.uniform(.8,2.1)*min(1.15,tall*.24)
        pigment=palette[1 if math.sin(angle)*radius+rng.uniform(-.45,.45)>.16 else 3]
        parts.append(path('M'+point(across-brush,down)+'q'+point(.15*brush,-1.7*brush)+' '+point(1.25*brush,-1.31*brush)+'q'+point(1.6*brush,-.5*brush)+' '+point(1.0*brush,1.05*brush)+'q'+point(-1.06*brush,1.11*brush)+' '+point(-2.25*brush,.26*brush)+'Z',pigment,extra='opacity=".80"'))
    brushes = [[] for pigment in palette]
    for index in range(max(12, round(wide*tall*.74))):
        angle = rng.uniform(0, math.tau)
        radius = rng.random()**.48*.97
        across, down = radius*math.cos(angle), radius*math.sin(angle)
        shade = 2+round(rng.uniform(-1.28, 1.28)-.72*down-.24*across)
        if radius>.77 and rng.random()<.30: shade = 0
        leaf = rng.uniform(.52, 1.18)
        brushes[min(4,max(0,shade))].append('M'+point(horizontal+wide*across, vertical+tall*down)+'q'+point(-leaf,-leaf*.8)+' '+point(.2,-leaf*1.46)+'q'+point(leaf,.23)+' '+point(-.2,leaf*1.46)+'Z')
    parts.extend(path(''.join(strokes), pigment) for strokes,pigment in zip(brushes,palette) if strokes)
    for index in range(max(3,round((wide+tall)*.47))):
        angle=rng.uniform(0,math.tau);radius=rng.choice((.97,.94,.85,.66,.28));cross=math.cos(angle);drop=math.sin(angle)
        tip=(horizontal+wide*cross*radius,vertical+tall*drop*radius);reach=rng.uniform(.68,1.53)
        parts.append(bough(tip,(tip[0]-.12,tip[1]+reach*.68),(tip[0]+reach*.5,tip[1]+reach),palette[0],rng.uniform(.46,.93)))
    for index,start in enumerate(rim):
        across,down=rim[(index+1)%len(rim)];sunlit=start[1]<vertical
        if rng.random()<(.72 if sunlit else .33):continue
        fraction=rng.uniform(.36,.88);end=(start[0]+(across-start[0])*fraction,start[1]+(down-start[1])*fraction)
        parts.append(bough(start,(start[0]*.45+end[0]*.55,start[1]*.45+end[1]*.55+.33),end,palette[0],rng.uniform(.50,.96)))
    return ''.join(parts)


def woody(rng, species, palette):
    clusters = {
        'umbrella': [(-6,-15.4,9.1,6.5),(5.5,-16.3,10.1,6.9),(-6.3,-23.6,8.6,8.1),(6,-24.5,8.4,8.0),(-1,-30.8,9,8.5)],
        'cloud-pine': [(-7.6,-14,8,4.0),(6.1,-15.8,9.7,4.6),(-2.2,-26,11.8,5.3),(-1,-31.6,8.5,7.5)],
        'spire': [(0,-12.1,13.7,8.8),(1.2,-19.7,13.8,9.5),(-1,-26.8,11.1,8.8),(-1.4,-32.8,7.6,7.2)],
        'shrub': [(-6.6,-16.3,8.8,10.3),(6,-20,9.5,12),(-.7,-28.3,9.8,10.8)],
    }[species]
    bark = '#514332' if species!='spire' else '#495037'
    parts = [path('M-2.3 .2Q-.7-4-1.6-10.2L-2.6-19.8L.2-29.4L1.3-20Q.8-11 1-5.8L2.1-.1L.2-1.3Z',bark), bough((-.65,-1),(.4,-8),(-.8,-18),'#967b54',.65)]
    for index,(horizontal,vertical,wide,tall) in enumerate(clusters):
        elbow=(horizontal*.81, vertical*.42)
        parts.append(bough((-.35,-4.2-index),elbow,(horizontal,vertical),bark,1.35))
        parts.append(bough((horizontal*.55,vertical*.42),(horizontal*.84,vertical*.49),(horizontal+wide*.48,vertical*.85),bark,.82))
    if species=='cloud-pine':
        parts.append(path('M-3.0-.4Q-1.6-7.5-2.7-15.5Q-3.1-20.8-.2-33.8L1.4-32.6Q.1-21.4.4-14Q.7-5.3 2.3-.6L-.1-1.7Z','#55432d','#3b3625',.45))
    for horizontal,vertical,wide,tall in clusters:
        parts.append(foliage(rng,horizontal+rng.uniform(-.45,.45),vertical,wide,tall,palette))
    if species=='spire':
        for side in (-1,1):
            parts.append(bough((side*.7,-2.5),(side*3,-15),(side*1.65,-27.5),palette[1],2.1))
            for joint in range(5):
                level=-5-joint*4.4;parts.append(bough((side*1.8,level),(side*4,level-.8),(side*rng.uniform(4.5,7.2),level-3.4),palette[0],.90))
    return ''.join(parts)


def willow(rng, palette):
    parts = [path('M-2.1 0Q-1.2-7-2.9-16L-2.2-24L.2-31L.6-21Q.3-8 1.3-3L2.4-.2L.1-1Z','#725736')]
    for across,top,bottom in [(-9,-32,-5),(-2,-39,-9),(6,-34,-7),(10,-30,-5)]:
        parts.append(bough((-.6,-5),(across*.9,-12),(across,top),'#635234',1.31))
        parts.append(foliage(rng,across,top+8.9,6.3,9.2,palette))
        for index in range(21):
            turn = rng.uniform(-5.4,5.4); start=top+abs(turn)*.48
            fall = rng.uniform(bottom-6,bottom); swing=turn*rng.uniform(.72,1.28)
            parts.append(bough((across+.24*turn,start),(across+turn*1.16,start+5.2),(across+swing,fall),rng.choice(palette[1:4]),rng.uniform(.45,.87)))
            for step in range(1,8):
                along=step/8; horizontal=across+swing*(1-(1-along)**2); vertical=start+(fall-start)*along
                parts.append(bough((horizontal,vertical),(horizontal+.85,vertical+.6),(horizontal+.25,vertical+2.25),rng.choice(palette[1:]),.56))
    return ''.join(parts)


def bamboo(rng,habit):
    parts=[]
    if habit=='thicket':
        for index in range(15):
            across=(index/14-.5)*26+rng.uniform(-.8,.8)
            height=36.8-abs(across)*.77+rng.uniform(-5.3,2.1)
            base=(rng.uniform(-2.8,2.8),rng.uniform(-2,.1));pigment=rng.choice(('#50612c','#7e9538'))
            parts.append(bough(base,(across*.48,-height*.34),(across,-height),pigment,.57))
            for joint in range(2,8):
                level=joint/8;node=(across*level,-height*level);reach=rng.uniform(2.4,5)*(1 if (index+joint)%2 else -1)
                tip=(node[0]+reach,node[1]-rng.uniform(1.7,4));parts.append(bough(node,(tip[0],node[1]-.5),tip,pigment,.69))
                for blade in range(9):
                    horizontal=tip[0]+rng.uniform(-2.3,2.3);vertical=tip[1]+rng.uniform(-2,1.8);slant=rng.uniform(-2.8,2.8);length=rng.uniform(1.8,4.2)
                    parts.append(path('M'+point(horizontal,vertical)+'q'+point(slant*.2,-length*.86)+' '+point(slant,-length)+'q'+point(-slant*.06,length*.78)+' '+point(-slant,length)+'Z',rng.choice(('#354921','#567c22','#80a932','#aacb50'))))
        return ''.join(parts)
    for index,(across,height) in enumerate([(-13,26),(-10,16),(-9,33),(-7,23),(-3,38),(0,21),(2,29),(4,16),(6,36),(10,22),(12,26)]):
        foot=rng.uniform(-3.2,3.2)+across*.16
        def culm(level):return (foot+(across-foot)*level**1.4,-height*level)
        parts.append(bough(culm(0),((across+3*foot)/4,-height*.5),culm(1),'#667938',.71))
        for joint in range(4):
            level=.19+.23*joint+rng.uniform(-.03,.04);side=(-1 if (index+joint)%2 else 1)
            start=culm(level);reach=side*rng.uniform(3.1,6.2);tip=(start[0]+reach,start[1]-rng.uniform(1.7,3.5))
            parts.append(bough(start,(start[0]+reach*.48,start[1]-.7),tip,'#495f32',.66))
            for blade in range(5):
                along=.17+.20*blade;node=(start[0]+reach*along,start[1]+(tip[1]-start[1])*along)
                span=side*rng.uniform(2.1,4.8);rise=rng.uniform(1.1,3.4) if blade%2 else -rng.uniform(1.6,4.3)
                parts.append(path('M'+point(*node)+'q'+point(span*.68,rise*.23-2.1)+' '+point(span,rise)+'q'+point(-span*.65,-rise*.27+1.25)+' '+point(-span,-rise)+'Z',rng.choice(('#334e19','#52771b','#84a925','#9fc636','#c1dc66'))))
    return ''.join(parts)


def flower_spray(rng):
    parts=[]
    for index in range(8):
        across=(index/7-.5)*26+rng.uniform(-.8,.8)
        height=36.8-abs(across)*.77+rng.uniform(-5.3,2.1)
        base=(rng.uniform(-2.8,2.8),rng.uniform(-2,.1));tip=(across,-height)
        pigment=rng.choice(('#704340','#8b5a53'))
        parts.append(bough(base,(across*.48,-height*.34),tip,pigment,.81))
        for joint in range(2,8):
            along=joint/8;center=(across*along,-height*along)
            reach=rng.uniform(2.4,5)*(1 if (index+joint)%2 else -1)
            end=(center[0]+reach,center[1]-rng.uniform(1.7,4));parts.append(bough(center,(end[0],center[1]-.5),end,pigment,.69))
            parts.append(ellipse(end[0],end[1],rng.uniform(1.6,2.8),rng.uniform(1.4,2.4),'#e9b3a5'))
            for leaf in range(9):
                horizontal=end[0]+rng.uniform(-2.3,2.3);vertical=end[1]+rng.uniform(-2.0,1.8)
                parts.append(ellipse(horizontal,vertical,rng.uniform(.48,1.10),rng.uniform(.48,1.03),rng.choice(('#b77e73','#d99787','#e9b3a5','#f5cfc4'))))
    return ''.join(parts)


def clipped_pair_tree(rng, palette):
    parts=[path('M-2.5 0Q-.8-5.5-2.2-15L.4-21L1.3-7L2.0-.9L.1-1.8Z','#554933'),
           bough((-.5,-3.3),(-10,-8),(-11,-17),'#4a492b',1.25),
           bough((1,-3.0),(7,-9),(10,-19),'#594f32',1.0),
           foliage(rng,-.5,-21.5,15,12.5,palette),foliage(rng,-2.3,-29.3,9.3,10.0,palette)]
    parts.append(bough((5.4,-9),(9.2,-19),(6.8,-28.3),palette[0],1.22))
    parts.append(bough((-9.1,-13),(-12,-19.2),(-9.5,-23.4),palette[1],1.0))
    parts.append(bough((-8.6,-7.3),(-1.6,-6.8),(5.5,-8.5),palette[0],.89))
    return ''.join(parts)


BLOSSOM = {
    'pink': ('#593535','#8c5657','#ad666d','#e9aab0','#f7cbd0','#ffe9de'),
    'ivory': ('#514336','#816657','#ad9088','#decfc6','#f4e9e3','#fff7e8'),
    'apricot': ('#624334','#895444','#b97869','#e6b29e','#f5cebe','#ffe4d2'),
}


def blooming_bough(rng, tone):
    bark, twig, calyx, half, petal, light = BLOSSOM[tone]
    bend = rng.uniform(-1.6,1.6)
    parts = [path(f'M-2.6 .1Q-.4-3.1 {number(bend-.6)}-10.2l2.2-2.1Q1-5.3 1.65-.4L.15-1.3Z',bark)]
    limbs = []; blossoms = []; tips = []
    for tip_x,tip_y,fork_y in [(-12,-27,-7),(-8,-35,-10),(1,-37,-16),(8,-33,-12),(13,-26,-8)]:
        tip_x += rng.uniform(-1.4,1.4); tip_y += rng.uniform(-1.8,1.1)
        fork = (bend+rng.uniform(-1.1,1.1),fork_y); elbow = (tip_x*.85,tip_y+9)
        limbs.append(bough((.2,-1.7),(bend+.65,-6.8),fork,bark,1.35))
        limbs.append(bough(fork,elbow,(tip_x,tip_y),bark,rng.uniform(.91,1.6)))
        for joint in range(5):
            fraction = .14+joint*.18
            start = tuple((1-fraction)**2*origin+2*(1-fraction)*fraction*middle+fraction**2*end for origin,middle,end in zip(fork,elbow,(tip_x,tip_y)))
            for side in (-1,1):
                reach = rng.uniform(2.1,4.7)*side
                end = (start[0]+reach,start[1]-rng.uniform(1.7,4.8))
                limbs.append(bough(start,(start[0]+reach*.75,start[1]-.72),end,twig,rng.uniform(.6,.95)))
                if (joint+side)%3==0:
                    tips.append(bough((end[0]-.6*side,end[1]+1.55),(end[0]+.47*side,end[1]+.92),end,bark,rng.uniform(.84,1.3)))
                    tips.append(ellipse(end[0]+.72*side,end[1]-.26,.63,.78,calyx))
                for cluster in range(rng.choice((2,3,4))):
                    across=end[0]+rng.uniform(-1.6,1.6); down=end[1]+rng.uniform(-1.8,1.4)
                    span=rng.uniform(.9,2.1)
                    blossoms.append(ellipse(across,down,span*1.12,span*.92,rng.choice((half,half,petal))))
                    blossoms.append(bough((across-span*.72,down+.48),(across,down+.65),(across-.20,down-.36),rng.choice((bark,calyx,calyx)),rng.uniform(.55,1.1)))
                    blossoms.append(ellipse(across+span*.4,down-span*.54,span*.61,span*.52,rng.choice((petal,light))))
    return ''.join(parts+limbs+blossoms+tips)


def blossom_spurs(rng, tone, leaders,leader_range=None):
    bark,twig,calyx,half,petal,light=BLOSSOM[tone]
    parts=[]
    for leader,(tip_x,tip_y) in enumerate(leaders):
        start=len(parts)
        parts.append('<g data-bough="flower-spurs">')
        elbow=(tip_x*.25+rng.uniform(-1.3,1.3),tip_y*.46)
        parts.append(bough((0,0),elbow,(tip_x,tip_y),bark,rng.uniform(1.05,1.65)))
        for joint in range(7):
            fraction=.16+.126*joint
            fork=tuple(2*(1-fraction)*fraction*bend+fraction**2*end for bend,end in zip(elbow,(tip_x,tip_y)))
            for side in (-1,1):
                reach=side*rng.uniform(2.5,5.1)*(1-.68*fraction**3)
                spur=(fork[0]+reach,fork[1]-rng.uniform(1.3,3.8))
                parts.append(bough(fork,(fork[0]+reach*.57,fork[1]+.3),spur,twig,rng.uniform(.65,1.04)))
                for bud in range(3):
                    across=spur[0]+rng.uniform(-1.6,1.6);down=spur[1]+rng.uniform(-1.4,1.8);wide=rng.uniform(1.3,2.4)
                    parts.append(ellipse(across,down,wide,wide*rng.uniform(.72,1.1),rng.choice((half,petal,petal))))
                    parts.append(ellipse(across-.32*wide,down-.30*wide,.57*wide,.53*wide,rng.choice((light,petal))))
                parts.append(bough((spur[0]-.72*side,spur[1]+1.0),(spur[0]+.4*side,spur[1]+.62),spur,rng.choice((bark,twig,calyx)),rng.uniform(.63,1.25)))
        parts.append('</g>')
        if leader_range is not None and leader not in leader_range:del parts[start:]
    return ''.join(parts)


def orchard_oval(rng, palette):
    parts=[path('M-3.3-.2Q-1.1-3.8-1.8-12.4L.4-22L2.3-9.4L1.7-3L3.1-.6L.5-1.6Z','#4a4127'),
           foliage(rng,0,-22.5,13.4,15.1,palette)]
    for across,down in [(-10,-19),(5,-24),(1,-29)]:
        parts.append(bough((-.5,-4),(across*.9,down*.55),(across,down),palette[0],rng.uniform(1.2,2.1)))
    for across,down in [(-6,-2.4),(4,.3),(9,-1.5)]:
        parts.append(ellipse(across,down,rng.uniform(.95,1.9),rng.uniform(.55,.95),'#665e3b'))
    return ''.join(parts)


def fern_bank(rng, palette):
    parts=[]
    for index in range(11):
        across=(index-5)*2.9+rng.uniform(-.7,.7); foot=(across*.69,-rng.uniform(1,6))
        high=-rng.uniform(23,36)+abs(across)*.45;end=(across,high)
        parts.append(bough(foot,(across*.6,high+3),end,palette[0],1.2))
        for joint in range(4):
            down=high+joint*4.2; center=across*(1-joint*.045)
            for side in (-1,1):
                outer=center+side*rng.uniform(1.6,4.3);drop=rng.uniform(1.2,3.8)
                parts.append(path('M'+point(center,down)+'Q'+point(outer,down-2.6)+' '+point(outer,down+drop)+'Q'+point(center,down+2.7)+' '+point(center,down)+'Z',rng.choice(palette[:4])))
    return ''.join(parts)


def pear_crown(rng,palette):
    palette=('#263d1e','#628653','#83b574','#a7cd91','#bddba6') if palette==PAINT['leaf'] else ('#3a481d','#96a745','#b5d46d','#c9df8b','#d8e6a3')
    parts=[bough((-3.9,.55),(3.4,1.4),(10.8,.72),'#364124',2.45),path('M-3.2 1.4Q-1.4-5.8-2.0-13.6L1.7-20L2.5-6.8L4.1.9Z','#33391d')]
    rim=[(-12,-11),(-15,-15),(-14,-22),(-11,-28),(-6,-34),(0,-38.5),(5,-38),(8,-33),(10,-27),(13,-21),(14,-16),(11,-11),(4,-9),(-4,-9)]
    rim=[(across*.94+1.6+rng.uniform(-.8,.8),down*.94+1.35+rng.uniform(-.6,.6)) for across,down in rim]
    parts.append(path(curve(rim),palette[2]))
    parts.append(path('M-10-12Q-12-17-9-23Q-6-29-2-30Q-5-24-4-19Q-6-16-3-9Z',palette[1],extra='opacity=".46"'))
    for index in (0,2,4,6,9,11,13):
        near,far=rim[index],rim[(index+1)%len(rim)];fraction=rng.uniform(.46,.93)
        end=tuple(start+(finish-start)*fraction for start,finish in zip(near,far))
        parts.append(bough(near,((near[0]+end[0])*.5+.35,(near[1]+end[1])*.5),end,palette[0],rng.uniform(2.45,3.7)))
    for index in range(35):
        down=rng.uniform(-31,-11);wide=min(10,(down+35)*.66);across=1.5+rng.uniform(-wide,wide)
        parts.append(ellipse(across,down,rng.uniform(.56,1.7),rng.uniform(.55,1.25),rng.choice(palette[1:]),'opacity=".81"'))
    parts.append(bough((.8,-7.5),(3.3,-11),(5.4,-13.7),palette[1],1.3))
    return ''.join(parts)


def tiered_pine(rng,palette):
    parts=[path('M-3.5-.2Q-4.9-3.8-3.2-9.2L-1.1-20.4L2.8-33.8L4.7-34Q.6-22.8 1.8-17.5L.1-7.5L1.7-1.1L-.5-.1Z','#433e28','#393c28',.65),
           bough((-2,-7),(-1,-18),(9,-19.5),'#4b432e',1.8),bough((1,-14),(-5.3,-17),(-12,-14.5),'#4b432e',1.5),
           bough((-.5,-3),(-1.9,-8),(.2,-13),'#8f7952',.96),ellipse(-3,.5,6.2,.91,'#596341')]
    for across,down,wide,tall in [(-6.3,-15.5,7.4,3.0),(8.9,-18.5,7.5,4.0)]:
        parts.append(foliage(rng,across,down,wide,tall,palette))
        parts.append(bough((across-wide*.78,down+tall*.64),(across-wide*.4,down+tall*.82),(across+.8,down+tall*.47),palette[0],1.56))
    hat=[(-12.2,-23.9),(-10,-28.3),(-7.1,-31.2),(-2.2,-35.8),(2.2,-37.4),(7.5,-35.7),(12.3,-32.1),(15,-29.4),(15.1,-26.7),(9.5,-25.9),(5.2,-26.2),(.1,-24.4),(-6.7,-23.4)]
    parts.append(path(curve(hat),'#76a76a'))
    for index in (0,2,4,6,8,10,12):
        start,end=hat[index],hat[(index+1)%len(hat)];parts.append(bough(start,((start[0]+end[0])*.5,(start[1]+end[1])*.5-.3),end,'#2d4327',rng.uniform(1.24,1.85)))
    for index in range(42):
        across=rng.uniform(-9.8,13.3);top=-37.1+abs(across-2.4)*.68;bottom=-24.65-max(0,across)*.16
        down=rng.uniform(top,bottom);parts.append(ellipse(across,down,rng.uniform(.49,1.5),rng.uniform(.48,1.15),rng.choice(('#609256','#95bd7d','#80ad70','#4e7b46'))))
    return ''.join(parts)


def low_pollard(rng,palette):
    parts=[path('M-3.4 .3Q-2.6-4-1.6-10.5L-3.9-17.4L-1.1-20.4L.9-12.6L6.5-20.7L8.7-18.9L2.3-9.3L1.1-2.6L3.2-.8Z','#4a4228','#343722',.68),
           bough((-5.0,.9),(-.6,.15),(5.6,1.3),'#566041',1.45),
           bough((-.65,-7.2),(-3.8,-10.9),(-9,-16.3),'#4d4929',1.5)]
    rim=[(-15.4,-20.4),(-14.6,-27.9),(-11.1,-33),(-5.4,-37.4),(2.6,-39.2),(9.3,-36.6),(14,-31.2),(15.6,-23.4),(13.7,-18.7),(7.7,-16.4),(.6,-17),(-6.1,-15),(-12.2,-16.5)]
    rim=[(across+rng.uniform(-.45,.45),down+rng.uniform(-.65,.65)) for across,down in rim]
    parts.append(path(curve(rim),palette[2]))
    parts.append(path('M-14.4-20.7Q-8-22.8-.6-19.6Q7.3-23.4 14.5-22.5L13-18.4Q8-15.5 2-17Q-5-13.6-11.4-16.7Z',palette[1]))
    for index in (0,2,4,6,8,10,12):
        start,end=rim[index],rim[(index+1)%len(rim)];point_on_edge=tuple(near+(far-near)*.62 for near,far in zip(start,end))
        parts.append(bough(start,((start[0]+point_on_edge[0])*.5,(start[1]+point_on_edge[1])*.5-.3),point_on_edge,palette[0],rng.uniform(.83,1.75)))
    for index in range(63):
        across=rng.uniform(-13.1,13.2);height=(1-(across/15.1)**2)**.5;down=-26.9+rng.uniform(-9.7,7.8)*height
        parts.append(ellipse(across,down,rng.uniform(.62,1.64),rng.uniform(.54,1.58),rng.choice(palette[1:4] if down>-24.5 else palette[1:]),'opacity=".80"'))
    for across,down in [(-9.9,-17.4),(2.6,-17.5),(9.2,-19.3)]:
        parts.append(bough((.7,-12.1),(.1+across*.42,-15.1),(across,down),palette[0],1.27))
    return ''.join(parts)


def open_spire(rng, tone):
    shades = {'leaf':('#243820','#528650','#81b778','#a7ce8c','#c7deb1'), 'sage':PAINT['sage']}.get(tone,('#303a19','#708e43','#b5cd79','#c6dc92','#dae8b2'))
    rim=[(-3.1,-.8),(-10.2,-4.5),(-13.6,-12.1),(-13.2,-20.4),(-10.3,-29.3),(-7.3,-35.3),(-1.7,-39.4),(3.8,-37.4),(9.1,-31),(12.3,-23),(13.5,-13.6),(11.8,-6.8),(6.9,-2.3)]
    rim=[(across*1.10+rng.uniform(-.6,.6),down+rng.uniform(-.55,.55)) for across,down in rim]
    parts=[path(curve(rim),shades[2]),path('M-3.1-36.5Q-9.2-22-9-13Q-7-8-7.5-4.9Q-14-10.7-12-19Q-10.4-32.5-3.1-36.5Z',shades[3]),
           path('M7.1-29.5Q13.7-20.4 12.6-12.1Q12.7-5.8 7.4-3.2L3.7-2Q8-11.9 6.8-17.5Q9.1-22.1 7.1-29.5Z',shades[1]),
           path('M-1.7 .7L-3.1-5.9Q-2.1-13.9-.7-20.6L.7-28.6L2.7-21.4L1.7-15.5Q1.5-6.2 3.2-.7Z',shades[0])]
    for level,side,reach in [(-3,-1,8.9),(-9,1,7.8),(-13,-1,6.6),(-19,1,4.7)]:
        parts.append(bough((.1,level),(side*reach*.62,level-1.6),(side*reach,level-7.2),shades[0],rng.uniform(1.0,1.8)))
    for index in (0,2,4,5,7,9,10,12):
        start,end=rim[index],rim[(index+1)%len(rim)];tip=tuple(first+(last-first)*rng.uniform(.53,.87) for first,last in zip(start,end));mid=((start[0]+tip[0])/2,(start[1]+tip[1])/2-.3)
        parts.append(bough(start,mid,tip,shades[0],rng.uniform(1.7,2.7)))
    for index in range(32):
        level=rng.uniform(-36.4,-3.1);radius=11.2*math.sin(math.pi*(-level/40))**.45;across=rng.uniform(-radius,radius)
        if abs(across)<1.9 and level>-24:continue
        parts.append(ellipse(across,level,rng.uniform(.65,1.7),rng.uniform(.67,1.95),rng.choice(shades[1:])))
    return ''.join(parts)


def bank_dome(rng):
    rim=[(-15,-14),(-13,-21),(-8.1,-28.3),(-4.4,-32.6),(-1.7,-38.5),(1.6,-37.4),(5.4,-32.8),(9.3,-29.3),(13.7,-19.5),(16,-14.5),(13,-10.9),(5.9,-8.7),(-1,-9),(-7.3,-7.2),(-12.2,-9.6)]
    parts=[path('M-3.3-.1L-2.4-15.2L1.3-20.7L1-5.6L2.8-.5Z','#47462c'),path(curve(rim),'#76a568'),
           path('M-14.4-14Q-9.1-13.3-4.1-16.5Q1-12.4 7.4-14L15-16L13-10.9Q4-8.6-.4-9.2Q-8-5.4-12.1-9.6Z','#568746')]
    for index in (0,3,7,9,10,12,13):
        start,end=rim[index],rim[(index+1)%len(rim)];parts.append(bough(start,((start[0]+end[0])*.5,(start[1]+end[1])*.5-.3),end,'#31472d',1.72))
    for index in range(34):
        level=rng.uniform(-34,-12.1);radius=12.4*(level+40)/28;across=rng.uniform(-radius,radius)
        parts.append(ellipse(across,level,rng.uniform(.65,1.8),rng.uniform(.83,2.1),rng.choice(('#729d63','#8ab67b','#9cc284','#699858'))))
    return ''.join(parts)


def low_round(rng,key):
    rim=[(-15.3,-9.6),(-16.1,-15),(-14.8,-22.9),(-11.5,-29.4),(-6.3,-35.3),(-1.7,-37.4),(4.5,-38.1),(8.2,-34.9),(12.8,-31.7),(15.1,-24.3),(14.6,-17.2),(12,-11.2),(8.6,-6.8),(2.6,-4.9),(-4.2,-4.5),(-10.2,-5.7)]
    wood=path('M-3.1 .2L-2.0-8.5L-.1-14.4L2.0-7.5L1.8-1.6L3.2-.3Z','#43422c')
    return wood+leaf_pad(rng,rim,('#264320','#508a46','#66aa5f','#76b970','#97ca82'),key+'-round',.55)


def planting(model,stem_index=None,leader_range=None):
    parts = [f'<g data-planting="{model["id"]}" transform="translate({model["x"]} {model["y"]})">']
    for index,stem in sorted(enumerate(model['stems']), key=lambda pair:pair[1]['root'][1]):
        if stem_index is not None and index!=stem_index:continue
        species=stem['species']; spread,height=stem['size']; horizontal,vertical=stem['root']
        rng=random.Random(f'{model["id"]}-stem-{index}');palette=PAINT[stem['paint']]
        tilt=f' skewX({number(-math.degrees(math.atan(stem["lean"]/40)))})' if stem.get('lean') else ''
        factor=-1 if stem.get('mirror') else 1
        parts.append(f'<g data-species="{species}" transform="translate({point(horizontal,vertical)}) scale({number(factor*spread/32)} {number(height/40)}){tilt}">')
        if leader_range is None or 0 in leader_range:parts.append(ellipse(.55,-.15,3.9,.95,'#736c4b','opacity=".31"'))
        key=f'{model["id"]}-{index}'
        if stem.get('habit')=='spreading-tiers':parts.append(spreading_crown(rng,stem,key))
        elif species=='tiered-pine' and stem.get('habit')=='trained-shelves':parts.append(trained_pine(rng,key))
        elif species=='umbrella' and stem.get('habit')=='forked-dome':parts.append(forked_dome(rng,stem['paint'],key))
        elif species=='willow' and 'bearingCrown' in stem:
            from .willow_boughs import bearing_crown
            parts.append(bearing_crown(stem['bearingCrown'],palette))
        elif species=='willow' and stem.get('habit')=='pendant-curtains':parts.append(pendant_willow(rng,key))
        elif species in ('bamboo','willow') and stem.get('habit')=='leafy-sprays':parts.append(leafy_sprays(rng,stem['sprays'],species=='willow'))
        elif species=='blooming-bough' and 'flowerFrame' in stem:
            from .blossom_clusters import blossom_clusters
            parts.append(blossom_clusters(rng,stem))
        elif species=='blooming-bough' and 'leaders' in stem:parts.append(blossom_spurs(rng,stem['bloom'],stem['leaders'],leader_range))
        elif species=='blooming-bough':parts.append(blooming_bough(rng,stem['bloom']))
        elif species=='orchard-oval':parts.append(orchard_oval(rng,palette))
        elif species in ('clipped-oval','pear-crown') and stem.get('habit')=='upright-broadleaf':
            from .upright_broadleaf import upright_broadleaf
            parts.append(upright_broadleaf(rng,palette))
        elif species=='pear-crown':parts.append(pear_crown(rng,palette))
        elif species=='tiered-pine':parts.append(tiered_pine(rng,palette))
        elif species=='low-pollard':parts.append(low_pollard(rng,palette))
        elif species=='spire' and stem.get('habit')=='bank-needle-forks':parts.append(bank_evergreen(rng,palette))
        elif species=='spire' and stem.get('habit')=='open-spire':parts.append(open_spire(rng,stem['paint']))
        elif species=='shrub' and stem.get('habit')=='bank-dome':parts.append(bank_dome(rng))
        elif species=='shrub' and stem.get('habit')=='low-round':parts.append(low_round(rng,key))
        elif species=='fern-bank' and 'fernFan' in stem:
            from .east_fern_beds import spreading_fern
            parts.append(spreading_fern(stem['fernFan'],palette))
        elif species=='fern-bank':parts.append(fern_bank(rng,palette))
        elif species=='willow':parts.append(willow(rng,palette))
        elif species=='clipped-oval':parts.append(clipped_pair_tree(rng,palette))
        elif species=='bamboo':parts.append(bamboo(rng,stem.get('habit','thicket')))
        elif species=='flower-spray':parts.append(flower_spray(rng))
        else:parts.append(woody(rng,species,palette))
        parts.append('</g>')
    return ''.join(parts)+'</g>'


def extent(stems):
    boxes=[]
    for stem in stems:
        horizontal,vertical=stem['root'];spread,height=stem['size']
        lean=spread*stem.get('lean',0)/32
        boxes.append([horizontal-spread*.70-1+min(0,lean), vertical-height*1.13-1, horizontal+spread*.70+1+max(0,lean), vertical+height*.05+1])
    return [min(box[0] for box in boxes),min(box[1] for box in boxes),max(box[2] for box in boxes),max(box[3] for box in boxes)]
