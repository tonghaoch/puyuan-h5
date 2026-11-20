"""A tapered bank planting: ascending needle sprays on a forked woody stem."""
from .crowns import curve
from .garden_trees import shoot
from .landscape import path


def needle_spray(rng, middle, base, span, length, sweep, palette):
    ink, shade, main, leaf, light = palette

    def at(across, rise):
        return middle + span * across + sweep * rise, base - length * rise

    rim = [at(across, rise) for across, rise in (
        (0, 0), (-.70, .07), (-1, .24), (-.88, .43), (-.96, .54),
        (-.58, .72), (-.46, .83), (-.10, 1), (.15, .95), (.55, .74),
        (.76, .64), (.66, .52), (.96, .39), (.86, .18), (.48, .05),
    )]
    parts = [path(curve(rim), main), path(curve([at(.22, .10), at(.8, .19),
             at(.91, .39), at(.64, .50), at(.70, .62), at(.44, .75),
             at(.48, .46), at(.40, .32), at(.12, .17)]), shade, extra='opacity=".62"')]
    for level in (.17, .39, .61):
        for side in (-1, 1):
            reach = side * (1 - level * .64) * rng.uniform(.72, .96)
            start = at(side * .075, level)
            elbow = at(reach * .63, level + .035)
            end = at(reach, level + rng.uniform(.12, .23))
            parts.append(shoot(start, elbow, end, rng.choice((shade, leaf, leaf)), 1.05))
            parts.append(shoot(elbow, at(reach * .78, level + .11), end, rng.choice((shade, light)), .61))
    for begin, end in ((1, 3), (6, 8), (10, 11), (13, 14)):
        parts.append(shoot(rim[begin], rim[(begin + end) // 2], rim[end], ink, rng.uniform(1.7, 2.6)))
    return '<g data-needle-spray="">' + ''.join(parts) + '</g>'


def bank_evergreen(rng, palette):
    ink, shade, *_ = palette
    leader = rng.uniform(-1.15, 1.15)
    parts = [path('M-3.5.3Q-1.6-2.8-2.1-9L-1.3-19.2L.8-23.8L1.7-11.4Q.9-4.1 2.7-.3L.55.35Z', ink),
             shoot((-.4, -1), (-.9, -7.5), (.6, -16.8), shade, .55)]
    tiers = ((0, -22.4, 5.7, 16.9, leader), (-4, -14.1, 5.8, 18.1, -2.35),
             (4.4, -12.9, 6, 19.6, 1.35), (-6.5, -5.3, 6.9, 17, -2.55),
             (6.6, -4.1, 7.1, 18.1, 1.85), (-1.75, -4.8, 5.1, 15.15, -.8))
    for middle, base, span, length, sweep in tiers:
        middle += rng.uniform(-.62, .62)
        parts.append(shoot((.1, base * .68 - .5), (middle * .67, base * .72),
                           (middle + sweep * .3, base - length * .56), ink, 1.45))
        parts.append(needle_spray(rng, middle, base, span, length, sweep, palette))
    parts.append(path('M-2.9.4Q-1.6-4.1-2.7-9.0L-4.6-16.5L-2.7-15.0L-.5-9.6L2-14.2L3.5-20.5L4.9-20.1L4-12.1L1.4-5.2L2.0.35Z', ink))
    parts.append(shoot((-1.4, -7.8), (-7.15, -9.65), (-8.95, -14.9), ink, 2.05))
    parts.append(shoot((-.3, -13.6), (-2.45, -19.3), (-1.3, -24.4), ink, 2.25))
    parts.append(shoot((2.3, -17.9), (6.7, -20.6), (7.4, -24.3), ink, 1.6))
    return '<g data-habit="bank-needle-forks">' + ''.join(parts) + '</g>'
