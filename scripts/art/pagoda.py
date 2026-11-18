"""Draw the illustrated silhouette; the dark upper mass is not identified from a photograph."""
import random
from .landscape import poly
from .street_houses import along, shifted, stroke


def terrace(ring):
    parts = []
    for level in range(3, -1, -1):
        edge = [(915 + (horizontal - 915) * (1 + level * .038),
                 579 + (vertical - 579) * (1 + level * .026) + level * 1.65) for horizontal, vertical in ring]
        parts.append(poly(edge, '#e1e3d4', '#85877a', .28))
        for side in range(3, 8):
            start, end = edge[side], edge[(side + 1) % len(edge)]
            parts.append(poly([start, end, shifted(end, 0, 1.0), shifted(start, 0, 1.0)],
                              ['#9a9483', '#c4c6b7', '#b8bcac', '#a9ad9c', '#aaa99a'][side - 3], '#747869', .27))
            for fraction in (.18, .45, .71):
                joint = along(start, end, fraction + .04 * (level % 2))
                parts.append(stroke([joint, shifted(joint, -.18, .85)], '#8e9383', .23))
    for side in range(3, 8):
        start, end = ring[side], ring[(side + 1) % len(ring)]
        for fraction in (.12, .39, .7, .92):
            outer = along(start, end, fraction); inner = along(outer, (915, 577), .22)
            parts.append(stroke([outer, inner], '#acaf9d', .38))
        parts.append(stroke([along(start, (915,577), .21),along(end, (915,577), .21)], '#b6baaa', .46))
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
    parts = [terrace(model['terrace']), upper_mass(model)]
    facing(parts, front(915.6, 567.6, 12.7), front(915.7, 585.2, 14.3),
           ['#816b59','#947865','#ad8e79','#bca699'], True)
    rng = random.Random(915568)
    for _ in range(64):
        start = (rng.uniform(902.6,928.3), rng.uniform(571.5,583.8))
        parts.append(stroke([start, shifted(start, rng.uniform(.28,1.35), rng.uniform(-.13,.16))], rng.choice(('#907a69','#ac9886','#977d69')), rng.uniform(.22,.49)))
    for center, height in ((906.6,578.5),(913.1,582.7),(921.9,581.8),(928.2,578.3)):
        parts.append(stroke([(center,height),(center+.2,height-1.6)], '#584b40', .86))
    for index in reversed(range(len(model['eaves']))):
        center, height, radius = model['eaves'][index]
        below = model['eaves'][index + 1][1] if index + 1 < len(model['eaves']) else 571.6
        upper = front(center, height, radius - 1.45); lower = front(center, below, radius - 1.1)
        facing(parts, upper, lower, ['#67564b','#8b7161','#a68c80','#c4b1a6'], True)
        for side in (0, 2, 3):
            lintel = along(upper[side], upper[side + 1], .45)
            sill = along(lower[side], lower[side + 1], .45)
            parts.append(stroke([along(lintel, sill, .28), along(lintel, sill, .78)], '#594b44', .82 if side == 2 else .58))
        lip = front(center, height - .1, radius)
        back = [(center-radius*.67,height-3.1),(center+radius*.42,height-3.5),(center+radius*.85,height-2.7)]
        parts.append(poly(lip + back[::-1], '#675c54', '#493e37', .29))
        parts.append(poly(lip + [shifted(point, 0, .94) for point in lip[::-1]], '#483e37', '#483d36', .29))
        for side, across in ((0,.12),(0,.66),(1,.28),(2,.63),(3,.80)):
            nose = along(lip[side],lip[side+1],across + rng.uniform(-.09,.09))
            parts.append(poly([shifted(nose,-.68,-.46),shifted(nose,.87,-.22),shifted(nose,.62,1.27),shifted(nose,-.47,1.11)], rng.choice(('#392f29','#4b3b33','#594a40'))))
        parts.append(stroke([along(lip[2],lip[3],.38),lip[3],along(lip[3],lip[4],.62)], '#a49b88', .28))
    parts.append(poly([(904.5,509.8),(908.0,505.1),(912.1,504.5),(916.1,498.3),(918.1,502.2),
                       (923.2,505.0),(927.7,509.8),(920.7,512.0),(913.5,512.4),(907.5,511.2)], '#403e3a', '#373533', .42))
    for points in [[(907.0,509.2),(910.0,505.3)],[(912.8,504.1),(915.7,500.0)],[(917.8,503.7),(923.5,507.4)],[(923.9,507.9),(926.4,509.4)]]:
        parts.append(stroke(points, '#aba79a', .62))
    return ''.join(parts)
