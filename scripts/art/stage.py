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
    return edge(rear) + edge(foot)[::-1] + [shifted(rear[0], 0, canopy['ribs'][0][2])]


def fan(canopy):
    rear, front, foot = profiles(canopy)
    parts = ['<g id="stage-glass-fan">']
    for bay, runs in enumerate(canopy['frameRuns']):
        def pane(across, down):
            return along(spline(rear, bay, across), spline(front, bay, across), down)
        def seam(start, end, count=6):
            return [pane(*along(start, end, step / count)) for step in range(count + 1)]
        back, lip, base = arc(rear, bay), arc(front, bay), arc(foot, bay)
        parts.append(f'<g data-glazing-bay="{bay}">')
        parts.append(poly(lip + base[::-1], ['#674b48', '#73524c', '#674b47'][bay % 3], '#4c3c39', .42))
        for across in (.04, .29, .57, .81):
            head = spline(front, bay, across); sill = spline(foot, bay, across)
            parts.append(stroke([head, sill], '#523b38', .49 if across == .04 else .28))
            parts.append(stroke([shifted(head, .35, .9), shifted(sill, .35, -.7)], '#906d62', .21))
        for level in (.17,.48,.70):
            parts.append(stroke([along(head,sill,level) for head,sill in zip(lip,base)],'#775955',.29))
        parts.append(stroke(base, '#473a39', .87))
        parts.append(poly(back + lip[::-1], ['#c5dae6','#c1d9e5','#cadde5'][bay % 3], '#80959f', .32))
        for across in (.19, .46, .74):
            left = across + (.03 if bay % 2 else 0)
            parts.append(poly([pane(left,.06),pane(left+.075,.06),pane(left+.01,.78),pane(left-.03,.81)], '#cfdee7'))
        rng=random.Random(f'stage-glass-{bay}')
        for across, down, end_across, end_down in runs:
            rib = seam((across, down), (end_across, end_down))
            parts.append(stroke(rib, '#92a4b0', .52))
            count=max(1,round(math.dist(rib[0],rib[-1])/2.3))
            for step in range(count):
                start=along((across,down),(end_across,end_down),(step+.06)/count)
                end=along((across,down),(end_across,end_down),(step+rng.uniform(.53,.96))/count)
                parts.append(stroke(seam(start,end),rng.choice(['#738591','#657d8a','#8296a3']),rng.uniform(.43,.64)))
            parts.append(stroke([shifted(point, .25, .48) for point in rib], '#dce5e8', .33))
        for index,start,depth,end,drop in canopy['beamRuns']:
            if index!=bay:continue
            beam=seam((start,depth),(end,drop));parts.append(stroke(beam,'#6d7880',.85))
            count=max(2,round(math.dist(beam[0],beam[-1])/1.85))
            for step in range(count):
                tip=along((start,depth),(end,drop),step/count);toe=along((start,depth),(end,drop),(step+.61)/count)
                parts.append(stroke(seam(tip,toe),'#444b52',.8))
        parts.extend([stroke(back,'#606d70',.63),stroke(lip,'#e1e2dd',1.06),stroke([shifted(point,0,1.05) for point in lip],'#464549',.74),'</g>'])
    back, lip = rear[0], front[0]
    parts.append(poly([back, lip, foot[0], shifted(back,0,canopy['ribs'][0][2])], '#e0dedb','#6c6464',.59))
    for fraction in (.12,.34,.61,.88):
        point=along(back,lip,fraction);parts.append(stroke([shifted(point,0,2.1),shifted(point,0,10.6)],'#c9c5c1',.29))
    for index in range(13):
        start=along(back,lip,index/13);end=along(back,lip,(index+.67)/13)
        parts.append(stroke([shifted(start,0,1.45),shifted(end,0,1.45)],'#59565a',.68))
    parts.append('</g>')
    return ''.join(parts)


def platform(model):
    rear_left,rear_right,front_right,front_left=model['corners']
    def board(across,down):return along(along(rear_left,rear_right,across),along(front_left,front_right,across),down)
    near=[shifted(board(step/12,1),0,-.8*math.sin(math.pi*step/12)) for step in range(13)]
    foot=[shifted(board(step/12,1),0,model['skirt'][3]*(1-step/12)+model['skirt'][2]*step/12) for step in range(13)]
    parts=['<g id="stage-floating-platform">',poly([rear_right,front_right,foot[-1],shifted(rear_right,0,model['skirt'][1])],'#b3b0aa','#52484b',.52),poly(near+foot[::-1],'#dedbd6','#575258',.51)]
    for fitting in model['sideFittings']:
        parts.extend([stroke(fitting,'#50494b',1.45),stroke([shifted(point,0,-.2) for point in fitting],'#e1ded9',.79)])
    parts.append(poly([rear_left,rear_right]+near[::-1],'#624741','#372f32',.7))
    rng=random.Random('stage-boards')
    for column in range(17):
        position=(column+.5)/17
        parts.append(stroke([board(position,.04),board(position,.94)],'#513b38',.32))
        for row in range(5):
            down=.065+row*.17+(column%2)*.045;length=rng.uniform(.046,.10)
            parts.append(stroke([board(position,down),board(position+.012,down+length)],rng.choice(['#352a2a','#473130','#79594e']),rng.uniform(.52,.85)))
    parts.extend([stroke([rear_left,rear_right],'#403638',.87),stroke(near,'#47383a',.70),stroke(foot,'#555258',.59),'</g>'])
    return ''.join(parts)


def stage(model):
    return fan(model['canopy']) + platform(model['deck'])
