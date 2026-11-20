"""South bank public floors with the pre-existing paving underneath the turf."""
from .landscape import number, path, poly, rounded_ring, shape


def ribbon(stations, near, far):
    return [(row[0], row[near]) for row in stations] + [(row[0], row[far]) for row in reversed(stations)]


def slope(unit):
    key = 'sw34-' + unit['id'] + '-slope'
    stations = unit['field']
    moist, meadow, dry = unit['moisture']
    defs = []; panels = []
    for index, (first, last) in enumerate(zip(stations, stations[1:])):
        left, top, bottom = first; right, high, low = last
        for half, (triangle, start, end, tangent) in enumerate((
            ([first[:2],last[:2],(right,low)], (right,high), (right,low), (right-left,high-top)),
            ([first[:2],(right,low),(left,bottom)], (left,top), (left,bottom), (right-left,low-bottom)),
        )):
            tag = f'{key}-{index}-{half}'
            matrix = ' '.join(map(number, (tangent[0],tangent[1],0,end[1]-start[1],start[0],start[1])))
            defs.append(f'<linearGradient id="{tag}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="1" gradientTransform="matrix({matrix})"><stop stop-color="{moist}"/><stop offset=".40" stop-color="{meadow}"/><stop offset="{unit["dryLevel"]}" stop-color="{dry}"/><stop offset=".96" stop-color="{dry}"/><stop offset="1" stop-color="{dry}" stop-opacity="0"/></linearGradient>')
            panels.append(poly(triangle, f'url(#{tag})', f'url(#{tag})', .25))
    if 'shelteredToe' in unit:
        across, down, spread, depth = unit['shelteredToe']; tag = key+'-shelter'
        defs.append(f'<radialGradient id="{tag}"><stop stop-color="{moist}"/><stop offset=".42" stop-color="{meadow}" stop-opacity=".87"/><stop offset="1" stop-color="{meadow}" stop-opacity="0"/></radialGradient>')
        panels.append(f'<ellipse cx="{across}" cy="{down}" rx="{spread}" ry="{depth}" fill="url(#{tag})"/>')
    left = stations[0][0]; right = stations[-1][0]
    defs.append(f'<linearGradient id="{key}-ease"><stop stop-color="black"/><stop offset=".07" stop-color="white"/><stop offset=".93" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient><mask id="{key}-ends" maskUnits="userSpaceOnUse" x="{left-1}" y="1100" width="{right-left+2}" height="260"><rect x="{left}" y="1100" width="{right-left}" height="260" fill="url(#{key}-ease)"/></mask>')
    return f'<g id="{key}"><defs>'+''.join(defs)+f'</defs><g mask="url(#{key}-ends)">'+''.join(panels)+'</g></g>'


def floor_bed(bed, units, original):
    if not units: return original
    cuts = []; surfaces = []; fields = []
    for unit in units:
        key = 'sw34-' + unit['id']; apron = unit['apron']
        outline = rounded_ring(ribbon(apron, 1, 3)); cuts.append(outline)
        rim = rounded_ring(ribbon(apron, 2, 3)); face = rounded_ring(ribbon(apron, 1, 2))
        parts = [path(outline, '#d4c6af', extra='opacity=".62"'), path(face, '#f3f1e9', extra='opacity=".72"'), path(rim, '#cbbda3', extra='opacity=".58"')]
        if unit.get('doorstep'):
            sill = unit['doorstep']; parts.append(path(rounded_ring(ribbon(sill, 1, 2)), '#aba793', extra='opacity=".65"'))
        surfaces.append(f'<g id="{key}-apron">'+''.join(parts)+'</g>'); fields.append(slope(unit))
    keys = '-'.join(unit['id'] for unit in units); opening = 'sw34-public-ground-'+keys
    boundary = 'sw34-planted-ground-'+keys
    definitions = f'<defs><clipPath id="{opening}"><path d="M0 0H2363V1672H0Z'+''.join(cuts)+'" clip-rule="evenodd"/></clipPath>'+f'<clipPath id="{boundary}"><path d="{shape(bed)}"/></clipPath></defs>'
    return definitions+f'<g clip-path="url(#{opening})">{original}</g><g clip-path="url(#{boundary})">'+''.join(fields)+'</g>'+''.join(surfaces)
