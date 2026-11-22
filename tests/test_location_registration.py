import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review_location_registration import MERCATOR_RADIUS, SPEC, audit, fit


class LocalRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(SPEC.read_text())
        self.world = list(map(float, (ROOT / self.spec['worldFile']).read_text().splitlines()))

    def test_fixed_holdouts_do_not_change_the_fit(self):
        before = audit(self.spec, self.world)
        self.spec['checks'][0]['scenePx'][0] += 10
        after = audit(self.spec, self.world)
        self.assertEqual(before['affineSatellitePxToScenePx'], after['affineSatellitePxToScenePx'])
        self.assertGreater(after['checkMaxMeters'], before['checkMaxMeters'])

    def test_converts_inverse_affine_residual_to_local_ground_meters(self):
        controls = [{'id': str(index), 'satellitePx': [east, south], 'scenePx': [3*east+south+4, south*2+7]}
                    for index, (east, south) in enumerate([(0, 0), (10, 0), (0, 10)])]
        checks = [{'id': 'check', 'satellitePx': [4, 3], 'scenePx': [31, 19]}]
        north_at_60 = MERCATOR_RADIUS * math.asinh(math.tan(math.radians(60)))
        result = audit({'region': 'synthetic', 'controls': controls, 'checks': checks},
                       (2, 0, 0, -2, -8, north_at_60+6))['checks'][0]
        self.assertAlmostEqual(result['predictedScenePx'][0], 19)
        self.assertAlmostEqual(result['predictedScenePx'][1], 13)
        self.assertAlmostEqual(result['referenceLonLat'][0], 0)
        self.assertAlmostEqual(result['referenceLonLat'][1], 60)
        self.assertAlmostEqual(result['equivalentMeters'], math.hypot(3, 3))

    def test_rejects_reused_and_collinear_landmarks(self):
        duplicate = copy.deepcopy(self.spec['controls'][0])
        duplicate['id'] = 'new-name'
        self.spec['checks'].append(duplicate)
        with self.assertRaisesRegex(ValueError, 'Repeated landmark'):
            audit(self.spec, self.world)
        with self.assertRaisesRegex(ValueError, 'two dimensions'):
            fit([{'satellitePx': [index, 2*index], 'scenePx': [index, index]} for index in range(4)])

    def test_yuqiao_is_the_largest_held_out_miss(self):
        result = audit(self.spec, self.world)
        worst = max(result['checks'], key=lambda point: point['equivalentMeters'])
        self.assertEqual(worst['id'], 'H1')
        self.assertAlmostEqual(result['checkMaxMeters'], 7.52, places=2)
        self.assertAlmostEqual(result['checkRmsMeters'], 5.34, places=2)
