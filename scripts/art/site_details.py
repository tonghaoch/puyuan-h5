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

def glass_hall(left,ridge,right,run,height,bays):
    rear_left,rear_ridge,rear_right=[offset(point,run) for point in (left,ridge,right)]
    sill_left,sill_right=[offset(point,(0,height)) for point in (left,right)]
    parts=[glazing([rear_right,right,sill_right,offset(rear_right,(0,height))],'#8198a5',bays,2,True),
           glazing([rear_left,rear_ridge,ridge,left],'#b1d3df',3,bays,True),
           glazing([rear_ridge,rear_right,right,ridge],'#8faebf',3,bays,True),
           glazing([left,right,sill_right,sill_left],'#a8c0ce',6,2,True),
           poly([left,ridge,right],'#b1cdd7','#455c69',.65)]
    for index in range(1,6):
        fraction=index/6
        top=between(left,ridge,2*fraction) if fraction<=.5 else between(ridge,right,2*fraction-1)
        parts.append(line([top,between(left,right,fraction)],'#607b87',.57))
    jamb_left,jamb_right=between(left,right,.37),between(left,right,.63)
    parts.append(glazing([offset(jamb_left,(0,.6)),offset(jamb_right,(0,.6)),offset(jamb_right,(0,height)),offset(jamb_left,(0,height))],'#798f87',2,1))
    parts.extend([line([rear_ridge,ridge],'#deebed',.72),line([left,ridge,right],'#3e535c',.97),line([sill_left,sill_right],'#516069',.9)])
    return ''.join(parts)

def visitor():
    p=[]
    p.append(glass_hall((684,379),(690,373),(696,378),(-1,-10),4,3))
    p.append(glass_hall((790,389),(805,377),(820,387),(-4,-41),6,9))
    p.append(glazing([(714,395),(741,391),(744,403),(715,406)],'#b8d5df',6,3,True))
    p.append(glazing([(715,406),(744,403),(744,409),(715,412)],'#a3bdca',6,2,True))
    p.append(glass_hall((694,405),(705,394),(716,403),(-2,-24),8,6))
    return ''.join(p)

DETAILS={'visitor-court':visitor}
