import math

from .architecture import path


def station(base, bend, tip, along):
    rest = 1-along
    return tuple(rest*rest*start + 2*rest*along*turn + along*along*end
                 for start, turn, end in zip(base, bend, tip))


def point(pair):
    return f'{pair[0]:.2f},{pair[1]:.2f}'


def leaf_axis(base, bend, tip, spread, palette, rank):
    dark, shadow, leaf, light, _ = palette
    parts = [f'<g data-fern-axis="{rank}">',path(f'M{point(base)}Q{point(bend)} {point(tip)}',
             stroke=shadow if rank=='front' else dark, width=.91)]
    for level, reach in ((.17, .58), (.36, .96), (.54, 1), (.73, .75), (.87, .43)):
        for side in (-1, 1):
            along = level + (.045 if side==1 else 0)
            joint = station(base,bend,tip,along)
            neck = station(base,bend,tip,min(.99,along+.16))
            dx, dy = neck[0]-joint[0], neck[1]-joint[1]; norm = math.hypot(dx,dy)
            arc = side*reach*spread*(.82 if side==1 else 1)
            lobe = (neck[0]-dy/norm*arc, neck[1]+dx/norm*arc+1.25*reach)
            shoulder = (joint[0]+(lobe[0]-joint[0])*.65-dx*.16, joint[1]+(lobe[1]-joint[1])*.25-1.6*reach)
            return_bend = (neck[0]+(lobe[0]-neck[0])*.86, neck[1]+(lobe[1]-neck[1])*.87+2.55*reach)
            paint = (light if side==1 else leaf) if rank=='front' else (leaf if side==1 else shadow)
            parts.append(path(f'M{point(joint)}Q{point(shoulder)} {point(lobe)}Q{point(return_bend)} {point(neck)}Z',paint))
    parts.append('</g>')
    return ''.join(parts)


def spreading_fern(design, palette):
    left, right = design['shoulders']; back = design['backLift']; front = design['frontReach']
    return '<g data-fern-habit="spreading-bed">'+''.join([
        leaf_axis((-1.4,-1.7),(-8,-back*.91),(left,-back*.7),4.4,palette,'back-left'),
        leaf_axis((.4,-1.8),(.2,-back*.86),(5,-back),3.85,palette,'back-high'),
        leaf_axis((.5,-1.4),(right*.59,-back*.93),(right,-back*.55),4.35,palette,'back-right'),
        leaf_axis((1,-.8),(-front*.74,-back*.51),(-front,-back*.29),4.7,palette,'front'),
    ])+'</g>'
