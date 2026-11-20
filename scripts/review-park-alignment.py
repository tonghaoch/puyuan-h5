"""Offline visual acceptance of the whole authored park at fixed illustration coordinates."""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from art.scene import compose_scene
from art.alignment_diagnostics import diagnose, layer_owners, LAYER_NAMES
from art.region_review import save_regions
from art.underpainting import save_underpainting
from art.ink_budget import capacity_report

ROOT = Path(__file__).resolve().parents[1]


def evaluation_mask(config):
    left, top, right, bottom = config['sourceBox']
    mask = np.zeros((bottom-top,right-left),np.uint8); origin = np.array([left,top])
    cv2.fillPoly(mask, [np.int32(config['scope'] - origin)], 1)
    for ring in config['printedInk']:
        cv2.fillPoly(mask, [np.int32(ring - origin)], 0)
    return mask


def dark(rgb, threshold):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY) < threshold


def counts(reference, native, valid):
    hit = int(np.count_nonzero(valid & reference & native))
    missed = int(np.count_nonzero(valid & reference & ~native))
    extra = int(np.count_nonzero(valid & ~reference & native))
    union = hit + missed + extra
    return {'pixels': int(np.count_nonzero(valid)), 'intersection': hit, 'union': union,
            'missed': missed, 'extra': extra, 'iou': hit / union if union else None}


def review(root, out, diagnostics=False, regions=False, compare_root=None, foreground=False, ink_budget=False):
    config_path = ROOT / 'docs/visual-acceptance-v1.json'
    config = json.loads(config_path.read_bytes())
    path = ROOT / 'references/puyuan-reference.jpg'
    if hashlib.sha256(path.read_bytes()).hexdigest() != config['referenceSha256']:
        raise ValueError('Reference differs from the acceptance image')
    left, top, right, bottom = config['sourceBox']
    width, height = right - left, bottom - top
    ref = Image.open(path).convert('RGB').crop(config['sourceBox'])
    def render(scene_root,omit=()):
        frame = json.loads((scene_root / 'src/data/reference-map.json').read_bytes())
        if frame['scene'] != {'width': width, 'height': height} or frame['sourceOffset'] != {'x': -left, 'y': -top}:
            raise ValueError('Scene frame differs from the fixed acceptance frame')
        return compose_scene(3, scene_root,omit).convert('RGB').resize(ref.size, Image.Resampling.LANCZOS)
    native = render(root)
    mask = evaluation_mask(config)
    valid = mask.astype(bool)
    ref_rgb, native_rgb = np.asarray(ref), np.asarray(native)
    target, drawing = (dark(rgb,config['grayBelow']) for rgb in (ref_rgb,native_rgb))
    def region(bounds):
        west, north, east, south = bounds
        window = np.s_[north-top:south-top, west-left:east-left]
        return counts(target[window], drawing[window], valid[window])
    report = counts(target, drawing, valid)
    windows = {key: region(bounds) for key, bounds in config['landmarkWindows'].items()}
    cells = []
    for north in range(top, bottom, 128):
        for west in range(left, right, 128):
            box = [west, north, min(west+128, right), min(north+128, bottom)]
            result = region(box)
            if result['pixels']:
                cells.append({'sourceBox': box, **result})
    cells.sort(key=lambda result: result['missed'] + result['extra'], reverse=True)
    for field in ('pixels', 'intersection', 'union', 'missed', 'extra'):
        if sum(cell[field] for cell in cells) != report[field]:
            raise ValueError(f'Incomplete cell coverage: {field}')
    out.mkdir(parents=True, exist_ok=True)
    overlay = np.asarray(native.convert('L').convert('RGB')).copy() // 3 + 120
    overlay[target & ~drawing] = [207, 54, 60]; overlay[drawing & ~target] = [39, 114, 198]
    overlay[~valid] = [224, 222, 214]
    diff = Image.fromarray(overlay)
    sheet = Image.new('RGB', (3*520, 450), '#eeeae0'); pen = ImageDraw.Draw(sheet)
    for index, (caption, image) in enumerate([('Reference', ref), ('Native', native), ('Red: missing dark / blue: excess dark', diff)]):
        preview = image.copy(); preview.thumbnail((520,424), Image.Resampling.LANCZOS)
        sheet.paste(preview, (index*520, 22)); pen.text((index*520+5,4),caption, fill='#33332e')
    sheet.save(out/'whole-park.jpg', quality=94); diff.save(out/'errors.png')
    report = {'metric': config['version'], 'specSha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
              'maskSha256': hashlib.sha256(mask.tobytes()).hexdigest(), 'wholePark': report,
              'landmarkWindows': windows, 'cellsByMismatch': cells}
    (out/'alignment.json').write_text(json.dumps(report, indent=2)+'\n')
    if ink_budget:
        capacity = capacity_report(config['sourceBox'], target, drawing, valid)
        if any(capacity['wholePark'][key] != report['wholePark'][key] for key in ('intersection', 'union', 'missed', 'extra')):
            raise ValueError('Ink budget disagrees with strict counts')
        capacity.update({key: report[key] for key in ('metric', 'specSha256', 'maskSha256')})
        (out/'ink-budget.json').write_text(json.dumps(capacity, indent=2)+'\n')
    if foreground:
        bare = render(root,('plant',)); under = dark(np.asarray(bare),config['grayBelow'])
        save_underpainting(out,config['sourceBox'],ref,bare,native,target,under,drawing,valid)
    if regions or compare_root:
        identity = {key: report[key] for key in ('metric','specSha256','maskSha256')}
        before = dark(np.asarray(render(compare_root)),config['grayBelow']) if compare_root else None
        save_regions(out,config['sourceBox'],ref,native,target,drawing,valid,counts,report['wholePark'],identity,before)
    if diagnostics:
        detail = diagnose(ref_rgb, target, drawing, valid, config['sourceBox'])
        (out/'distance-context.json').write_text(json.dumps(detail, indent=2)+'\n')
        owners=layer_owners(root)
        groups={name:counts(target,drawing,valid & (owners==index)) for index,name in enumerate(LAYER_NAMES)}
        for field in ('pixels','intersection','union','missed','extra'):
            if sum(group[field] for group in groups.values())!=report['wholePark'][field]:
                raise ValueError(f'Incomplete layer coverage: {field}')
        layer_report={'note':'Diagnostic partition only: topmost native asset with alpha >=128 at illustration scale. '
                      'Uncovered land/water use the authored water polygons, not reference segmentation. '
                      'A missing tree or house can therefore be counted against land. The strict metric is unchanged.',
                      'layers':groups}
        (out/'layer-context.json').write_text(json.dumps(layer_report,indent=2)+'\n')
    print(json.dumps(report['wholePark']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--diagnose', action='store_true', help='Also group strict errors by distance and surrounding reference colour')
    parser.add_argument('--regions', action='store_true', help='Report four disjoint work areas and an eight-pixel seam diagnostic')
    parser.add_argument('--compare-root', type=Path, help='Also count corrected and regressed dark pixels against another native build, by region')
    parser.add_argument('--foreground', action='store_true', help='Compare the fully drawn map with the same layers underneath the foreground plant tiles')
    parser.add_argument('--ink-budget', action='store_true', help='Bound ink redistribution in nested cells without relaxing the acceptance metric')
    args = parser.parse_args()
    review(args.root.resolve(), args.out, args.diagnose, args.regions, args.compare_root, args.foreground, args.ink_budget)
