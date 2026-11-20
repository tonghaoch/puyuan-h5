"""Dry coping, supported toes and turned ends at two surveyed water edges."""

from .landscape import poly


def ledge(stations, shades):
    faces = []
    for (foot, rim, back), (next_foot, next_rim, next_back), shade in zip(stations, stations[1:], shades):
        faces.append(poly([foot, next_foot, next_rim, rim], shade))
        faces.append(poly([rim, next_rim, next_back, back], '#e3e1d3'))
    return ''.join(faces)


def pool_turn():
    arc_seat = [
        ((1152.8,353.8), (1152.8,350.6), (1153.9,348.6)),
        ((1156.0,356.3), (1157.1,352.7), (1158.2,350.7)),
        ((1158.1,357.8), (1160.2,353.8), (1161.1,351.9)),
    ]
    lowered_seat = [
        ((1167.0,360.2), (1167.5,358.8), (1168.5,355.6)),
        ((1175.7,362.9), (1176.3,361.1), (1177.4,357.9)),
        ((1182.2,364.0), (1182.5,363.4), (1183.1,360.3)),
        ((1188.6,365.3), (1188.9,363.9), (1189.4,361.6)),
        ((1194.0,365.8), (1194.4,363.8), (1194.8,361.8)),
    ]
    return '<g id="pool-turn-stone-seats">'+ledge(arc_seat, ['#6b6259']*2)+ledge(lowered_seat, ['#70604c']*4)+'</g>'


def quay_steps():
    return pool_turn()
