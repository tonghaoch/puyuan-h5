import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from calibrate_illustration import MODEL, calibrate, cross, inputs
from register_illustration import ROOT, build_registration


class ParkRegistrationTest(unittest.TestCase):
    def test_model_reproduces_and_triangles_preserve_orientation(self):
        _, controls, checks, final, world = inputs()
        runtime, report = calibrate(controls, checks, final, world)
        baseline = json.loads((ROOT / 'references/geodata/illustration-registration-baseline.json').read_text())
        self.assertEqual(json.loads(json.dumps(runtime)), baseline)
        active, _, _, _ = build_registration()
        self.assertEqual(active, json.loads(MODEL.read_text()))
        self.assertLess(report['checkRmsMeters'], report['affineRmsMeters'])
        self.assertEqual(len(runtime['exclusionSites']), 2)
        self.assertLess(report['releaseMaxMeters'], 10)
        for triangle in runtime['triangles']:
            for key in ('controls', 'targets'):
                self.assertGreater(cross(*[runtime[key][index] for index in triangle]), 0)

    def test_release_checks_cannot_change_model_or_coverage(self):
        _, controls, checks, final, world = inputs()
        before, report = calibrate(controls, checks, final, world)
        changed = copy.deepcopy(final)
        changed[0]['scenePx'][1] += 80
        after, other = calibrate(controls, checks, changed, world)
        self.assertEqual(before, after)
        self.assertNotEqual(report['releaseMaxMeters'], other['releaseMaxMeters'])

    def test_no_reused_holdouts(self):
        _, controls, checks, final, world = inputs()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            calibrate(controls, checks, final + controls[:1], world)
