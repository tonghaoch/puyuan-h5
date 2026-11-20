"""Survey the width and centre of visible tawny streets along authored guide lines, offline."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from art.atlas_layout import PRINT_EXCLUSIONS

ROOT = Path(__file__).resolve().parents[1]

GUIDES = {
    'south-perimeter': (29, [(148,1365),(343,1337),(469,1317),(678,1314),(860,1284),(1052,1254),(1234,1226),(1320,1218)]),
    'west-perimeter': (27, [(138,1330),(158,1211),(184,1093),(265,1052),(368,1020),(432,1002)]),
    'visitor-approach': (24, [(608,303),(607,365),(604,435),(566,466),(473,496)]),
    'visitor-north-lane': (11, [(619,323),(709,311),(812,303),(879,290),(973,273),(1081,262),(1151,254)]),
    'visitor-east-lane': (4, [(873,295),(876,332),(884,383)]),
    'west-spine': (6, [(466,517),(475,557),(494,610),(492,675),(492,706),(500,765),(504,845),(514,880),(526,912),(537,957),(526,999)]),
    'watch-crossing': (4, [(495,701),(530,693),(558,691),(599,681)]),
    'watch-east-lane': (4, [(541,590),(547,633),(547,677),(562,688),(569,738),(575,765)]),
    'fuma-riverside': (5, [(598,682),(630,698),(675,697),(741,679),(785,662),(833,644),(851,619),(852,558),(856,512)]),
    'fuma-north-lane': (6, [(770,523),(819,518),(872,510)]),
    'central-west-lane': (5, [(602,755),(627,784),(636,826),(647,872),(668,862),(730,851),(783,844)]),
    'central-island-west': (5, [(721,724),(762,726),(772,786),(783,841),(805,872)]),
    'temple-west-lane': (6, [(823,694),(843,715),(850,767),(864,833),(876,870),(894,910)]),
    'central-canal-lane': (5, [(521,990),(604,981),(672,974),(740,955),(802,937),(872,918),(958,892),(1035,874),(1106,857),(1188,839),(1230,845)]),
    'temple-east-lane': (5, [(1132,471),(1128,521),(1124,579),(1117,645),(1119,710),(1122,752),(1099,775),(1089,803),(1111,851),(1129,885),(1141,917)]),
    'designer-quay-lane': (5, [(1297,436),(1299,481),(1299,534),(1292,585),(1289,628),(1294,682),(1264,726),(1242,776),(1213,817),(1210,846)]),
    'south-west-canal-lane': (6, [(285,1259),(291,1190),(297,1149),(344,1105),(401,1058),(470,1048),(523,1023),(564,1002)]),
    'longwan-quay': (5, [(373,1206),(444,1186),(516,1166),(601,1142),(621,1080),(624,1046),(620,1033),(526,1047)]),
    'south-cross-lane': (10, [(707,1116),(744,1107),(775,1097),(810,1091),(840,1081),(870,1076),(915,1060),(945,1043),(1000,1015),(1030,1000),(1090,982),(1147,949)]),
    'south-market-spine': (7, [(856,965),(875,1007),(890,1048),(925,1083),(935,1139),(939,1185),(949,1216)]),
    'south-island-spine': (5, [(1036,900),(1062,950),(1084,994),(1107,1059),(1124,1126),(1136,1195),(1143,1225)]),
    'east-island-spine': (6, [(1275,951),(1263,997),(1264,1052),(1262,1101),(1266,1157),(1269,1200)]),
}


def survey(rgb):
    red, green, blue = np.moveaxis(rgb.astype(np.int16), -1, 0)
    ochre = ((red>169)&(red<212)&(green>151)&(green<194)&(red-green>=9)&(red-green<=24)
             &(green-blue>=12)&(green-blue<=30)).astype(np.uint8)
    for outline in PRINT_EXCLUSIONS:
        cv2.fillPoly(ochre,[np.int32(outline)],0)
    ochre = cv2.medianBlur(ochre,3)
    result = []
    for name,(nominal,guide) in GUIDES.items():
        knots = np.float32(guide)
        distance = np.r_[0,np.cumsum(np.linalg.norm(np.diff(knots,axis=0),axis=1))]
        stations = np.linspace(0,distance[-1],1+int(np.ceil(distance[-1]/6)))
        raw = np.column_stack([np.interp(stations,distance,column) for column in knots.T])
        tangents = np.gradient(raw,axis=0); tangents /= np.linalg.norm(tangents,axis=1)[:,None]
        normals = tangents[:,::-1]*[1,-1]; reach = nominal+13
        offsets = np.arange(-reach,reach+1)
        sides = []
        for point,normal,tangent in zip(raw,normals,tangents):
            samples = point + offsets[:,None,None]*normal + np.array([-1.5,0,1.5])[None,:,None]*tangent
            horizontal,vertical = np.moveaxis(np.rint(samples).astype(int),-1,0)
            street = np.sum(ochre[vertical,horizontal],axis=1)>=2
            spans = np.flatnonzero(np.diff(np.r_[False,street,False])).reshape(-1,2)
            options = []
            for start,end in spans:
                width = end-start; center = offsets[start]+(width-1)/2
                if max(2,nominal*.37)<=width<=nominal*1.85+1 and abs(center)<max(nominal*.65,10):
                    options.append((abs(center)+abs(width-nominal)*.40,center,width))
            sides.append(min(options)[1:] if options else (np.nan,np.nan))
        sides = np.array(sides); good = ~np.isnan(sides[:,0])
        if good.sum()<4:continue
        splits = np.split(np.flatnonzero(good),np.flatnonzero(np.diff(stations[good])>35)+1)
        for section in splits:
            if len(section)<4:continue
            first,last = section[[0,-1]]; positions = stations[first:last+1]
            center,width = [np.interp(positions,stations[section],column[section]) for column in sides.T]
            smooth = lambda values: np.convolve(np.pad(values,(1,1),mode='edge'),[.25,.5,.25],'valid')
            central = raw[first:last+1]+normals[first:last+1]*smooth(center)[:,None]; width=smooth(width)
            simplified = cv2.approxPolyDP(np.float32(central),1.25,False).reshape(-1,2)
            selected = set(np.argmin(np.linalg.norm(central-point,axis=1)) for point in simplified)
            for index in range(0,len(central),5):selected.add(index)
            profile = [[*np.round(central[index],1),round(width[index],1)] for index in sorted(selected)]
            result.append({'street':name,'profile':profile})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('out',type=Path); args=parser.parse_args()
    if args.out.resolve().is_relative_to(ROOT/'src/data'):
        parser.error('Write the proposal outside src/data for review')
    streets = survey(np.asarray(Image.open(ROOT/'references/puyuan-reference.jpg').convert('RGB')))
    args.out.write_text(json.dumps(streets,indent=2)+'\n')
    print(f'{len(streets)} visible spans on {len({item["street"] for item in streets})} street guides')
