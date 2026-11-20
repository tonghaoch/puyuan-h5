"""The enclosed timber link between the two cross ranges at the islet bridge."""
import math
from .landscape import poly


def court_link(model, link, key):
    left, top, right, end, depth_x, depth_y, rise, height, kind = model
    joints, depth = link['joints'], link['capDepth']
    if kind != 'shop' or link['build'] != 'quay-timber-link':
        raise ValueError('Not a timber quay link')
    if not 0 < depth <= 1 or len(joints)<3 or joints[0]!=0 or joints[-1]!=1 or joints!=sorted(set(joints)):
        raise ValueError('Invalid range or joint stations')
    width = math.hypot(right-left,end-top)

    def at(station, return_depth, drop):
        return left+(right-left)*station+depth_x*return_depth,top+(end-top)*station+depth_y*return_depth+drop

    near, head, foot = .02, -.08, height-.11
    back, crest, pitch = near+depth, near+depth*.65, rise*.28

    def front(start, stop, upper, lower):
        return [at(start,near,upper),at(stop,near,upper),at(stop,near,lower),at(start,near,lower)]

    body, capping = [], []
    for start, stop in zip(joints,joints[1:]):
        span = stop-start; stile = min(.43/width,span*.13)
        body.append(poly([at(start,near,head),at(start,back,head-.12),at(start,back,foot-.12),at(start,near,foot)],'#695044'))
        body.append(poly(front(start,stop,head,foot),'#775343'))
        body.append(poly(front(start+stile,stop-stile,head+.54,foot-.51),'#805c4b'))
        body.append(poly(front(start+stile,stop-stile,foot-.74,foot-.46),'#684b3e'))
        for jamb in (start,stop-stile):
            body.append(poly(front(jamb,jamb+stile,head+.14,foot),'#574238'))
        body.append(poly(front(start,stop,head,head+.36),'#533f36'))
        body.append(poly(front(start,stop,foot-.27,foot),'#68594b'))
        capping.append(poly([at(start,back,head),at(stop,back,head),at(stop,crest,head-pitch),at(start,crest,head-pitch)],'#746961'))
        capping.append(poly([at(start,crest,head-pitch),at(stop,crest,head-pitch),at(stop,near,head),at(start,near,head)],'#584a42'))
        count = max(1,round(span*width/2.4))
        for joint in range(count):
            pos = start+span*(joint+.38)/count
            thickness = min(.12/width,span*.07)
            capping.append(poly([at(pos,crest,head-pitch),at(pos+thickness,crest,head-pitch),at(pos+thickness,near,head),at(pos,near,head)],'#8b8075'))
    return f'<g data-islet-link-body="{key}">'+''.join(body)+'</g>', f'<g data-islet-link-cap="{key}">'+''.join(capping)+'</g>'
