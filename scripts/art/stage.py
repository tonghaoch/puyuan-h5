"""Fan glazing, timber eave and lake platform in illustration coordinates."""
import math
import random
from .landscape import poly
from .street_houses import along, shifted, stroke


def spline(points, bay, amount):
    first, start, end, last = (points[max(0, min(len(points) - 1, index))] for index in (bay - 1, bay, bay + 1, bay + 2))
    return tuple(.5 * (2 * begin + (-before + finish) * amount + (2 * before - 5 * begin + 4 * finish - after) * amount ** 2 + (-before + 3 * begin - 3 * finish + after) * amount ** 3) for before, begin, finish, after in zip(first, start, end, last))


def profiles(canopy):
    ribs = canopy['ribs']
    return [rib[0] for rib in ribs], [rib[1] for rib in ribs], [shifted(rib[1], 0, rib[2]) for rib in ribs]


def arc(profile, bay):
    return [spline(profile, bay, step / 8) for step in range(9)]


def roof_outline(canopy):
    rear, front, foot = profiles(canopy)
    def edge(profile):
        return [spline(profile, bay, step / 8) for bay in range(len(profile) - 1) for step in range(8)] + [profile[-1]]
    return edge(rear) + edge(foot)[::-1] + [shifted(rear[0], 0, canopy['endDrop'])]


def glazing_bar(run, seed):
    start_x,start_y,end_x,end_y,gauge,camber=run
    head=(start_x,start_y);toe=(end_x,end_y);length=math.dist(head,toe)
    normal=(-(end_y-start_y)/length,(end_x-start_x)/length)
    def at(fraction):
        offset=4*fraction*(1-fraction)*camber
        return shifted(along(head,toe,fraction),normal[0]*offset,normal[1]*offset)
    rail=[at(step/6) for step in range(7)];rng=random.Random(seed)
    parts=[stroke([shifted(point,.28,.59) for point in rail],'#d8eaf3',.69),stroke(rail,('#b1c7d4','#9db5c2','#899fac')[gauge],(.62,.67,.79)[gauge])]
    count=max(1,round(length/3.15));inks=('#728d9b','#526f7e','#405866')
    for step in range(count):
        start=(step+rng.uniform(.035,.19))/count;stop=(step+rng.uniform(.66,.93))/count
        parts.append(stroke([at(start),at((start+stop)/2),at(stop)],inks[gauge],(.73,.85,.96)[gauge]))
    return '<g data-glazing-bar="'+str(gauge)+'">'+''.join(parts)+'</g>'


def lake_eave(bay, lip, base, canopy):
    start, end = canopy['capDepths'][bay:bay+2]
    nose = [shifted(point, 0, start+(end-start)*step/(len(lip)-1)) for step,point in enumerate(lip)]
    parts = [f'<g data-eave-bay="{bay}">', poly(nose + base[::-1], ['#70534e','#6b504b','#765650'][bay % 3])]
    for end, adjacent, width in ((0, 1, canopy['pierWidths'][bay]), (-1, -2, canopy['pierWidths'][bay+1])):
        across = width / (2 * math.dist(nose[end], nose[adjacent]))
        side_head = along(nose[end], nose[adjacent], across)
        side_foot = along(base[end], base[adjacent], across)
        parts.append(poly([nose[end],side_head,side_foot,base[end]], '#4d3837' if end == 0 else '#614744'))
    parts.extend([stroke(base,'#382b2b',1.03), poly(lip+nose[::-1],'#e1dddc'), stroke(nose,'#483b3a',.87), '</g>'])
    return ''.join(parts)


def fan(canopy):
    rear, front, foot = profiles(canopy)
    parts = ['<g id="stage-glass-fan">']
    for bay, runs in enumerate(canopy['muntins']):
        def pane(across, down):
            return along(spline(rear, bay, across), spline(front, bay, across), down)
        back, lip, base = arc(rear, bay), arc(front, bay), arc(foot, bay)
        parts.append(lake_eave(bay, lip, base, canopy))
        parts.append(f'<g data-glazing-bay="{bay}">')
        parts.append(poly(back + lip[::-1], ['#c5dae6','#c1d9e5','#cadde5'][bay % 3], '#80959f', .32))
        clip = f'stage-glass-panel-{bay}'
        parts.append(f'<defs><clipPath id="{clip}">{poly(back + lip[::-1], "white")}</clipPath></defs><g clip-path="url(#{clip})">')
        for across in (.19, .46, .74):
            left = across + (.03 if bay % 2 else 0)
            parts.append(poly([pane(left,.06),pane(left+.075,.06),pane(left+.01,.78),pane(left-.03,.81)], '#cfdee7'))
        for index,run in enumerate(runs):
            parts.append(glazing_bar(run,f'stage-glass-{bay}-{index}'))
        if bay == len(rear)-2:
            cheek = canopy['eastCheek']
            parts.extend([poly(cheek,'#e1e4dc'), stroke(cheek[2:],'#4f5352',.85)])
        parts.extend(['</g>',stroke(back,'#545b5a',.92),stroke(lip,'#45464a',.89),'</g>'])
    for head, sill in zip(rear[1:],front[1:]):
        parts.append(stroke([head,sill],'#768b97',.87))
        count=max(2,round(math.dist(head,sill)/2.8))
        for step in range(count):
            parts.append(stroke([along(head,sill,(step+.07)/count),along(head,sill,(step+.67)/count)],'#455960',.91))
    back, lip = rear[0], front[0]
    end_foot=shifted(back,0,canopy['endDrop'])
    parts.append(poly([back, lip, foot[0], end_foot], '#e8e5e3','#746d6c',.48))
    parts.append(stroke([end_foot,foot[0]],'#504a48',.92))
    for fraction in (.12,.34,.61,.88):
        point=along(back,lip,fraction);parts.append(stroke([shifted(point,0,2.1),shifted(point,0,10.6)],'#c9c5c1',.29))
    for index in range(16):
        start=along(back,lip,index/16);end=along(back,lip,(index+.74)/16)
        parts.append(stroke([shifted(start,0,.53),shifted(end,0,.72)],'#393b3b',1.01))
    flashing=canopy['endFlashing'];cornice=[shifted(along(back,lip,at),0,drop) for at,drop in flashing]
    parts.extend([stroke(cornice,'#b4b8b2',.76),stroke([shifted(point,0,.64) for point in cornice],'#f4f3e8',.52)])
    for near,far in zip(cornice,cornice[1:]):
        clips=max(1,round(math.dist(near,far)/3.2))
        for index in range(clips):parts.append(stroke([along(near,far,(index+.08)/clips),along(near,far,(index+.73)/clips)],'#494e4a',.91))
    parts.append('</g>')
    return ''.join(parts)


def platform(model):
    rear_left,rear_right,front_right,front_left=model['corners']
    def board(across,down):return along(along(rear_left,rear_right,across),along(front_left,front_right,across),down)
    def skirt(across):return shifted(board(across,1),0,model['skirt'][3]*(1-across)+model['skirt'][2]*across)
    foot=[skirt(0),skirt(1)]
    inset=model['bearer']['inset']/math.dist(*foot)
    support=[skirt(inset),skirt(1-inset)]
    parts=['<g id="stage-floating-platform">',poly(support+[shifted(point,0,model['bearer']['depth']) for point in support[::-1]],'#303e3f')]
    for fitting in model['sideFittings']:
        parts.extend([stroke([shifted(point,0,.42) for point in fitting],'#3e4749',1.25),stroke(fitting,'#deddda',.90)])
    parts.extend([poly([rear_left,front_left,foot[0],shifted(rear_left,0,model['skirt'][0])],'#958f90','#504a4d',.5),
                  poly([front_left,front_right,foot[1],foot[0]],'#c5c3c1','#615d5e',.44)])
    parts.append('<g data-stage-boards="true">')
    for column in range(model['planks']):
        left=column/model['planks'];right=(column+1)/model['planks']
        parts.append(poly([board(left,0),board(right,0),board(right,1),board(left,1)],('#563b32','#594038','#61463b','#513a34')[column%4],'#46332e',.28))
        for depth in (.14,.47,.85):
            nail=board(left+(right-left)*.32,depth)
            parts.append(stroke([nail,shifted(nail,.16,.51)],'#392922',.52))
    parts.extend(['</g>',stroke([rear_left,rear_right],'#3c3230',.85),stroke([front_left,front_right],'#443431',.65),'</g>'])
    return ''.join(parts)


def stage(model):
    return fan(model['canopy']) + platform(model['deck'])
