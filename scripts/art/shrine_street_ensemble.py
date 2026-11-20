from .landscape import poly


def gate_return(model):
    sections = model['sections']; parts = ['<g id="west-gate-capped-return">']
    for start,stop in zip(sections,sections[1:]):
        rear,ridge,edge,foot = start; next_rear,next_ridge,next_edge,next_foot = stop
        parts.append(poly([edge,next_edge,next_foot,foot],'#e5e1d6','#a8a095',.26))
        parts.append(poly([rear,next_rear,next_ridge,ridge],'#69645e'))
        parts.append(poly([ridge,next_ridge,next_edge,edge],'#535053','#484647',.22))
    return ''.join(parts)+'</g>'
