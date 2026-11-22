"""Select a smooth registration on controls alone; export a small offline H5 model."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean, median

from PIL import Image
from review_location_registration import ROOT, OUTPUT, MERCATOR_RADIUS, fit, panel, solve

SPEC = ROOT / 'references/geodata/park-registration.json'
MODEL = ROOT / 'src/data/illustration-registration.json'
CENTER = (700, 600)
SCALE = 256
SUPPORT = 170
CHECK_BUDGET_M = 20


class Mesh:
    def __init__(self, points):
        self.sites = [point['satellitePx'] for point in points]
        self.targets = [point['scenePx'] for point in points]
        size = len(points)
        sites = self.sites + [[-10000, -10000], [20000, -10000], [0, 20000]]
        triangles = [(size, size+1, size+2)]
        for index, point in enumerate(self.sites):
            outside, boundary = [], set()
            for triangle in triangles:
                corners = [(sites[vertex][0]-point[0], sites[vertex][1]-point[1]) for vertex in triangle]
                determinant = sum((east**2+south**2)*cross((0, 0), corners[(side+1)%3], corners[(side+2)%3])
                                  for side, (east, south) in enumerate(corners))
                if determinant < 0:
                    outside.append(triangle)
                    continue
                for start, end in zip(triangle, triangle[1:] + triangle[:1]):
                    if (end, start) in boundary:
                        boundary.remove((end, start))
                    else:
                        boundary.add((start, end))
            triangles = outside + [(start, end, index) for start, end in sorted(boundary)
                                   if cross(sites[start], sites[end], point) > 0]
        self.triangles = [triangle for triangle in triangles if max(triangle) < size]

    def project(self, query):
        best = None
        for triangle in self.triangles:
            first, second, third = [self.sites[index] for index in triangle]
            area = cross(first, second, third)
            weights = [cross(second, third, query)/area, cross(third, first, query)/area, cross(first, second, query)/area]
            if best is None or min(weights) > best[0]:
                best = min(weights), weights, triangle
            if min(weights) >= 0:
                break
        _, weights, triangle = best
        return [sum(weight*self.targets[index][axis] for weight, index in zip(weights, triangle)) for axis in (0, 1)]


def normalized(point):
    return [(value - center) / SCALE for value, center in zip(point, CENTER)]


def kernel(first, second):
    squared = sum((a-b)**2 for a, b in zip(first, second))
    return squared * math.log(squared) if squared else 0.0


def linear_system(matrix, targets):
    size = len(matrix)
    rows = [row[:] + target[:] for row, target in zip(matrix, targets)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda index: abs(rows[index][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        if abs(rows[col][col]) < 1e-11:
            raise ValueError('Degenerate control geometry')
        divisor = rows[col][col]
        rows[col] = [value/divisor for value in rows[col]]
        for index, row in enumerate(rows):
            if index != col:
                factor = row[col]
                rows[index] = [value-factor*other for value, other in zip(row, rows[col])]
    return [row[size:] for row in rows]


def train(points, smoothing):
    if smoothing == 'mesh':
        return Mesh(points)
    sites = [normalized(point['satellitePx']) for point in points]
    targets = [point['scenePx'] for point in points]
    if smoothing is None:
        rows = fit([dict(satellitePx=site, scenePx=target) for site, target in zip(sites, targets)])
        return [], [list(pair) for pair in zip(*rows)]
    affine = [site + [1] for site in sites]
    matrix = [[kernel(site, other) + (smoothing if index == col else 0)
               for col, other in enumerate(sites)] + affine[index] for index, site in enumerate(sites)]
    matrix.extend(list(column) + [0, 0, 0] for column in zip(*affine))
    return sites, linear_system(matrix, targets + [[0, 0]] * 3)


def predict(model, pixel):
    if isinstance(model, Mesh):
        return model.project(pixel)
    sites, weights = model
    query = normalized(pixel)
    basis = [kernel(query, site) for site in sites] + query + [1]
    return [sum(value * weight[axis] for value, weight in zip(basis, weights)) for axis in (0, 1)]


def cross(start, end, point):
    return (end[0]-start[0]) * (point[1]-start[1]) - (end[1]-start[1]) * (point[0]-start[0])


def hull(points):
    pixels = sorted(point['satellitePx'] for point in points)

    def side(sequence):
        chain = []
        for pixel in sequence:
            while len(chain) >= 2 and cross(chain[-2], chain[-1], pixel) <= 0:
                chain.pop()
            chain.append(pixel)
        return chain[:-1]

    return side(pixels) + side(reversed(pixels))


def supported(query, points):
    ring = hull(points)
    return (all(cross(start, end, query) >= 0 for start, end in zip(ring, ring[1:]+ring[:1])) and
            min(math.dist(query, point['satellitePx']) for point in points) <= SUPPORT)


def measurement(model, point, world):
    pixel = point['satellitePx']
    predicted = predict(model, pixel)
    delta = [value-observed for value, observed in zip(predicted, point['scenePx'])]
    east, north = world[4] + world[0]*pixel[0], world[5] + world[3]*pixel[1]
    latitude = math.atan(math.sinh(north / MERCATOR_RADIUS))
    dx = predict(model, [pixel[0]+0.01, pixel[1]])
    dy = predict(model, [pixel[0], pixel[1]+0.01])
    jacobian = [[(dx[axis]-predicted[axis])*100, (dy[axis]-predicted[axis])*100] for axis in (0, 1)]
    source_error = solve(*jacobian, delta)
    meters = math.cos(latitude) * math.hypot(source_error[0]*world[0], source_error[1]*world[3])
    return dict(point, predictedScenePx=predicted, equivalentMeters=meters,
                referenceLonLat=[math.degrees(east/MERCATOR_RADIUS), math.degrees(latitude)])


def rms(values):
    return math.sqrt(mean(value**2 for value in values))


def calibrate(controls, checks, release, world):
    for key in ('id', 'satellitePx', 'scenePx'):
        values = [str(point[key]) for point in controls + checks + release]
        if len(set(values)) != len(values):
            raise ValueError(f'Duplicate landmark {key}')
    if world[1:3] != [0, 0] or abs(world[0]+world[3]) > 1e-8 or world[0] <= 0:
        raise ValueError('Expected north-up square Mercator pixels')
    folds = [(point, controls[:index]+controls[index+1:]) for index, point in enumerate(controls)]
    folds = [(point, rest) for point, rest in folds if supported(point['satellitePx'], rest)]
    if len(folds) < 5:
        raise ValueError('Too few supported leave-one-out predictions')
    scores = []
    for smoothing in (None, 0, 0.01, 0.1, 0.5, 2, 'mesh'):
        errors = [math.dist(predict(train(rest, smoothing), point['satellitePx']), point['scenePx'])
                  for point, rest in folds]
        candidate = train(controls, smoothing)
        anchor_max = max(math.dist(predict(candidate, point['satellitePx']), point['scenePx']) for point in controls)
        scores.append(dict(smoothing=smoothing, looRmsScenePx=rms(errors), maxAnchorPx=anchor_max))
    chosen = min((item for item in scores if item['maxAnchorPx'] <= 4), key=lambda item: item['looRmsScenePx'])['smoothing']
    model = train(controls, chosen)
    baseline = train(controls, None)
    def measure(point):
        return dict(measurement(model, point, world), supported=supported(point['satellitePx'], controls),
                    affineMeters=measurement(baseline, point, world)['equivalentMeters'])
    measured = list(map(measure, checks))
    exclusions = [point['satellitePx'] for point in measured if point['supported'] and point['equivalentMeters'] > CHECK_BUDGET_M]
    fresh = list(map(measure, release))
    for point in measured + fresh:
        point['supported'] &= all(math.dist(point['satellitePx'], site) > SUPPORT for site in exclusions)
    errors = [point['equivalentMeters'] for point in measured if point['supported']]
    loo_errors = [measurement(train(rest, chosen), point, world)['equivalentMeters'] for point, rest in folds]
    runtime = dict(world=world, hull=hull(controls),
                   controls=[point['satellitePx'] for point in controls], exclusionSites=exclusions,
                   supportPx=SUPPORT, registrationAllowanceM=math.ceil(max(errors + loo_errors)), imageryAllowanceM=5)
    if isinstance(model, Mesh):
        runtime.update(kind='mesh', triangles=model.triangles, targets=model.targets)
    else:
        runtime.update(kind='spline', center=CENTER, scale=SCALE, weights=model[1])
    release_errors = [point['equivalentMeters'] for point in fresh if point['supported']]
    report = dict(controlCount=len(controls), looCount=len(folds), candidates=scores, smoothing=chosen,
                  checkRmsMeters=rms(errors), checkMedianMeters=median(errors), checkMaxMeters=max(errors),
                  affineRmsMeters=rms([point['affineMeters'] for point in measured if point['supported']]), checks=measured,
                  releaseChecks=fresh, releaseRmsMeters=rms(release_errors) if release_errors else None,
                  releaseMaxMeters=max(release_errors, default=None))
    return runtime, report


def inputs():
    spec = json.loads(SPEC.read_text())
    base = json.loads((SPEC.parent / spec['base']).read_text())
    promoted = set(spec['promotedToControl'])
    controls = base['controls'] + [point for point in base['checks'] if point['id'] in promoted] + spec['controls']
    checks = [point for point in base['checks'] if point['id'] not in promoted] + spec['checks']
    return base, controls, checks, spec['releaseChecks'], list(map(float, (ROOT / base['worldFile']).read_text().splitlines()))


def review(report, base):
    with Image.open(ROOT / base['scene']) as art, Image.open(ROOT / base['satellite']) as satellite:
        if art.size != (1520, 1240) or satellite.size != (1400, 1200):
            raise ValueError('Registration raster dimensions changed')
        cards = []
        for point in report['checks'] + report['releaseChecks']:
            figures = []
            for image, key in ((satellite, 'satellitePx'), (art, 'scenePx')):
                cx, cy = point[key]
                radius = max(36, math.ceil(math.dist(point['scenePx'], point['predictedScenePx']))+8)
                figures.append(panel(image, (cx-radius, cy-radius, cx+radius+1, cy+radius+1), [point], key, True))
            note = '' if point['supported'] else '（覆盖外，不显示）'
            cards.append(f'<article><h2>{point["id"]} · {point["label"]}</h2><p>{point["equivalentMeters"]:.1f} 米 {note}</p>'
                         f'<section>{"".join(figures)}</section></article>')
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>手绘定位 · 离线验收</title><style>body{{max-width:800px;margin:auto;padding:16px;background:#faf5e8;color:#302b24}}
article{{margin:18px 0}}section{{display:flex;gap:4px}}svg{{width:49%;height:auto}}.check{{fill:none;stroke:cyan;stroke-width:.7}}
.estimate{{fill:none;stroke:#f22;stroke-width:1}}body:has(input:not(:checked)) .estimate{{display:none}}</style>
<h1>手绘定位 · 留出地标对照</h1><p>左为卫星影像，右为最终手绘图。青圈是人工辨认的同一地物，红叉是预测。御桥已用于拟合，不计入成绩。</p>
<p>这里检验模型本身，不含设备误差或园界筛选。<a href="coverage.html">查看不同设备精度下，应用实际画点的范围</a>。</p>
<p>有覆盖的检查点均方根偏差 {report['checkRmsMeters']:.1f} 米，最大 {report['checkMaxMeters']:.1f} 米。是影像配准，不是手机 GPS 实测。</p>
<p>H/V 点用于筛查覆盖（不拟合）；F 点既不拟合也不参与覆盖筛选。覆盖内 F 点 RMS {report['releaseRmsMeters']:.1f} 米，最大 {report['releaseMaxMeters']:.1f} 米。覆盖外保留失败结果，不画点。</p>
<label><input type="checkbox" checked>显示预测点与偏移线</label>{''.join(cards)}</html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-model', action='store_true', help='update the bundled production model')
    args = parser.parse_args()
    base, controls, checks, release, world = inputs()
    runtime, report = calibrate(controls, checks, release, world)
    if args.write_model:
        if runtime['kind'] != 'mesh' or any(cross(*[runtime['targets'][index] for index in triangle]) <= 0
                                             for triangle in runtime['triangles']):
            raise ValueError('H5 currently accepts only an orientation-preserving triangle mesh')
        MODEL.write_text(json.dumps(runtime, separators=(',', ':'), allow_nan=False)+'\n')
    OUTPUT.mkdir(exist_ok=True, parents=True)
    (OUTPUT/'park-review.html').write_text(review(report, base))
    (OUTPUT/'park-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f'{OUTPUT}/park-review.html\nLOO: {report["looCount"]}, smoothing: {report["smoothing"]}, '
          f'held-out RMS: {report["checkRmsMeters"]:.2f} m (affine: {report["affineRmsMeters"]:.2f} m)')
    for point in report['checks'] + report['releaseChecks']:
        print(f'{point["id"]} {point["equivalentMeters"]:.2f} m, supported={point["supported"]}')


if __name__ == '__main__':
    main()
