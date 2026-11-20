"""Transfer an observed elevation from overlapping material parents to one frame."""
from .landscape import poly
from .street_houses import along, stroke


def owned_surface(feature, raw, frames):
    from .surface_finishes import sample_footprint, sampled_shape
    relevant = [frame for frame in frames if feature['id'] in frame[1]]
    original = raw(dict(feature, nwRawFront=True))
    if not relevant:
        return original
    key = 'single-face-' + feature['id']
    openings, fronts, cuts, rectangles = [], [], [], []
    for name, sources, head, foot, bays, sill in relevant:
        def point(station, depth):
            return along(along(*head, station), along(*foot, station), depth)
        def strip(left, right, top, bottom, paint):
            return poly([point(left, top), point(right, top), point(right, bottom), point(left, bottom)], paint)
        ring = [*head, *reversed(foot)]
        openings.append('M'+'L'.join(f'{x},{y}' for x,y in ring)+'Z')
        cuts.append(poly(ring, 'black'))
        rectangles.append((min(x for x,y in ring), min(y for x,y in ring), max(x for x,y in ring), max(y for x,y in ring)))
        if feature['id'] != sources[0]:
            continue
        spans = []
        for start, stop, infill in bays:
            if infill == 'closed':
                spans.append(strip(start, stop, .13, .99, '#755043'))
                spans.append(stroke([point((start+stop)/2, .22), point((start+stop)/2, .96)], '#50392f', .43))
            elif infill == 'slot':
                spans.extend([strip(start, stop, .13, .43, '#755043'), strip(start, stop, .72, .99, '#69483e')])
            elif infill == 'rail':
                spans.append(strip(start, stop, .75, .87, '#69483e'))
            elif infill != 'open':
                raise ValueError(infill)
        for station in sorted({edge for start,stop,_ in bays for edge in (start,stop)}):
            spans.append(stroke([point(station, .08), point(station, .98)], '#50392f', .72))
        spans.append(strip(0, 1, 0, .16, '#493a34'))
        if sill:
            spans.append(strip(0, 1, .9, 1, '#584039'))
        fronts.append(f'<g id="{name}">'+''.join(spans)+'</g>')
    outside = 'M0,0H2363V1672H0Z'+''.join(openings)
    clip = f'<defs><clipPath id="{key}"><path d="{outside}" clip-rule="evenodd"/></clipPath></defs>'
    footprint, _ = sample_footprint(feature)
    assert original.count(footprint) == 1
    original = original.replace(footprint, footprint[:-7]+''.join(cuts)+'</mask>')
    for panel in feature.get('streetObservation', {}).get('timber', []):
        xs, ys = zip(*panel['points'])
        if not any(min(xs)<right and max(xs)>=left and min(ys)<bottom and max(ys)>=top for left,top,right,bottom in rectangles):
            continue
        item = sampled_shape(panel, 'url(#surface-timber-'+feature['id']+')')
        assert original.count(item) == 1
        original = original.replace(item, f'<g clip-path="url(#{key})">{item}</g>')
    return clip+original+''.join(fronts)
