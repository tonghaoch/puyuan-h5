"""Flowering boughs in the existing 32 × 40 rooted planting frame."""

from .landscape import ellipse, number, path


PALETTES = {
    'pink': ('#503b39', '#855351', '#98565f', '#df95a2', '#f4bdc6', '#ffe1dc'),
    'apricot': ('#574033', '#88604c', '#9d624c', '#e1a18c', '#f4c5b2', '#ffe2cd'),
}
DEFAULT_LEADERS = ((-12, -26), (-7, -34), (1, -37), (7, -28), (12, -33))


def point(position):
    return ' '.join(number(value) for value in position)


def segment(start, end, fraction):
    return tuple(first + (last - first) * fraction for first, last in zip(start, end))


def joint(start, bend, end, fraction):
    return segment(segment(start, bend, fraction), segment(bend, end, fraction), fraction)


def stalk(start, bend, end, width, paint):
    return path(f'M{point(start)} Q{point(bend)} {point(end)}', stroke=paint, width=width)


def panicle(socket, tip, spread, palette, direction):
    _, twig, calyx, half, petal, light = palette
    bend = (socket[0] + direction * .62, tip[1] + 1.8)
    parts = ['<g data-part="flower-spray">', stalk(socket, bend, tip, .83, twig)]
    for level, side, size in ((.30, -direction, .78), (.65, direction, 1), (1, 0, .74)):
        neck = joint(socket, bend, tip, level)
        width = size * spread
        center = (neck[0] + side * width * 1.22, neck[1] - .94 * width)
        parts.append(stalk(neck, (center[0], neck[1]), center, .73, calyx))
        parts.append('<g transform="translate(' + point(center) + ') scale(' + number(width) + ')">')
        parts.append(path('M-1.42 .2Q-1.78-.89-.75-.88Q-.48-1.78.33-1.24Q1.5-1.47 1.4-.45Q2.05.26 1.11.73Q.4 1.45-.18.93Q-1.27 1.4-1.42.2Z', half))
        parts.append(path('M-1.39-.16Q-1.42-1.24-.67-.99Q-.53-1.82.28-1.28Q1.11-1.47 1.28-.68Q1.52.04.45.15Q-.2.66-.67.24Z', petal))
        parts.append(ellipse(-.40, -.85, .56, .34, light))
        if side == direction:
            parts.append(path('M-.8 .48Q-.24 .89 .79 .30Q.46 1.34 .02 1.46Z', calyx))
        parts.append('</g>')
    return ''.join(parts) + '</g>'


def blossom_clusters(rng, stem):
    frame = stem['flowerFrame']
    palette = PALETTES[stem['bloom']]
    bark, twig = palette[:2]
    fork = (rng.uniform(-1.3, 1.3), -frame['fork'])
    trunk = f'M-1.85 0 Q-.65 -2.6 {point((fork[0] - 1, fork[1]))} l1.8 -.8 Q.92 -3.4 1.4 -.45 Z'
    wood = [path(trunk, bark)]
    sprays = []
    for index, (wide, high) in enumerate(stem.get('leaders', DEFAULT_LEADERS)):
        side = -1 if wide < 0 else 1
        tip = (wide * frame['span'], high)
        elbow = segment(fork, tip, .58)
        elbow = (elbow[0] + side * rng.uniform(.7, 1.7), elbow[1])
        lower = (fork[0] + .24 * (elbow[0] - fork[0]), elbow[1] + 1.5)
        upper = (elbow[0] + side, elbow[1] - 3.8)
        wood.extend([stalk(fork, lower, elbow, 1.48, bark), stalk(elbow, upper, tip, 1.0, twig)])
        turn = side if index % 3 else -side
        for station, direction in ((frame['bare'] + rng.uniform(-.12, .13), turn), (rng.uniform(.66, .90), -turn)):
            socket = joint(fork, lower, elbow, station / .58) if station < .58 else joint(elbow, upper, tip, (station - .58) / .42)
            sprig = (socket[0] + direction * rng.uniform(1.9, 4.1), socket[1] - rng.uniform(3.2, 7.5))
            sprays.append(panicle(socket, sprig, frame['tuft'] * rng.uniform(.95, 1.32), palette, direction))
        sprays.append(panicle(joint(elbow, upper, tip, .64), tip, frame['tuft'] * 1.09, palette, side))
    return '<g data-part="flower-frame"><g data-part="wood">' + ''.join(wood) + '</g>' + ''.join(sprays) + '</g>'
