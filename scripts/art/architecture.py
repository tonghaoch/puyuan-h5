"""Small deterministic 2.5D architecture drawing primitives, independent of map coordinates."""
import math
from xml.sax.saxutils import escape


def poly(points, fill, stroke='none', width=1, extra=''):
    coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    return f'<polygon points="{coords}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def line(points, stroke, width=1, extra=''):
    coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    return f'<polyline points="{coords}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def path(d, fill='none', stroke='none', width=1, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def ellipse(x,y,rx,ry,fill,extra=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def project(x, y, z=0):
    return x + y*.13, y*.60-z


def plane(x,y,w,d,z=0):
    return [project(x,y,z),project(x+w,y,z),project(x+w,y+d,z),project(x,y+d,z)]


def slab(x,y,w,d,height,fill='#d3c9ad'):
    return ''.join([
        poly(plane(x+6,y+6,w,d), '#6a6e53', extra='opacity=".12"'),
        poly([project(x,y+d),project(x+w,y+d),project(x+w,y+d,height),project(x,y+d,height)],'#b9af91'),
        poly([project(x+w,y),project(x+w,y+d),project(x+w,y+d,height),project(x+w,y,height)],'#a69e83'),
        poly(plane(x,y,w,d,height),fill,'#c9c1a6',.7),
    ])


def paving(x,y,w,d,spacing=15):
    p=[poly(plane(x,y,w,d),'#ddd5bb')]
    for i in range(1,int(d/spacing)):
        p.append(line([project(x,y+i*spacing),project(x+w,y+i*spacing)],'#bcb79f',.6,extra='opacity=".6"'))
    for i in range(1,int(w/spacing)):
        p.append(line([project(x+i*spacing,y),project(x+i*spacing,y+d)],'#bcb79f',.5,extra='opacity=".45"'))
    return ''.join(p)


def lantern(x,y,s=1):
    return f'<g transform="translate({x} {y}) scale({s})">'+line([(0,-8),(0,0)],'#82704b',1.2)+ellipse(0,7,5,7,'url(#lantern)')+line([(-3,1),(3,1)],'#e4c47d',1.2)+line([(-3,13),(3,13)],'#d9b469',1.2)+line([(0,14),(0,20)],'#c89e55',1)+path('M-2 2Q-4 7-2 12M2 2Q4 7 2 12',stroke='#edd798',width=.6)+'</g>'


def building(x,y,w,d,h=32,gold=False,glass=False,lanterns=False,base_z=0,timber=False):
    p=[]
    p3=lambda px,py,pz=0:project(px,py,pz+base_z)
    light='#a8b2a1' if not gold else '#d5ba74'
    dark='#314c47' if not gold else '#887040'
    roof_fill='url(#glassRoof)' if glass else 'url(#goldRoof)' if gold else 'url(#jadeRoof)'
    # Floor, plaster walls, wood beams, front and right elevations.
    p.append(poly(plane(x+8,y+8,w,d),'#4d604b',extra='opacity=".14"'))
    p.append(poly([p3(x,y+d),p3(x+w,y+d),p3(x+w,y+d,h),p3(x,y+d,h)], 'url(#timber)' if timber else 'url(#plaster)','#aaa085',.7))
    p.append(poly([p3(x+w,y),p3(x+w,y+d),p3(x+w,y+d,h),p3(x+w,y,h)], '#8f795c' if timber else '#b5b69a','#8e9b81',.7))
    for beam_h in [4,h-4]:
        p.append(line([p3(x,y+d,beam_h),p3(x+w,y+d,beam_h)],'#6b6550',2.2))
    bays=max(2,int(w/18))
    for i in range(bays):
        xx=x+(i+.5)*w/bays
        ww=w/bays*.67
        yy=y+d+.1
        p.append(poly([p3(xx-ww/2,yy,5),p3(xx+ww/2,yy,5),p3(xx+ww/2,yy,h-8),p3(xx-ww/2,yy,h-8)],'#657362','#605f48',.6))
        p.append(poly([p3(xx-ww/2+1.5,yy,8),p3(xx+ww/2-1.5,yy,8),p3(xx+ww/2-1.5,yy,h-10),p3(xx-ww/2+1.5,yy,h-10)], '#aea47b' if timber else '#aeb293'))
        for f in [0,.5,1]:
            wx=xx-ww/2+ww*f
            p.append(line([p3(wx,yy,7),p3(wx,yy,h-8)],'#646a50',.65))
        for f in [.35,.7]:
            p.append(line([p3(xx-ww/2,yy,5+(h-13)*f),p3(xx+ww/2,yy,5+(h-13)*f)],'#697155',.65))
        p.append(line([p3(x+i*w/bays,yy),p3(x+i*w/bays,yy,h)],'#8b7150',2))
        if i%2==0:
            # Bracket sets directly below eaves.
            bx,by=p3(xx,yy,h-2)
            p.append(path(f'M{bx-4} {by+2}h8m-6 2h4m-3 2h2',stroke='#a98e5d',width=1.2))
    for i in range(max(2,int(d/18))):
        yy=y+(i+.5)*d/max(2,int(d/18))
        p.append(line([p3(x+w,yy,6),p3(x+w,yy,h-7)],'#70795f',2))
    if glass:
        front='#b2cdc2'
        p.append(poly([p3(x,y+d,2),p3(x+w,y+d,2),p3(x+w,y+d,h),p3(x,y+d,h)],front,'#668b82',1))
        for i in range(1,bays*2):
            p.append(line([p3(x+i*w/(bays*2),y+d,2),p3(x+i*w/(bays*2),y+d,h)],'#6e968e',.7))
        p.append(line([p3(x,y+d,h*.5),p3(x+w,y+d,h*.5)],'#6e968e',.8))
    # Lifted hip roof. All buildings share one projection and sun direction.
    e=7
    a=p3(x-e,y-e,h+3)
    b=p3(x+w+e,y-e,h+3)
    c=p3(x+w+e,y+d+e,h+3)
    dd=p3(x-e,y+d+e,h+3)
    ridge_z=h+max(13,d*.27)
    r1=p3(x+w*.14,y+d*.5,ridge_z)
    r2=p3(x+w*.86,y+d*.5,ridge_z)
    p.append(poly([a,b,r2,r1], '#b8d0c3' if glass else '#799183' if not gold else '#b69b5d',dark,.7))
    p.append(poly([a,r1,dd], '#a4c4b8' if glass else '#5d7a6b' if not gold else '#bc9d5a',dark,.7))
    p.append(poly([b,c,r2],dark,dark,.7))
    p.append(poly([dd,c,r2,r1],roof_fill,dark,.8))
    # Distinct tile channels and overlapping rows follow the roof slopes.
    tile_count=max(10,int(w/4.5))
    for i in range(1,tile_count):
        t=i/tile_count
        start=(r1[0]+(r2[0]-r1[0])*t,r1[1]+(r2[1]-r1[1])*t)
        end=(dd[0]+(c[0]-dd[0])*t,dd[1]+(c[1]-dd[1])*t)
        p.append(line([start,end],light,.65,extra='opacity=".66"'))
        p.append(line([(start[0]+1,start[1]),(end[0]+1,end[1])],dark,.5,extra='opacity=".45"'))
    for i in range(1,7):
        t=i/7
        left=(r1[0]+(dd[0]-r1[0])*t,r1[1]+(dd[1]-r1[1])*t)
        right=(r2[0]+(c[0]-r2[0])*t,r2[1]+(c[1]-r2[1])*t)
        p.append(line([left,right],dark,.7,extra='opacity=".42"'))
    # Ridgeline, ornamental ridge ends and upturned eaves.
    p.append(line([a,r1,r2,b],light,1.8))
    p.append(path(f'M{dd[0]-3} {dd[1]-5}Q{dd[0]} {dd[1]+1} {dd[0]+8} {dd[1]+2}L{c[0]-8} {c[1]+2}Q{c[0]} {c[1]+1} {c[0]+3} {c[1]-6}',stroke=light,width=2))
    p.append(line([dd,c,b],dark,1.3))
    p.append(path(f'M{r1[0]-5} {r1[1]-6}Q{r1[0]-6} {r1[1]+1} {r1[0]+3} {r1[1]}L{r2[0]-3} {r2[1]}Q{r2[0]+6} {r2[1]} {r2[0]+5} {r2[1]-6}',stroke='#cbbd8c' if gold else '#b8c0a3',width=2.2))
    for t in [.13,.2,.8,.87]:
        xx=r1[0]+(r2[0]-r1[0])*t; yy=r1[1]+(r2[1]-r1[1])*t
        p.append(path(f'M{xx-2} {yy}v-3q3-4 4 0v3',fill=light))
    if lanterns:
        for frac in [.15,.85]:
            xx,yy=p3(x+w*frac,y+d+2,h-5)
            p.append(lantern(xx,yy,.65))
    return ''.join(p)


def pine(x,y,s=1):
    p=[f'<g transform="translate({x} {y}) scale({s})">',ellipse(5,3,17,5,'#61704b',extra='opacity=".14"'),path('M0 0 2-36m-1 18-12-10m13 4 12-10',stroke='#8d7955',width=3)]
    for cx,cy,r in [(-8,-27,11),(8,-35,12),(-2,-43,10),(0,-51,7)]:
        p.append(path(f'M{cx-r} {cy}q0-9 {r*.7}-8q6-7 {r*.9} 0q{r*.8} 0 {r*.5} 8q-8 5-15 2q-8 4-{r*.1} -2Z',fill='#7c9771',stroke='#708963',width=.5))
        p.append(path(f'M{cx-r+4} {cy-1}q{r*.5}-5 {r} -2',stroke='#a6b68b',width=1))
    return ''.join(p)+'</g>'


def wrap(width,height,body,title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><defs>
<linearGradient id="jadeRoof" x2="0.2" y2="1"><stop stop-color="#6c8878"/><stop offset=".45" stop-color="#4e6d60"/><stop offset="1" stop-color="#3a574e"/></linearGradient>
<linearGradient id="goldRoof" x2=".2" y2="1"><stop stop-color="#d5b875"/><stop offset=".5" stop-color="#b29451"/><stop offset="1" stop-color="#8d783f"/></linearGradient>
<linearGradient id="glassRoof" x2=".3" y2="1"><stop stop-color="#d2e2cf"/><stop offset="1" stop-color="#93baad"/></linearGradient>
<linearGradient id="timber" x2="0" y2="1"><stop stop-color="#b2946b"/><stop offset="1" stop-color="#8d7355"/></linearGradient>
<linearGradient id="plaster" x2="0" y2="1"><stop stop-color="#f3ead2"/><stop offset="1" stop-color="#d5c8a9"/></linearGradient>
<radialGradient id="lantern"><stop stop-color="#f9e3a3"/><stop offset=".6" stop-color="#dcbb74"/><stop offset="1" stop-color="#b98f54"/></radialGradient>
</defs>{body}</svg>'''
