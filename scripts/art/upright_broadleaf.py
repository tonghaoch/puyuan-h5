"""One upright garden tree, rooted at (0, 0) in a 32 by 40 frame."""
from .crowns import curve
from .garden_trees import shoot
from .landscape import path


def crown_rim(rng):
    leader = rng.uniform(-3.0, 2.0)
    shoulder = rng.uniform(-1.3, 1.3)
    spread = rng.uniform(.94, 1.03)
    points = [(leader, -38.5), (leader + 4.1, -37.9), (6.6, -34.3),
              (8.5 + shoulder, -30.2), (9.1 + shoulder, -27.1), (12.6, -24.0),
              (14.2, -19.0), (14.0, -14.1), (12.4, -10.8), (7.5, -10.2),
              (4.4, -8.7), (.8, -9.5), (-3.9, -8.9), (-7.1, -10.2),
              (-11.6, -10.7), (-14.2, -13.1), (-14.3, -18.3), (-12.7, -21.2),
              (-12.7, -24.4), (-9.8, -29.8), (-7.8, -31.4), (-5.9, -35.6)]
    return [(wide * spread + rng.uniform(-.45, .45), high + rng.uniform(-.65, .65))
            for wide, high in points]


def upright_broadleaf(rng, palette):
    ink, shade, main, leaf, light = palette
    bark = '#41412b'
    parts = ['<g data-habit="upright-broadleaf"><g data-bearing-stem="">',
             path('M-3.1 .4Q-1.6-2.8-2.1-9.2L-3.6-15.5L-2.5-21L-.8-14.2L.5-10.5Q3.1-13.2 4.9-18.2L6.3-19.7Q5.4-12.5 2-8L2-2.4L3.1-.1L.8-.6Z', bark),
             shoot((-.8, -2.0), (-.4, -6.3), (-1.6, -11.2), '#837554', .85),
             shoot((-1.4, -6.7), (-5.9, -10.6), (-8.6, -15.0), bark, 1.45),
             shoot((-1.5, -.8), (-3.4, .3), (-5.8, -.3), bark, 1.55), '</g>']
    rim = crown_rim(rng)
    parts.extend(('<g data-broad-crown="">', path(curve(rim), main),
                  path('M-12.1-17.5Q-10.2-15.9-8.5-16.4Q-7-13.9-3.4-14Q-1.1-11.7 2.6-12.2Q.5-9.6-2.2-10.2Q-4.1-9.4-6.8-11.2Q-11.8-11-12.1-17.5Z', shade),
                  path('M.7-34.6Q5.6-33.8 6.7-29.1Q4.2-29.8 3.5-28.3Q2.7-31.0 .4-30.7Q2.0-32.5 .7-34.6Z', leaf)))
    for index in (0, 2, 5, 7, 9, 12, 14, 16, 18, 21):
        start, end = rim[index], rim[(index + 1) % len(rim)]
        reach = rng.uniform(.55, .88)
        tip = tuple(near + (far - near) * reach for near, far in zip(start, end))
        mid = ((start[0] + tip[0]) / 2, (start[1] + tip[1]) / 2 - .23)
        parts.append(shoot(start, mid, tip, ink, rng.uniform(1.7, 2.8)))
    for across, down, side in [(-5, -26, -1), (1, -32, 1), (6, -20, 1), (-7, -15, -1)]:
        base = (across + rng.uniform(-.9, .9), down + rng.uniform(-.8, .8))
        for step in (0, 1, 2):
            joint = (base[0] + side * step * .7, base[1] - step * 1.4)
            reach = side * rng.uniform(1.1, 2.2) * (1 if step != 1 else -.8)
            bud = [(joint[0], joint[1]), (joint[0] + reach, joint[1] - .4),
                   (joint[0] + reach * 1.45, joint[1] - 2.5), (joint[0] + reach * .35, joint[1] - 2)]
            parts.append(path(curve(bud), rng.choice((shade, leaf, light))))
    parts.extend(('</g>', shoot((-.2, -7.9), (.1, -10.5), (2.1, -12.1), bark, 1.12), '</g>'))
    return ''.join(parts)
