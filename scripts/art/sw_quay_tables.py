"""Dry quays: a walkable table, its supporting face, and the traces they replace."""

from .landscape import bank_course, poly


ACTIVE = ('merchant',)

TABLES = {
    'merchant-grass-shelf': {
        'case': 'merchant', 'trace': 'wood-497',
        'back': [(732.9,964.7),(745.8,961.8),(762.8,957.7),(779.2,953.5),(793.4,950.4)],
        'rim': [(734.9,976.0),(746.4,972.7),(761.3,967.3),(780.8,961.7),(793.7,958.0)],
        'join': {'cap': [(731.6,976.0),(734.3,975.5),(736.6,974.0)],
                 'toe': [(731.7,979.9),(735,979.0),(737.5,977.9)]},
    },
}


def active_tables():
    return ((name,table) for name,table in TABLES.items() if table['case'] in ACTIVE)


def retired_traces():
    return {table['trace'] for name,table in active_tables()}


def table_tops():
    result=[]
    for name,table in active_tables():
        grass='join' in table;back,rim=table['back'],table['rim'];top=poly(back+rim[::-1],'url(#spring-turf)' if grass else '#dfd6b9')
        if not grass:
            coping=[(east+(rear-east)*.15,south+(north-south)*.15) for (east,south),(rear,north) in zip(rim,back)]
            top+=poly(coping+rim[::-1],'#c9bda0')
        result.append(f'<g id="sw21-{name}-top">{top}</g>')
    return ''.join(result)


def bank_with_tables(course):
    for name,table in active_tables():
        if table.get('replaces')!=tuple(course['toe'][0]):continue
        rim,toe=table['rim'],table['toe'];result=[bank_course({'cap':rim,'toe':toe,'tone':'umber'})]
        east,north=table['back'][-1];edge=rim[-1];foot=toe[-1];mid=(edge[0]+(east-edge[0])*.37,edge[1]+(north-edge[1])*.37)
        result.append(poly([edge,mid,(mid[0],mid[1]+.8),foot],'#786a54'))
        return f'<g id="sw21-{name}-face">'+''.join(result)+'</g>'
    return bank_course(course)


def joined_faces():
    return ''.join(f'<g id="sw21-{name}-return">'+bank_course(table['join'])+'</g>' for name,table in active_tables() if 'join' in table)
