"""Measure what the existing native foreground changes, without editing any artwork."""
import json

import numpy as np
from PIL import Image, ImageDraw

from .region_review import region_map, REGIONS


def foreground_counts(target, under, final, scope):
    darkened = scope & ~under & final
    lightened = scope & under & ~final
    return {'correctDarkening': int(np.count_nonzero(darkened & target)),
            'extraDarkening': int(np.count_nonzero(darkened & ~target)),
            'correctLightening': int(np.count_nonzero(lightened & ~target)),
            'missedAfterLightening': int(np.count_nonzero(lightened & target)),
            'missedInBoth': int(np.count_nonzero(scope & target & ~under & ~final)),
            'extraInBoth': int(np.count_nonzero(scope & ~target & under & final))}


def save_underpainting(out, bounds, reference, bare, native, target, under, final, valid):
    owners = region_map(bounds); regions = {}; sheet = Image.new('RGB',(960,4*158),'#eeeae0'); pen = ImageDraw.Draw(sheet)
    for index,name in enumerate(REGIONS):
        scope = valid & (owners == index); rows = foreground_counts(target,under,final,scope)
        cells = []
        for northing in range(0,scope.shape[0],64):
            for easting in range(0,scope.shape[1],64):
                cut = np.s_[northing:northing+64,easting:easting+64]
                if not scope[cut].any():continue
                tally = foreground_counts(target[cut],under[cut],final[cut],scope[cut])
                rect = [easting,northing,min(easting+64,scope.shape[1]),min(northing+64,scope.shape[0])]
                cells.append({'sourceBox':[value+bounds[pos%2] for pos,value in enumerate(rect)],**tally})
        rows['inspectionWindows'] = sorted(cells,key=lambda row:row['extraDarkening']+row['missedAfterLightening'],reverse=True)[:6]
        regions[name] = rows; box = rows['inspectionWindows'][0]['sourceBox']
        cut = [value-bounds[pos%2] for pos,value in enumerate(box)]
        for column,(label,image) in enumerate((('Paper',reference),('Below foreground',bare),('Published',native))):
            preview = image.crop(cut).resize((136,136),Image.Resampling.NEAREST)
            sheet.paste(preview,(column*320+88,index*158+19)); pen.text((column*320+6,index*158+2),f'{name} {label} {box}',fill='#332e29')
    (out/'foreground-impact.json').write_text(json.dumps({'note':'Native layers below the plant tiles are held fixed. These are dark-state transitions, not botanical labels, deletion proposals, or acceptance scores.', 'regions':regions},indent=2)+'\n')
    sheet.save(out/'foreground-impact.jpg',quality=95)
