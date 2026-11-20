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

def quay_edge(region,quay):
    ring=region['holes'][quay['hole']] if 'hole' in quay else region['points']
    start=ring.index(quay['from']);end=ring.index(quay['to'])
    return (ring+ring)[start:(end if end>=start else end+len(ring))+1]


def quay_face(edge,height,stone):
    if isinstance(stone,dict):
        from .masonry_bank import inset_face
        start,end=stone['span']
        if stone['finish']!='dressed-quay' or not 0<=start<end<len(edge):raise ValueError('Invalid dressed quay span')
        prefix=quay_face(edge[:start+1],height,stone['base']) if start else ''
        suffix=quay_face(edge[end:],height,stone['base']) if end<len(edge)-1 else ''
        return prefix+inset_face(edge[start:end+1],stone['rise'],stone['copingWidth'])+suffix
    top=[(x,y-height) for x,y in edge];parts=[poly(edge+top[::-1],stone)]
    for (x,y),(xx,yy) in zip(edge,edge[1:]):
        count=max(1,round(math.hypot(xx-x,yy-y)/4.3))
        for index in range(count):
            at=(index+.35)/count;parts.append(path(f'M{number(x+(xx-x)*at)},{number(y+(yy-y)*at-.2)}v-{number(height-.4)}',stroke='#a09982',width=.28))
    parts.append(path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in top),stroke='#b9b29a',width=.65))
    return ''.join(parts)


def island_quay(region,quay):
    ring=region['holes'][quay['hole']];key=quay['id'];outline=rounded_ring(ring)
    return f'<defs><clipPath id="{key}">'+path(outline,'white')+'</clipPath></defs>'+f'<g clip-path="url(#{key})">'+path(outline,'url(#island-stone)')+quay_face(quay_edge(region,quay),quay['height'],quay.get('stone','#766f5f'))+'</g>'


def bank_course(course):
    toe, cap = course['toe'], course['cap']
    def trace(points):
        return 'M'+'L'.join(f'{number(horizontal)},{number(vertical)}' for horizontal,vertical in points)
    def measured(points):
        distances=[0]
        for first,last in zip(points,points[1:]):distances.append(distances[-1]+math.dist(first,last))
        def at(fraction):
            target=distances[-1]*fraction
            for index,(start,end) in enumerate(zip(distances,distances[1:])):
                if target<=end:
                    across=(target-start)/max(.001,end-start)
                    return [first+(last-first)*across for first,last in zip(points[index],points[index+1])]
            return points[-1]
        return distances[-1],at
    colors={'umber':('#70604c','#4f4b40','#b5a58b'),'granite':('#777772','#535650','#b9b9ad'),'moss':('#626c50','#475641','#a0a786')}
    body,foot,lip=colors[course.get('tone','umber')]; length,base=measured(toe); _,coping=measured(cap)
    parts=[poly(toe+cap[::-1],body),path(trace(toe),stroke=foot,width=.50)]
    joints=max(1,round(length/6.2))
    for index in range(joints):
        start=base((index+.38)/joints);end=coping((index+.45)/joints)
        if math.dist(start,end)>1.45:parts.append(path(trace([start,end]),stroke=foot,width=.32,extra='opacity=".62"'))
    parts.append(path(trace(cap),stroke=lip,width=.44))
    return ''.join(parts)


def street_bed(walk):
    profile=walk['profile']; left=[]; right=[]
    for index,(horizontal,vertical,width) in enumerate(profile):
        before=profile[max(0,index-1)]; after=profile[min(len(profile)-1,index+1)]
        along,down=after[0]-before[0],after[1]-before[1]; norm=max(.01,math.hypot(along,down))
        side_x,side_y=-down*width/(2*norm),along*width/(2*norm)
        left.append((horizontal+side_x,vertical+side_y)); right.append((horizontal-side_x,vertical-side_y))
    if walk.get('material')=='garden-sand':
        parts=[]
        for fraction,color in [(1,'#d7cdb5'),(.83,'#d3c4ad'),(.54,'#cebea7')]:
            def verge(side):return [(station[0]+(point[0]-station[0])*fraction,station[1]+(point[1]-station[1])*fraction) for station,point in zip(profile,side)]
            parts.append(path(rounded_ring(verge(left)+verge(right)[::-1]),color))
        return f'<g id="{walk["id"]}">'+''.join(parts)+'</g>'
    return f'<g id="{walk["id"]}">'+path(rounded_ring(left+right[::-1]),'#c5b29d','#c8b7a2',.4)+'</g>'


def flag_cut(points, tone):
    parts=[]
    for start,end in zip(points,points[1:]):
        across,down=end[0]-start[0],end[1]-start[1]
        length=math.hypot(across,down)
        normal=(-down/length,across/length)
        breadth=min(.37,.16+length*.013)
        def place(travel,edge):
            return (start[0]+across*travel+normal[0]*edge,start[1]+down*travel+normal[1]*edge)
        parts.append(poly([start,place(.18,-breadth*.63),place(.70,-breadth),end,place(.81,breadth*.48),place(.24,breadth*.71)],tone))
    return ''.join(parts)


def stone_lip(course):
    rim=course['rim'];drop=course['drop'];rng=random.Random(str(rim[0]))
    toe=[(across,down+drop) for across,down in rim]
    parts=[poly(rim+toe[::-1],'#c4c0bf')]
    for near,far in zip(rim,rim[1:]):
        blocks=max(1,round(math.dist(near,far)/4.3))
        def place(fraction,sink):
            return (near[0]+(far[0]-near[0])*fraction,near[1]+(far[1]-near[1])*fraction+sink)
        for index in range(blocks):
            left,right=index/blocks,(index+1)/blocks
            stone=rng.choice(('#c5c6c5','#acacac','#d4d3d2','#ddd9d2','#b9bec2'))
            parts.append(poly([place(left,.22),place(right,.20),place(right,drop-.12),place(left,drop)],stone))
            if rng.random()<.54:
                parts.append(poly([place(left,drop*.72),place(left+.37/blocks,drop*.73),place(left+.40/blocks,drop),place(left,drop+.18)],'#737876'))
    return ''.join(parts)


def ground_bed(bed):
    outline=rounded_ring(bed['points']) if bed.get('softVerge') else shape(bed)
    parts=[f'<g id="{bed["id"]}">',path(outline,f'url(#{bed["material"]})')]
    rng=random.Random(bed['id'])
    for horizontal,vertical,wide,tall in bed.get('tufts',[]):
        parts.append(ellipse(horizontal,vertical,wide*.48,tall*.38,'#adca86'))
        for tuft in range(max(4,round(wide*tall*.38))):
            angle=rng.random()*math.tau;radius=rng.random()**.5
            base_x=horizontal+math.cos(angle)*radius*wide*.5;base_y=vertical+math.sin(angle)*radius*tall*.5
            reach=rng.uniform(-1.35,1.35);rise=rng.uniform(.52,2.1)
            parts.append(path(f'M{number(base_x)},{number(base_y)}q{number(reach*.17)},{number(-rise*.68)} {number(reach)},{number(-rise)}',stroke=rng.choice(('#586e3d','#85a85e','#73924e','#ccdc9c')),width=rng.uniform(.38,.85)))
    return ''.join(parts)+'</g>'

MATERIALS='''<defs>
<linearGradient id="spring-sward" x1=".2" y1=".8" x2=".8" y2=".1"><stop stop-color="#dce7cf"/><stop offset=".42" stop-color="#e4edcf"/><stop offset=".8" stop-color="#dbe7c4"/><stop offset="1" stop-color="#e5e9d7"/></linearGradient>
<pattern id="cool-flagstone" width="37" height="23" patternUnits="userSpaceOnUse"><rect width="37" height="23" fill="#dce4e5"/><path d="M0 4q6-2 14-.7t12-.4v3q-10 1.8-16-.2T0 6Z" fill="#d8e1e3"/><path d="M8 16q5-1.6 10-1l6 .3-2 1.5-9 1.2zM30 7q3-.8 5-.4l-2 1z" fill="#e2e8e7"/><path d="M5 10l.9-.3m2.8 1.7 1.5-.2m9 7.8 2-.4m7-16 1.6-.4m-5.8 1.9 1.3-.1" fill="none" stroke="#c6d2d3" stroke-width=".45"/></pattern>
<linearGradient id="cinder-clay" x1="0" y1=".2" x2=".95" y2=".65"><stop stop-color="#9b8e86"/><stop offset=".4" stop-color="#a08c89"/><stop offset="1" stop-color="#9f8e89"/></linearGradient>
<pattern id="track-grit" width="13" height="9" patternUnits="userSpaceOnUse"><path d="M1 2.4l1.5-.3m5.1 3.2 1.4.3m1.8-4.1.8.4M3.3 7l.9-.3" fill="none" stroke="#827970" stroke-width=".46" opacity=".55"/><path d="M4.6 3.5l.8-.3m5.2 4.1.9.4" fill="none" stroke="#bcaaa0" stroke-width=".58" opacity=".52"/></pattern>
<linearGradient id="willow-turf" x1=".2" y1="0" x2=".8" y2="1"><stop stop-color="#c6dcb1"/><stop offset=".48" stop-color="#abd39c"/><stop offset="1" stop-color="#bfdca8"/></linearGradient>
<linearGradient id="spring-turf" x1="0" y1="1" x2=".85" y2=".1"><stop stop-color="#d6ddbf"/><stop offset=".55" stop-color="#c6dbaf"/><stop offset="1" stop-color="#a9ca95"/></linearGradient>
<linearGradient id="avenue-turf" x1=".45" y1="0" x2=".55" y2="1"><stop stop-color="#c0d8ac"/><stop offset=".55" stop-color="#d8dec0"/><stop offset="1" stop-color="#e4ddc6"/></linearGradient>
<pattern id="silver-setts" width="19" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-3)"><rect width="19" height="12" fill="#e2e1dd"/><path d="M0 0h8v5H0Z M12 6h7v6h-7Z" fill="#e6e5e0"/><path d="M0 5.7h7.2m1.3 0H19M8 .2v4.4m4 2.6v4.3M2 11.6h8" fill="none" stroke="#cfcfca" stroke-width=".33"/></pattern>
<pattern id="blue-grey-flags" width="27" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(-4)"><rect width="27" height="18" fill="#9ea2ae"/><path d="M0 0h14v8H0ZM17 10h10v8H17Z" fill="#a4a6b0"/><path d="M5 10h8v6H5ZM20 2h5v4h-5Z" fill="#9ba0ab"/><path d="M0 8.5h11.3m.6 0h7M14 0v5.6M5 11v4.3m3.3 2.4h7" fill="none" stroke="#b2b3bb" stroke-width=".28"/></pattern>
<pattern id="island-stone" width="13" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-53)"><rect width="13" height="7" fill="#e6e1d2"/><path d="M0 .2h13M0 3.6h13M3 .2v3.4m6 0v3.4" fill="none" stroke="#c6c1af" stroke-width=".26"/></pattern>
<linearGradient id="water" x1="0" y1="0" x2=".4" y2="1"><stop stop-color="#a2dfeb"/><stop offset=".45" stop-color="#95d7e4"/><stop offset="1" stop-color="#87cdda"/></linearGradient>
<pattern id="ripples" width="83" height="47" patternUnits="userSpaceOnUse"><path d="M4 9q6-.3 12-1.7m28 16q9 0 15-2M22 40q4-.3 9-1.6" fill="none" stroke="#d9f3f5" stroke-width=".56" opacity=".7"/><path d="M8 16l6-1m27-9 10-.8" stroke="#67adbd" stroke-width=".35" opacity=".45"/></pattern>
<pattern id="pavers" width="16" height="10" patternUnits="userSpaceOnUse"><rect width="16" height="10" fill="#d5d4bd"/><path d="M0 0h16M0 5h16M8 0v5M3 5v5M15 5v5" stroke="#aeb49d" stroke-width=".35"/><path d="M.5 1h7m1 5h6" stroke="#efead3" stroke-width=".5" opacity=".8"/><path d="M9 1h6v3H9ZM4 6h9v3H4Z" fill="#c9cdb5" opacity=".45"/></pattern>
<pattern id="sand" width="23" height="19" patternUnits="userSpaceOnUse"><rect width="23" height="19" fill="#dad6b9"/><path d="M1 3h3m8 7h2M4 15h1m15-9h2" stroke="#a7b091" stroke-width=".35" opacity=".5"/><circle cx="17" cy="16" r=".45" fill="#f0e5c4"/></pattern>
<pattern id="lane-setts" width="29" height="17" patternUnits="userSpaceOnUse" patternTransform="rotate(-3)"><rect width="29" height="17" fill="#dedfce"/><path d="M.1 3h9.3l.4 4.7H0zM17.3 13.1l11.7-.5v4.4H17.2z" fill="#d7d9ca"/><path d="M0 3h9.2l3.5-.4 16.3.2M0 8l17-.4 12 .2M0 13.3l11-.6 18 .2m-11.8.1.1 4M9.3 3l.5 4.7m12.8-4.9-.3 4.6M4 8.3l.2 4.4" fill="none" stroke="#bfc3b5" stroke-width=".31"/></pattern>
<pattern id="silver-flags" width="24" height="15" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)"><rect width="24" height="15" fill="#e6e6de"/><path d="M1 3h8v4H.8zM15 10h8v4h-8z" fill="#dfe1d9"/><path d="M0 2.7h7.6l.3 4.4 9.5-.2M20.2 3.2l3.8-.5M0 10.1h14.3l.4 4.9" fill="none" stroke="#c5c8bf" stroke-width=".36"/></pattern>
<pattern id="quay" width="12" height="6" patternUnits="userSpaceOnUse"><rect width="12" height="6" fill="#b4b99e"/><path d="M0 0h12M0 3h12M5 0v3M10 3v3" stroke="#7f927a" stroke-width=".35"/><path d="M0 1h4m2 3h3" stroke="#dee0c1" stroke-width=".5"/></pattern>
</defs>'''

def tree(model):
    if 'canalGrove' in model:
        from .canal_groves import canal_grove
        return canal_grove(model)
    if model.get('stems'):
        from .plantings import planting
        return planting(model)
    rng=random.Random(model['id']);kind=model['kind'];s=model['scale']
    if 'volume' in model.get('crown',{}):
        from .crowns import crown
        return crown(model,rng)
    if 'crown' in model:return observed_crown(model,rng)
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

def crown_extent(model):
    if model.get('stems'):
        from .plantings import extent
        return extent(model['stems'])
    scale=model['scale']; room=22*scale
    if 'crown' not in model:return [-room,-44*scale,room,5]
    if 'volume' in model['crown']:
        rows=model['crown']['volume']['stations']
        return [min([-room]+[center-radius-3 for level,center,radius in rows]),rows[0][0]-3,
                max([room]+[center+radius+3 for level,center,radius in rows]),max(5,rows[-1][0]+4)]
    leaves=model['crown']['lobes']
    return [min([-room]+[cx-rx*1.25-1 for cx,cy,rx,ry,*_ in leaves]),
            min(cy-ry*1.25-1 for cx,cy,rx,ry,*_ in leaves),
            max([room]+[cx+rx*1.25+1 for cx,cy,rx,ry,*_ in leaves]),
            max([5]+[cy+ry*1.25+1 for cx,cy,rx,ry,*_ in leaves])]


def observed_crown(model,rng):
    descriptor=model['crown'];lobes=descriptor['lobes'];scale=model['scale']
    palettes={'leaf':['#3e5e37','#659152','#89ad68','#a4c481','#c5dc9e'],
              'spring':['#3c5a20','#669026','#91b641','#b1ce66','#d3e799'],
              'pink':['#835749','#ad7569','#d39382','#eab5aa','#f9d5c7'],
              'gold':['#795c40','#a28148','#c39b54','#d7ae67','#e8d789']}
    colors=palettes[descriptor['tone']]
    ink='#354431' if descriptor['tone'] in ('leaf','spring') else '#654739'
    parts=[f'<g data-crown="{model["id"]}" transform="translate({model["x"]} {model["y"]})">',
           ellipse(1.2*scale,.8*scale,5.8*scale,1.3*scale,'#667047','opacity=".35"')]
    for cx,cy,rx,ry,band,shade,light in lobes:
        parts.append(path(f'M0 0Q{number(-scale)},{number(cy*.40)} {number(cx)},{number(cy)}',stroke='#544f39',width=1.25*scale))
    for order,(cx,cy,rx,ry,band,shade,light) in enumerate(lobes):
        light_angle=light*math.pi/4; across=math.cos(light_angle); down=math.sin(light_angle)
        if descriptor['tone']=='pink':
            parts.append(ellipse(cx,cy,rx*.93,ry*.92,'#edc0b3','opacity=".62"'))
            for spray in range(max(4,round(rx*ry*.19))):
                angle=rng.random()*math.tau; span=rng.random()**.5
                tip_x=cx+rx*math.cos(angle)*span; tip_y=cy+ry*math.sin(angle)*span
                stem_x=tip_x+rng.uniform(-1.3,1.3); stem_y=tip_y+rng.uniform(1.0,2.1)
                if spray%3==0:
                    parts.append(path(f'M{number(stem_x)},{number(stem_y)}Q{number(tip_x-.7)},{number(tip_y+.7)} {number(tip_x)},{number(tip_y)}',stroke=ink,width=.55))
                tone=colors[min(4,max(1,band+rng.choice([-1,0,0,1])))]
                parts.append(ellipse(tip_x,tip_y,.86,.75,tone))
                parts.append(ellipse(tip_x+.67,tip_y-.47,.65,.56,'#f8cdc0'))
                if spray%4==0:parts.append(ellipse(tip_x-.38,tip_y+.3,.38,.32,'#99594b'))
            continue
        key=f'foliage-{model["id"]}-{order}'
        parts.append(f'<defs><linearGradient id="{key}" x1="{number(.5-.5*across)}" y1="{number(.5-.5*down)}" x2="{number(.5+.5*across)}" y2="{number(.5+.5*down)}"><stop stop-color="{colors[max(0,band-1)]}"/><stop offset=".28" stop-color="{colors[band]}"/><stop offset=".8" stop-color="{colors[band]}"/><stop offset="1" stop-color="{colors[min(4,band+1)]}"/></linearGradient></defs>')
        outline=[]
        for index in range(13):
            angle=index*math.tau/13;rad=rng.uniform(.85,1.04)
            outline.append((cx+rx*math.cos(angle)*rad,cy+ry*math.sin(angle)*rad))
        contour=f'M{number(outline[0][0])},{number(outline[0][1])}'
        for index,tip in enumerate(outline[1:]+outline[:1]):
            angle=(index+.5)*math.tau/13;rad=rng.uniform(1,1.18)
            contour+=f'Q{number(cx+rx*math.cos(angle)*rad)},{number(cy+ry*math.sin(angle)*rad)} {number(tip[0])},{number(tip[1])}'
        parts.append(path(contour+'Z',f'url(#{key})'))
        count=max(7,round(rx*ry*.30))
        for index in range(count):
            angle=rng.random()*math.tau;rad=rng.random()**.48*.93
            horizontal=cx+rx*math.cos(angle)*rad;vertical=cy+ry*math.sin(angle)*rad
            dim=rng.random()<.30+shade*.07-.26*math.cos(angle-light_angle)*rad
            tone=colors[max(0,band-2) if dim else min(4,band+1)]
            if dim and index%3==0:tone=ink
            length=min(1.85,max(.63,rx*.24))*rng.uniform(.70,1.24)
            parts.append(ellipse(horizontal,vertical,length*.61,length*rng.uniform(.50,.95),tone))
            if dim:parts.append(ellipse(horizontal-length*.53,vertical-length*.78,length*.34,length*.45,tone))
            if index%5==0:
                edge_x=cx+rx*math.cos(angle);edge_y=cy+ry*math.sin(angle)
                parts.append(path(f'M{number(edge_x)},{number(edge_y)}q-.55 -.86 .36 -1.42',stroke=ink,width=.54))
        if model['kind']=='willow' and ry>4:
            for across in (-.61,.14,.53):
                start=cx+across*rx;foot=cy+ry*math.sqrt(1-across**2)
                parts.append(path(f'M{number(start)},{number(foot-1)}q.55 1.4 -.22 2.45',stroke=colors[max(0,band-1)],width=.42))
    return ''.join(parts)+'</g>'


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
    if model.get('form')=='stone-steps':
        sections=model['sections'];parts=[]
        near=[right for left,right in sections];far=[left for left,right in sections]
        def line(points,color,width):
            return path('M'+'L'.join(f'{number(horizontal)},{number(vertical)}' for horizontal,vertical in points),stroke=color,width=width)
        def between(first,last,fraction):return [start+(end-start)*fraction for start,end in zip(first,last)]
        slate=model.get('stone')=='slate';rng=random.Random(model['id'])
        face,rail,cap=('#95989b','#424348','#b3bab9') if slate else ('#c7c5c1','#5b5757','#e8e4de')
        parts.append(poly(far+near[::-1],face,rail,.42))
        for (start,end),(next_start,next_end) in zip(sections,sections[1:]):
            steps=max(1,round(math.dist(start,next_start)/2.0))
            for index in range(steps):
                left=between(start,next_start,index/steps); right=between(end,next_end,index/steps)
                if slate:
                    lower_left=between(start,next_start,(index+1)/steps);lower_right=between(end,next_end,(index+1)/steps)
                    split=rng.uniform(.31,.67)
                    for low,high in ((.1,split-.013),(split+.013,.9)):
                        flags=[between(left,right,low),between(left,right,high),between(lower_left,lower_right,high),between(lower_left,lower_right,low)]
                        parts.append(poly(flags,rng.choice(['#a1a5a4','#979a9a','#83898b','#b3b3af','#8f8e93'])))
                parts.append(line([between(left,right,.13),between(left,right,.87)],cap,.4))
        for side in (far,near):
            parapet=[(horizontal,vertical-1.6) for horizontal,vertical in side]
            parts.append(line(side,rail,1.12));parts.append(poly(side+parapet[::-1],rail));parts.append(line(parapet,cap,.66))
            for start,end in zip(side,side[1:]):
                count=max(1,round(math.dist(start,end)/5.5))
                for index in range(count):
                    horizontal,vertical=between(start,end,index/count)
                    parts.append(path(f'M{number(horizontal)},{number(vertical)}v-2.8',stroke=rail,width=.94))
                    parts.append(ellipse(horizontal,vertical-2.9,.65,.38,cap))
        return f'<g id="{model["id"]}">'+''.join(parts)+'</g>'
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
