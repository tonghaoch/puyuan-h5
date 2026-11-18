"""Generate seven decorative card illustrations. Main map: prepare-reference-map.py."""
from pathlib import Path
import random
import math

random.seed(26)
OUT = Path(__file__).resolve().parents[1] / 'public' / 'art'
OUT.mkdir(parents=True, exist_ok=True)
parts = []

def add(s): parts.append(s)
def path(d, fill='none', stroke='none', width=1, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'

def building(x, y, scale=1, roof='#526c68', variant=0):
    p = [f'<g transform="translate({x} {y}) scale({scale})">']
    p += [path('M0 68 111 94 163 66 54 41Z', '#5b654b', extra='opacity=".16" transform="translate(10 27)"')]
    p += [path('M12 49 108 70 108 108 12 86Z', '#eee2bf'), path('M108 70 150 45 150 83 108 108Z', '#c4b998')]
    p += [path('M14 83 107 104 107 110 14 89Z', '#b6a78b'), path('M108 104 149 79 149 85 108 110Z', '#9c927e')]
    for i in range(5):
        xx = 23 + i * 17
        yy = 59 + i * 3.8
        p += [path(f'M{xx} {yy}v24l11 2.5v-24Z', '#736a52'), path(f'M{xx+2} {yy+2}v20l7 1.6v-20Z', '#a69d75')]
        p += [path(f'M{xx+5.5} {yy+2}v21m-3.5-12 7 1.6', stroke='#5d5a48', width='.9')]
    for i in range(2):
        xx=117+i*15; yy=72-i*9
        p += [path(f'M{xx} {yy}v20l8-5v-20Z', '#6e705b')]
    p += [path('M11 53 109 75 152 49', stroke='#6c6551', width='5')]
    p += [path('M40 11 77 -4Q117 9 166 15L133 36Z', '#74867a')]
    p += [path('M40 11 133 32Q126 53 111 65Q59 58 2 40Q30 34 40 11Z', roof)]
    p += [path('M133 32 166 15Q161 34 154 44L111 65Q128 46 133 32Z', '#3a514e')]
    for i in range(1,14):
        a=i/14; xx=40+93*a; yy=11+21*a; bx=2+109*a; by=40+25*a
        p += [path(f'M{xx:.1f} {yy:.1f}Q{(xx+bx)/2+4:.1f} {(yy+by)/2+5:.1f} {bx:.1f} {by:.1f}', stroke='#d3d4b8', width='.85', extra='opacity=".32"')]
    for j in range(1,5):
        t=j/5
        p += [path(f'M{40-38*t:.1f} {11+29*t:.1f}Q80 {28+25*t:.1f} {133-22*t:.1f} {32+33*t:.1f}', stroke='#1f3835', width='.75', extra='opacity=".45"')]
    p += [path('M1 36Q2 41 13 44L100 65Q110 69 114 60M39 7Q40 12 50 14L124 31Q133 34 136 26M154 40 167 15', stroke='#d8d1ad', width='3')]
    p += [path('M2 42 110 68 155 43', stroke='#304943', width='2')]
    if variant % 3 == 0:
        for xx, yy in [(22,56),(93,72)]:
            p += [path(f'M{xx} {yy}v5', stroke='#5b4831'), f'<ellipse cx="{xx}" cy="{yy+9}" rx="3.6" ry="5" fill="#be7447"/>', path(f'M{xx} {yy+14}v4', stroke='#ba8e42')]
    if variant % 4 == 0:
        p += [path('M56 77v18l15 3V80Z','#554e3e'), path('M58 77 69 80v14l-11-2Z','#ad734a')]
    p += ['</g>']
    return ''.join(p)

def tree(x, y, s=1, pink=False):
    c = ['#7c9271','#91a17a','#a4ae82','#bcc394'] if not pink else ['#c78f8e','#d7aaa2','#e1b9ab','#f0cfc0']
    p=[f'<g transform="translate({x} {y}) scale({s})">', '<ellipse cy="4" rx="19" ry="7" fill="#57634d" opacity=".12"/>', path('M0 2v-32m0 21-7-11m7 4 9-11',stroke='#7a7960',width='2.8')]
    for cx,cy,r in [(-9,-25,11),(8,-27,13),(0,-38,12),(-10,-39,8),(10,-41,8),(0,-49,7)]:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{random.choice(c)}"/>')
    p += [path('M-12-34q5-6 10-3m1-9q4-6 9-2m-5 24 6-5',stroke='#e6e5bb',width='1.8',extra='opacity=".5"'),'</g>']
    return ''.join(p)

def bridge(x,y,s=1,rot=0):
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">' + path('M-55 0Q0-40 55-4L55 15Q0-19-55 19Z','#b5ad8c') + path('M-55 0Q0-40 55-4L52-17Q0-50-52-13Z','#e7dcb8', '#b6ab8e',1) + path('M-55-12Q0-49 55-16M-55 5Q0-31 55 2',stroke='#eee4c6',width=4) + ''.join(path(f'M{xx} {-32+abs(xx)*.35}v11',stroke='#d2c8a9',width=3) for xx in range(-48,49,12)) + '</g>'

# Card illustrations use the same visual world and independent compositions.
for kind in ['stage','temple','market','tea','food','noodles','dessert']:
    bg={'stage':'#cad4bf','temple':'#dbdac1','market':'#ded1af','tea':'#c6d0b9','food':'#ded0b0','noodles':'#e5d7b9','dessert':'#d7cfaf'}[kind]
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="450" viewBox="0 0 720 450"><defs><radialGradient id="bg"><stop stop-color="#f1e8ce"/><stop offset="1" stop-color="{bg}"/></radialGradient><pattern id="mat" width="12" height="12" patternUnits="userSpaceOnUse"><path d="M0 2h12M2 0v12" stroke="#b8aa85" stroke-width=".5" opacity=".35"/></pattern></defs><rect width="720" height="450" fill="url(#bg)"/>']
    if kind in ['stage','temple','market']:
        s += [path('M0 310Q200 240 370 320T720 290V450H0Z','#94b6a5'),path('M0 301Q200 231 370 311T720 281',stroke='#e7d9b8',width=12)]
        for k in range(7): s.append(path(f'M{20+k*100} {355+(k%3)*20}q40-8 65 0',stroke='#d2e0c3',width=2))
        s += [building(105,195,1.05,'#63746a',2),building(300,130,1.7,'#556e63' if kind!='temple' else '#948759',3),building(500,222,.85,'#5e7166',1)]
        if kind=='market':
            for i in range(4): s.append(building(80+i*143,250,.55,['#8b7b60','#6a8071'][i%2],i))
        s += [tree(70,290,1.7,True),tree(620,300,1.8),tree(570,180,1.2,True)]
        s += [bridge(260,345,1.15,8)]
    else:
        s += ['<ellipse cx="370" cy="290" rx="250" ry="105" fill="#b09f77" opacity=".17"/>',path('M95 225 462 150 645 285 278 372Z','#cdbb92'),path('M95 225 462 150 645 285 278 372Z','url(#mat)')]
        if kind=='tea':
            s += ['<ellipse cx="350" cy="285" rx="84" ry="37" fill="#9da88b"/>','<ellipse cx="350" cy="260" rx="67" ry="27" fill="#ebdfbd"/>',path('M283 259Q290 335 350 330Q411 330 417 259Z','#758e79'),'<ellipse cx="350" cy="257" rx="63" ry="25" fill="#e7ddbc"/>','<ellipse cx="350" cy="257" rx="53" ry="20" fill="#9b9a5d"/>',path('M412 268Q470 263 445 303Q430 317 409 303',stroke='#748c77',width=12),path('M334 210q-22-30 0-54m25 50q-15-23 4-48',stroke='#f7f1dc',width=5,extra='opacity=".8"')]
            for x,y in [(500,220),(525,245),(475,260)]:
                s += [f'<ellipse cx="{x}" cy="{y}" rx="25" ry="14" fill="#b49362"/>',f'<ellipse cx="{x}" cy="{y-7}" rx="25" ry="14" fill="#e1c48c"/>',path(f'M{x-14} {y-8}h28m-14-6v12',stroke='#bc9d67',width=1.5)]
        elif kind=='dessert':
            s += ['<ellipse cx="360" cy="285" rx="130" ry="58" fill="#7d927e"/>','<ellipse cx="360" cy="277" rx="117" ry="48" fill="#e9dfbc"/>']
            for x,y in [(305,275),(365,255),(420,280)]:
                s += [path(f'M{x-28} {y}v-30q28-20 56 0v30q-28 20-56 0Z','#d8bc85'),f'<ellipse cx="{x}" cy="{y-30}" rx="28" ry="13" fill="#f0dda3"/>']
                for j in range(12): s.append(f'<circle cx="{x+random.randint(-19,19)}" cy="{y-30+random.randint(-7,7)}" r="1.7" fill="#bd924b"/>')
        else:
            s += ['<ellipse cx="365" cy="310" rx="117" ry="42" fill="#9b9e7a" opacity=".4"/>',path('M245 243Q260 345 365 345Q472 345 485 243Z','#789180'),'<ellipse cx="365" cy="244" rx="120" ry="52" fill="#eee3bf"/>','<ellipse cx="365" cy="244" rx="106" ry="43" fill="#b7a16d"/>']
            for j in range(12):
                x=290+random.randint(0,80);y=225+random.randint(0,25)
                s.append(path(f'M{x} {y}q30-25 70 3t-50 17',stroke='#ead5a2',width=3))
            for x,y in [(310,226),(400,238),(360,270)]: s.append(path(f'M{x} {y}q-25-30-10-37q29 8 10 37Z','#718d55'))
            for x,y in [(345,227),(386,254)]: s.append(f'<ellipse cx="{x}" cy="{y}" rx="22" ry="12" fill="#b47c51" transform="rotate(-20 {x} {y})"/>')
            s += [path('M455 142 300 320m166-174L313 324',stroke='#6a674c',width=5),path('M335 167q-20-20 0-47m34 42q-15-21 7-48',stroke='#f7f1dc',width=5,extra='opacity=".7"')]
        s += [path('M90 100q40 100 110 80m-75-45q-40-35-55-20 12 30 55 20m20 25q-5-50 18-55 20 30-18 55',stroke='#859476',width=3,fill='#98a381')]
    s.append('</svg>')
    (OUT/f'{kind}.svg').write_text(''.join(s))
print('Created 7 decorative card artworks.')
