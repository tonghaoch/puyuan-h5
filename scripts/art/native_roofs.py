"""Native roof volumes and articulated street elevations inside the authored town layout."""
import math
from .landscape import path, poly

def slate(feature):
    value=62+feature.get('streetObservation',{}).get('slate',2)*7
    return (value+3,value,value+1)

def volume_planes(f):
    faces=f.get('roofVolume',{}).get('faces',[])
    if not faces:return ''
    result=[]
    gold=f['kind']=='gold'
    base=(172,137,69) if gold else slate(f)
    for index,face in enumerate(faces):
        key=f'volume-{f["id"]}-{index}';shade=face['shade']
        rgb=[round(max(0,min(255,c+shade*(19 if gold else 11)))) for c in base]
        fill='#'+''.join(f'{c:02x}' for c in rgb)
        d='M'+'L'.join(f'{x},{y}' for x,y in face['points'])+'Z'
        d+=''.join('M'+'L'.join(f'{x},{y}' for x,y in hole)+'Z' for hole in face['holes'])
        light='#d2bc81' if gold else '#ada8a0';dark='#7f6537' if gold else '#37343a'
        result.append(f'<defs><pattern id="{key}" width="1.7" height="3.1" patternUnits="userSpaceOnUse" patternTransform="rotate({face["angle"]})"><path d="M.3 0V3.1" stroke="{light}" stroke-width=".16" opacity=".55"/><path d="M1.3 0V3.1M0 1.55H1.7" stroke="{dark}" stroke-width=".18" opacity=".6"/></pattern></defs>')
        result.append(path(d,fill,dark,.24,'fill-rule="evenodd"'))
        result.append(path(d,f'url(#{key})','none',.1,'fill-rule="evenodd"'))
    return ''.join(result)

def facade(f):
    if f['kind'] not in ['roof','gold'] or f['area']<28 or f.get('streetObservation',{}).get('plaster'):return ''
    x,y,w,h=f['bounds'];height=min(5.8,2.2+math.sqrt(f['area'])*.13)
    timber=f.get('facade')=='timber'
    wall='#896655' if timber else '#e9e5d9';shadow='#787369';frame='#696052'
    p=[]
    for a,b in zip(f['points'],f['points'][1:]+f['points'][:1]):
        length=math.dist(a,b)
        if length<7 or abs(a[1]-b[1])>abs(a[0]-b[0])*.48 or (a[1]+b[1])/2<y+h*.58:continue
        left,right=sorted([a,b]);xx,yy=left;rx,ry=right
        p.append(poly([left,right,(rx,ry+height),(xx,yy+height)],wall,shadow,.24))
        p.append(path(f'M{xx} {yy+.7}L{rx} {ry+.7}',stroke='#3d5947',width=.65,extra='opacity=".7"'))
        bays=max(1,int(length/5.5))
        for i in range(bays):
            t=(i+.5)/bays;cx=xx+(rx-xx)*t;cy=yy+(ry-yy)*t;ww=min(3.4,length/bays*.67)
            p.append(poly([(cx-ww/2,cy+1.3),(cx+ww/2,cy+1.3),(cx+ww/2,cy+height-.65),(cx-ww/2,cy+height-.65)],'#56694f',frame,.2))
            p.append(path(f'M{cx} {cy+1.4}v{height-2.15}',stroke='#b9b08a',width=.16))
            p.append(path(f'M{cx-ww/2} {cy+height*.58}h{ww}',stroke='#c6bc94',width=.17))
            p.append(path(f'M{cx-ww/2-.5} {cy+1}v{height-1}',stroke=frame,width=.35))
        p.append(path(f'M{xx} {yy+height}L{rx} {ry+height}',stroke='#b4b99b',width=.55))
    return ''.join(p)

def planes(f):
    compiled=volume_planes(f)
    if compiled:return compiled
    if f['kind'] not in ['roof','gold'] or f['area']<45:return ''
    x,y,w,h=f['bounds']
    # Compact roof footprints can carry a coherent pitched volume. Complex joined blocks
    # retain their authored contour and construction lines until split into separate roofs.
    if f['area']/(w*h)<.70 or any(len(hole)>4 for hole in f['holes']):return ''
    a=math.radians(f['angle']);u=(math.cos(a),math.sin(a));v=(-u[1],u[0])
    pu=[px*u[0]+py*u[1] for px,py in f['points']];pv=[px*v[0]+py*v[1] for px,py in f['points']]
    lo,hi=min(pu),max(pu);bottom,top=min(pv),max(pv);mid=(bottom+top)/2
    def point(p,q):return (u[0]*p+v[0]*q,u[1]*p+v[1]*q)
    light=[point(lo-2,bottom-2),point(hi+2,bottom-2),point(hi+2,mid),point(lo-2,mid)]
    dark=[point(lo-2,mid),point(hi+2,mid),point(hi+2,top+2),point(lo-2,top+2)]
    p=[poly(light,'#d1d2aa'),poly(dark,'#153e2e')]
    p=['<g opacity=".15">'+''.join(p)+'</g>']
    inset=min(4,(hi-lo)*.15);ra,rb=point(lo+inset,mid),point(hi-inset,mid)
    p.append(path(f'M{ra[0]:.2f} {ra[1]:.2f}L{rb[0]:.2f} {rb[1]:.2f}',stroke='#294b39',width=.7))
    p.append(path(f'M{ra[0]-.25:.2f} {ra[1]-.25:.2f}L{rb[0]-.25:.2f} {rb[1]-.25:.2f}',stroke='#bcc4a2',width=.27))
    return ''.join(p)
