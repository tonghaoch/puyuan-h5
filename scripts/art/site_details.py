"""Site-specific visible forms, checked against the supplied map and first-party photographs."""

def poly(points,fill,stroke='#4a5147',width=.35):
    return '<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def line(points,color,width=.4):
    return '<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>'
def roof(points,key,angle=0,gold=False):
    base='#b78c45' if gold else '#48534f';light='#e0be76' if gold else '#929e91';dark='#795e33' if gold else '#293b33'
    pattern=f'<defs><linearGradient id="{key}-slope" x1="0" y1="0" x2=".18" y2="1"><stop stop-color="{light}" stop-opacity=".30"/><stop offset=".35" stop-color="{base}" stop-opacity="0"/><stop offset="1" stop-color="{dark}" stop-opacity=".55"/></linearGradient><pattern id="{key}" width="1.45" height="2.8" patternUnits="userSpaceOnUse" patternTransform="rotate({angle})"><path d="M.25 0V2.8" stroke="{light}" stroke-width=".16" opacity=".55"/><path d="M1.2 0V2.8M0 1.4H1.45" stroke="{dark}" stroke-width=".14" opacity=".55"/></pattern></defs>'
    return pattern+poly(points,base,dark,.35)+poly(points,f'url(#{key}-slope)','none')+poly(points,f'url(#{key})',dark,.2)
def windows(x1,x2,y,height,step=7):
    out=[]
    for i,x in enumerate(range(int(x1),int(x2),step)):
        out.append(poly([(x,y),(x+step-1,y),(x+step-1,y+height),(x,y+height)],'#72553e','#493d32',.3))
        out.append(poly([(x+.7,y+height*.60),(x+step-1.7,y+height*.60),(x+step-1.7,y+height-.8),(x+.7,y+height-.8)],'#8d6847','#5c4633',.18))
        out.append(poly([(x+.8,y+1),(x+step-1.8,y+1),(x+step-1.8,y+height*.53),(x+.8,y+height*.53)],'#4a5143','#b09b70',.2))
        for t in [.32,.66]:
            xx=x+.8+(step-2.6)*t
            out.append(line([(xx,y+1),(xx,y+height*.53)],'#b6a276',.16))
        out.append(line([(x+.8,y+height*.28),(x+step-1.8,y+height*.28)],'#b6a276',.16))
        out.append(line([(x+step-1,y),(x+step-1,y+height)],'#b28c5e',.32))
    return ''.join(out)

def between(start,end,fraction):
    return tuple(first+(last-first)*fraction for first,last in zip(start,end))

def offset(point,delta):
    return (point[0]+delta[0],point[1]+delta[1])

def glazing(corners,fill,columns,rows,framed=False):
    upper_left,upper_right,lower_right,lower_left=corners
    def pane(across,down):
        return between(between(upper_left,upper_right,across),between(lower_left,lower_right,across),down)
    parts=[poly(corners,fill,'#516e70',.4)]
    for column in range(columns):
        for row in range(rows):
            if (column+2*row)%4==1:
                parts.append(poly([pane((column+.1)/columns,(row+.76)/rows),pane((column+.60)/columns,(row+.11)/rows),pane((column+.87)/columns,(row+.11)/rows),pane((column+.32)/columns,(row+.76)/rows)],'#dce8df','none'))
    for column in range(1,columns):
        parts.append(line([pane(column/columns,0),pane(column/columns,1)],'#3e525b' if framed else '#63868a',.78 if framed else .37))
    for row in range(1,rows):
        parts.append(line([pane(0,row/rows),pane(1,row/rows)],'#58717c' if framed else '#819ea0',.59 if framed else .29))
    parts.append(line([upper_left,upper_right],'#e4eadc',.48))
    return ''.join(parts)

def glass_hall(left,ridge,right,run,height,bays,long_lights=False):
    rear_left,rear_ridge,rear_right=[offset(point,run) for point in (left,ridge,right)]
    sill_left,sill_right=[offset(point,(0,height)) for point in (left,right)]
    parts=[glazing([rear_right,right,sill_right,offset(rear_right,(0,height))],'#8198a5',bays,2,True)]
    if long_lights:
        parts.append('<g data-part="east-glass-long-hall"><defs><linearGradient id="east-glass-light"><stop stop-color="#a8cbdc"/><stop offset=".6" stop-color="#bedee9"/><stop offset="1" stop-color="#96bac9"/></linearGradient><linearGradient id="east-glass-reflection"><stop stop-color="#a8c4d2"/><stop offset=".4" stop-color="#a1b5c3"/><stop offset="1" stop-color="#848793"/></linearGradient></defs>')
        def station(point,bay):return between(point,offset(point,run),bay/bays)
        parts.append(glazing([rear_left,left,sill_left,offset(sill_left,run)],'#97b5c5',bays,2,True))
        for low,pigment in [(left,'east-glass-light'),(right,'east-glass-reflection')]:
            parts.append(poly([offset(low,run),rear_ridge,ridge,low],f'url(#{pigment})','#647b89',.55))
            for across in (.32,.68):
                foot=between(low,ridge,across)
                parts.append(line([offset(foot,run),foot],'#93afbe',.42))
        for bay in range(1,bays):
            near,high,far=[station(point,bay) for point in (left,ridge,right)]
            parts.append('<g data-east-roof-bent="'+str(bay)+'">')
            parts.extend([line([near,high],'#81a1b2',.78),line([high,far],'#8999a6',.72),
                          line([offset(near,(0,-.55)),offset(high,(0,-.55))],'#d1e5eb',.46)])
            for point,shade in [(ridge,'#314b5d'),(right,'#54606f')]:
                tail,head=station(point,bay-.34),station(point,bay+.34)
                parts.extend([poly([offset(tail,(-.62,0)),offset(head,(-.62,0)),offset(head,(.78,.27)),offset(tail,(.78,.27))],shade,'none'),
                              line([offset(tail,(-.70,-.2)),offset(head,(-.70,-.2))],'#bad0da',.32)])
            parts.append('</g>')
        parts.extend([poly([left,ridge,right,sill_right,sill_left],'#aecbd7','#455c69',.68),'<g data-part="east-end-truss">'])
        for fraction in (.12,.28,.5,.61,.82,.97):
            head=between(left,ridge,fraction*2) if fraction<=.5 else between(ridge,right,fraction*2-1)
            parts.append(line([head,between(sill_left,sill_right,fraction)],'#506d79',.94 if fraction==.5 else .62))
        for level in (.42,.87):
            parts.append(line([between(left,sill_left,level),between(right,sill_right,level)],'#557382',.71))
        parts.extend([line([between(left,ridge,.65),between(ridge,right,.35)],'#64818d',.64),
                      line([left,right],'#536e7b',.86),line([sill_left,sill_right],'#3e5662',1.0),
                      line([left,ridge,right],'#394d59',1.03),'</g></g>'])
        return ''.join(parts)
    parts.extend([glazing([rear_left,rear_ridge,ridge,left],'#b1d3df',3,bays,True),
                  glazing([rear_ridge,rear_right,right,ridge],'#8faebf',3,bays,True)])
    parts.extend([glazing([left,right,sill_right,sill_left],'#a8c0ce',6,2,True),
                  poly([left,ridge,right],'#b1cdd7','#455c69',.65)])
    for index in range(1,6):
        fraction=index/6
        top=between(left,ridge,2*fraction) if fraction<=.5 else between(ridge,right,2*fraction-1)
        parts.append(line([top,between(left,right,fraction)],'#607b87',.57))
    jamb_left,jamb_right=between(left,right,.37),between(left,right,.63)
    parts.append(glazing([offset(jamb_left,(0,.6)),offset(jamb_right,(0,.6)),offset(jamb_right,(0,height)),offset(jamb_left,(0,height))],'#798f87',2,1))
    parts.extend([line([rear_ridge,ridge],'#deebed',.72),line([left,ridge,right],'#3e535c',.97),line([sill_left,sill_right],'#516069',.9)])
    return ''.join(parts)

def visitor():
    p=['<g id="visitor-glass-halls">']
    p.append(glass_hall((686.3,375.5),(690.5,371.3),(696.2,374.8),(-1.1,-8.6),2.7,3))
    p.append(glass_hall((790.1,388.65),(804.85,377.8),(819.8,385.8),(-9.15,-46.5),4.8,9,True))
    left,ridge,right=(697.1,405.6),(705.4,393.3),(716.7,403.2)
    sill_left,sill_right=(697.3,414.0),(716.7,411.8);run=(-3.6,-24.4)
    foot=[offset(sill_left,run),sill_left,sill_right];shade=offset(sill_left,(-6.3,-1.6))
    p.append('<g data-part="west-hall-shadow" opacity=".47">'+poly([offset(foot[0],(-5.1,-1.6)),foot[0],foot[1],foot[2],offset(foot[2],(-3,.7)),shade],'#6b6d79','none')+'</g>')
    cornice=[(715.6,397.0),(741.5,393.55)];transom=[(716.65,406.6),(743.05,402.8)];plinth=[(716.8,411.65),(743.3,407.55)]
    p.append('<g data-part="west-link-frame">'+glazing([(714.1,393.6),(739.4,390.7),cornice[1],cornice[0]],'#b6d3e2',5,1,True))
    p.append(glazing([*cornice,transom[1],transom[0]],'#bcdae6',3,1))
    p.append(poly([*transom,plinth[1],plinth[0]],'#b9d2dd','#556c78',.35))
    for level,depth in [(cornice,.67),(transom,.98),(plinth,.68)]:
        p.append(poly([*level,offset(level[1],(0,depth)),offset(level[0],(0,depth))],'#40535f','none'))
        p.append(line(level,'#506676',.57))
    for fraction in (0,.34,.65,1):
        head,foot=between(*transom,fraction),between(*plinth,fraction)
        p.append(line([head,foot],'#546874',.89))
    p.extend([line([cornice[1],transom[1],plinth[1]],'#4e6673',.91),'</g>'])
    p.append('<g data-part="west-glass-elevation">'+glazing([offset(left,run),left,sill_left,offset(sill_left,run)],'#789cae',5,2,True))
    for bay in range(6):
        post=between(offset(left,run),left,bay/5);p.append(line([post,offset(post,(0,8.2))],'#405461',.79))
    p.append(line([offset(sill_left,run),sill_left],'#364652',.9)+'</g>')
    for first,last,fill in [(left,ridge,'#a6c8d6'),(ridge,right,'#b5d7e5')]:
        rear_first=offset(first,run);rear_last=offset(last,run)
        p.append(glazing([rear_first,rear_last,last,first],fill,2,5,True))
    p.append('<g data-part="west-pitched-frames">')
    for bay in range(1,6):
        head=between(ridge,offset(ridge,run),bay/5)
        edge=between(left,offset(left,run),bay/5)
        far=between(right,offset(right,run),bay/5)
        p.extend([line([edge,head],'#4c687b',.85),line([head,far],'#7a98a9',.65),
                  line([offset(head,(0,-.48)),offset(edge,(0,-.48))],'#c5dae0',.38)])
    p.extend([line([offset(right,run),right],'#496879',.90),'</g>'])
    p.append(poly([left,ridge,right],'#adccd7','#344956',.97))
    for fraction in (.25,.51,.77):
        head=between(left,ridge,fraction*2) if fraction<.5 else between(ridge,right,fraction*2-1)
        p.append(line([head,between(left,right,fraction)],'#6a8693',.57))
    p.append(glazing([left,right,sill_right,sill_left],'#aecbd7',4,2,True))
    for fraction in (0,.37,.57,.79,1):
        head=between(left,right,fraction);foot=between(sill_left,sill_right,fraction)
        p.append(line([head,foot],'#364550',.98 if fraction in (0,1,.37) else .74))
    p.append(line([offset(sill_left,(0,-1.8)),offset(sill_right,(0,-1.8))],'#637481',.68))
    p.append(line([sill_left,left,ridge,offset(ridge,run)],'#334954',1.02))
    p.append(line([left,right,sill_right,sill_left],'#3e4f59',1.02))
    return ''.join(p)+'</g>'

DETAILS={'visitor-court':visitor}
