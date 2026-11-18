"""Draw eaves observed in the illustration, not geographic footprints."""
import math
import random
from .landscape import number, path, poly
from .surface_finishes import path_shape, render_surface, timber_facings
from .native_roofs import slate


def street_areas(data):
    return {**data['sites'],**data['background']}


def overlaps_box(ring,box):
    left,top,right,bottom=box
    return min(x for x,y in ring)<right and max(x for x,y in ring)>left and min(y for x,y in ring)<bottom and max(y for x,y in ring)>top


def shifted(point, dx, dy):
    return (point[0]+dx, point[1]+dy)


def along(start, end, fraction):
    return (start[0]+(end[0]-start[0])*fraction, start[1]+(end[1]-start[1])*fraction)


def stroke(points, color, width):
    return path('M'+'L'.join(f'{number(x)},{number(y)}' for x,y in points),stroke=color,width=width)


def canopy_frame(left,right,rear_left,rear_right,height,formal=False):
    parts=[]
    for start,finish in [(rear_left,rear_right),(left,right)]:
        posts=max(1,round(math.dist(start,finish)/9))
        for index in range(posts+1):
            post=along(start,finish,(index+.07)/(posts+.14));base=shifted(post,0,height)
            parts.append(stroke([post,base],'#533c34' if formal else '#635341',1.03 if formal else .66))
            parts.append(stroke([shifted(base,-.42,0),shifted(base,.42,0)],'#9e9784',.51))
            parts.append(stroke([shifted(post,-.55,.55),shifted(post,0,1.3),shifted(post,.55,.55)],'#857058',.31))
            if formal:
                parts.append(stroke([shifted(post,-1.2,.6),shifted(post,1.2,.6)],'#684c3c',.66))
                parts.append(stroke([shifted(post,-.75,1.23),shifted(post,.75,1.23)],'#8d694b',.48))
        parts.append(stroke([shifted(start,0,.7),shifted(finish,0,.7)],'#655544',.54))
    return ''.join(parts)


def roof_slope(start,end,fraction,sag):
    return shifted(along(start,end,fraction),0,4*sag*fraction*(1-fraction))


def slope_points(start,end,sag):
    return [roof_slope(start,end,index/8,sag) for index in range(9)]


def water_piers(front,rear,height):
    parts=[]
    for fraction,width in [(0,.18),(.72,.23)]:
        left=along(front,rear,fraction);right=along(front,rear,fraction+width)
        parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#dfded7','#514e4a',.52))
        parts.append(stroke([shifted(left,0,height-.4),shifted(right,0,height-.4)],'#7e827a',.79))
    parts.append(poly([front,rear,shifted(rear,0,1.3),shifted(front,0,1.3)],'#5d524a','#524d49',.34))
    return ''.join(parts)


def curled_hip(rear,crest,front,sag,color):
    tip=shifted(front,0,-2.5);drip=slope_points(rear,tip,.78)
    edge=[shifted(roof_slope(crest,front,index/8,sag),0,-2.5*(index/8)**2) for index in range(9)]
    parts=[poly(drip+[shifted(point,0,1.04) for point in reversed(drip)],'#50423a','#403631',.24),
           poly(slope_points(rear,crest,sag)+edge[1:]+drip[-2::-1],color,'#393739',.28)]
    for index in range(1,8):
        parts.append(stroke([crest,along(crest,drip[index],.53),drip[index]],'#73706c',.23))
    parts.append(stroke(drip,'#73665b',.4))
    return ''.join(parts)


def panel(top_left, top_right, bottom_left, bottom_right, color, face, lift=0,glazed=False,sag=0,weathered=False,inked=False,aged=False):
    def tile(across,down):
        point=roof_slope(along(top_left,top_right,across),along(bottom_left,bottom_right,across),down,sag)
        return shifted(point,0,-lift*abs(2*across-1)**5*down**2)
    def course(down):return [tile(index/16,down) for index in range(17)]
    outline=[top_left,top_right]+(course(1)[::-1] if lift else [bottom_right,bottom_left])
    if sag:outline=[top_left,top_right]+[tile(1,index/8) for index in range(1,8)]+course(1)[::-1]+[tile(0,index/8) for index in range(7,0,-1)]
    parts=[poly(outline,color,'#363435',.34)]
    if aged:
        rng=random.Random(f'{top_left[0]:.2f}/{top_left[1]:.2f}')
        columns=max(2,round(math.dist(bottom_left,bottom_right)/1.65));bands=max(2,round(math.dist(top_left,bottom_left)/2.1))
        for column in range(columns):
            across=(column+.5)/columns
            start=rng.uniform(.08,.51);end=rng.uniform(.59,.96)
            parts.append(stroke([tile(across,start),tile(across,(start+end)/2),tile(across,end)],rng.choice(['#4d494d','#605d60','#6e6a6b']),.33))
            for band in range(bands):
                level=(band+rng.uniform(.25,.68))/bands
                if rng.random()<.36:continue
                half=rng.uniform(.30,.49)/columns;drop=min(1-level,rng.uniform(.32,.68)/bands)
                color=rng.choice(['#1b191e','#262428','#434044','#777477','#999495'])
                parts.append(poly([tile(across-half,level),tile(across+half,level-.06/bands),tile(across+half*.72,level+drop*.68),tile(across-half*.86,level+drop)],color))
        return ''.join(parts)
    count=max(3,round(math.dist(bottom_left,bottom_right)/(2.9 if glazed else 1.15)))
    for index in range(1,count):
        fraction=index/count
        channel=[tile(fraction,down) for down in ((0,.25,.5,.75,1) if sag else (0,.5,1))]
        parts.append(stroke(channel,('#985e35' if face else '#99623b') if glazed else ('#292831' if face else '#383840'),.72 if glazed else .25))
        parts.append(stroke([shifted(point,.36 if glazed else .26,0) for point in channel],('#eed09b' if index%3 else '#f7d8a4') if glazed else ('#898783' if face else '#a19c94'),.32 if glazed else .18))
        if glazed:
            start=.12+.08*(index%4);end=.82+.04*(index%3)
            parts.append(stroke([tile(fraction,down) for down in (start,(start+end)/2,end)],'#835029' if index%3 else '#754324',.82 if index%2 else 1.05))
        if weathered and index%5 in (0,2):
            start=.11+.06*((index*17)%9);end=min(.94,start+.14+.04*((index*3)%7))
            parts.append(stroke([tile(fraction,start),tile(fraction,end)],'#302e2e' if index%3 else '#928878',.5))
        if inked and index%4!=1:
            for band in range(1+int(math.dist(top_left,bottom_left)>8)):
                level=.12+.075*((index*13+band*4)%10);span=.07+.02*(index%5)
                parts.append(stroke([tile(fraction,level),tile(fraction,min(1,level+span))],'#302d31' if (index+band)%4 else '#9a9892',.55 if index%2 else .72))
    courses=max(2,round(math.dist(top_left,bottom_left)/1.8))
    for index in range(1,courses):
        parts.append(stroke(course(index/courses) if lift else [tile(0,index/courses),tile(1,index/courses)],'#b98250' if glazed else '#4b4746',.18))
    if lift:parts.append(stroke(course(1),'#eac48b' if glazed else '#bab1a0',.55))
    return ''.join(parts)


def roof_frame(model,form=None):
    left_x,left_y,right_x,right_y,depth_x,depth_y,rise,height,kind=model
    left=(left_x,left_y);right=(right_x,right_y)
    rear_left=shifted(left,depth_x,depth_y);rear_right=shifted(right,depth_x,depth_y)
    if form and 'rear' in form:rear_left,rear_right=form['rear']
    hip=.19 if kind in ('canopy','hall') else .13 if kind in ('temple','temple-portico') else .025
    left_depth=(rear_left[0]-left_x,rear_left[1]-left_y) if form else (depth_x,depth_y)
    right_depth=(rear_right[0]-right_x,rear_right[1]-right_y) if form else (depth_x,depth_y)
    ridge_left=shifted(along(left,right,hip),left_depth[0]/2,left_depth[1]/2-rise)
    ridge_right=shifted(along(left,right,1-hip),right_depth[0]/2,right_depth[1]/2-rise)
    if form and 'ridge' in form:ridge_left,ridge_right=form['ridge']
    return left,right,rear_left,rear_right,ridge_left,ridge_right


def end_wall(model,frame,form):
    left,right,rear_left,rear_right,ridge_left,ridge_right=frame
    depth_x,depth_y,rise,height,kind=model[4:];inset=.965 if depth_x>=0 else .035;near=along(left,right,inset)
    if form and form.get('endFace')=='limewash':return right,ridge_right,rear_right
    if form:return near,shifted(ridge_right if depth_x>=0 else ridge_left,0,.4),along(rear_left,rear_right,inset)
    return near,shifted(near,depth_x/2,depth_y/2-rise+.4),shifted(near,depth_x*.94,depth_y*.94)


def roof_faces(model,frame,form):
    left,right,rear_left,rear_right,ridge_left,ridge_right=frame;kind=model[-1]
    faces=[[left,right,ridge_right,ridge_left],[rear_left,rear_right,ridge_right,ridge_left]]
    sag=(form or {}).get('sag',0)
    if sag:faces=[slope_points(ridge_left,edge_left,sag)+slope_points(edge_right,ridge_right,sag) for edge_left,edge_right in [(left,right),(rear_left,rear_right)]]
    if kind in ('canopy','hall','temple','temple-portico'):faces.extend([[left,rear_left,ridge_left],[right,rear_right,ridge_right]])
    return faces


def tree_blockers(model,form=None):
    frame=roof_frame(model,form);left,right,rear_left,rear_right,ridge_left,ridge_right=frame
    depth_x,depth_y,rise,height,kind=model[4:];faces=roof_faces(model,frame,form)
    if kind in ('canopy','temple-portico'):return faces
    start=along(left,right,.035);end=along(left,right,.965)
    faces.append([start,end,shifted(end,0,height),shifted(start,0,height)])
    near,peak,far=end_wall(model,frame,form)
    faces.append([near,peak,far,shifted(far,0,height),shifted(near,0,height)])
    return faces


def colonnade(frame,height):
    left,right=frame['beam'];parts=[]
    if frame.get('infill')=='lime-timber':
        parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#e4e0dc','#595250',.4))
        if 'transom' in frame:
            depth,bars=frame['transom'];parts.append(poly([left,right,shifted(right,0,depth),shifted(left,0,depth)],'#726765','#393335',.45))
            for index in range(1,bars):
                post=along(left,right,index/bars);parts.append(stroke([shifted(post,0,.4),shifted(post,0,depth-.2)],'#302d2e',.77))
        for column in frame['columns']:
            post=along(left,right,column)
            parts.append(stroke([post,shifted(post,0,height+.65)],'#332e30',frame['postWidth']))
            parts.append(stroke([shifted(post,.48,.3),shifted(post,.48,height-.45)],'#746961',.36))
        for level,width in frame['rails']:
            parts.append(stroke([shifted(left,0,height*level),shifted(right,0,height*level)],'#393436',width))
        return f'<g data-bays="{len(frame["columns"])-1}" data-infill="lime-timber">'+''.join(parts)+'</g>'
    for fraction,depth,width in frame.get('pierFeet',[]):
        post=along(left,right,fraction);base=shifted(post,0,height-.6)
        parts.append(poly([shifted(base,-width/2,0),shifted(base,width/2,0),shifted(base,width*.3,depth),shifted(base,-width*.30,depth+.2)],'#7e7267','#534d48',.36))
        parts.append(stroke([shifted(base,-width*.21,.65),shifted(base,-width*.20,depth-.3)],'#b6ada2',.36))
    if frame.get('infill')=='storeyed-shutters':
        parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#785046','#4b3734',.55))
        for top,bottom in zip(frame['floors'],frame['floors'][1:]):
            sill=(bottom-top)*height
            for bay,(start,end) in enumerate(zip(frame['columns'],frame['columns'][1:])):
                jamb=shifted(along(left,right,start+.019),0,top*height);stop=shifted(along(left,right,end-.019),0,top*height)
                parts.append(poly([shifted(jamb,0,1.15),shifted(stop,0,1.15),shifted(stop,0,sill*.83),shifted(jamb,0,sill*.83)],'#61423d' if bay%2 else '#704b42','#513936',.37))
                for fraction in (.18,.44,.68,.86):
                    post=along(jamb,stop,fraction);parts.append(stroke([shifted(post,0,1.45),shifted(post,0,sill*.79)],'#9b7061' if fraction==.44 else '#513c37',.28))
                parts.append(stroke([shifted(jamb,0,sill*.40),shifted(stop,0,sill*.40)],'#493633',.43))
                stile=along(jamb,stop,.25 if bay%2 else .72)
                parts.append(stroke([shifted(stile,0,1.3),shifted(stile,0,min(sill*.62,3.8))],'#372622',.84))
            parts.append(stroke([shifted(left,0,top*height+.35),shifted(right,0,top*height+.35)],'#352522',1.15))
        for fraction in frame['columns']:
            post=along(left,right,fraction);parts.append(stroke([post,shifted(post,0,height)],'#4c3631',.76))
        parts.append(stroke([shifted(left,0,height),shifted(right,0,height)],'#5a453c',.84))
        return f'<g data-bays="{len(frame["columns"])-1}" data-storeys="{len(frame["floors"])-1}">'+''.join(parts)+'</g>'
    if frame.get('infill')=='pier-gallery':
        parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#dedbd3','#514d49',.58))
        for start,end in zip(frame['columns'],frame['columns'][1:]):
            low=along(left,right,start+.028);high=along(left,right,end-.028)
            for top,bottom in [(1.6,height*.49),(height*.64,height-1.6)]:
                parts.append(poly([shifted(low,0,top),shifted(high,0,top),shifted(high,0,bottom),shifted(low,0,bottom)],'#65534e','#9b9086',.4))
                post=along(low,high,.55);parts.append(stroke([shifted(post,0,top),shifted(post,0,bottom)],'#a59181',.43))
        parts.append(stroke([shifted(left,0,height-.4),shifted(right,0,height-.4)],'#6a6662',.84))
        return f'<g data-bays="{len(frame["columns"])-1}" data-infill="pier-gallery">'+''.join(parts)+'</g>'
    if frame.get('infill')=='lattice-panels':
        parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#694438','#453932',.45))
        for index,(start,end) in enumerate(zip(frame['columns'],frame['columns'][1:])):
            low=along(left,right,start);high=along(left,right,end);bay=math.dist(low,high)
            for fraction in (0,.5):
                jamb=along(low,high,fraction+.35/bay);stop=along(low,high,fraction+.5-.35/bay)
                parts.append(poly([shifted(jamb,0,1.3),shifted(stop,0,1.3),shifted(stop,0,height*.43),shifted(jamb,0,height*.43)],'#58403a','#896556',.24))
                for division in (1,2,3):
                    bar=along(jamb,stop,division/4);parts.append(stroke([shifted(bar,0,1.38),shifted(bar,0,height*.43)],'#846253',.25))
                parts.append(poly([shifted(jamb,0,height*.54),shifted(stop,0,height*.54),shifted(stop,0,height-.92),shifted(jamb,0,height-.92)],'#80574a' if index%3 else '#785044','#654438',.22))
            parts.append(stroke([low,shifted(low,0,height)],'#493831',.83))
        for offset,color,width in [(height*.48,'#49362f',.78),(height-.25,'#4c3a32',.62),(height+.35,'#b5ad9b',.48)]:
            parts.append(stroke([shifted(left,0,offset),shifted(right,0,offset)],color,width))
        return f'<g data-bays="{len(frame["columns"])-1}" data-infill="lattice-panels">'+''.join(parts)+'</g>'
    if 'recess' in frame:
        delta=frame['recess'];rear_left=shifted(left,*delta);rear_right=shifted(right,*delta)
        plastered=frame.get('plasteredOpening');openings=[plastered] if plastered else zip(frame['columns'],frame['columns'][1:])
        parts.append(poly([rear_left,rear_right,shifted(rear_right,0,height),shifted(rear_left,0,height)],'#e4ddd2' if plastered else '#795446','#61463b',.4))
        for start,end in openings:
            low=along(rear_left,rear_right,start+.02);high=along(rear_left,rear_right,end-.02)
            parts.append(poly([shifted(low,0,1.3),shifted(high,0,1.3),shifted(high,0,height*.68),shifted(low,0,height*.68)],'#473d36','#986e56',.3))
            for step in (1,2,3):
                bar=along(low,high,step/4);parts.append(stroke([shifted(bar,0,1.4),shifted(bar,0,height*.68)],'#a68263',.24))
    parts.append(poly([left,right,shifted(right,0,1.35),shifted(left,0,1.35)],'#594033','#463930',.28))
    for column in frame['columns']:
        post=along(left,right,column);base=shifted(post,0,height)
        parts.append(stroke([post,base],'#50392f',frame.get('postWidth',1.22)))
        parts.append(stroke([shifted(post,-1.45,.65),shifted(post,1.45,.65)],'#745641',.7))
        parts.append(stroke([shifted(post,-.88,1.45),shifted(post,.88,1.45)],'#95755a',.51))
        parts.append(stroke([shifted(base,-.75,0),shifted(base,.75,0)],'#a0998b',.59))
    return f'<g data-bays="{len(frame["columns"])-1}">'+''.join(parts)+'</g>'


def house(model,tone=None,form=None,front_frame=None):
    left_x,left_y,right_x,right_y,depth_x,depth_y,rise,height,kind=model
    frame=roof_frame(model,form);left,right,rear_left,rear_right,ridge_left,ridge_right=frame
    shrine=kind in ('temple','temple-portico');open_frame=kind in ('canopy','temple-portico');hipped=kind in ('canopy','hall');glazed=tone=='ochre-glaze'
    wall_left=along(left,right,.035);wall_right=along(left,right,.965)
    sill_left=shifted(wall_left,0,height);sill_right=shifted(wall_right,0,height)
    is_timber=kind in ('shop','temple','gallery','arcade','hall','pier-shop')
    arcade=kind=='arcade'
    facing={'arcade':'#49423c','hall':'#795044','pier-shop':'#dfd8c8'}.get(kind,'#795548' if is_timber else '#eeeae1')
    parts=[poly([wall_left,wall_right,sill_right,sill_left],facing,'#6b655c',.3)]
    near_gable=end_wall(model,frame,form);end,peak,far_end=near_gable
    sag=(form or {}).get('sag',0)
    verge=slope_points(end,peak,sag)+slope_points(peak,far_end,sag)[1:] if sag else [end,peak,far_end]
    parts.append(poly(verge+[shifted(far_end,0,height),shifted(end,0,height)],'#776154' if shrine else '#e1dfe0' if tone=='aged-pan' else '#e4e0d6','#726e66',.3))
    if abs(depth_x)>3 and not (form and form.get('endFace')):
        parts.append(stroke([shifted(end,0,height*.84),shifted(far_end,0,height*.84)],'#aaa69c',.44))
        center=along(end,far_end,.52)
        parts.append(stroke([shifted(center,0,-rise*.4),shifted(center,0,-rise*.4+.8)],'#655f59',.72))
    bays=max(1,round(abs(right_x-left_x)/(5.7 if arcade else 6.6 if is_timber else 7)))
    if kind in ('pier-shop','hall'):
        for index in range(bays):
            start=along(wall_left,wall_right,(index+.1)/bays);finish=along(wall_left,wall_right,(index+.91)/bays)
            lintel=.76;bottom=height-.45
            parts.append(poly([shifted(start,0,lintel),shifted(finish,0,lintel),shifted(finish,0,bottom),shifted(start,0,bottom)],'#503e39' if kind=='pier-shop' else '#754b43','#55433c',.25))
            for fraction in (.12,.51,.89):
                bar=along(start,finish,fraction);parts.append(stroke([shifted(bar,0,1),shifted(bar,0,bottom)],'#95806a',.19))
            parts.append(stroke([shifted(start,0,height*.35),shifted(finish,0,height*.35)],'#53423b',.32))
            bracket=along(start,finish,.06);parts.append(stroke([shifted(bracket,0,.35),shifted(bracket,0,1.05)],'#c4af91',.58))
    elif kind=='blind-wall':
        parts.append(stroke([shifted(sill_left,0,-.55),shifted(sill_right,0,-.55)],'#c4bbac',.7))
        for post in (wall_left,wall_right):parts.append(stroke([post,shifted(post,0,height)],'#706a5f',.58))
    elif abs(right_x-left_x)>2:
        for index in range(bays):
            low,high=(index+.16)/bays,(index+.84)/bays
            start=along(wall_left,wall_right,low);end=along(wall_left,wall_right,high)
            if arcade:
                post=along(wall_left,wall_right,index/bays)
                parts.append(poly([shifted(start,0,height*.44),shifted(end,0,height*.44),shifted(end,0,height*.90),shifted(start,0,height*.90)],'#b9aa95','none'))
                parts.append(stroke([post,shifted(post,0,height)],'#785344',.9))
                parts.append(stroke([shifted(start,0,height*.62),shifted(end,0,height*.62)],'#6e5446',.4))
                parts.append(stroke([shifted(post,-.55,1.35),shifted(post,0,.65),shifted(post,.72,1.35)],'#b99b78',.33))
                continue
            top=.9 if is_timber else height*.22;bottom=height*(.84 if is_timber else .68)
            parts.append(poly([shifted(start,0,top),shifted(end,0,top),shifted(end,0,bottom),shifted(start,0,bottom)],'#493c36' if is_timber else '#615b53','#8e7962',.21))
            mid=along(start,end,.5);parts.append(stroke([shifted(mid,0,top),shifted(mid,0,bottom)],'#c4aa8d',.25))
            parts.append(stroke([shifted(start,0,height*.49),shifted(end,0,height*.49)],'#a59079',.24))
            if is_timber:
                if index%3==1 and kind=='shop':
                    parts.append(poly([shifted(start,0,top),shifted(end,0,top),shifted(end,0,height*.93),shifted(start,0,height*.93)],'#795848','#513c36',.27))
                    parts.append(stroke([shifted(mid,0,top),shifted(mid,0,height*.93)],'#493b34',.3))
                post=along(wall_left,wall_right,index/bays)
                parts.append(stroke([post,shifted(post,0,height)],'#4f3932',.62))
                parts.append(stroke([shifted(post,-.55,.8),shifted(post,.62,.8)],'#c5aa86',.45))
    parts.append(stroke([sill_left,sill_right],'#9b9486',.65))
    walls=canopy_frame(wall_left,wall_right,rear_left,rear_right,height,shrine) if open_frame else ''.join(parts);parts=[]
    if form and form.get('support')=='water-piers':
        walls=poly(verge+[far_end,end],'#dedbd6','#716f6b',.4)+water_piers(end,far_end,height)
    if front_frame:
        walls=colonnade(front_frame,height)
        if front_frame.get('exposedReturn'):
            front,crest,rear=near_gable
            side=poly([front,crest,rear,shifted(rear,0,height-.3),shifted(front,0,height)],'#dad6cd','#756e67',.42)
            side+=stroke([shifted(rear,0,height-.65),shifted(front,0,height-.35)],'#827c76',.59)
            walls=side+walls
    inked=tone=='ink-slate'
    rear_tone,front_tone={'river-grey':('#777873','#575b58'),'warm-tile':('#736a65','#59514f'),'smoke-tile':('#615b56','#494440'),'ink-slate':('#5c595a','#49484b'),'ochre-glaze':('#c58e5b','#e2a76e')}.get(tone,('#666363','#565355' if kind=='gallery' else '#504e51'))
    aged=tone=='aged-pan'
    if aged:rear_tone,front_tone='#605d60','#555257'
    parts.append(panel(rear_left,rear_right,ridge_left,ridge_right,rear_tone,False,glazed=glazed,sag=sag,weathered=tone=='smoke-tile',inked=inked,aged=aged))
    if glazed:
        for ridge,rear,front,color in [(ridge_left,rear_left,left,'#ad7546'),(ridge_right,rear_right,right,'#d9a367')]:
            tip=shifted(front,0,-2.5)
            parts.append(panel(ridge,ridge,rear,tip,color,False,glazed=True,sag=sag))
            parts.append(stroke(slope_points(rear,ridge,sag)+slope_points(ridge,tip,sag)[1:],'#e4bb83',.7))
    elif kind=='temple-portico':
        parts.append(curled_hip(rear_left,ridge_left,left,sag,'#565357'))
        parts.append(curled_hip(rear_right,ridge_right,right,sag,'#464246'))
    elif shrine:
        parts.append(poly([rear_left,ridge_left,shifted(left,0,-2.5)],'#565357','#343138',.3))
        parts.append(poly([rear_right,ridge_right,shifted(right,0,-2.5)],'#454449','#343138',.3))
    if hipped:
        parts.append(panel(ridge_left,ridge_left,rear_left,left,'#5e5a59',False))
        parts.append(panel(ridge_right,ridge_right,right,rear_right,'#484448',True))
    parts.append(panel(ridge_left,ridge_right,left,right,front_tone,True,2.5 if shrine else 0,glazed,sag,tone=='smoke-tile',inked,aged))
    parts.append(stroke([ridge_left,ridge_right],'#e9c38b' if glazed else '#a7a199',.68 if glazed else .52))
    if aged:
        parts.append(stroke([ridge_left,ridge_right],'#494347',.86))
        count=max(1,round(math.dist(ridge_left,ridge_right)/3.2))
        for index in range(count):
            start=along(ridge_left,ridge_right,(index+.07)/count);end=along(ridge_left,ridge_right,(index+.71)/count)
            parts.append(stroke([start,end],'#262326' if index%5 in (1,2,4) else '#7c7877',1.03))
    if form and form.get('ridgeCaps'):
        for tip,sign in [(ridge_left,-1),(ridge_right,1)]:
            parts.append(stroke([shifted(tip,-sign*1.6,.1),tip,shifted(tip,sign*.55,-1.45)],'#363033',.96))
        parts.append(stroke([left,shifted(left,.5,.75),shifted(right,-.6,.55),right],'#302e30',.86))
        crest=along(ridge_left,ridge_right,.62)
        parts.append(stroke([shifted(crest,0,.2),shifted(crest,0,-1.45)],'#383136',.94))
        for peak,tip in [(ridge_left,left),(ridge_right,right)]:parts.append(stroke(slope_points(peak,tip,sag),'#383539',.62))
    curl=1.65 if shrine else .35
    if not shrine:
        parts.append(stroke([shifted(left,-.6,-curl),left,right,shifted(right,.6,-curl)],'#373338',.7))
        parts.append(stroke([shifted(left,0,.49),shifted(right,0,.49)],'#9a8b7b',.25))
    if shrine:
        for tip,sign in [(ridge_left,-1),(ridge_right,1)]:
            parts.append(stroke([tip,shifted(tip,sign*1.1,-.48),shifted(tip,sign*1.65,-1.55)],'#987446' if glazed else '#625852',.59))
    if kind=='gable':
        front,crest,rear=near_gable
        parts.append(poly(verge+[shifted(point,0,.85) for point in reversed(verge)],'#eeeae0','#78736d',.22))
        parts.append(stroke(verge,'#514f50',.46))
        if form and form.get('endFace')=='limewash' and form.get('support')!='water-piers':
            base=[shifted(front,0,height-.17),shifted(rear,0,height-.17)]
            if form.get('baseTrim')!='lime-wash':
                parts.append(stroke([shifted(point,0,-.52) for point in base],'#b1aaa0',.85))
                parts.append(stroke(base,'#5f5a53',.88))
            for corner in [front,rear]:parts.append(stroke([shifted(corner,0,1.0),shifted(corner,0,height-.72)],'#77746f',.55))
            parts.append(stroke([shifted(point,0,.68) for point in verge],'#e8e7df',.94))
            if aged:
                for start,end in ((front,crest),(crest,rear)):
                    count=max(2,round(math.dist(start,end)/1.7))
                    for index in range(count):
                        tip=roof_slope(start,end,(index+.17)/count,sag);foot=roof_slope(start,end,(index+.73)/count,sag)
                        parts.append(stroke([shifted(tip,0,-.17),shifted(foot,0,.06)],'#3e393b' if index%4 else '#918c88',.78))
            for corner in [front,rear]:parts.append(stroke([shifted(corner,0,.4),shifted(corner,0,1.35)],'#605c59',.5))
        elif not (form and form.get('support')=='water-piers'):
            mid=along(front,rear,.5);half=min(1.05,abs(depth_x)*.12);level=mid[1]+height*.46
            parts.append(poly([(mid[0]-half,level),(mid[0],level-.78),(mid[0]+half,level),(mid[0],level+.78)],'#746e64','#a59d8f',.18))
    return walls,''.join(parts)


def wall(points,height,cap=.87,skirting=0):
    parts=[]
    for start,end in zip(points,points[1:]):
        parts.append(poly([start,end,shifted(end,0,height),shifted(start,0,height)],'#e5e1d6','#aaa399',.22))
        parts.append(stroke([start,end],'#656160',cap))
        parts.append(stroke([shifted(start,0,-.4),shifted(end,0,-.4)],'#a9a39a',.26))
        if skirting:parts.append(stroke([shifted(start,0,height-.2),shifted(end,0,height-.2)],'#68635e',skirting))
        if cap>1.3:
            length=math.dist(start,end);count=max(1,round(length/1.3));across=(-(end[1]-start[1])/length,(end[0]-start[0])/length)
            for index in range(count):
                center=along(start,end,(index+.5)/count)
                parts.append(stroke([shifted(center,-across[0]*cap*.42,-across[1]*cap*.42),shifted(center,across[0]*cap*.42,across[1]*cap*.42)],'#918a80',.22))
    return ''.join(parts)


def screen_wall(model):
    left,right=model['beam'];height=model['height'];parts=[wall([left,right],height,1.15)]
    for start,end in model['bays']:
        jamb=along(left,right,start);stop=along(left,right,end);sill=height*.89
        parts.append(poly([shifted(jamb,0,1.6),shifted(stop,0,1.6),shifted(stop,0,sill),shifted(jamb,0,sill)],'#674e43','#89766b',.37))
        parts.append(stroke([shifted(along(jamb,stop,.5),0,1.9),shifted(along(jamb,stop,.5),0,sill)],'#483f39',.47))
    return ''.join(parts)


def eave_end(detail):
    parts=[]
    for coping in detail.get('coping',[]):
        parts.append(stroke([shifted(point,0,.42) for point in coping],'#554f4a',1.32))
        parts.append(stroke(coping,'#ece8dd',.82))
    if 'gableHead' in detail:
        foot,crest,tip=detail['gableHead']
        parts.append(poly([foot,crest,tip],'#e7e2d7','#524b46',.52))
        parts.append(stroke([shifted(foot,0,-.45),shifted(crest,0,-.6),shifted(tip,0,-.45)],'#635e59',.71))
        parts.append(stroke([shifted(crest,0,1.0),along(foot,tip,.50)],'#b9afa2',.37))
    for upper,lower in detail.get('tileLips',[]):
        parts.append(poly(upper+lower[::-1],'#545052','#403d3f',.28))
        for start,end,foot,tip in zip(upper,upper[1:],lower,lower[1:]):
            count=max(1,round(math.dist(foot,tip)/1.1))
            for index in range(count):
                fraction=(index+.5)/count
                parts.append(stroke([along(start,end,fraction),along(foot,tip,fraction)],'#77716e',.24))
        parts.append(stroke(lower,'#393638',.42))
    for frame in detail.get('timber',[]):
        parts.append(stroke(frame,'#51453d',.87))
        parts.append(stroke([shifted(point,.18,-.21) for point in frame],'#967e67',.22))
    return ''.join(parts)


def visible_eaves(group,features):
    prefix=group['id'];rings=group['replace'];houses=group['houses']
    points=[point for ring in rings for point in ring]
    left=min(x for x,y in points);right=max(x for x,y in points);top=min(y for x,y in points);bottom=max(y for x,y in points)
    roofs=[];timber=[];ink=[];defs=[];outlines=[]
    for feature in features:
        sx,sy,width,height=feature['bounds']
        if sx>=right or sy>=bottom or sx+width<=left or sy+height<=top:continue
        if feature['kind']=='wood':
            timber.append(render_surface(dict(feature,id=prefix+'-'+feature['id'])));continue
        if feature['kind']!='roof':continue
        center=(sx+width/2,sy+height/2)
        def distance(model):
            start_x,start_y,end_x,end_y=model[:4];dx=end_x-start_x;dy=end_y-start_y
            fraction=max(0,min(1,((center[0]-start_x)*dx+(center[1]-start_y)*dy)/(dx*dx+dy*dy)))
            return math.hypot(center[0]-start_x-fraction*dx,center[1]-start_y-fraction*dy)
        model=min(houses,key=distance);angle=math.degrees(math.atan2(model[3]-model[1],model[2]-model[0]))
        key=prefix+'-'+feature['id'];contour=path_shape(feature);color='#'+''.join(f'{channel:02x}' for channel in slate(feature))
        defs.append(f'<pattern id="{key}-tiles" width="1.3" height="2.3" patternUnits="userSpaceOnUse" patternTransform="rotate({angle:.2f})"><rect width="1.3" height="2.3" fill="{color}"/><path d="M.24 0v2.3M.3 1.15h1" stroke="#343237" stroke-width=".22"/><path d="M.67 0v2.3" stroke="#a8a39c" stroke-width=".16"/></pattern>')
        roofs.append(path(contour,f'url(#{key}-tiles)','#49454a',.26,'fill-rule="evenodd"'))
        outlines.append(f'<path d="{contour}" clip-rule="evenodd"/>')
        observation=feature.get('streetObservation',{})
        for seam in observation.get('ink',[]):ink.append(stroke(seam,'#373238',.47))
        for ridge in feature['finishing'].get('observedRoofMarks',[]):ink.append(stroke(ridge,'#ada79d',.32))
        timber.append(timber_facings(feature,prefix))
    roof_clip=prefix+'-roof-outline';scope=prefix+'-extent'
    defs.append(f'<clipPath id="{scope}">'+''.join(poly(ring,'white') for ring in rings)+'</clipPath>')
    defs.append(f'<clipPath id="{roof_clip}">'+''.join(outlines)+'</clipPath>')
    return '<defs>'+''.join(defs)+'</defs>'+f'<g clip-path="url(#{scope})">'+''.join(roofs)+f'<g clip-path="url(#{roof_clip})">'+''.join(ink)+'</g>'+''.join(timber)+'</g>'


def stone_platform(model):
    rim=model['rim'];drop=model['rise'];parts=[poly([shifted(point,0,drop) for point in rim],'#b0aaa0','#8e8a82',.32),poly(rim,'#e5e2d9','#aaa69d',.32)]
    back_left,back_right,front_right,front_left=model['flight'];steps=model['steps']
    for level in range(steps):
        start=along(back_left,front_left,level/steps);end=along(back_right,front_right,level/steps)
        foot=along(back_left,front_left,(level+1)/steps);tip=along(back_right,front_right,(level+1)/steps)
        parts.append(poly([start,end,tip,foot],'#e4e0d6','#b0aaa0',.22))
        parts.append(stroke([foot,tip],'#938e85',.42))
    return f'<g data-stair-treads="{steps}">'+''.join(parts)+'</g>'


def gate_terrace(model):
    deck=model['deck'];crest=model['merlons'];base=model['foot'];left,right=model['opening'];height=model['openingHeight']
    parts=[poly(deck,'#dad7d3','#76716c',.66)]
    for near,far in model['sideRails']:
        parts.append(stroke([shifted(near,0,-.8),shifted(far,0,-.8)],'#a39d98',.64))
        for index in range(6):
            foot=along(near,far,index/5);head=shifted(foot,-.18,-1.7)
            parts.extend([stroke([foot,head],'#5e5856',.72),stroke([shifted(head,-.4,0),shifted(head,.45,0)],'#89837d',.5)])
    for left_joint,right_joint in model['deckSeams']:parts.append(stroke([left_joint,right_joint],'#bcb6af',.38))
    parts.extend([poly(crest+base[::-1],'#d9d7d4','#615b58',.7),stroke(crest,'#656062',.96)])
    for start,end in zip(crest,crest[1:]):
        if end[0]-start[0]>1.4:parts.append(stroke([shifted(start,.1,.76),shifted(end,-.25,.76)],'#efebe4',.45))
    for index,(start,end) in enumerate(model['joints']):
        parts.append(stroke([start,end],'#777174' if index%3 else '#98918c',.75))
        parts.append(stroke([shifted(start,0,.68),shifted(end,0,.68)],'#eae6df',.45))
    parts.append(poly([left,right,shifted(right,0,height),shifted(left,0,height)],'#c4beb2','#4e4948',.8))
    parts.append(poly([shifted(left,-.8,-1.8),shifted(right,.7,-1.8),shifted(right,1,.7),shifted(left,-1,.7)],'#474144','#3b3838',.4))
    for down in (.41,.75):parts.append(stroke([shifted(left,.5,height*down),shifted(right,-.35,height*down)],'#a1998c',.5))
    plaque=model['plaque'];parts.extend([poly(plaque,'#716969','#403b3b',.5),stroke([along(plaque[0],plaque[3],.53),along(plaque[1],plaque[2],.53)],'#d6d1c7',.56)])
    return '<g data-masonry="gate-parapet">'+''.join(parts)+'</g>'


def detail_body(groups,features):
    parts=[]
    by_id={feature['id']:feature for feature in features}
    for group in groups:
        parts.append(f'<g id="{group["id"]}">')
        measured=''
        if 'slateOutlines' in group:
            key=group['id']+'-measured-slate'
            outlines=''.join(poly(by_id[surface]['points'],'white') for surface in group['slateOutlines'])
            parts.append(f'<defs><clipPath id="{key}">{outlines}</clipPath></defs>');measured=f' clip-path="url(#{key})"'
        marks_id=group['id']+'-tile-accents'
        if 'surfaceFinish' in group:
            accents=[]
            for source in group['surfaceFinish']:
                feature=by_id[source];gold=feature['kind']=='gold';study=feature.get('streetObservation',{})
                accents.extend(path('M'+'L'.join(f'{x},{y}' for x,y in ring)+'Z','#322c30',extra='opacity=".16"') for ring in study.get('shade',[]))
                accents.extend(stroke(seam,'#3f3739',.61) for seam in study.get('ink',[]))
                for seam in feature['finishing']['observedRoofMarks']:
                    accents.append(stroke([shifted(point,0,.4) for point in seam],'#6c442c' if gold else '#403c3d',.67))
                    accents.append(stroke(seam,'#e1ba86' if gold else '#aea99e',.38))
            parts.append(f'<defs><g id="{marks_id}">'+''.join(accents)+'</g></defs>')
        if group.get('visibleOnly'):
            key=group['id']+'-visible'
            parts.append(f'<defs><clipPath id="{key}">'+''.join(poly(ring,'white') for ring in group['replace'])+f'</clipPath></defs><g clip-path="url(#{key})">')
        paving='#e6e2d7'
        if 'courtFinish' in group:
            lawn=group['courtFinish']=='garden-lawn';key=group['id']+'-court-finish';paving=f'url(#{key})'
            tiles='<rect width="19" height="12" fill="#b9cb9e"/><path d="M2 9l1.5-.65m2.8-4.1 1.3.2m6.3 2.8 1.1-.55m1.1 5 .9-.3" stroke="#aebf91" stroke-width=".28"/>' if lawn else '<rect width="19" height="12" fill="#e6e3dd"/><path d="M0 0h19M0 6h19M7 0v6M15 6v6" stroke="#d7d2ca" stroke-width=".3"/>'
            parts.append(f'<defs><pattern id="{key}" patternUnits="userSpaceOnUse" width="19" height="12">{tiles}</pattern></defs>')
        if 'pavingAngle' in group:
            key=group['id']+'-setts';paving=f'url(#{key})'
            parts.append(f'<defs><pattern id="{key}" width="8.5" height="4.8" patternUnits="userSpaceOnUse" patternTransform="rotate({group["pavingAngle"]})"><rect width="8.5" height="4.8" fill="#e2dccc"/><path d="M0 .2h8.5M0 2.5h8.5M2.6 .2v2.3m4.7 0v2.3" fill="none" stroke="#b6b09c" stroke-width=".22"/><path d="M.7 2.1h1.2m3.3 2.2h1.6" stroke="#eee9da" stroke-width=".28"/></pattern></defs>')
        for court in group.get('courts',[]):
            parts.append(poly(court,paving,'#b8b2a7',.38))
        for segment in group.get('walls',[]):parts.append(wall(*segment))
        for screen in group.get('screens',[]):parts.append(screen_wall(screen))
        for platform in group.get('platforms',[]):parts.append(stone_platform(platform))
        if 'gateTerrace' in group:parts.append(gate_terrace(group['gateTerrace']))
        if group.get('retainObservedSurfaces',True):parts.append(visible_eaves(group,features))
        for index,model in enumerate(group['houses']):
            form=group.get('roofForms',{}).get(str(index));walls,roof=house(model,group.get('roofTones',{}).get(str(index)),form,group.get('frontFrames',{}).get(str(index)));key=f'{group["id"]}-roof-{index}'
            finish=eave_end(group.get('eaveEnds',{}).get(str(index),{}))
            roof_layer=f'<g id="{key}">{roof}</g>'
            if 'surfaceFinish' in group:
                face_id=key+'-planes'
                faces=roof_faces(model,roof_frame(model,form),form)
                parts.append(f'<defs><clipPath id="{face_id}">'+''.join(poly(face,'white') for face in faces)+'</clipPath></defs>')
                roof_layer+=f'<g clip-path="url(#{face_id})"><use href="#{marks_id}"/></g>'
            if measured:roof_layer=f'<g{measured}>{roof_layer}</g>'
            if form and 'clerestory' in form:
                aperture=key+'-clerestory';points=roof_frame(model,form)
                left=min(x for x,y in points)-4;top=min(y for x,y in points)-4
                area=f'x="{left}" y="{top}" width="{max(x for x,y in points)+4-left}" height="{max(y for x,y in points)+4-top}"'
                parts.append(f'<defs><mask id="{aperture}" maskUnits="userSpaceOnUse" {area}><rect {area} fill="white"/>'+poly(form['clerestory'],'black')+'</mask></defs>')
                roof_layer=f'<g mask="url(#{aperture})">{roof_layer}</g>'
            parts.append(f'<g data-front="{model[-1]}">{walls}{roof_layer}{finish}</g>')
        if group.get('visibleOnly'):parts.append('</g>')
        parts.append('</g>')
    return ''.join(parts)


def replace_traces(body,box,groups):
    left,top,right,bottom=box
    overlaps=[ring for group in groups for ring in group['replace'] if overlaps_box(ring,box)]
    if not overlaps:return body
    masks=''.join(poly(ring,'black') for ring in overlaps)
    area=f'x="{left}" y="{top}" width="{right-left}" height="{bottom-top}"'
    return f'<defs><mask id="street-cut" maskUnits="userSpaceOnUse" {area}><rect {area} fill="white"/>{masks}</mask></defs><g mask="url(#street-cut)">{body}</g>'
