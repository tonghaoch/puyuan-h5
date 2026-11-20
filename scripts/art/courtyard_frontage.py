"""Closed courtyard fronts: recessed shutters, separate piers and solid end walls."""
from .landscape import poly
from .street_houses import along, shifted, stroke


def courtyard_front(frame, height, render_front):
    left, right = frame['beam']
    feet = frame.get('footDepths', [height, height])

    def point(station, drop):
        depth = feet[0] + (feet[1]-feet[0])*station
        return shifted(along(left, right, station), 0, drop*depth/height)

    def strip(start, end, head, foot, paint):
        return poly([point(start, head), point(end, head), point(end, foot), point(start, foot)], paint)

    if 'openings' in frame:
        parts = [render_front({key:value for key,value in frame.items() if key!='apronJoints'}, height)]
        sill = height * frame['apronLevel']
        parts.append(stroke([point(0, sill), point(1, sill)], '#655a54', .72))
        for station in frame['apronJoints']:
            parts.append(stroke([point(station, sill), point(station, height-.6)], '#898179', .54))
        parts.append(stroke([point(0, height-.3), point(1, height-.3)], '#69665e', .63))
    else:
        parts = []
        if 'limeEnd' in frame:
            end = frame['limeEnd']
            parts += [poly([right, end, shifted(end, 0, height), point(1, height)], '#e6e2db'),
                      stroke([end, shifted(end, 0, height), point(1, height)], '#57534e', .77)]
        parts.append(strip(0, 1, 0, height, '#684c43'))
        for start, end in zip(frame['columns'], frame['columns'][1:]):
            stile = start + (end-start)*.52
            jamb, stop = start + (end-start)*.07, end - (end-start)*.07
            parts += [strip(jamb, stop, .75, height-.46, '#725148'),
                      strip(jamb, stop, .74, 1.38, '#9d8276'),
                      strip(jamb, stop, 1.38, 1.72, '#513a35'),
                      stroke([point(stile, 1.72), point(stile, height-.48)], '#533c35', .37)]
        parts += [strip(0, 1, 0, .66, '#4e3b36'), strip(0, 1, height-.42, height, '#59443b')]
        lime = frame.get('limePiers', [])
        for station in frame['columns']:
            pale = station in lime
            parts.append(stroke([point(station, .84 if pale else .18), point(station, height-.12)],
                                '#dfd5c9' if pale else '#443530', 1.12 if pale else .64))
    bays = f' data-bays="{len(frame["columns"])-1}"' if 'columns' in frame else ''
    return '<g data-infill="courtyard-front"'+bays+'>'+''.join(parts)+'</g>'
