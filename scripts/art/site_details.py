"""Site-specific visible forms, checked against the supplied map and first-party photographs."""

def poly(points,fill,stroke='#4a5147',width=.35):
    return '<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
def line(points,color,width=.4):
    return '<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>'
def roof(points,key,angle=0,gold=False):
    base='#b78c45' if gold else '#48534f';light='#e0be76' if gold else '#929e91';dark='#795e33' if gold else '#293b33'
    pattern=f'<defs><linearGradient id="{key}-slope" x1="0" y1="0" x2=".18" y2="1"><stop stop-color="{light}" stop-opacity=".30"/><stop offset=".35" stop-color="{base}" stop-opacity="0"/><stop offset="1" stop-color="{dark}" stop-opacity=".55"/></linearGradient><pattern id="{key}" width="1.45" height="2.8" patternUnits="userSpaceOnUse" patternTransform="rotate({angle})"><path d="M.25 0V2.8" stroke="{light}" stroke-width=".16" opacity=".55"/><path d="M1.2 0V2.8M0 1.4H1.45" stroke="{dark}" stroke-width=".14" opacity=".55"/></pattern></defs>'
    return pattern+poly(points,base,dark,.35)+poly(points,f'url(#{key}-slope)','none')+poly(points,f'url(#{key})',dark,.2)
def windows(x1,x2,y,height,step=7):
    out=[]
    for i,x in enumerate(range(int(x1),int(x2),step)):
        out.append(poly([(x,y),(x+step-1,y),(x+step-1,y+height),(x,y+height)],'#72553e','#493d32',.3))
        out.append(poly([(x+.7,y+height*.60),(x+step-1.7,y+height*.60),(x+step-1.7,y+height-.8),(x+.7,y+height-.8)],'#8d6847','#5c4633',.18))
        out.append(poly([(x+.8,y+1),(x+step-1.8,y+1),(x+step-1.8,y+height*.53),(x+.8,y+height*.53)],'#4a5143','#b09b70',.2))
        for t in [.32,.66]:
            xx=x+.8+(step-2.6)*t
            out.append(line([(xx,y+1),(xx,y+height*.53)],'#b6a276',.16))
        out.append(line([(x+.8,y+height*.28),(x+step-1.8,y+height*.28)],'#b6a276',.16))
        out.append(line([(x+step-1,y),(x+step-1,y+height)],'#b28c5e',.32))
    return ''.join(out)

def hotel():
    p=[]
    # Low, wide exterior and two continuous roof rings, preserving the original image silhouette.
    p.append(poly([(1133,593),(1283,595),(1281,611),(1134,609)],'#775542'))
    p.append(windows(1136,1280,597,11,8))
    p.append(roof([(1148,570),(1274,571),(1290,598),(1129,596)],'hotel-lower'))
    p.append(poly([(1146,558),(1275,560),(1273,581),(1145,580)],'#755746'))
    p.append(windows(1149,1271,566,12,7))
    p.append(poly([(1140,573),(1280,575),(1278,581),(1140,579)],'#e5e0d0','#bfc4b0',.3))
    # Recessed court and bent inner garden wings, not an empty square.
    p.append(poly([(1167,494),(1258,495),(1266,561),(1153,560)],'#aabf97','#879c7b',.4))
    p.append(poly([(1173,503),(1253,503),(1257,553),(1163,552)],'#cad5b4','#aebd9b',.3))
    for points in [
        [(1183,508),(1201,508),(1202,539),(1224,539),(1224,551),(1191,550),(1191,520),(1183,520)],
        [(1215,501),(1226,502),(1227,520),(1248,520),(1249,535),(1216,534)],
        [(1164,535),(1179,534),(1180,552),(1200,553),(1201,561),(1164,560)],
    ]: p.append(poly(points,'#785a45','#4c493b',.4))
    p.append(roof([(1181,507),(1203,506),(1205,537),(1225,537),(1227,542),(1198,543),(1198,512),(1182,513)],'hotel-inner'))
    p.append(roof([(1213,500),(1229,500),(1229,518),(1248,518),(1251,522),(1224,523),(1224,505),(1213,505)],'hotel-inner-b'))
    p.append(windows(1204,1223,544,5,4))
    p.append(windows(1230,1247,525,6,4))
    for a,b in [((1199,514),(1199,537)),((1226,505),(1226,517))]:
        p.append(line([a,b],'#c1c5ab',.45))
    # Fine stone paths and planting beds sit inside the existing folded courts.
    for points in [[(1170,521),(1187,521),(1187,539)],[(1232,540),(1254,540),(1256,548)],[(1204,514),(1210,514),(1210,530)]]:
        p.append(line(points,'#dfe0c8',1.2))
    for x,y,rx,ry in [(1172,543,3,2),(1184,527,2,3),(1237,545,3,2),(1207,522,1.8,3)]:
        p.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#819872" stroke="#b6c09a" stroke-width=".35"/>')
    # Four roof slopes around the observed outer ring.
    p.append(roof([(1161,483),(1265,484),(1255,501),(1173,500)],'hotel-north',0))
    p.append(roof([(1161,483),(1173,500),(1159,550),(1146,569)],'hotel-west',80))
    p.append(roof([(1265,484),(1278,571),(1264,550),(1255,501)],'hotel-east',88))
    p.append(roof([(1159,550),(1264,550),(1278,571),(1146,569)],'hotel-front',0))
    p.append(line([(1161,483),(1265,484),(1278,571),(1146,569),(1161,483)],'#b2b7a4',.7))
    p.append(line([(1173,500),(1255,501),(1264,550),(1159,550),(1173,500)],'#d6d3bc',.5))
    return ''.join(p)

def temple_hall():
    p=[poly([(877,683),(974,685),(980,703),(877,703)],'#ded8c4','#b9b69f',.4)]
    for i in range(5):
        p.append(poly([(909-i,695+i*1.5),(945+i,695+i*1.5),(946+i,697+i*1.5),(908-i,697+i*1.5)],'#e4dfcd','#b2b49b',.2))
    p.append(poly([(881,666),(969,668),(969,692),(881,691)],'#655340','#4c4435',.5))
    for x in range(886,970,10):
        p.append(line([(x,673),(x,692)],'#a27742',2.2))
        p.append(line([(x-2,678),(x+2,678)],'#d0ad63',.7))
    p.append(roof([(880,655),(965,657),(979,679),(868,677)],'temple-lower',0,True))
    p.append(poly([(897,649),(950,650),(953,663),(894,662)],'#79582f','#5b462a',.35))
    for x in range(900,953,8): p.append(line([(x,651),(x,661)],'#bc9652',1))
    p.append(roof([(901,638),(944,638),(967,661),(882,660)],'temple-upper',0,True))
    p.append(line([(899,638),(905,639),(940,639),(946,637)],'#e6c482',1))
    for y,x1,x2 in [(661,882,967),(679,868,979)]:
        p.append(f'<path d="M{x1-2} {y-4}Q{x1} {y+1} {x1+8} {y+1}L{x2-8} {y+1}Q{x2} {y+1} {x2+2} {y-4}" fill="none" stroke="#d5b36c" stroke-width=".9"/>')
    p.append(poly([(914,682),(938,682),(938,692),(914,692)],'#403f32','#8e7040',.4))
    return ''.join(p)

def stage():
    p=['<path d="M950 365C965 314 1007 285 1065 281L1137 286L1135 307C1052 300 1012 334 989 390Z" fill="#b7d0cf" stroke="#769c9c" stroke-width=".7"/>']
    # Paired Bezier boundaries give each rib its own position in the curved fan.
    def curve(points,t):
        return tuple((1-t)**3*points[0][i]+3*(1-t)**2*t*points[1][i]+3*(1-t)*t*t*points[2][i]+t**3*points[3][i] for i in range(2))
    outer=[(950,365),(965,302),(1050,272),(1137,286)]
    inner=[(989,390),(1010,332),(1060,302),(1135,307)]
    for i in range(1,24):
        a=curve(outer,i/24);b=curve(inner,i/24);p.append(line([a,b],'#668b8a',.4))
        p.append(line([(a[0]+.7,a[1]),(b[0]+.7,b[1])],'#e1eade',.3))
    p.append('<path d="M950 365 950 373 987 398 989 390Z" fill="#7e6251" stroke="#655b4b" stroke-width=".5"/>')
    p.append(poly([(1037,359),(1067,353),(1081,372),(1043,380)],'#775d44','#524938',.5))
    for i in range(1,10): p.append(line([(1038+i*3,359-i*.55),(1044+i*3,379-i*.55)],'#b79c72',.35))
    return ''.join(p)

def visitor():
    p=[]
    # Complete the short northern gallery hidden by the printed label.
    p.append(poly([(663,339),(789,331),(793,342),(665,351)],'#e6e2d4','#a7afa0',.3))
    p.append(roof([(659,337),(783,326),(797,337),(666,348)],'visitor-north',-5))
    # Keep the actual glass atrium outlines; thin structural bars replace the former giant generic pyramids.
    panes=[[(697,373),(716,360),(735,381),(718,392)],[(697,373),(718,392),(716,413),(695,399)],[(718,392),(760,390),(760,410),(716,413)],[(790,345),(803,330),(822,348),(820,397),(790,399)]]
    for index,points in enumerate(panes):
        p.append(poly(points,'#b3cfca','#6a9893',.45))
        x1=min(x for x,y in points);x2=max(x for x,y in points);y1=min(y for x,y in points);y2=max(y for x,y in points)
        d='M'+'L'.join(f'{x},{y}' for x,y in points)+'Z'
        p.append(f'<defs><clipPath id="glazing-{index}"><path d="{d}"/></clipPath></defs><g clip-path="url(#glazing-{index})">')
        for x in range(x1,x2+1,4):p.append(line([(x,y1),(x,y2)],'#719d98',.35))
        for y in range(y1,y2+1,5):p.append(line([(x1,y),(x2,y)],'#719d98',.35))
        p.append('</g>')
    return ''.join(p)

DETAILS={'visitor-court':visitor,'zen-courtyard':hotel,'temple-hall':temple_hall,'waterside-stage':stage}
