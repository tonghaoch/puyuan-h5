"""A projected eave lining above a closed, recessed shutter front."""
import math

from .landscape import poly


def eaved_shutters(frame, height, render_front):
    def station(edge, fraction):
        return tuple(start + fraction * (end-start) for start, end in zip(*edge))

    soffit = frame['soffit']
    if not 0 < soffit['recess'] < 1 or height <= 0:
        raise ValueError('The recessed beam must remain above the sill')
    drop = height * soffit['recess']
    beam = [(east, south + drop) for east, south in frame['beam']]
    eave = soffit['eave']
    if any(head[1] < lip[1] for head, lip in zip(beam, eave)):
        raise ValueError('The eave cannot cross the recessed beam')
    front = dict(frame, beam=beam)
    del front['soffit']
    bevel = [tuple(start + .22 * (end-start) for start, end in zip(lip, head)) for lip, head in zip(eave, beam)]
    parts = [render_front(front, height-drop), '<g data-soffit="recessed-shutters">',
             poly([*eave, *reversed(bevel)], '#a79583'), poly([*bevel, *reversed(beam)], '#ded2bf')]
    half_width = min(.7, height*.14) / math.dist(*beam)
    for column in frame['columns']:
        start, end = max(0,column-half_width), min(1,column+half_width)
        parts.append('<g data-eave-bearing="timber">'+poly([station(bevel,start),station(bevel,end),
                     station(beam,end),station(beam,start)],'#655246')+'</g>')
    return ''.join(parts)+'</g>'
