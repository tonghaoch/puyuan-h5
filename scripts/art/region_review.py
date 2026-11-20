"""Fixed, non-overlapping work areas in paper coordinates, not landmark crops."""
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw


REGIONS = ('nw', 'ne', 'sw', 'se')


def region_map(bounds):
    left, top, right, bottom = bounds
    northing, easting = np.ogrid[top:bottom, left:right]
    split = np.where((northing >= 420) & (northing < 850), 1018, 910)
    return ((northing >= 850) * 2 + (easting >= split)).astype(np.uint8)


def change_counts(target, before, after, scope):
    changed = scope & (before != after)
    return {'corrected': int(np.count_nonzero(changed & (after == target))),
            'regressed': int(np.count_nonzero(changed & (after != target)))}


def save_regions(out, bounds, reference, native, target, drawing, valid, counts, whole, identity, before=None):
    owners = region_map(bounds)
    seam = cv2.morphologyEx(owners, cv2.MORPH_GRADIENT, np.ones((17,17), np.uint8)) != 0
    regions = {name: counts(target, drawing, valid & (owners == index))
               for index, name in enumerate(REGIONS)}
    for field in ('pixels', 'intersection', 'union', 'missed', 'extra'):
        if sum(row[field] for row in regions.values()) != whole[field]:
            raise ValueError(f'Incomplete region coverage: {field}')
    report = {**identity, 'partition': 'park-quadrants-v1', 'wholePark': whole, 'regions': regions,
              'seam8': counts(target, drawing, valid & seam)}
    if before is not None:
        report['changedDarkPixels'] = {name: change_counts(target,before,drawing,valid & (owners == index))
                                       for index,name in enumerate(REGIONS)}
        report['changedSeamPixels'] = change_counts(target,before,drawing,valid & seam)
    (out/'regions.json').write_text(json.dumps(report, indent=2)+'\n')
    edge = cv2.morphologyEx(owners, cv2.MORPH_GRADIENT, np.ones((3,3), np.uint8)) != 0
    sheet = Image.new('RGB', (1200,515), '#eeeae0'); pen = ImageDraw.Draw(sheet)
    for column, (caption, image) in enumerate((('Paper', reference), ('Native', native))):
        preview = np.asarray(image).copy(); preview[~valid] = preview[~valid] // 3 + 155
        preview[edge & valid] = [190,36,101]
        panel = Image.fromarray(preview); panel.thumbnail((600,490), Image.Resampling.LANCZOS)
        sheet.paste(panel,(600*column,22)); pen.text((600*column+6,4),caption, fill='#332e29')
    sheet.save(out/'regions.jpg',quality=94)
