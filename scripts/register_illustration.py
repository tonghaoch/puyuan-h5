"""Reproduce the active correspondence corrections and audit every retained check."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from calibrate_illustration import MODEL, Mesh, cross, hull, inputs, supported
from review_location_registration import ROOT, OUTPUT
from smooth_illustration_mesh import boundary_crossings, select_on_controls
from trial_illustration_registration import assess, inside, lonlat, pick_sensitivity, review, spatial_audit, substitute, totals

RECIPE = Path('references/geodata/registration-release-07.json')


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_registration(root=ROOT):
    recipe_path = root / RECIPE
    recipe = json.loads(recipe_path.read_text())
    data = recipe_path.parent
    hashes = {name: fingerprint(data / name) for name in recipe['inputSha256']}
    if hashes != recipe['inputSha256']:
        raise ValueError('Registration sources changed; revise the recorded observations and recipe explicitly')
    baseline = json.loads((data / recipe['baseline']).read_text())
    base, original, screening, release, world = inputs(root)
    if (baseline['controls'] != [point['satellitePx'] for point in original] or
            baseline['targets'] != [point['scenePx'] for point in original] or baseline['world'] != world):
        raise ValueError('Frozen baseline does not match the original observed controls')
    added_checks = [point for name in recipe['checkSources']
                    for point in json.loads((data / name).read_text())['newChecks']]
    checks = screening + release + added_checks
    for name in recipe.get('checkReobservations', []):
        for correction in json.loads((data / name).read_text())['corrections']:
            index = next(index for index, point in enumerate(checks) if point['id'] == correction['id'])
            previous = checks[index]
            if any(previous[key] != value for key, value in correction['previous'].items()):
                raise ValueError('Reobserved check does not match the preserved original values')
            checks[index] = dict(correction['corrected'], priorObservation=previous, group='reobserved')
    controls = original
    corrections = []
    for correction in recipe['corrections']:
        spec = json.loads((data / correction['source']).read_text())
        selected = [point for point in spec['replaceControls'] if point['id'] in correction['ids']]
        if {point['id'] for point in selected} != set(correction['ids']):
            raise ValueError('Release recipe names an unknown correction')
        for point in selected:
            corrections.append(dict(old=next(old for old in original if old['id'] == point['id']), new=point))
        controls = substitute(controls, dict(replaceControls=selected, addControls=[]), checks)
    fitted, selection = select_on_controls(controls, 4)
    if not isinstance(fitted, Mesh):
        raise ValueError('Control-only selection changed model family; this release requires a separate review')
    if any(cross(*[fitted.targets[index] for index in tri]) <= 0 for tri in fitted.triangles):
        raise ValueError('Corrected mesh folds')
    if boundary_crossings(fitted.sites, fitted.targets, fitted.triangles):
        raise ValueError('Corrected mesh boundary intersects itself')
    folds = []
    for index, point in enumerate(controls):
        rest = controls[:index]+controls[index+1:]
        if not supported(point['satellitePx'], rest):
            continue
        mesh = Mesh(rest)
        result = assess(dict(controls=mesh.sites, targets=mesh.targets, triangles=mesh.triangles), point, world)
        if result['meters'] is None:
            raise ValueError('A supported control leave-one-out result cannot be measured')
        folds.append(dict(id=point['id'], **result))
    allowance = max(baseline['registrationAllowanceM'], math.ceil(max(point['meters'] for point in folds)))
    runtime = dict(world=world, hull=hull(controls),
                   controls=fitted.sites, targets=fitted.targets, triangles=[list(triangle) for triangle in fitted.triangles],
                   kind='mesh', supportPx=baseline['supportPx'], imageryAllowanceM=baseline['imageryAllowanceM'],
                   registrationAllowanceM=allowance, exclusionSites=baseline['exclusionSites'],
                   coverageGuard=dict(hull=baseline['hull'], controls=baseline['controls']),
                   calibrationVersion=recipe['version'])
    ring = json.loads((root / 'public/geodata/boundary.geojson').read_text())['features'][0]['geometry']['coordinates'][0]
    rows = [dict(point, group=point.get('group', 'screening' if point in screening else 'previous-release' if point in release else 'prior-trial'),
                 publicPark=inside(lonlat(point['satellitePx'], world), ring), current=assess(baseline, point, world),
                 trial=assess(runtime, point, world), pickSensitivity=pick_sensitivity(runtime, point, world)) for point in checks]
    summaries = {name: {key: totals(subset, key) for key in ('current', 'trial')} for name, subset in
                 [('all', rows), ('publicPark', [row for row in rows if row['publicPark']]), ('new', [])]}
    serialized = json.dumps(runtime, separators=(',', ':'), allow_nan=False)+'\n'
    report = dict(trial=recipe['version'], previousTrial=None, baselineLabel='原配准版', candidateLabel='本地修正版',
                  baselineSha256=fingerprint(data / recipe['baseline']),
                  candidateSha256=hashlib.sha256(serialized.encode()).hexdigest(),
                  recipeSha256=fingerprint(recipe_path), inputSha256=hashes, summary=summaries, checks=rows,
                  boundarySha256=fingerprint(root / 'public/geodata/boundary.geojson'),
                  corrections=corrections, addedControls=[], controlCount=len(controls), hasImageryAudit=False,
                  modelSelection=None, controlSelection=selection, controlLeaveOneOut=folds,
                  spatial=spatial_audit(ring, baseline, runtime, rows, world))
    def legacy_row(point):
        row = next(row for row in rows if row['id'] == point['id'])
        observed = {key: row[key] for key in ('id', 'label', 'satellitePx', 'scenePx')}
        if 'priorObservation' in row:
            observed['priorObservation'] = row['priorObservation']
        return dict(observed, referenceLonLat=lonlat(row['satellitePx'], world),
                    predictedScenePx=row['trial']['scene'], equivalentMeters=row['trial']['meters'])
    report['coverageChecks'] = dict(checks=list(map(legacy_row, screening)),
                                   releaseChecks=list(map(legacy_row, release)), trialChecks=list(map(legacy_row, added_checks)))
    return runtime, report, serialized, base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-model', action='store_true')
    args = parser.parse_args()
    runtime, report, serialized, base = build_registration()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.write_model:
        if fingerprint(MODEL) not in (report['baselineSha256'], report['candidateSha256']):
            raise ValueError('Active model has unrelated changes; inspect them before applying this release')
        MODEL.write_text(serialized)
    (OUTPUT / 'release-07-model.json').write_text(serialized)
    (OUTPUT / 'release-07.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    (OUTPUT / 'release-07.html').write_text(review(report, base))
    (OUTPUT / 'park-report.json').write_text(json.dumps(report['coverageChecks'], ensure_ascii=False, indent=2)+'\n')
    (OUTPUT / 'park-review.html').write_text(review(report, base))
    print(json.dumps(dict(version=runtime['calibrationVersion'], controls=len(runtime['controls']),
                          selection=report['controlSelection']['chosen'], allowance=runtime['registrationAllowanceM'],
                          baseline=report['summary']['all']['current'], corrected=report['summary']['all']['trial']), indent=2))


if __name__ == '__main__':
    main()
