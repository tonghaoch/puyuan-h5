"""Native landscape materials and detailed botanical/bridge drawing primitives."""
import math, random

def number(x):return f'{x:.2f}'.rstrip('0').rstrip('.')
def path(d,fill='none',stroke='none',width=.5,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'
def poly(points,fill,stroke='none',width=.4):
    return path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in points)+'Z',fill,stroke,width)
def ellipse(x,y,rx,ry,fill,extra=''):
    return f'<ellipse cx="{number(x)}" cy="{number(y)}" rx="{number(rx)}" ry="{number(ry)}" fill="{fill}" {extra}/>'
def rounded_ring(points):
    corners=[]
    for i,b in enumerate(points):
        a=points[i-1];c=points[(i+1)%len(points)]
        before=math.dist(a,b);after=math.dist(b,c)
        if min(before,after)<.01:continue
        radius=min(1.35,before*.24,after*.24)
        entry=(b[0]+(a[0]-b[0])*radius/before,b[1]+(a[1]-b[1])*radius/before)
        leave=(b[0]+(c[0]-b[0])*radius/after,b[1]+(c[1]-b[1])*radius/after)
        corners.append((entry,b,leave))
    if not corners:return ''
    p=[f'M{number(corners[-1][2][0])},{number(corners[-1][2][1])}']
    for entry,b,leave in corners:
        p.append(f'L{number(entry[0])},{number(entry[1])}Q{number(b[0])},{number(b[1])} {number(leave[0])},{number(leave[1])}')
    return ''.join(p)+'Z'
def shape(item):return rounded_ring(item['points'])+''.join(rounded_ring(h) for h in item.get('holes',[]))

def quay_edge(ring,quay):
    start=ring.index(quay['from']);end=ring.index(quay['to'])
    return (ring+ring)[start:(end if end>=start else end+len(ring))+1]


def quay_face(edge,height,stone):
    top=[(x,y-height) for x,y in edge];parts=[poly(edge+top[::-1],stone)]
    for (x,y),(xx,yy) in zip(edge,edge[1:]):
        count=max(1,round(math.hypot(xx-x,yy-y)/4.3))
        for index in range(count):
            at=(index+.35)/count;parts.append(path(f'M{number(x+(xx-x)*at)},{number(y+(yy-y)*at-.2)}v-{number(height-.4)}',stroke='#a09982',width=.28))
    parts.append(path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in top),stroke='#b9b29a',width=.65))
    return ''.join(parts)


def island_quay(region,quay):
    ring=region['holes'][quay['hole']];key=quay['id'];outline=rounded_ring(ring)
    return f'<defs><clipPath id="{key}">'+path(outline,'white')+'</clipPath></defs>'+f'<g clip-path="url(#{key})">'+path(outline,'url(#island-stone)')+quay_face(quay_edge(ring,quay),quay['height'],'#766f5f')+'</g>'

MATERIALS='''<defs>
<pattern id="silver-setts" width="19" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-3)"><rect width="19" height="12" fill="#e2e1dd"/><path d="M0 0h8v5H0Z M12 6h7v6h-7Z" fill="#e6e5e0"/><path d="M0 5.7h7.2m1.3 0H19M8 .2v4.4m4 2.6v4.3M2 11.6h8" fill="none" stroke="#cfcfca" stroke-width=".33"/></pattern>
<pattern id="blue-grey-flags" width="27" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(-4)"><rect width="27" height="18" fill="#9ea2ae"/><path d="M0 0h14v8H0ZM17 10h10v8H17Z" fill="#a4a6b0"/><path d="M5 10h8v6H5ZM20 2h5v4h-5Z" fill="#9ba0ab"/><path d="M0 8.5h11.3m.6 0h7M14 0v5.6M5 11v4.3m3.3 2.4h7" fill="none" stroke="#b2b3bb" stroke-width=".28"/></pattern>
<pattern id="island-stone" width="13" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-53)"><rect width="13" height="7" fill="#e6e1d2"/><path d="M0 .2h13M0 3.6h13M3 .2v3.4m6 0v3.4" fill="none" stroke="#c6c1af" stroke-width=".26"/></pattern>
<linearGradient id="water" x1="0" y1="0" x2=".4" y2="1"><stop stop-color="#91bfb4"/><stop offset=".45" stop-color="#73a89e"/><stop offset="1" stop-color="#5e968d"/></linearGradient>
<pattern id="ripples" width="65" height="32" patternUnits="userSpaceOnUse"><path d="M4 8q9-2 17 0m18 12q10-2 19 0M18 29q6-1.6 12 0" fill="none" stroke="#d5e5ce" stroke-width=".45" opacity=".55"/><path d="M0 16h8m23-12h13" stroke="#527f75" stroke-width=".35" opacity=".25"/></pattern>
<pattern id="pavers" width="16" height="10" patternUnits="userSpaceOnUse"><rect width="16" height="10" fill="#d5d4bd"/><path d="M0 0h16M0 5h16M8 0v5M3 5v5M15 5v5" stroke="#aeb49d" stroke-width=".35"/><path d="M.5 1h7m1 5h6" stroke="#efead3" stroke-width=".5" opacity=".8"/><path d="M9 1h6v3H9ZM4 6h9v3H4Z" fill="#c9cdb5" opacity=".45"/></pattern>
<pattern id="sand" width="23" height="19" patternUnits="userSpaceOnUse"><rect width="23" height="19" fill="#dad6b9"/><path d="M1 3h3m8 7h2M4 15h1m15-9h2" stroke="#a7b091" stroke-width=".35" opacity=".5"/><circle cx="17" cy="16" r=".45" fill="#f0e5c4"/></pattern>
<pattern id="quay" width="12" height="6" patternUnits="userSpaceOnUse"><rect width="12" height="6" fill="#b4b99e"/><path d="M0 0h12M0 3h12M5 0v3M10 3v3" stroke="#7f927a" stroke-width=".35"/><path d="M0 1h4m2 3h3" stroke="#dee0c1" stroke-width=".5"/></pattern>
</defs>'''

def tree(model):
    rng=random.Random(model['id']);kind=model['kind'];s=model['scale']
    if kind in ['pine','cypress','bamboo']:return evergreen(model)
    if kind=='blossom' and model.get('form')=='open-flowering':return flowering_tree(model,rng)
    palettes={'willow':['#456b4c','#5a8055','#729460','#8ca872','#b0be87'],
              'blossom':['#9c6971','#bd8590','#d3a2aa','#e5b8b8','#f1d0c6'],
              'ginkgo':['#9a8b48','#b3a451','#c6b866','#d8cc83','#e5dd9f']}
    colors=palettes[kind]
    if kind=='willow' and model.get('foliage')=='spring':colors=['#729044','#82a346','#93b64d','#a9c563','#c2d97c']
    p=[f'<g transform="translate({model["x"]} {model["y"]}) scale({s})">',ellipse(2,1.5,10,3.8,'#385b3d','opacity=".16"'),
       path('M0 0Q-1-8 0-19M0-8Q-4-16-9-20M0-12Q4-20 10-23',stroke='#6c6550',width=1.6),
       path('M.5-1Q.1-9 1-17',stroke='#b8aa78',width=.45)]
    # Irregular lobed clusters, twig shadows, and individually positioned leaves/petals.
    clusters=[(-6,-15,7),(6,-16,7.8),(-7,-23,6.8),(3,-25,8),(10,-23,5.5),(-1,-30,6)]
    for i,(cx,cy,r) in enumerate(clusters):
        points=[]
        for j in range(18):
            a=j*math.tau/18;rad=r*rng.uniform(.81,1.14)
            points.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad*.82))
        p.append(poly(points,colors[min(3,i%3+1)],colors[0],.22))
        p.append(path(f'M{cx-r*.5} {cy+r*.25}q{r*.45} {-r*.55} {r*.9} {-r*.1}',stroke=colors[0],width=.4,extra='opacity=".35"'))
        for j in range(24):
            a=rng.random()*math.tau;rad=math.sqrt(rng.random())*r*.9
            x=cx+math.cos(a)*rad;y=cy+math.sin(a)*rad*.78
            if kind=='blossom':
                p.append(ellipse(x,y,rng.uniform(.3,.7),rng.uniform(.24,.5),rng.choice(colors[2:])))
                if j%5==0:p.append(ellipse(x+.2,y-.1,.18,.18,'#f2dfb6'))
            else:
                p.append(path(f'M{number(x)} {number(y)}q-1-1.7 1.5-1.7q.5 1.2-1.5 1.7Z',rng.choice(colors[1:]),width=.2))
    if kind=='willow':
        for i in range(7):
            x=-9+i*3;y=-14-abs(i-3)*1.3
            p.append(path(f'M{x} {y}q2 5 .4 12',stroke='#668657',width=.4))
            for j in range(4):p.append(path(f'M{x+1} {y+j*2.4}q2-.3 1 1.7',stroke='#99af74',width=.65))
    return ''.join(p)+'</g>'

def flowering_tree(model,rng):
    parts=[f'<g transform="translate({model["x"]} {model["y"]}) scale({model["scale"]})">',ellipse(1.3,.7,6.6,2.1,'#667453','opacity=".16"'),path('M0 0Q-1-8 .2-15L1-27',stroke='#735749',width=1.18)]
    for level in range(7):
        xx=(-1 if level%2 else 1)*rng.uniform(1,5.1);yy=-7.6-level*2.85
        parts.append(ellipse(xx,yy,rng.uniform(2.4,4.1),rng.uniform(2.6,4.5),'#d8aaa4','opacity=".79"'))
    for level in range(13):
        side=1 if level%2 else -1;root=-6-level*1.14
        span=side*(11.7-level*.46)*rng.uniform(.68,1.09);height=root-rng.uniform(6.6,11.1)
        parts.append(path(f'M0 {number(root)}Q{number(span*.42)} {number(root-.9)} {number(span)} {number(height)}',stroke='#77594c',width=.65))
        for twig in range(4):
            fraction=.32+twig*.20;xx=span*fraction;yy=root+(height-root)*fraction*fraction
            end_x=xx+side*rng.uniform(.8,2.9);end_y=yy-rng.uniform(2.7,5.6)
            parts.append(path(f'M{number(xx)} {number(yy)}L{number(end_x)} {number(end_y)}',stroke='#8d6958',width=.37))
            for petal in range(10):
                angle=rng.random()*math.tau;radius=rng.random()**.57*2.9
                tone=rng.choice(['#deb0aa','#eed0c3','#e7b5b0','#c78282','#efd4ca','#714e49','#a96763'])
                parts.append(ellipse(end_x+math.cos(angle)*radius,end_y+math.sin(angle)*radius*.84,rng.uniform(.56,1.14),rng.uniform(.53,.98),tone))
        for bud in range(7):
            fraction=rng.uniform(.18,.95);xx=span*fraction;yy=root+(height-root)*fraction*fraction
            parts.append(ellipse(xx+rng.uniform(-1.6,1.7),yy+rng.uniform(-1.65,1.0),.78,.68,rng.choice(['#cd8784','#eac3b6','#c48b84'])))
    return ''.join(parts)+'</g>'


def evergreen(model):
    rng=random.Random(model['id']);kind=model['kind'];s=model['scale']
    p=[f'<g transform="translate({model["x"]} {model["y"]}) scale({s})">',ellipse(1.5,1.5,9,3,'#385d41','opacity=".15"')]
    if kind=='pine':
        p.append(path('M0 0Q-3-7 0-17T1-31M0-12-10-19M0-19 10-26',stroke='#75654b',width=1.7))
        p.append(path('M.5-1Q-1-8 1-15',stroke='#b3a373',width=.4))
        for cx,cy,rx in [(-9,-17,9),(8,-22,10),(-5,-27,9),(3,-33,7)]:
            p.append(path(f'M{cx-rx} {cy}q1-4 5-4q4-5 8-1q6-1 {rx*2-13} 5q-7 3-13 1Z','#527b54','#3e6248',.25))
            for i in range(19):
                xx=cx+rng.uniform(-rx*.8,rx*.8);yy=cy+rng.uniform(-3.2,.7)
                p.append(path(f'M{number(xx)} {number(yy)}l-1.6-1.1m1.6 1.1 .2-1.8m-.2 1.8 1.7-.8',stroke=rng.choice(['#80a16c','#9ab17b','#6f925e']),width=.24))
    elif kind=='cypress':
        tender=model.get('foliage')=='spring'
        p.append(path('M0 0V-29',stroke='#7e7252',width=1.2))
        if tender:
            p.append(path('M-.7-36Q-5-36-5.3-30Q-9-29-7.5-24Q-11-18-8.3-15Q-10-7-3-6Q-.4-2 3.5-6Q11-6 8.4-14Q10-19 6.8-23Q8-28 4.1-29Q4-35-.7-36Z','#91b266','#556e43',.5))
            p.append(path('M-1.7-34Q-6-32-3.8-28Q-7-26-6.2-20Q-9-14-5.2-10Q-4-7-1.4-7Q2-9 .7-14Q5-20 1.7-24Q4-30-1.7-34Z','#afc975'))
            for index in range(72):
                yy=rng.uniform(-33,-7.3);span=2+5.9*math.sin(math.pi*(yy+36)/34);xx=rng.uniform(-span,span)
                p.append(ellipse(xx,yy,rng.uniform(.44,1.0),rng.uniform(.55,1.2),rng.choice(['#5a7544','#b9ce7a','#7f9f56','#85a85c','#78994e','#a6c76d'])))
        else:
            p.append(path('M0-37C-2-29-6-25-5-21C-10-13-7-7 0-6C7-7 10-13 5-21C6-25 2-29 0-37Z','#4e7754','#3e654a',.3))
            for i in range(60):
                yy=rng.uniform(-34,-8);ww=min(5,(yy+37)*.38);xx=rng.uniform(-ww,ww)
                p.append(path(f'M{number(xx)} {number(yy)}q1-2 2-1.3',stroke=rng.choice(['#7b9b69','#94ab77','#65895a']),width=.38))
    else:
        for i in range(7):
            xx=-5+i*1.65;top=-rng.uniform(25,38)
            p.append(path(f'M{xx} 0Q{xx-2} -17 {xx+1} {top}',stroke='#6b8252',width=.65))
            for j in range(4):
                yy=top+j*4.5
                p.append(path(f'M{xx} {yy}l-5-2m5 2 5-3',stroke='#778c58',width=.35))
                for side in [-1,1]:
                    bx=xx+side*3;by=yy-2
                    for k in range(3):
                        p.append(path(f'M{bx} {by+k}q{side*3} -3 {side*4} -.5q{-side} 2 {-side*4} .5Z',rng.choice(['#698852','#86a064','#a6b57d'])))
    return ''.join(p)+'</g>'

def bridge(model):
    length=model['length'];w=model['width'];half=length/2
    if model.get('form')=='humpback-footbridge':
        def rail(side):return [(half*pos,w*side-3.1*(1-pos*pos)) for pos in [index/8 for index in range(-8,9)]]
        far=rail(-.44);near=rail(.48);parts=[poly(far+near[::-1],'#c6b8a4','#685952',.5),poly(near+[(x,y+1.3) for x,y in reversed(near)],'#7b6e61','#5b534d',.42)]
        for index,(left,right) in enumerate(zip(far,near)):
            if index%2:parts.append(poly([left,(left[0]+.38,left[1]),(right[0]+.38,right[1]),right],'#938a7e'))
        for edge in [far,near]:
            for x,y in edge[::4]:parts.append(path(f'M{number(x)} {number(y)}v-1.6',stroke='#48413d',width=.85))
            parts.append(path('M'+'L'.join(f'{number(x)},{number(y-1.6)}' for x,y in edge),stroke='#514842',width=.7))
        return f'<g id="{model["id"]}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">'+''.join(parts)+'</g>'
    if model.get('form')=='masonry-parapet':
        parts=[]
        def paving(along,across):return (half*along,w*across-1.6*(1-along*along))
        def edge(across):return [paving(-1+step/8,across) for step in range(17)]
        for side in (-.77,.73):
            abut=paving(side,.48);parts.append(poly([(abut[0]-1.25,abut[1]),(abut[0]+1.25,abut[1]),(abut[0]+.9,abut[1]+3.0),(abut[0]-.85,abut[1]+3.3)],'#797770','#514f49',.5))
        near=edge(.50);parts.append(poly(near+[(x,y+1.6) for x,y in reversed(near)],'#635f59','#4d4a47',.3))
        parts.append(poly(edge(-.58)+near[::-1],'#d2ccc1','#817b72',.43))
        for across in (-.59,.48):
            line=edge(across);upper=[(x,y-2.7) for x,y in line]
            for index in range(6):
                post=paving(-.96+index*.38,across);parts.append(path(f'M{number(post[0])},{number(post[1])}v-3',stroke='#6c655c',width=1.02))
            parts.append(path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in upper),stroke='#4f4e4b',width=1.0))
            parts.append(path('M'+'L'.join(f'{number(x)},{number(y-.53)}' for x,y in upper),stroke='#c6c3bc',width=.42))
        return f'<g id="{model["id"]}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">'+''.join(parts)+'</g>'
    if model.get('form')=='stone-slab':
        parts=[poly([(-half,-w*.5),(half,-w*.5),(half,w*.5+1),(-half,w*.5+1)],'#767971','#5a5e57',.4),poly([(-half,-w*.5),(half,-w*.5),(half,w*.5),(-half,w*.5)],'#cecac3','#97948d',.38)]
        for index in range(1,round(length/1.65)):
            across=-half+index*1.65;parts.append(path(f'M{number(across)} {-w*.48}l.32 {w*.94}',stroke='#999994',width=.35))
        for side in (-1,1):
            edge=side*w*.43;parts.append(path(f'M{-half} {edge}q{half} -2.1 {length} 0',stroke='#a7a5a0',width=.72))
            for fraction in (.06,.35,.64,.94):
                post=-half+length*fraction;parts.append(path(f'M{number(post)} {edge+.4}v-1.95',stroke='#777972',width=.66))
        return f'<g id="{model["id"]}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">'+''.join(parts)+'</g>'
    if model.get('form')=='low-trestle':
        parts=[poly([(-half,-w*.5),(half,-w*.5),(half,w*.5),(-half,w*.5)],'#876d57','#51483d',.5)]
        for index in range(1,round(length/1.35)):
            xx=-half+1.35*index;parts.append(path(f'M{number(xx)} {-w*.47}v{w*.94}',stroke='#57493f',width=.28))
        parts.append(poly([(-half,w*.32),(half,w*.32),(half,w*.5+1.1),(-half,w*.5+1.1)],'#5b463a','#423b32',.32))
        for fraction in (.12,.39,.68,.94):
            post=-half+length*fraction;parts.append(path(f'M{number(post)} {w*.44}v4.5m0-3.1 2.4-1.6',stroke='#4a4035',width=1.0))
        parts.append(path(f'M{-half} {-w*.5-.4}h{length}',stroke='#56483a',width=.85))
        return f'<g id="{model["id"]}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">'+''.join(parts)+'</g>'
    stone=model['material']=='stone';deck='#d8d6b9' if stone else '#a58a60';edge='#8d9f83' if stone else '#635e43'
    p=[f'<g transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">']
    for side in [-1,1]:
        xx=side*half
        p.append(poly([(xx-2,-w*.7),(xx+2,-w*.7),(xx+2,w*.8),(xx-2,w*.8)],'#c6c7aa','#879a7c',.3))
        for step in range(3):
            sx=xx+side*(step+1)*1.1
            p.append(path(f'M{number(sx)} {-w*.63}v{w*1.35}',stroke='#e3ddbd',width=.65))
    p += [
       ellipse(1,3,half+1,w*.68,'#254f43','opacity=".2"'),
       path(f'M{-half} {-w*.4}Q0 {-w*.4-4} {half} {-w*.4}V{w*.5}Q0 {w*.5-3} {-half} {w*.5}Z',deck,edge,.45),
       path(f'M{-half} {w*.5}Q0 {w*.5-3} {half} {w*.5}v2Q0 {w*.5} {-half} {w*.5+2}Z',edge)]
    if stone:
        p.append(path(f'M{-half} {w*.5}Q0 {w*.5-3} {half} {w*.5}v4Q0 {w*.5-1.6} {-half} {w*.5+4}Z','#b6bea0','#809779',.3))
        for i in range(1,10):
            xx=-half+length*i/10;rise=3*(1-(xx/half)**2)
            p.append(path(f'M{number(xx)} {number(w*.5-rise*.5)}l{number(xx/half*.7)} 2.4',stroke='#e0dfbf',width=.4))
    count=max(5,int(length/2))
    for i in range(1,count):
        x=-half+length*i/count;arch=-3*(1-(x/half)**2)
        p.append(path(f'M{number(x)} {number(-w*.4+arch)}v{w*.9}',stroke='#8d9a7f' if stone else '#6d674b',width=.25))
    for side in [-1,1]:
        y=side*w*.53
        p.append(path(f'M{-half} {y-2}Q0 {y-6} {half} {y-2}',stroke='#e8e2c4' if stone else '#d2bd86',width=.8))
        p.append(path(f'M{-half} {y-3.5}Q0 {y-7.5} {half} {y-3.5}',stroke=edge,width=.35))
        for i in range(8):
            x=-half+i*length/7;arch=-4*(1-(x/half)**2)
            p.append(path(f'M{number(x)} {number(y+arch)}v-3.4',stroke=deck,width=.85))
            p.append(ellipse(x,y+arch-3.5,.75,.45,'#ece5c6'))
    return ''.join(p)+'</g>'

def boat(model):
    bamboo=model.get('canopy','bamboo')=='bamboo'
    roof,rib=('#b59b67','#dcc99b') if bamboo else ('#526769','#9aaea4')
    parts=[f'<g transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]}) scale({model["scale"]})">',
           ellipse(1.5,3.8,14,3.4,'#315b51','opacity=".22"'),
           path('M-14 0Q-8-4 9-3L16-1Q13 4 9 5Q-4 7-11 4Z','#805a41','#544a39',.48),
           path('M-14 0Q-8-5 9-4L16-1Q5 3-10 2Z','#b88e61','#64563e',.38),
           path('M-10 2Q3 4 13 .4M-8 4Q2 6 9 4.5',stroke='#d4b68a',width=.32)]
    for seat in (8,10.5,13):parts.append(path(f'M{seat} -2.6l.6 2.8',stroke='#81603f',width=.65))
    for post in (-9,-4,1,6):
        parts.append(path(f'M{post} .9v-5.3',stroke='#5e503c',width=.68))
        parts.append(path(f'M{post+.3} .7v-4.9',stroke='#e1c59a',width=.21))
    parts.append(path('M-11-3.1Q-11-9-6-9.2L3-9.6Q7-9.8 8-4.3L6.5-2.8Z',roof,'#526152',.4))
    for beam in (-9,-5,-1,3):parts.append(path(f'M{beam} -3.2q.3-3.9 2.7-5.6',stroke=rib,width=.44))
    parts.append(path('M-10-3.1 7-3.1M-10 1.1 7 1.1',stroke='#c8ad82',width=.47))
    return ''.join(parts)+'</g>'

def landing(model):
    w=model['width'];d=model['reach'];stone=model['material']=='stone'
    if model.get('form')=='washed-stone-steps':
        parts=[f'<g id="{model["id"]}" transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">']
        for step,(left,right,shade) in enumerate([(-.40,.41,'#968f82'),(-.51,.49,'#aaa9a1'),(-.48,.54,'#949e9c'),(-.44,.50,'#899999')]):
            top=-2.6+step*d/3.15;foot=top+d/3.15;start=w*left;end=w*right
            parts.append(poly([(start+.3,top),(end-.7,top-.25),(end,foot-.3),(start,foot)],shade,'#737774',.3))
            parts.append(poly([(start,foot),(end,foot-.3),(end,foot+.85),(start,foot+1.1)],'#596765','#666f69',.3))
            for joint in (.2+step%2*.13,.68-step%2*.09):
                seam=start+(end-start)*joint;parts.append(path(f'M{seam} {top+.3}l.32 {d/3.15-.6}',stroke='#646c69',width=.42))
        return ''.join(parts)+'</g>'
    fill='#cecdb0' if stone else '#ac946a';edge='#8c9d7e' if stone else '#6e6749'
    p=[f'<g transform="translate({model["x"]} {model["y"]}) rotate({model["angle"]})">',
       poly([(-w/2,-2),(w/2,-2),(w/2,d+2),(-w/2,d+2)],'#3c6750'),
       poly([(-w/2,-2),(w/2,-2),(w/2,d),(-w/2,d)],fill,edge,.35),
       poly([(-w/2,d),(w/2,d),(w/2,d+1.4),(-w/2,d+1.4)],edge)]
    if stone:
        for i in range(5):
            yy=-1+i*(d+1)/4
            p.append(path(f'M{-w/2} {yy}h{w}',stroke='#f0e5c4',width=.5))
            p.append(path(f'M{-w/2} {yy+.45}h{w}',stroke='#929f80',width=.25))
    else:
        for xx in range(-int(w/2)+1,int(w/2),2):p.append(path(f'M{xx} -2V{d}',stroke='#d9c18b',width=.3))
    for xx in [-w/2+1,w/2-1]:
        for yy in [0,d]:
            p.append(path(f'M{xx} {yy+2}v-4.6',stroke=edge,width=.9))
            p.append(ellipse(xx,yy-2.6,.85,.4,'#ddd0a7'))
        p.append(path(f'M{xx} -1.6V{d-1.6}',stroke='#d7c391' if not stone else '#dcdabd',width=.5))
    return ''.join(p)+'</g>'
