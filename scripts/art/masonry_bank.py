"""A projected stone plinth with a dry-side coping on a registered quay edge."""
import math

from .landscape import number, path, poly


def curb_sections(edge, rise, width):
    if len(edge) < 2 or not (rise > 0 and width > 0):
        raise ValueError('A quay needs a positive rise and coping width')
    normals = []
    for (east, south), (next_east, next_south) in zip(edge, edge[1:]):
        length = math.hypot(next_east-east, next_south-south)
        if not length:
            raise ValueError('Zero length quay edge')
        normals.append(((south-next_south)/length, (next_east-east)/length))
    sections = []
    for index, (east, south) in enumerate(edge):
        before = normals[max(0,index-1)]; after = normals[min(index,len(normals)-1)]
        divisor = max(.9, 1 + before[0]*after[0] + before[1]*after[1])
        inner = (east+width*(before[0]+after[0])/divisor, south-rise+width*(before[1]+after[1])/divisor)
        sections.append(((east,south), (east,south-rise), inner))
    return sections


def inset_face(edge, rise, width):
    sections = curb_sections(edge, rise, width)
    parts = ['<g data-finish="dressed-quay">']
    distance = 0.0; next_joint = 3.75
    for (foot, rim, back), (next_foot, next_rim, next_back) in zip(sections,sections[1:]):
        across = next_foot[0]-foot[0]; down = next_foot[1]-foot[1]; reach = math.hypot(across,down)
        shade = '#696053' if down/reach > .5 else '#756857'
        parts.append(poly([foot,next_foot,next_rim,rim],shade))
        parts.append(poly([foot,next_foot,(next_foot[0],next_foot[1]-.23*rise),(foot[0],foot[1]-.23*rise)],'#524c42'))
        parts.append(poly([rim,next_rim,next_back,back],'#c5b99f'))
        while next_joint < distance+reach:
            fraction = (next_joint-distance)/reach
            east = foot[0]+fraction*across; south = foot[1]+fraction*down
            inner = tuple(first+fraction*(last-first) for first,last in zip(back,next_back))
            parts.append(path(f'M{number(east)},{number(south-.25)}V{number(south-rise)}L{number(inner[0])},{number(inner[1])}',stroke='#847967',width=.32))
            next_joint += 6.5
        distance += reach
    return ''.join(parts)+'</g>'
