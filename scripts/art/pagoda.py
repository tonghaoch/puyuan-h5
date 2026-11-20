"""Draw the illustrated silhouette; the dark upper mass is not identified from a photograph."""
import random
from .landscape import poly
from .street_houses import along, shifted, stroke


def terrace(model):
    steps = model['foresteps']
    parts = ['<g id="pagoda-cut-stone-steps">',poly(model['terrace'], '#d8dace', '#85877a', .48)]
    for level,(back,lip) in reversed(list(enumerate(zip(steps,steps[1:])))):
        parts.append(poly(back+lip[::-1], ['#e4e6d9','#e1e6d8','#e7e9dd'][level%3]))
        toe=[shifted(point,0,1.08) for point in lip]
        parts.append(poly(lip+toe[::-1], '#969b8c'))
        parts.append(stroke([shifted(point,0,-.35) for point in lip], '#eff0e6',.72))
        for side,(start,end) in enumerate(zip(lip,lip[1:])):
            fraction=.22+.13*((level+side*2)%5);outer=along(start,end,fraction);inner=along(back[side],back[side+1],fraction+.035)
            parts.append(stroke([inner,outer,shifted(outer,0,.91)],'#a5a998',.45))
            parts.append(stroke([along(start,end,.26),along(start,end,.72)],'#858a7a',.58))
    for cheek in model['stairCheeks']:
        parts.append(poly(cheek,'#a99d87','#695e4c',.67))
        for index,(start,end) in enumerate(zip(cheek,cheek[1:])):
            if index%3==1:parts.append(stroke([along(start,end,.13),along(start,end,.86)],'#615441',1.09))
            if index%3==2:parts.append(stroke([along(start,end,.19),along(start,end,.83)],'#d6c6ad',.67))
    parts.append('</g>')
    return ''.join(parts)


def upper_mass(model):
    outline = model['crown']
    parts = [poly(model['cap'], '#443f43', '#363b3e', .55),
             poly([(908.4,470.0),(912.3,471.0),(916.6,469.6),(916.0,471.6),(912.2,473.1),(909.3,472.3)], '#4e4544'),
             f'<defs><clipPath id="pagoda-upper-mask">{poly(outline, "white")}</clipPath></defs>',
             poly(outline, '#4c494a', '#322f30', .6), '<g clip-path="url(#pagoda-upper-mask)">',
             poly([(896,474),(902.8,475.6),(905.9,522),(898,520)], '#433c3e'),
             poly([(902.8,475.6),(913.5,474.1),(916.3,521),(905.7,522)], '#403f3e'),
             poly([(917.2,474.4),(927.5,474.0),(932.4,520.0),(919.3,518.2)], '#595556')]
    rng = random.Random(897476)
    for _ in range(310):
        start = (rng.uniform(896, 933), rng.uniform(474, 521))
        parts.append(stroke([start, shifted(start, rng.uniform(-.25, .48), rng.uniform(.28, 2.4))],
                            rng.choice(('#383738','#484447','#595457','#514e4c')), rng.uniform(.23, .62)))
    parts.append('</g>')
    return ''.join(parts)


def front(center, height, radius):
    return [(center + radius * across, height + drop) for across, drop in
            [(-1, -1.5),(-.67, .0),(-.18, 1.3),(.46, 1.0),(1, -1.6)]]


def facing(parts, upper, lower, colors, joints=False):
    for side, color in enumerate(colors):
        start, end = upper[side:side + 2]; foot, toe = lower[side:side + 2]
        parts.append(poly([start, end, toe, foot], color, '#5e5048', .18))
        if joints:
            mid = along(start, foot, .54); other = along(end, toe, .54)
            parts.append(stroke([mid, other], '#887567', .28))
            for across, down in ((.23,.54),(.72,.15)):
                seam = along(along(start, end, across), along(foot, toe, across), down)
                parts.append(stroke([seam, shifted(seam, -.1, 1.9)], '#705e51', .28))


def pagoda(model):
    parts = [terrace(model), upper_mass(model)]
    drum=front(915.6, 567.6, 12.7);foot=model['drumFoot']
    facing(parts, drum, foot,['#816b59','#947865','#ad8e79','#bca699'], True)
    rng = random.Random(915568)
    for _ in range(64):
        start = (rng.uniform(902.6,928.3), rng.uniform(571.5,583.8))
        parts.append(stroke([start, shifted(start, rng.uniform(.28,1.35), rng.uniform(-.13,.16))], rng.choice(('#907a69','#ac9886','#977d69')), rng.uniform(.22,.49)))
    for across,down,wide,tall in model['drumOpenings']:
        left=(across-wide*.5,down);right=(across+wide*.5,down-.15)
        parts.append(poly([left,right,shifted(right,0,tall),shifted(left,0,tall+.18)],'#654937','#68513f',.42))
        parts.append(stroke([shifted(left,-.43,tall+.12),shifted(right,.36,tall)],'#4c352a',.81))
    for fraction in (.63,.83,.98):
        course=[along(start,end,fraction) for start,end in zip(drum,foot)]
        for index,(start,end) in enumerate(zip(course,course[1:])):
            parts.append(stroke([along(start,end,.16*(index%2)),along(start,end,.66+.21*(index%2))], '#594638',.95 if fraction<.95 else .65))
    skirts=[]
    for index in reversed(range(len(model['eaves']))):
        center, height, radius = model['eaves'][index]
        below = model['eaves'][index + 1][1] if index + 1 < len(model['eaves']) else 571.6
        upper = front(center, height, radius - 1.45); lower = front(center, below, radius - 1.1)
        facing(parts, upper, lower, ['#775b50','#aa8b7b','#c1a296','#e0cdc3'], True)
        for side in range(4):
            start,end=upper[side:side+2];foot,toe=lower[side:side+2]
            lintel=along(along(start,foot,.30),along(end,toe,.30),.48)
            sill=along(along(start,foot,.76),along(end,toe,.76),.48)
            breadth=(1.03,1.52,1.10,1.22)[side]
            parts.append(poly([shifted(lintel,-breadth*.63,0),shifted(lintel,breadth*.64,-.18),shifted(sill,breadth*.57,-.2),shifted(sill,-breadth*.64,0)],'#49372f' if side<2 else '#4c3b38'))
            parts.append(stroke([shifted(lintel,-breadth*.63,-.23),shifted(lintel,breadth*.82,-.42)],'#9e8174',.51))
            shoulder=along(start,foot,.58);parts.append(stroke([shoulder,along(start,foot,.86)],'#695249',.70))
        lip = front(center, height - .1, radius)
        for side,(start,end) in enumerate(zip(lip,lip[1:])):
            high=shifted(along(start,end,.13),.35,-1.47);upper_end=shifted(along(start,end,.98),-.27,-1.65)
            skirts.append(poly([start,high,upper_end,end],['#594c40','#776152','#837865','#939183'][side],'#4c443a',.32))
            skirts.append(poly([start,end,shifted(end,0,.83),shifted(start,0,1.22)],'#362d29','#45392f',.26))
            for across in (.19,.48,.80):
                tile=along(start,end,across);skirts.append(stroke([shifted(tile,.35,-1.2),tile],'#afa590' if across==.48 else '#65574d',.43))
        for side, across in ((0,.12),(0,.66),(1,.28),(2,.63),(3,.80)):
            nose = along(lip[side],lip[side+1],across + rng.uniform(-.09,.09))
            skirts.append(poly([shifted(nose,-.83,-.46),shifted(nose,.96,-.24),shifted(nose,.74,1.45),shifted(nose,-.47,1.18)], rng.choice(('#332820','#41322b','#554438'))))
    parts.extend(skirts)
    parts.append(poly([(904.5,509.8),(908.0,505.1),(912.1,504.5),(916.1,498.3),(918.1,502.2),
                       (923.2,505.0),(927.7,509.8),(920.7,512.0),(913.5,512.4),(907.5,511.2)], '#403e3a', '#373533', .42))
    for points in [[(907.0,509.2),(910.0,505.3)],[(912.8,504.1),(915.7,500.0)],[(917.8,503.7),(923.5,507.4)],[(923.9,507.9),(926.4,509.4)]]:
        parts.append(stroke(points, '#aba79a', .62))
    return ''.join(parts)
