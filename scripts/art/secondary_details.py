"""Source-aligned finishing for the stone gate and red timber loft; no new place coordinates."""
from .site_details import poly,line,roof,windows

def north_gate():
    # The source shows a timber pavilion above terraces, with open lower bays.
    p=[poly([(527,561),(564,560),(570,579),(523,581)],'#c6c8b7','#8d9985',.35)]
    p.append(poly([(564,560),(570,562),(573,580),(570,579)],'#aab4a1','#8d9985',.3))
    for y in [564,568,572,576,580]:
        p.append(line([(526,y+.7),(570,y-1)],'#e0e0cb',.5))
        p.append(line([(526,y+1.3),(570,y-.4)],'#8b9985',.25))
        for x in range(529,569,8):
            offset=4 if y%8 else 0
            p.append(line([(x+offset,y-2),(x+offset,y+.3)],'#9da792',.22))
    # A narrow central stair crosses the stone courses.
    p.append(poly([(542,560),(551,560),(554,581),(539,581)],'#d9d9c5','#a0aa94',.25))
    for n in range(10):
        y=562+n*1.9;half=4.5+n*.26
        p.append(line([(546.5-half,y),(546.5+half,y)],'#879782',.34))
        p.append(line([(546.5-half,y+.45),(546.5+half,y+.45)],'#ece8d1',.3))
    for x,y in [(527,559),(535,559),(560,558),(567,559)]:
        p.append(poly([(x-1,y),(x+1,y),(x+1,y+4),(x-1,y+4)],'#d9d9c5','#8d9985',.22))
        p.append(line([(x-1.6,y),(x+1.6,y)],'#ece7ce',.5))
    # Recessed plaster panels remain behind the dark, source-visible frame.
    p.append(poly([(531,538),(558,538),(559,556),(531,557)],'#d6d5c2','#8a9480',.25))
    p.append(poly([(558,538),(564,540),(564,555),(559,556)],'#adb7a0','#64745f',.25))
    for x in [531,537,548,558]:
        p.append(line([(x,539),(x,557)],'#414c3f',1.25))
        p.append(line([(x+.45,539),(x+.45,556)],'#9b9d7c',.23))
        p.append(poly([(x-1,556),(x+1.1,556),(x+1.1,557.3),(x-1,557.3)],'#b5bca4','#7d8c77',.2))
    for y in [540,544,554,556]:
        p.append(line([(530,y),(560,y-.3)],'#39483b',.9))
        p.append(line([(530,y+.6),(560,y+.3)],'#aaa98a',.25))
    for x in range(534,560,3):
        p.append(line([(x,540.5),(x,543)],'#4c5848',.45))
    for x in [534,541,551,557]:
        p.append(line([(x,537.7),(x-1,539)],'#9d9e7b',.5))
    p.append(roof([(531,534),(557,533),(567,541),(525,541)],'north-watchtower-lower',0))
    p.append(poly([(535,530),(555,530),(556,536),(533,536)],'#5d6350','#35483b',.25))
    for x in range(536,555,3):p.append(line([(x,531),(x,535)],'#b7b28d',.25))
    p.append(roof([(534,522),(547,521),(561,534),(527,534)],'north-watchtower-upper',0))
    p.append(poly([(547,521),(561,534),(551,533)],'#35483e','#34463a',.2))
    p.append(line([(533,522),(547,521)],'#b1b59a',.6))
    for x,y in [(527,534),(525,541),(561,534),(567,541)]:
        p.append(f'<path d="M{x-1} {y-2}q1 2.5 3 2" fill="none" stroke="#939f87" stroke-width=".4"/>')
    return ''.join(p)

def dressing_loft():
    # Keep the taller red loft on the right of the two lower riverfront houses.
    p=[poly([(708,1146),(733,1140),(736,1164),(709,1170)],'#875b42','#584432',.35)]
    p.append(poly([(733,1140),(737,1142),(739,1162),(736,1164)],'#684939','#4c4434',.3))
    for n in range(3):
        y=1147+n*7.3
        for x in range(711,735,5):
            yy=y-(x-709)*.22
            p.append(poly([(x,yy),(x+3.2,yy-.7),(x+3.2,yy+3.7),(x,yy+4.4)],'#4e4c36','#b89562',.2))
            p.append(line([(x+1.5,yy-.3),(x+1.5,yy+4)],'#c0a271',.2))
            p.append(line([(x,yy+1.8),(x+3.2,yy+1.1)],'#b09465',.17))
        p.append(line([(708.7,y+6.1),(736,y+.1)],'#473d2e',.75))
        p.append(line([(708.7,y+6.6),(736,y+.6)],'#b28e5a',.23))
    for x in [709,718,727,735]:p.append(line([(x,1146-(x-709)*.22),(x+.5,1169-(x-709)*.22)],'#4a3e2e',.65))
    p.append(roof([(709,1137),(729,1133),(738,1140),(706,1147)],'dressing-loft-roof',-12))
    p.append(line([(709,1137),(729,1133)],'#aab39c',.55))
    return ''.join(p)

SECONDARY_DETAILS={'north-watchtower':north_gate,'dressing-house':dressing_loft}
