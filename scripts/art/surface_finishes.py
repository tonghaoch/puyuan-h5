"""Fine material treatment within source contours. Coordinates and source voids remain unchanged."""
import math
from .native_roofs import facade, planes, slate
from .nw_court_roofs import COURTS, court_roof

PROFILES = {
 'north-watchtower': ('石台与门楼', '#d2d1bd', '#76816f', 'stone'),
 'fuma-residence': ('院落木构与窗棂', '#70513a', '#c4ae80', 'lattice'),
 'zen-gallery': ('深色立面与檐口', '#62584c', '#9d9c86', 'panel'),
 'designer-quarter': ('纵向屋脊与檐边', '#526258', '#a8b5a0', 'seam'),
 'xiangyun-temple': ('斜向院落与木柱', '#78553a', '#c7ab73', 'bracket'),
 'merchant-hall': ('会馆门窗与木饰面', '#705039', '#cbb482', 'lattice'),
 'meijing-theater': ('戏台檐口与窗格', '#745641', '#cbb27d', 'lattice'),
 'night-dining': ('街铺门楣与木门', '#84603f', '#cab17b', 'shop'),
 'storytelling-house': ('书场栏杆与木格', '#75553b', '#c9ae76', 'baluster'),
 'dayou-bridge-quarter': ('桥头石基与墙脚', '#a5aa95', '#dfdcc4', 'stone'),
 'pu-family-residence': ('宅院窗格与墙脚', '#775b40', '#c9b384', 'lattice'),
 'dressing-house': ('木楼分层与窗门', '#83553d', '#c9a675', 'baluster'),
 'longwan-dining': ('临水店铺与门楣', '#80583b', '#cbb17c', 'shop'),
 'food-center': ('排屋檐口与门窗', '#7a5a3f', '#c7b183', 'shop'),
}

def poly_path(points): return 'M'+'L'.join(f'{x:.3f},{y:.3f}' for x,y in points)+'Z'
def path_shape(f):return poly_path(f['points'])+''.join(poly_path(hole) for hole in f['holes'])


def sampled_shape(feature,paint):
    return (f'<path d="{path_shape(feature)}" transform="translate(.5 .5)" fill="{paint}" fill-rule="evenodd" '
            f'stroke="{paint}" stroke-width="1" stroke-linejoin="round"/>')


def sample_footprint(feature):
    """The tracer records indices of perimeter samples, not their outer cell edges."""
    horizontal,vertical,width,height=feature['bounds']
    area=f'x="{horizontal}" y="{vertical}" width="{width}" height="{height}"'
    mask=(f'<mask id="finish-{feature["id"]}" maskUnits="userSpaceOnUse" {area}>'
          +sampled_shape(feature,'white')+'</mask>')
    return mask,area


def timber_facings(feature,prefix):
    panels=feature.get('streetObservation',{}).get('timber',[])
    if not panels:return ''
    key=prefix+'-timber-'+feature['id']
    material=f'<defs><pattern id="{key}" width="5.1" height="3.6" patternUnits="userSpaceOnUse"><rect width="5.1" height="3.6" fill="#745145"/><path d="M.4 0v3.6M1.9 .25h2.5v2.05H1.9Z" fill="#5a4039" stroke="#493c37" stroke-width=".28"/><path d="M3.12 .35V2.1M1.9 1.24h2.5M.82 0v3.6" stroke="#b0987f" stroke-width=".2"/></pattern></defs>'
    return material+''.join(sampled_shape(panel,f'url(#{key})') for panel in panels)
def stroke(points,color,width=.25,opacity=1):
    return '<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>'
def color(rgb):return '#'+''.join(f'{int(max(0,min(255,c))):02x}' for c in rgb)

def roof_folds(f):
    # These two long ridges are visible in the source; retain the distinct paired slopes.
    folds={
        'roof-987': ([(1327,513),(1341,505),(1341,578),(1327,592)],[(1341,505),(1357,512),(1357,592),(1341,578)],[(1341,509),(1341,577)]),
        'roof-975': ([(1299,534),(1311,528),(1311,582),(1299,590)],[(1311,528),(1325,535),(1325,590),(1311,582)],[(1311,534),(1311,580)]),
    }
    item=folds.get(f['id']) if f['owner']=='designer-quarter' and f['kind']=='roof' else None
    if item is None:return ''
    left,right,ridge=item
    return (f'<path d="{poly_path(left)}" fill="#bac4ac" opacity=".14"/>'
            +f'<path d="{poly_path(right)}" fill="#183127" opacity=".17"/>'
            +stroke(ridge,'#293b31',.8,.85)
            +stroke([(x-.5,y) for x,y in ridge],'#b4bda3',.28,.6))

def render_surface(f):
    if f['id'] in ('roof-973','wood-634','wood-630','wood-629','wood-619') and not f.get('nwRawFront'):
        from .nw_frontage_owner import owned_surface
        from .nw_pool_fronts import FRAMES
        return owned_surface(f, render_surface, FRAMES)
    key=f['id'];kind=f['kind'];x,y,w,h=f['bounds'];angle=f['angle'];source=f['color']
    profile=PROFILES.get(f['owner'],('街巷瓦木细节','#775b43','#c2ad80','lattice'))
    lum=sum(source)/3
    if kind=='roof':base=color(slate(f));edge='#3b383a';light='#b0a9a0'
    elif kind=='gold':base='#b08645';edge='#77582e';light='#e1c17d'
    elif kind=='wood':base=color([source[0]*.75+20,source[1]*.70+17,source[2]*.65+14]);edge='#514539';light=profile[2]
    elif kind=='glass':base='#b8d1c8';edge='#6a9088';light='#ebf0e2'
    else:base=color([lum*.44+127,lum*.44+123,lum*.42+111]);edge='#a4aa95';light='#f8f3e3'
    footprint,area=sample_footprint(f)
    defs=[footprint,f'<linearGradient id="finish-shade-{key}" x1="0" y1="0" x2=".25" y2="1"><stop stop-color="#fff5d5" stop-opacity=".16"/><stop offset=".55" stop-color="#e1e4ce" stop-opacity="0"/><stop offset="1" stop-color="#19352a" stop-opacity=".18"/></linearGradient>']
    if kind in ['roof','gold']:
        texture=f'<path d="M.24 0V3.4" stroke="{light}" stroke-width=".22" opacity=".55"/><path d="M1.5 0V3.4M0 1.7H1.9" stroke="{edge}" stroke-width=".24" opacity=".66"/><path d="M.7 1.7q.32 .42 .65 0" fill="none" stroke="{light}" stroke-width=".12" opacity=".5"/>'
        tw,th=1.9,3.4
    elif kind=='wood':
        texture=f'<path d="M0 2.2H4.4m-.8-2.2v4.4" stroke="{edge}" stroke-width=".24"/><path d="M0 2.5H4.4" stroke="{light}" stroke-width=".14" opacity=".48"/>'
        tw,th=4.4,4.4
        angle=angle%180
        if angle>90:angle-=180
        if abs(angle)>45:angle=0
    elif kind=='glass':
        texture=f'<path d="M0 0H4V5H0Z" fill="none" stroke="{edge}" stroke-width=".32"/><path d="M.5 1 3.2 4.1" stroke="{light}" stroke-width=".28" opacity=".6"/>'
        tw,th=4,5
    else:
        texture='<path d="M0 2H7m-2-2v2m-3 0v2" stroke="#b6baa6" stroke-width=".13" opacity=".35"/>'
        tw,th=7,4;angle=0
    defs.append(f'<pattern id="finish-tile-{key}" width="{tw}" height="{th}" patternUnits="userSpaceOnUse" patternTransform="rotate({angle} {x} {y})">{texture}</pattern>')
    p=['<defs>'+''.join(defs)+'</defs>']
    p.append(facade(f))
    if kind in ['roof','gold']:
        p.append(f'<g transform="translate(.35 .65)"><rect {area} mask="url(#finish-{key})" fill="#253e32" opacity=".18"/></g>')
    p.append(f'<g mask="url(#finish-{key})"><rect {area} fill="{base}"/>')
    observed=f.get('finishing',{})
    for patch in observed.get('sourceRelief',{}).get('tones',[]):
        level=patch['level'];tone='#14251e' if level<0 else '#e6dfc3'
        opacity=(.065 if abs(level)==1 else .13) if kind in ['roof','gold'] else (.10 if abs(level)==1 else .22)
        if level==-3:opacity=.44
        outline=poly_path(patch['points'])+''.join(poly_path(hole) for hole in patch['holes'])
        p.append(f'<path d="{outline}" fill="{tone}" opacity="{opacity}" fill-rule="evenodd"/>')
    texture_opacity=.36 if kind in ['roof','gold'] else .32
    p.append(f'<rect {area} fill="url(#finish-tile-{key})" opacity="{texture_opacity}"/>')
    p.append(f'<rect {area} fill="url(#finish-shade-{key})"/>')
    p.append(court_roof(f) if key in COURTS else planes(f))
    study=f.get('streetObservation',{})
    for points in study.get('ink',observed.get('sourceRelief',{}).get('seams',[])):
        p.append(stroke(points,edge,.43,.78))
        p.append(stroke([(a+.5,b+.25) for a,b in points],light,.2,.4))
    if kind in ['roof','gold']:
        for patch in study.get('shade',observed.get('sourceShadePatches',[])):
            p.append(f'<path d="{poly_path(patch)}" fill="#28242a" opacity=".28"/>')
        for points in observed.get('observedRoofMarks',[]):
            p.append(stroke([(a+.18,b+.28) for a,b in points],edge,.75,.45))
            p.append(stroke(points,light,.3,.62))
        for a,b in zip(f['points'],f['points'][1:]+f['points'][:1]):
            length=math.dist(a,b)
            if length<5:continue
            if (a[1]+b[1])/2<y+h*.45:p.append(stroke([a,b],light,.32,.7))
            if (a[1]+b[1])/2>y+h*.62 and abs(a[1]-b[1])<abs(a[0]-b[0])*.65:
                p.append(stroke([a,b],edge,.65,.6))
                ux,uy=(b[0]-a[0])/length,(b[1]-a[1])/length
                for i in range(1,int(length/1.6)):
                    cx=a[0]+ux*i*1.6;cy=a[1]+uy*i*1.6
                    p.append(f'<path d="M{cx-.45:.2f} {cy-.4:.2f}q.45 .55 .9 0" fill="none" stroke="{light}" stroke-width=".18" opacity=".85"/>')
    elif kind=='wall':
        # Narrow visible faces get a stone plinth; broad white plazas do not get fake windows.
        if min(w,h)<22 and f['area']>20:
            p.append(f'<rect x="{x}" y="{y+h-1.6}" width="{w}" height="1.6" fill="#87927b" opacity=".16"/>')
            p.append(stroke([(x,y+h-1.6),(x+w,y+h-1.6)],'#b6baa1',.3,.6))
    elif kind=='wood' and w>=7 and 3<=h<=24 and f['area']>18:
        # Fine panel joints and brackets sit only within the observed timber face.
        mode=profile[3]
        if mode in ['lattice','shop','baluster','bracket']:
            for xx in range(x+2,x+w,5):
                p.append(stroke([(xx,y+.8),(xx,y+h-.5)],'#443e31',.45,.65))
                p.append(stroke([(xx+.4,y+1),(xx+.4,y+h-.6)],light,.18,.4))
            p.append(stroke([(x,y+1.1),(x+w,y+1.1)],light,.5,.5))
            p.append(stroke([(x,y+h*.68),(x+w,y+h*.68)],'#443b2e',.4,.65))
            if mode=='lattice':
                for xx in range(x,x+w,5):
                    for yy in range(y+2,y+h-1,4):
                        p.append(stroke([(xx,yy+1.5),(xx+1.8,yy),(xx+3.6,yy+1.5),(xx+1.8,yy+3),(xx,yy+1.5)],light,.14,.35))
            if mode=='bracket':
                for xx in range(x+2,x+w,6):
                    p.append(f'<path d="M{xx-1.2} {y+1.7}h2.4m-1.8 .7h1.2" fill="none" stroke="{light}" stroke-width=".25" opacity=".6"/>')
        elif mode=='panel':
            for yy in range(y+1,y+h,2):p.append(stroke([(x,yy),(x+w,yy)],'#b2a58a',.16,.35))
    p.append('</g>')
    p.append(timber_facings(f,'surface'))
    for opening in observed.get('observedOpenings',[]):
        points=opening['points'];hx,hy,hw,hh=opening['bounds'];outline=poly_path(points)
        p.append(f'<path d="{outline}" fill="none" stroke="#aaa78c" stroke-width=".7"/>')
        p.append(f'<path d="{outline}" fill="none" stroke="#59604b" stroke-width=".3"/>')
        p.append(stroke([(hx+hw*.5,hy+.8),(hx+hw*.5,hy+hh-.8)],'#b7b28d',.25,.7))
    return ''.join(p)
