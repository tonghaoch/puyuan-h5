import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from calibrate_illustration import MODEL
from register_illustration import RECIPE, ROOT, build_registration
from trial_illustration_registration import lonlat


class ActiveRegistrationTest(unittest.TestCase):
    def copy_inputs(self, directory):
        data = directory / 'references/geodata'
        data.mkdir(parents=True)
        recipe = json.loads((ROOT / RECIPE).read_text())
        for name in list(recipe['inputSha256']) + [RECIPE.name]:
            (data / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / 'references/geodata' / name, data / name)
        boundary = directory / 'public/geodata'
        boundary.mkdir(parents=True)
        shutil.copyfile(ROOT / 'public/geodata/boundary.geojson', boundary / 'boundary.geojson')

    def test_active_model_reproduces_and_only_changes_the_confirmed_observations(self):
        runtime, report, serialized, _ = build_registration()
        self.assertEqual(runtime, json.loads(MODEL.read_text()))
        self.assertEqual(hashlib.sha256(serialized.encode()).hexdigest(), report['candidateSha256'])
        baseline = json.loads((ROOT / 'references/geodata/illustration-registration-baseline.json').read_text())
        self.assertEqual(runtime['exclusionSites'], baseline['exclusionSites'])
        self.assertEqual(runtime['coverageGuard'], dict(hull=baseline['hull'], controls=baseline['controls']))
        self.assertEqual(len(runtime['controls']), 23)
        changes = [index for index, (before, after) in enumerate(zip(baseline['controls'], runtime['controls'])) if before != after]
        self.assertEqual(changes, [19, 20])
        self.assertEqual(runtime['targets'][19], [257, 1059])
        self.assertEqual(runtime['controls'][20], [536, 921])
        self.assertEqual(len(report['checks']), 17)
        self.assertEqual({item['new']['id'] for item in report['corrections']}, {'S1', 'S2'})
        bridge = next(point for point in report['checks'] if point['id'] == 'K4')
        self.assertEqual(bridge['satellitePx'], [347, 1035])
        self.assertEqual(bridge['scenePx'], [345, 1044])
        self.assertEqual(bridge['priorObservation']['satellitePx'], [316, 1020])
        displayed = next(point for point in report['coverageChecks']['trialChecks'] if point['id'] == 'K4')
        self.assertEqual(displayed['satellitePx'], bridge['satellitePx'])
        self.assertEqual(displayed['referenceLonLat'], lonlat(bridge['satellitePx'], runtime['world']))
        street = next(point for point in report['checks'] if point['id'] == 'V6')
        self.assertEqual(street['satellitePx'], [636, 996])
        self.assertEqual(street['priorObservation']['satellitePx'], [634, 987])

    def test_checks_can_change_audit_results_but_not_the_fit_or_visibility_policy(self):
        before, report, _, _ = build_registration()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.copy_inputs(root)
            path = root / 'references/geodata/park-registration.json'
            spec = json.loads(path.read_text())
            spec['releaseChecks'][0]['scenePx'][0] += 80
            path.write_text(json.dumps(spec))
            recipe_path = root / RECIPE
            recipe = json.loads(recipe_path.read_text())
            recipe['inputSha256'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            recipe_path.write_text(json.dumps(recipe))
            after, other, _, _ = build_registration(root)
        self.assertEqual(before, after)
        self.assertNotEqual(next(point['trial'] for point in report['checks'] if point['id'] == 'F1'),
                            next(point['trial'] for point in other['checks'] if point['id'] == 'F1'))

    def test_unrecorded_observation_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.copy_inputs(root)
            path = root / 'references/geodata/registration-trial-02.json'
            spec = json.loads(path.read_text())
            spec['replaceControls'][0]['scenePx'][0] += 1
            path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError, 'sources changed'):
                build_registration(root)
