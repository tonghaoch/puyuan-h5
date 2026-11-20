"""Compare a reference-free rebuild with the working illustration without modifying either."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rebuild', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
parser.add_argument('--strict',action='store_true',help='Require all native runtime WebPs to be byte-identical as well')
args = parser.parse_args()
rebuild = args.rebuild.resolve()
if rebuild == ROOT or not rebuild.is_dir() or (rebuild / 'references').exists():
    parser.error('Expected a separate rebuild without a references directory')


def matching_paths(pattern):
    actual = {file.relative_to(ROOT) for file in ROOT.glob(pattern)}
    rebuilt = {file.relative_to(rebuild) for file in rebuild.glob(pattern)}
    if not actual or actual != rebuilt:
        raise ValueError(f'{pattern}: path mismatch: {sorted(actual ^ rebuilt)}')
    return sorted(actual)


def identical(path):
    return hashlib.sha256((ROOT / path).read_bytes()).digest() == hashlib.sha256((rebuild / path).read_bytes()).digest()


names = ['landmark-models', 'architecture-tiles', 'native-landscape', 'meadow-tiles', 'roof-volumes']
svgs = matching_paths('public/art/**/*.svg')
for path in svgs + [Path('src/data') / f'{name}.json' for name in names]:
    if not identical(path):
        raise ValueError(f'{path}: generated geometry differs')

models = json.loads((ROOT / 'src/data/landmark-models.json').read_text())['models']
images = matching_paths('public/art/landmarks/*.scene.webp')
if set(images) != {Path('public') / model['heroAsset'].lstrip('/') for model in models}:
    raise ValueError('Detail images do not match the landmark manifest')
heroes = {}
for path in images:
    with Image.open(ROOT / path) as current, Image.open(rebuild / path) as other:
        if current.size != other.size:
            raise ValueError(f'{path}: detail sizes differ')
        difference = ImageChops.difference(current.convert('RGB'), other.convert('RGB'))
        mean = round(sum(ImageStat.Stat(difference).mean) / 3, 4)
    heroes[path.name] = {'byteIdentical': identical(path), 'meanAbsoluteChannelDifference': mean}

report = {'rebuild': str(rebuild), 'referencePresent': False, 'identicalArtSVGs': len(svgs),
          'identicalJSON': names, 'heroImages': heroes}
if args.strict:
    runtime = sorted({file for layer in ('native','landmarks','architecture','meadow') for file in ROOT.glob(f'public/art/{layer}/*.webp')})
    rebuilt = {file.relative_to(rebuild) for layer in ('native','landmarks','architecture','meadow') for file in rebuild.glob(f'public/art/{layer}/*.webp')}
    expected = {file.relative_to(ROOT) for file in runtime}
    mismatches = sorted(str(file) for file in expected&rebuilt if not identical(file))
    report['runtimeWebPs'] = {'count':len(expected),'different':mismatches,'missingOrAdditional':sorted(str(file) for file in expected^rebuilt)}
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(report, indent=2) + '\n')
if args.strict and (mismatches or expected!=rebuilt):raise SystemExit('Native runtime WebPs differ; see '+str(args.out))
print(f'{len(svgs)} SVGs, {len(names)} manifests and {len(heroes)} detail images compared')
