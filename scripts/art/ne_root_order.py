"""Order existing rooted stems at documented contacts without moving their forms."""
import json
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[2]/'src/data/ne-root-order.json'


def contact_order(visible,paint):
    ordered=sorted(visible,key=lambda model:model['y'])
    if not SOURCE.exists():return ''.join(paint(model) for model in ordered)
    groups=json.loads(SOURCE.read_bytes())['stations'];by_id={model['id']:model for model in ordered};station={};after={};forks={}
    for group in groups:
        present=[model for model in ordered if model['id'] in group['feet']]
        if len(present)<2:continue
        for model in present:
            roots=[[round(model['x']+stem['root'][0],3),round(model['y']+stem['root'][1],3)] for stem in model['stems']]
            if roots!=group['feet'][model['id']]:raise ValueError('B32 grounding changed: '+model['id'])
            station[model['id']]=roots
        for foreground,background in group['contactAfter']:
            if foreground[0] not in by_id:continue
            for other in background:
                if other[0] not in by_id:continue
                if station[other[0]][other[1]][1]>=station[foreground[0]][foreground[1]][1]:raise ValueError('B32 inverted source grounding')
                after.setdefault(tuple(foreground),set()).add(tuple(other))
        for key,index,start,tips in group.get('overhangingLeaders',[]):
            if key not in by_id:continue
            leaders=by_id[key]['stems'][index]['leaders']
            if leaders!=tips or not 0<start<len(tips):raise ValueError('B32 leader geometry changed: '+key)
            forks[key,index]=(range(start),range(start,len(tips)))
    result=[];seen=set();emitted=set();pending=[]
    def emit(member):
        identity,index=member;args=(forks[member][1],) if member in forks else ();result.append(paint(by_id[identity],index,identity not in seen,*args));seen.add(identity);emitted.add(member)
    for model in ordered:
        identity=model['id']
        if identity not in station:result.append(paint(model));continue
        for index in sorted(range(len(station[identity])),key=lambda idx:station[identity][idx][1]):
            member=(identity,index)
            if member in forks:result.append(paint(model,index,identity not in seen,forks[member][0]));seen.add(identity)
            if after.get(member,set())-emitted:pending.append(member);continue
            emit(member)
            for waiting in pending[:]:
                if after[waiting]<=emitted:emit(waiting);pending.remove(waiting)
    if pending:raise ValueError('Cyclic ground order')
    return ''.join(result)
