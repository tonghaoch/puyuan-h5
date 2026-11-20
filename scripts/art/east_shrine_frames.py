"""The backed porch and closed timber drums of the main sanctuary."""
import math

from .landscape import number, poly


def outline(points):
    return 'M' + 'L'.join(f'{number(x)},{number(y)}' for x, y in points) + 'Z'


def terraced_wall(original, model, frame, key):
    left_x, left_y, right_x, right_y, _, _, _, height, kind = model
    style, stations = frame['profile'], frame['posts']
    if kind != 'temple' or style not in ('backed-porch', 'closed-drum'):
        raise ValueError('Not a closed sanctuary timber frame')
    if len(stations) < 2 or sorted(set(stations)) != stations or not 0 < stations[0] < stations[-1] < 1:
        raise ValueError('Ordered bearing stations required')
    width = .93 * math.hypot(right_x - left_x, right_y - left_y)
    margin, head, edge = .42 / width, .42 / height, .84 / width

    def at(across, down):
        ratio = .035 + .93 * across
        return left_x + (right_x-left_x)*ratio, left_y + (right_y-left_y)*ratio + height*down

    def band(start, stop, upper, lower):
        return [at(start, upper), at(stop, upper), at(stop, lower), at(start, lower)]

    inside = outline(band(margin, 1-margin, head, 1-head))
    backing = '#725346' if style == 'backed-porch' else '#775748'
    timber = [f'<path d="{inside}" fill="{backing}" fill-rule="evenodd"/>']
    for index, (left, right) in enumerate(zip(stations, stations[1:])):
        span = right-left
        if style == 'backed-porch':
            seat, stop = left+span*.12, right-span*.12
            timber.append(poly(band(left+edge, seat, .23, .87), '#4d3b34', 'none', 0))
            timber.append(poly(band(seat, stop, .24, .84), '#705043' if index%2 else '#805f4d', 'none', 0))
            timber.append(poly(band((seat+stop)*.5-.15/width, (seat+stop)*.5+.15/width, .32, .82), '#594237', 'none', 0))
            timber.append(poly(band(seat, stop, .81, .88), '#513f36', 'none', 0))
        else:
            timber.append(poly(band(left+edge, right-edge, .34, .77), '#694c40' if index%2 else '#725448', 'none', 0))
            timber.append(poly(band(left+edge, left+edge+span*.12, .35, .76), '#554038', 'none', 0))
    for where in stations:
        timber.append(poly(band(where-edge, where+edge, .16, .99), '#634639', 'none', 0))
        timber.append(poly(band(where-edge, where-edge*.25, .24, .96), '#96745a', 'none', 0))
        timber.append(poly(band(where+edge*.55, where+edge, .29, .97), '#4b3830', 'none', 0))
        timber.append(poly([at(where-edge*2.15, .18), at(where+edge*2.0, .18), at(where+edge*1.38, .29), at(where-edge*1.32, .29)], '#815f49', 'none', 0))
    timber.append(poly(band(0, 1, .04, .20), '#503c33', 'none', 0))
    timber.append(poly(band(0, 1, .19, .26), '#916f54', 'none', 0))
    if style == 'closed-drum':
        timber.append(poly(band(0, 1, .78, .87), '#5a4438', 'none', 0))
    clip = 'inset-' + key
    defs = f'<clipPath id="{clip}"><path d="{inside}"/></clipPath>'
    return f'<g data-shrine-frame="{key}"><defs>{defs}</defs><g data-original-walls="1">{original}</g><g clip-path="url(#{clip})">'+''.join(timber)+'</g></g>'
