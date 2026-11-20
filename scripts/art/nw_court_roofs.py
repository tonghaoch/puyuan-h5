"""Joined northwestern roofs whose transverse ranges have separate ridges."""
import math
from .native_roofs import volume_planes


COURTS = {
    'roof-973': ('nw12-fuma-cross-halls', (
        ('north-hall', ((716,545),(752,541)), ((716,551),(754,551)), ((721,546),(749,543))),
        ('west-return', ((713,555),(712,579)), ((720,555),(721,579)), ((717,557),(717,575))),
        ('court-link', ((734.5,560),(735.5,575)), ((738.5,560),(740,575)), ((736.4,561),(737.8,573))),
        ('middle-hall', ((714,554.5),(748,553)), ((714,562),(748,561)), ((718,556.5),(745,555))),
        ('pool-wing', ((753,547.5),(753,571.5)), ((767,547),(771,571)), ((758,549),(762,568))),
        ('south-hall', ((712,573.5),(749,572.5)), ((712,585),(751,585.5)), ((716,577.3),(747,576.8))),
    )),
    'roof-866': ('nw12-fork-island-ranges', (
        ('canal-loft', ((550.5,819),(579,811.6)), ((551.2,828.5),(581,823)), ((554,820.8),(577,815.4))),
        ('east-return', ((572.5,823),(573.4,848)), ((580.8,821.6),(582,846.5)), ((576.5,824),(577.7,844.5))),
        ('court-range', ((545.5,832),(572,829.6)), ((544.8,842.6),(573.2,841.4)), ((548.6,835.5),(569.8,833.5))),
    )),
}


def slope(start, end, tips):
    dx,dy=end[0]-start[0],end[1]-start[1]
    length=math.hypot(dx,dy);nx,ny=-dy/length,dx/length
    inner=tips[0]
    if (inner[0]-start[0])*nx+(inner[1]-start[1])*ny<0:nx,ny=-nx,-ny
    return {'points':[start,end,*tips],'holes':[], 'shade':round(-nx*.62-ny*.78,3),
            'angle':round(math.degrees(math.atan2(dy,dx)),2)}


def court_roof(feature):
    author,units=COURTS[feature['id']];parts=[]
    for name,rear,front,ridge in units:
        faces=[slope(*rear,[ridge[1],ridge[0]]),slope(*front,[ridge[1],ridge[0]]),
               slope(rear[0],front[0],[ridge[0]]),slope(rear[1],front[1],[ridge[1]])]
        key=author+'-'+name
        parts.append(f'<g id="{key}">'+volume_planes(dict(feature,id=key,roofVolume={'faces':faces}))+'</g>')
    return f'<g id="{author}">'+''.join(parts)+'</g>'
