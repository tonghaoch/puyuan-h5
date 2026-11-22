"""Compare frozen illustrated-map trials without modifying the model bundled with the H5."""
import argparse
import hashlib
import json
import math
from html import escape

from PIL import Image

from calibrate_illustration import MODEL, Mesh, cross, hull, inputs
from review_location_registration import MERCATOR_RADIUS, OUTPUT, ROOT, panel

TRIAL_DIR = ROOT / 'references/geodata'


def substitute(original, spec, checks):
    replacements = {point['id']: point for point in spec['replaceControls']}
    if len(replacements) != len(spec['replaceControls']) or not replacements.keys() <= {p['id'] for p in original}:
        raise ValueError('Unknown or repeated replacement control')
    candidate = [replacements.get(point['id'], point) for point in original] + spec['addControls']
    for key in ('id', 'satellitePx', 'scenePx'):
        values = [json.dumps(point[key]) for point in candidate + checks]
        if len(values) != len(set(values)):
            raise ValueError(f'Control/check overlap or duplicate {key}')
    return candidate


def transfer(query, source, target, triangles):
    matches = []
    for triangle in triangles:
        corners = [source[index] for index in triangle]
        area = cross(*corners)
        if area <= 0:
            raise ValueError('Triangle folds or collapses')
        weights = [cross(corners[(index+1) % 3], corners[(index+2) % 3], query) / area for index in range(3)]
        if min(weights) >= -1e-9:
            matches.append([sum(weight * target[vertex][axis] for weight, vertex in zip(weights, triangle)) for axis in (0, 1)])
    if any(math.dist(matches[0], match) > 1e-5 for match in matches[1:]):
        raise ValueError('Overlapping inverse triangles: no unique position')
    return matches[0] if matches else None


def lonlat(pixel, world):
    return (math.degrees((world[4] + world[0] * pixel[0]) / MERCATOR_RADIUS),
            math.degrees(math.atan(math.sinh((world[5] + world[3] * pixel[1]) / MERCATOR_RADIUS))))


def ground_distance(start, end, world):
    lon1, lat1 = map(math.radians, lonlat(start, world))
    lon2, lat2 = map(math.radians, lonlat(end, world))
    half = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2 * MERCATOR_RADIUS * math.asin(min(1, math.sqrt(half)))


def inside(point, ring):
    east, north = point
    crossings = sum((start[1] > north) != (end[1] > north) and
                    east < start[0] + (end[0]-start[0]) * (north-start[1]) / (end[1]-start[1])
                    for start, end in zip(ring, ring[1:] + ring[:1]))
    return bool(crossings % 2)


def assess(model, point, world):
    source, target, triangles = model['controls'], model['targets'], model['triangles']
    projected = transfer(point['satellitePx'], source, target, triangles)
    inverse = transfer(point['scenePx'], target, source, triangles)
    reason = 'outside-source-mesh' if projected is None else 'outside-painted-mesh' if inverse is None else None
    return {'scene': projected, 'reason': reason,
            'meters': None if reason else ground_distance(point['satellitePx'], inverse, world)}


def totals(results, key):
    measured = [row[key]['meters'] for row in results if row[key]['meters'] is not None]
    return dict(points=len(results), below10=sum(error < 10 for error in measured),
                atLeast10=sum(error >= 10 for error in measured), unmeasured=len(results)-len(measured),
                maxMeasuredM=max(measured, default=None))


def pick_sensitivity(model, point, world):
    """Sample declared pick tolerances; these are assumptions, not certified error bounds."""
    observation = point.get('observation')
    if not observation:
        return None
    source_tolerance = observation['satellitePickTolerancePx']
    target_tolerance = observation['scenePickTolerancePx']
    values, missing = [], 0
    for dx in (-source_tolerance, 0, source_tolerance):
        for dy in (-source_tolerance, 0, source_tolerance):
            for tx in (-target_tolerance, 0, target_tolerance):
                for ty in (-target_tolerance, 0, target_tolerance):
                    changed = dict(point, satellitePx=[point['satellitePx'][0]+dx, point['satellitePx'][1]+dy],
                                   scenePx=[point['scenePx'][0]+tx, point['scenePx'][1]+ty])
                    result = assess(model, changed, world)
                    if result['meters'] is None:
                        missing += 1
                    else:
                        values.append(result['meters'])
    return dict(samples=81, sampledMinMeters=min(values, default=None), sampledMaxMeters=max(values, default=None),
                sampledBelow10=sum(value < 10 for value in values), sampledAtLeast10=sum(value >= 10 for value in values),
                unmeasured=missing)


def spatial_audit(ring, current, trial, results, world):
    outline = [[(math.radians(lon)*MERCATOR_RADIUS-world[4])/world[0],
                (math.asinh(math.tan(math.radians(lat)))*MERCATOR_RADIUS-world[5])/world[3]] for lon, lat in ring]
    hulls = {key: hull([{'satellitePx': point} for point in model['controls']]) for key, model in [('current', current), ('trial', trial)]}
    landmarks = [point['satellitePx'] for point in results if point['publicPark']]
    if not landmarks:
        raise ValueError('No check landmarks inside the public polygon')
    counts = dict.fromkeys(hulls, 0)
    gaps = []
    pitch = 10
    bounds = [range(pitch * math.floor(min(row[axis] for row in outline)/pitch),
                    math.ceil(max(row[axis] for row in outline)), pitch) for axis in (0, 1)]
    for east in bounds[0]:
        for south in bounds[1]:
            site = [east, south]
            if not inside(site, outline):
                continue
            for key, polygon in hulls.items():
                if all(cross(start, end, site) >= 0 for start, end in zip(polygon, polygon[1:] + polygon[:1])):
                    counts[key] += 1
            nearest = min(landmarks, key=lambda check: math.dist(site, check))
            gaps.append((ground_distance(site, nearest, world), site))
    priorities = []
    for distance, site in sorted(gaps, reverse=True):
        if all(ground_distance(site, prev['satellitePx'], world) >= 150 for prev in priorities):
            priorities.append(dict(satellitePx=site, lonLat=lonlat(site, world), nearestCheckM=round(distance, 1)))
        if len(priorities) == 3:
            break
    return dict(gridStepPx=pitch, parkSamples=len(gaps), insideSourceHull=counts,
                within50mOfCheck=sum(distance <= 50 for distance, _ in gaps), priorities=priorities)


def evaluate(specs):
    if not specs or [spec['version'] for spec in specs] != list(range(1, len(specs) + 1)):
        raise ValueError('Trials must be a nonempty contiguous sequence starting at one')
    base, original, screening, release, world = inputs()
    prior = [point for spec in specs[:-1] for point in spec['newChecks']]
    groups = [('screening', screening), ('previous-release', release), ('prior-trial', prior), ('new', specs[-1]['newChecks'])]
    checks = [point for _, points in groups for point in points]
    controls = original
    previous_controls = original
    policy = None
    previous_policy = None
    for spec in specs:
        previous_controls = controls
        previous_policy = policy
        controls = substitute(controls, spec, checks)
        if 'modelSelection' in spec:
            policy = spec['modelSelection']
    def build(points, selection):
        if selection is not None:
            from smooth_illustration_mesh import build_smooth_candidate
            return build_smooth_candidate(points, selection)
        candidate = Mesh(points)
        return dict(controls=candidate.sites, targets=candidate.targets, triangles=candidate.triangles), None
    trial, model_selection = build(controls, policy)
    live = json.loads(MODEL.read_text())
    if live['kind'] != 'mesh' or world != live['world']:
        raise ValueError('Trial requires the same north-up world file and deployed mesh model')
    models = dict(current=live, trial=trial)
    if len(specs) > 1:
        models['previousTrial'], _ = build(previous_controls, previous_policy)
    ring = json.loads((ROOT / 'public/geodata/boundary.geojson').read_text())['features'][0]['geometry']['coordinates'][0]
    rows = [dict(point, group=group, publicPark=inside(lonlat(point['satellitePx'], world), ring),
                 pickSensitivity=pick_sensitivity(trial, point, world),
                 **{key: assess(model, point, world) for key, model in models.items()})
            for group, points in groups
            for point in points]
    summary = {group: {key: totals(subset, key) for key in models} for group, subset in
               [('all', rows), ('publicPark', [row for row in rows if row['publicPark']]),
                ('new', [row for row in rows if row['group'] == 'new'])]}
    revised = {point['id'] for spec in specs for point in spec['replaceControls']}
    corrections = [dict(old=old, new=next(point for point in controls if point['id'] == old['id'])) for old in original if old['id'] in revised]
    return base, dict(baselineSha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(), trial=specs[-1]['version'],
                      trialInputSha256=[hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False,
                                                                separators=(',', ':')).encode()).hexdigest() for spec in specs],
                      previousTrial=len(specs)-1 if len(specs) > 1 else None,
                      modelSelection=model_selection,
                      controlCount=len(controls), summary=summary, checks=rows, corrections=corrections,
                      addedControls=[point for spec in specs for point in spec['addControls']],
                      hasImageryAudit=bool(specs[-1].get('imageryAudit')),
                      spatial=spatial_audit(ring, live, trial, rows, world))


def review(report, base):
    articles = []
    evidence = []
    def meters(result):
        return '无法反算（网外）' if result['meters'] is None else f'{result["meters"]:.1f} 米'
    with Image.open(ROOT / base['satellite']) as satellite, Image.open(ROOT / base['scene']) as scene:
        for item in report['corrections']:
            old, new = item['old'], item['new']
            figures = []
            for image, field, title in [(satellite, 'satellitePx', '卫星'), (scene, 'scenePx', '手绘')]:
                before, after = old[field], new[field]
                box = (min(before[0], after[0])-34, min(before[1], after[1])-34,
                       max(before[0], after[0])+35, max(before[1], after[1])+35)
                renamed = [dict(old, id='A'), dict(new, id='B')]
                figures.append(f'<figure><figcaption>{title}：A 原点，B 新点</figcaption>{panel(image, box, renamed, field)}</figure>')
            evidence.append(f'<article><h3>{escape(new["id"])} · {escape(new["label"])}</h3><p>{escape(new["evidence"])}</p><section>{"".join(figures)}</section></article>')
        for point in report['addedControls']:
            figures = []
            for image, field, title in [(satellite, 'satellitePx', '影像控制点'), (scene, 'scenePx', '手绘控制点')]:
                cx, cy = point[field]
                figures.append(f'<figure><figcaption>{title}</figcaption>{panel(image, (cx-32, cy-32, cx+33, cy+33), [point], field)}</figure>')
            evidence.append(f'<article><h3>{escape(point["id"])} · {escape(point["label"])}</h3>'
                            f'<p>{escape(point["evidence"])}</p><p>用于拟合，不计入检查点成绩。</p><section>{"".join(figures)}</section></article>')
        for point in report['checks']:
            figures = []
            keys = ['current'] + (['previousTrial'] if report['previousTrial'] is not None else []) + ['trial']
            delta = [math.dist(point[key]['scene'], point['scenePx']) for key in keys if point[key]['scene']]
            radius = math.ceil(max([30] + delta)) + 8
            panels = [('影像地标', satellite, 'satellitePx', None), (report.get('baselineLabel', '应用模型'), scene, 'scenePx', 'current')]
            if report['previousTrial'] is not None:
                panels.append((f'候选 {report["previousTrial"]}', scene, 'scenePx', 'previousTrial'))
            panels.append((report.get('candidateLabel', f'候选 {report["trial"]}'), scene, 'scenePx', 'trial'))
            for title, image, field, model in panels:
                mark = dict(point)
                if model and point[model]['scene'] is not None:
                    mark['predictedScenePx'] = point[model]['scene']
                cx, cy = mark[field]
                svg = panel(image, (cx-radius, cy-radius, cx+radius+1, cy+radius+1), [mark], field, True)
                result = '' if not model else '：' + meters(point[model])
                figures.append(f'<figure><figcaption>{title}{result}</figcaption>{svg}</figure>')
            scope = '公开园界内' if point['publicPark'] else '公开园界外，仍保留'
            sensitivity = point['pickSensitivity']
            note = ''
            if point.get('priorObservation'):
                prior = point['priorObservation']
                note += (f'<p>此地标已按源图重新辨认。保留的原观察：影像 {escape(str(prior["satellitePx"]))}，'
                         f'画面 {escape(str(prior["scenePx"]))}。原配对身份不成立，不能把旧误差当作定位精度。</p>')
            if sensitivity:
                limits = [sensitivity['sampledMinMeters'], sensitivity['sampledMaxMeters']]
                span = '—' if None in limits else f'{limits[0]:.1f}–{limits[1]:.1f} 米'
                note += (f'<p>按所声明的选点容差做 81 组偏移抽样，候选几何偏差范围为 {span}，'
                        f'{sensitivity["unmeasured"]} 组网外。这是敏感性诊断，不是已证明的误差区间；'
                        '不移动冻结点，不改变上方名义计数，也不含手机或影像绝对偏差。</p>')
            articles.append(f'<article><h3>{escape(point["id"])} · {escape(point["label"])}</h3><small>{scope}</small>'
                            f'<p>{escape(point.get("evidence", ""))}</p>{note}<section>{"".join(figures)}</section></article>')
    current, trial = [report['summary']['all'][key] for key in ('current', 'trial')]
    spatial = report['spatial']
    headline = (f'<p>全部 {trial["points"]} 个检查点（含园界外）：严格小于 10 米 {current["below10"]} → {trial["below10"]}，'
                f'超标或恰好 10 米 {current["atLeast10"]} → {trial["atLeast10"]}，无法反算 {current["unmeasured"]} → {trial["unmeasured"]}。</p>'
                f'<p>公开园界的 {spatial["parkSamples"]} 个采样位置中，只有 {spatial["within50mOfCheck"]} 个离一个园内检查点不超过 50 米；'
                '即使靠近检查点，也不能视作已证明该位置的误差。K 点来自同一影像，不是独立测绘。</p>')
    if report['previousTrial'] is not None:
        previous = report['summary']['all']['previousTrial']
        fresh = report['summary']['new']['trial']
        headline += (f'<p>在同一批 {trial["points"]} 个点上，候选 {report["previousTrial"]} → {report["trial"]}：'
                     f'小于 10 米 {previous["below10"]} → {trial["below10"]}，'
                     f'超标 {previous["atLeast10"]} → {trial["atLeast10"]}，网外 {previous["unmeasured"]} → {trial["unmeasured"]}。'
                     f'本轮新冻结 {fresh["points"]} 个检查点：{fresh["below10"]} 个小于 10 米、'
                     f'{fresh["atLeast10"]} 个超标、{fresh["unmeasured"]} 个网外。选点本身的不确定性仍须另验。</p>')
    if report['hasImageryAudit']:
        headline += f'<p><a href="trial-{report["trial"]:02d}-sources.html">查看新选点的原插画、原影像和缓存影像</a>（需生成来源对照页）。</p>'
    if report['modelSelection']:
        selection = report['modelSelection']
        last = selection['refinement'][-1]
        headline += (f'<p>模型仅用 {selection["observedControlCount"]} 个观察控制点、'
                     f'{selection["looCount"]} 个有支持的留一折选择平滑强度 {selection["chosen"]}，'
                     f'控制点最大位移门槛仍为 {selection["maxAnchorPx"]} 画面像素。'
                     f'转换三角网有 {last["meshNodes"]} 个计算节点、{last["triangles"]} 个三角形、'
                     f'{last["foldedTriangles"]} 个折叠。这些节点不是新增观测，不增加已验证区域。</p>')
    if report.get('refinementCheck'):
        refinement = report['refinementCheck']
        fine = refinement['summary']['fine']
        headline += (f'<p>进一步细分的数值诊断：在粗细网均可反算的点上，米数最大变化 '
                     f'{refinement["maxMeasuredDifferenceMeters"]:.3f} 米；'
                     f'精细网仍为 {fine["below10"]} 个小于 10 米、{fine["atLeast10"]} 个超标、'
                     f'{fine["unmeasured"]} 个无法反算。发生分类变化的点：'
                     f'{escape(", ".join(refinement["classificationChanges"]) or "无")}。'
                     '详见同目录 refinement JSON；这是数值诊断，不是独立精度证明。</p>')
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>逐点比较 · 10 米目标</title><style>body{max-width:1100px;margin:auto;padding:14px;background:#faf5e8;color:#302b24}section{display:flex;gap:5px}figure{margin:0;flex:1;min-width:0}svg{width:100%}.control,.check{stroke:cyan;fill:none;stroke-width:1}.estimate{stroke:#f22;fill:none;stroke-width:1}@media(max-width:650px){section{flex-wrap:wrap}figure{flex:1 1 45%}}</style>
<h1>同一地标：原版 / 比较版</h1><p>青圈是人工辨认的位置，红叉是拟合预测。米数是把青圈用原三角网精确反算回地面，与影像点比较的距离估计；不在三角网内就不外推。这里不按应用的安全区过滤，网外、错岸和大偏差均须保留。不是手机实测或全园精度证明。</p>''' + headline + '<h2>修正依据（不计成绩）</h2>' + ''.join(evidence) + '<h2>检查点（不参与拟合）</h2>' + ''.join(articles) + '</html>'


def refinement_report(specs, report):
    from smooth_illustration_mesh import sample_mesh, select_on_controls
    _, controls, _, _, world = inputs()
    policy = None
    for spec in specs:
        controls = substitute(controls, spec, report['checks'])
        policy = spec.get('modelSelection', policy)
    if not policy:
        raise ValueError('Refinement diagnostic requires a smooth mesh selection policy')
    fitted, selection = select_on_controls(controls, policy['maxAnchorPx'])
    coarse, _ = sample_mesh(controls, fitted, policy['subdivisionLevels'])
    fine, fine_audit = sample_mesh(controls, fitted, policy['subdivisionLevels']+1)
    rows = []
    for point in report['checks']:
        before, after = assess(coarse, point, world), assess(fine, point, world)
        rows.append(dict(id=point['id'], coarse=before, fine=after,
                         absoluteDifferenceMeters=None if before['meters'] is None or after['meters'] is None
                         else abs(before['meters']-after['meters'])))
    def classification(result):
        return 'unmeasured' if result['meters'] is None else 'below10' if result['meters'] < 10 else 'atLeast10'
    return dict(purpose='Numerical refinement at fixed regression checks; no independent accuracy evidence.',
                baselineSha256=report['baselineSha256'], trialInputSha256=report['trialInputSha256'],
                chosen=selection['chosen'], coarseLevel=policy['subdivisionLevels'], fineLevel=policy['subdivisionLevels']+1,
                refinement=fine_audit, checks=rows, summary={key: totals(rows, key) for key in ('coarse', 'fine')},
                maxMeasuredDifferenceMeters=max((row['absoluteDifferenceMeters'] for row in rows
                                                if row['absoluteDifferenceMeters'] is not None), default=0),
                classificationChanges=[row['id'] for row in rows if classification(row['coarse']) != classification(row['fine'])])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    versions = sorted(int(path.stem.rsplit('-', 1)[1]) for path in TRIAL_DIR.glob('registration-trial-[0-9][0-9].json'))
    parser.add_argument('--trial', type=int, choices=versions, default=max(versions))
    parser.add_argument('--refine', action='store_true', help='also compare the selected smooth mesh with one finer subdivision')
    args = parser.parse_args()
    specs = [json.loads((TRIAL_DIR / f'registration-trial-{index:02d}.json').read_text()) for index in range(1, args.trial + 1)]
    base, report = evaluate(specs)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    name = f'trial-{args.trial:02d}'
    if args.refine:
        refinement = refinement_report(specs, report)
        report['refinementCheck'] = refinement
        (OUTPUT / f'{name}-refinement.json').write_text(json.dumps(refinement, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    (OUTPUT / f'{name}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    (OUTPUT / f'{name}.html').write_text(review(report, base))
    print(json.dumps(report['summary'], indent=2))
    for point in report['checks']:
        print(point['id'], *[None if point[key]['meters'] is None else round(point[key]['meters'], 2) for key in ('current', 'trial')])


if __name__ == '__main__':
    main()
