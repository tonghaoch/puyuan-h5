"""A short willow bole with staggered boughs in the rooted 32 × 40 stem frame."""
from .crowns import curve
from .garden_trees import shoot
from .landscape import path


def callus(fork):
    across, level = fork
    rim = [(-2.2, .05), (-1.1, -3.2), (across - 1.45, level - .3),
           (across - .9, level - 3.4), (across + .85, level - 3.3),
           (across + 1.15, level + 1.9), (1.05, -2.0), (2.1, -.2), (.15, -.5)]
    return path(curve(rim), '#675633') + shoot((-.4, -1.7), (.15, -3.6),
                                               (across, level + 1.3), '#908053', .68)


def bearing_arm(fork, axis, depth):
    across, head, span, drop = axis
    direction = -1 if across < fork[0] else 1
    joint = (fork[0] + (across - fork[0]) * .72, fork[1] - (4.4 if depth == 2 else 3.1))
    seat = (across, head + drop * .56)
    rim = [(fork[0] - .8 * direction, fork[1] + .9),
           (joint[0] - .85 * direction, joint[1] - .55),
           (seat[0] + .6 * direction, seat[1] - 2.2), seat,
           (joint[0] + .72 * direction, joint[1] + .8),
           (fork[0] + .65 * direction, fork[1] + .85)]
    spur = (across - .39 * span * direction, head + drop * .33)
    return path(curve(rim), '#655a34') + shoot(joint, (spur[0], joint[1] - 2.7), spur, '#5e5d35', 1.05)


def hanging_fan(axis, depth, palette):
    across, head, radius, fall = axis
    ink, shadow, main, leaf, pale = palette
    def local(horizontal, vertical):
        return (across + horizontal * radius, head + vertical * fall)
    def wash(points, paint):
        return path(curve([local(*point) for point in points]), paint)
    rim = [(-.98,.49),(-.81,.22),(-.56,.14),(-.28,-.015),(.16,.015),(.42,.12),
           (.72,.19),(.94,.43),(.91,.67),(.77,.86),(.48,.99),(.37,.79),
           (.13,.92),(-.13,1.01),(-.26,.84),(-.58,.96),(-.62,.76),(-.86,.82)]
    body = wash(rim, (shadow, main, leaf)[depth]); under = (ink, shadow, main)[depth]
    body += wash([(-.94,.52),(-.63,.65),(-.45,.49),(-.32,.42),(-.24,.68),
                  (-.45,.83),(-.58,.95),(-.63,.75),(-.86,.81)], under)
    body += wash([(-.62,.30),(-.39,.12),(-.18,.065),(.14,.08),(.39,.17),(.61,.26),
                  (.34,.25),(.12,.32),(-.07,.24),(-.28,.35),(-.33,.27)], (main, leaf, pale)[depth])
    for position, reach, sense in ((-.69,.83,-1),(-.22,.96,-1),(.26,.86,1),(.64,.90,1)):
        socket = local(position * .65, .28 + abs(position) * .17)
        elbow = local(position * 1.12, .55)
        tip = local(position, reach)
        body += shoot(socket, elbow, tip, (shadow, shadow, main)[depth], .57)
        for offset in (.50, .72):
            joint = local(position, offset)
            blade = [joint, local(position + sense * .17, offset + .015),
                     local(position + sense * .12, offset + .13), local(position, offset + .09)]
            body += path(curve(blade), (main, leaf, pale)[depth])
    return body


def bearing_crown(frame, palette):
    fork, arms = frame['fork'], frame['arms']
    if len(arms) != 3:
        raise ValueError('Expected back, side and fore bearing arms')
    parts = ['<g data-willow-frame="bearing-boughs">', callus(fork)]
    for depth, axis in enumerate(arms):
        parts.extend((f'<g data-bough-depth="{depth}">', bearing_arm(fork, axis, depth),
                      hanging_fan(axis, depth, palette), '</g>'))
    return ''.join(parts) + '</g>'
