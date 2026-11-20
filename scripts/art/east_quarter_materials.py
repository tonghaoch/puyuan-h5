"""An enclosed earth forecourt, behind the independently drawn gate."""
import math
import random

from .landscape import number, path, poly


def inset(ring,padding):
    signed=sum(x*ring[(idx+1)%len(ring)][1]-y*ring[(idx+1)%len(ring)][0] for idx,(x,y) in enumerate(ring))
    hand=1 if signed>0 else -1;edges=[]
    for idx,(x,y) in enumerate(ring):
        xx,yy=ring[(idx+1)%len(ring)];length=math.hypot(xx-x,yy-y)
        if length<.1:return []
        dx,dy=(xx-x)/length,(yy-y)/length;edges.append((x-hand*dy*padding,y+hand*dx*padding,dx,dy))
    result=[]
    for idx,(xx,yy,dx,dy) in enumerate(edges):
        px,py,ux,uy=edges[idx-1];det=ux*dy-uy*dx
        if abs(det)<.01:return []
        offset=((xx-px)*dy-(yy-py)*dx)/det;point=(px+offset*ux,py+offset*uy)
        if any(hand*(vx*(point[1]-cy)-vy*(point[0]-cx))<-.01 for cx,cy,vx,vy in edges):return []
        result.append(point)
    return result


def clipped(key,ring,body):
    clip='east-quarter-'+key
    return f'<g data-east-material="{key}"><defs><clipPath id="{clip}">{poly(ring,"white","none",0)}</clipPath></defs><g clip-path="url(#{clip})">{body}</g></g>'


def earth_court(key,ring):
    inner=inset(ring,.68)
    if not inner:return ''
    center=tuple(sum(point[axis] for point in ring)/len(ring) for axis in (0,1));parts=[poly(ring,'#dcd3b9','none',0)]
    for idx in (0,2):
        near,far=ring[idx],ring[(idx+1)%len(ring)]
        def shoulder(across,depth):
            edge=(near[0]+(far[0]-near[0])*across,near[1]+(far[1]-near[1])*across)
            return (edge[0]+depth*(center[0]-edge[0]),edge[1]+depth*(center[1]-edge[1]))
        parts.append(poly([near,far,shoulder(.91,.10),shoulder(.62,.16),shoulder(.38,.09),shoulder(.16,.18)],'#d2c8ac','none',0))
    rng=random.Random(key);xmin=min(x for x,y in ring);xmax=max(x for x,y in ring);ymin=min(y for x,y in ring);ymax=max(y for x,y in ring)
    for idx in range(round((xmax-xmin)*(ymax-ymin)/34)):
        cross=rng.uniform(xmin,xmax);down=rng.uniform(ymin,ymax);wide=rng.uniform(.3,.85)
        parts.append(path(f'M{number(cross)},{number(down)}q{number(wide*.38)},.09 {number(wide)},-.05',stroke='#c6baa0' if idx%3 else '#e9e0ca',width=.25))
    return clipped(key,inner,''.join(parts))
