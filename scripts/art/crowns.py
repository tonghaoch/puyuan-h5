"""Ink-and-wash botanical forms drawn from six crown widths and a few main branches."""
import math

from .landscape import ellipse, number, path

PIGMENTS={
    'leaf':['#29452e','#437646','#629358','#82af69','#9cc787','#b9dca0','#d3eabc'],
    'spring':['#354a23','#52732d','#71952d','#90b343','#adc65f','#c8dd88','#dfecb0'],
    'pink':['#5e3d3a','#8e5a50','#af796e','#d09588','#e2ab9d','#f1c3b4','#f9daca'],
    'gold':['#58432c','#84603c','#a87e3d','#c69b4c','#d7b364','#ebd391','#f4e3b2'],
}


def curve(points):
    result=[f'M{number(points[0][0])},{number(points[0][1])}']; size=len(points)
    for index,start in enumerate(points):
        before,end,after=(points[(index+offset)%size] for offset in (-1,1,2))
        first=[start[axis]+(end[axis]-before[axis])*.12 for axis in (0,1)]
        second=[end[axis]-(after[axis]-start[axis])*.12 for axis in (0,1)]
        result.append('C'+' '.join(f'{number(x)},{number(y)}' for x,y in (first,second,end)))
    return ''.join(result)+'Z'


def crown(model,rng):
    form=model['crown'];volume=form['volume'];rows=volume['stations'];lobes=form['lobes']
    colors=PIGMENTS[form['tone']];flowers=form['tone']=='pink';wash=volume['wash'];grain=volume['grain']
    seed=model['id'];key='crown-volume-'+seed;scale=model['scale'];ink='#69473e' if flowers else '#36452d'
    outline=[]
    for side,stations in ((1,rows),(-1,rows[::-1])):
        outline.extend((center+side*radius,level) for level,center,radius in stations)
    body=curve(outline); height=rows[-1][0]-rows[0][0];foot_x=rows[-1][1]*.45
    foot_y=max(.6,rows[-1][0]+1.6*scale)
    parts=[f'<g data-crown="{seed}" transform="translate({model["x"]} {model["y"]})">',
           ellipse(foot_x+.7*scale,foot_y,3.8*scale,1.05*scale,'#668656','opacity=".31"'),
           f'<defs><clipPath id="{key}">'+path(body,'white')+'</clipPath></defs>']
    for cx,cy,rx,ry,band,shade,direction in lobes:
        neck_x=foot_x*.65+cx*.35;neck_y=foot_y+(cy-foot_y)*.44
        parts.append(path(f'M{number(foot_x)},{number(foot_y)}Q{number(neck_x)},{number(neck_y)} {number(cx)},{number(cy)}',stroke=ink,width=.83*scale))
    parts.extend([path(body,colors[wash],extra=f'opacity="{.87-grain*.12:.2f}"'),f'<g clip-path="url(#{key})">'])
    for index,(cx,cy,rx,ry,band,shade,direction) in enumerate(lobes):
        angle=math.pi*direction/4;glow=key+f'-wash-{index}'; light=min(6,band+2);dark=max(0,band)
        parts.append(f'<defs><radialGradient id="{glow}" cx="{number(.50+.23*math.cos(angle))}" cy="{number(.50+.23*math.sin(angle))}" r=".69"><stop stop-color="{colors[light]}"/><stop offset=".68" stop-color="{colors[band+1]}" stop-opacity=".87"/><stop offset="1" stop-color="{colors[dark]}" stop-opacity="0"/></radialGradient></defs>')
        parts.append(ellipse(cx,cy,rx*1.35,ry*1.35,f'url(#{glow})'))
    marks={};sprigs=[]
    def mark(color,xx,yy,wide,tall,tilt):
        command=f'M{number(xx)},{number(yy)}q{number(-wide*.94)},{number(-tall*.68)} {number(tilt)},{number(-tall)}q{number(wide*1.22)},{number(tall*.36)} {number(-tilt)},{number(tall)}Z'
        marks.setdefault(color,[]).append(command)
    for cx,cy,rx,ry,band,shade,direction in lobes:
        sun=direction*math.pi/4
        for bough in range(max(2,round(rx*ry*(.048+grain*.008)))):
            angle=rng.random()*math.tau;rad=rng.random()**.48*.93
            xx=cx+rx*math.cos(angle)*rad; yy=cy+ry*math.sin(angle)*rad
            radius=min(3.2,max(1.35,math.sqrt(rx*ry)*rng.uniform(.24,.45)))
            light_side=math.cos(angle-sun)*rad; shadow=max(0,band-1); bright=min(6,band+2+int(grain>1))
            tip_x=xx+radius*.96*math.cos(sun);tip_y=yy+radius*.82*math.sin(sun)
            sprigs.append(f'M{number(xx-radius*.65)},{number(yy+radius*.75)}q{number(radius*.74)} {number(-radius*.36)} {number(tip_x-xx+radius*.65)} {number(tip_y-yy-radius*.75)}')
            for leaf in range(5+grain):
                turn=rng.random()*math.tau;distance=radius*rng.random()**.55
                tipx=xx+distance*math.cos(turn);tipy=yy+distance*.88*math.sin(turn)
                lit=light_side+.58*math.cos(turn-sun)+rng.uniform(-.5,.5)
                tone=colors[bright if lit>.18 else shadow if lit<-.23 else min(6,band+1)]
                size=rng.uniform(.85,1.35)*(1+.12*grain)
                mark(tone,tipx,tipy,size*1.17,size*1.32,.42*math.cos(turn))
        for spray in range(max(4,round(rx*ry*(.22+grain*.023)))):
            angle=rng.random()*math.tau;rad=rng.random()**.48*1.17
            xx=cx+rx*math.cos(angle)*rad; yy=cy+ry*math.sin(angle)*rad
            shaded=rng.random()<.30+shade*.07-.26*math.cos(angle-sun)*rad
            length=rng.uniform(.86,1.55)*min(1.55,max(.88,rx*.31)); tilt=rng.uniform(-.54,.54)*length
            tone=colors[max(0,band-1-int(grain>1)) if shaded else min(6,band+2+int(grain>1))]
            if shaded and spray%3==0:tone=ink
            mark(tone,xx,yy,length*.96,length*1.28,tilt)
            mark(tone,xx+.63*length,yy+.20*length,length*.66,length*.72,-tilt+.20)
            if flowers or spray%3==0:mark(colors[min(6,band+3)],xx-.68,yy-.44,length*.69,length*.74,tilt)
            if shaded and spray%4==0:sprigs.append(f'M{number(xx+.5)},{number(yy+.7)}q1.04 1.15 .79 2.26')
    parts.append(path(''.join(sprigs),stroke=ink,width=.57,extra='opacity=".82"'))
    parts.extend(path(''.join(pieces),tone) for tone,pieces in marks.items())
    parts.append('</g>')
    for side in (-1,1):
        for upper,lower in zip(rows,rows[1:]):
            for mark_index in range(max(1,round((lower[0]-upper[0])/2.0))):
                fraction=rng.uniform(.1,.92); xx=upper[1]+(lower[1]-upper[1])*fraction+side*(upper[2]+(lower[2]-upper[2])*fraction);yy=upper[0]+(lower[0]-upper[0])*fraction
                if rng.random()<.18:continue
                parts.append(path(f'M{number(xx-side*.45)},{number(yy-.7)}q{number(side*.95)} .28 {number(side*.48)} {number(min(2.0,height*.11))}',stroke=ink if mark_index%3!=1 else colors[max(0,wash-1)],width=rng.uniform(.42,.84)))
    return ''.join(parts)+'</g>'
