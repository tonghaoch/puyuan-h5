import copy
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from trial_illustration_registration import TRIAL_DIR, assess, evaluate, ground_distance, substitute, totals, transfer


class IllustrationTrialTest(unittest.TestCase):
    def test_inverse_uses_deployed_diagonal_even_when_error_crosses_it(self):
        world = [1, 0, 0, -1, 0, 0]
        model = {'controls': [[0, 0], [100, 0], [100, 100], [0, 100]],
                 'targets': [[0, 0], [200, 0], [100, 100], [0, 50]], 'triangles': [[0, 1, 2], [0, 2, 3]]}
        observed = transfer([20, 70], model['controls'], model['targets'], model['triangles'])
        error = assess(model, {'satellitePx': [70, 20], 'scenePx': observed}, world)
        self.assertAlmostEqual(error['meters'], math.sqrt(5000), places=5)
        self.assertEqual(ground_distance([1, 2], [1, 2], world), 0)
        self.assertEqual(assess(model, {'satellitePx': [0, 0], 'scenePx': [500, 500]}, world)['reason'], 'outside-painted-mesh')
        self.assertIsNone(assess(model, {'satellitePx': [-1, 0], 'scenePx': [0, 0]}, world)['meters'])

    def test_never_counts_boundary_threshold_or_missing_as_a_pass(self):
        rows = [{'trial': {'meters': value}} for value in [0, 9.99, 10, 19, None]]
        self.assertEqual(totals(rows, 'trial'), dict(points=5, below10=2, atLeast10=2, unmeasured=1, maxMeasuredM=19))

    def test_frozen_checks_cannot_double_as_controls(self):
        held = {'id': 'K', 'satellitePx': [20, 20], 'scenePx': [18, 19]}
        for field in ['id', 'satellitePx', 'scenePx']:
            anchor = {'id': 'S', 'satellitePx': [1, 0], 'scenePx': [2, 0], field: held[field]}
            with self.assertRaisesRegex(ValueError, 'overlap'):
                substitute([anchor], {'replaceControls': [], 'addControls': []}, [held])

    def test_public_boundary_does_not_remove_drawn_island_or_other_missing_results(self):
        specs = [json.loads((TRIAL_DIR / f'registration-trial-{index:02d}.json').read_text()) for index in [1, 2]]
        _, report = evaluate(specs)
        rows = {row['id']: row for row in report['checks']}
        self.assertFalse(rows['V5']['publicPark'])
        self.assertGreater(rows['V5']['trial']['meters'], 10)
        self.assertEqual(rows['K1']['group'], 'prior-trial')
        self.assertEqual(rows['K3']['group'], 'new')
        self.assertLess(rows['V6']['trial']['meters'], 10)
        self.assertLess(report['spatial']['within50mOfCheck'], report['spatial']['parkSamples'])
        self.assertEqual(report['summary']['all']['trial']['points'], len(rows))
        modified = copy.deepcopy(specs)
        modified[1]['newChecks'][0]['scenePx'][0] += 3
        _, other = evaluate(modified)
        self.assertEqual([row['trial']['scene'] for row in report['checks']], [row['trial']['scene'] for row in other['checks']])

    def test_previous_candidate_is_recomputed_on_the_same_expanded_check_set(self):
        specs = [json.loads((TRIAL_DIR / f'registration-trial-{index:02d}.json').read_text()) for index in [1, 2, 3]]
        _, second = evaluate(specs[:2])
        _, third = evaluate(specs)
        before = {row['id']: row for row in second['checks']}
        after = {row['id']: row for row in third['checks']}
        self.assertEqual(set(after), set(before) | {'K4', 'K5'})
        for point_id, row in before.items():
            self.assertEqual(after[point_id]['previousTrial'], row['trial'])
            self.assertEqual(after[point_id]['current'], row['current'])
        self.assertEqual(third['previousTrial'], 2)
        self.assertEqual(third['summary']['new']['trial']['points'], 2)
        for key in ['current', 'previousTrial', 'trial']:
            counts = third['summary']['all'][key]
            self.assertEqual(counts['points'], len(after))
            self.assertEqual(counts['below10'] + counts['atLeast10'] + counts['unmeasured'], len(after))
        self.assertEqual(after['K3']['group'], 'prior-trial')
        self.assertNotIn('R3-WB', after)
        # Both nominal check classifications are sensitive to the explicitly assumed pick tolerances.
        for point_id in ['K4', 'K5']:
            sensitivity = after[point_id]['pickSensitivity']
            self.assertLess(sensitivity['sampledMinMeters'], 10)
            self.assertGreater(sensitivity['sampledMaxMeters'], 10)
            self.assertEqual(sensitivity['sampledBelow10'] + sensitivity['sampledAtLeast10'] + sensitivity['unmeasured'], 81)

    def test_missing_or_reordered_trial_history_is_rejected(self):
        specs = [json.loads((TRIAL_DIR / f'registration-trial-{index:02d}.json').read_text()) for index in [1, 2, 3]]
        for history in [[], specs[1:], [specs[0], specs[2]], list(reversed(specs))]:
            with self.assertRaisesRegex(ValueError, 'contiguous'):
                evaluate(history)

    def test_model_family_experiment_changes_no_observed_points_or_application_baseline(self):
        specs = [json.loads((TRIAL_DIR / f'registration-trial-{index:02d}.json').read_text()) for index in [1, 2, 3, 4]]
        _, third = evaluate(specs[:3])
        _, fourth = evaluate(specs)
        self.assertEqual(fourth['baselineSha256'], third['baselineSha256'])
        self.assertEqual(fourth['controlCount'], third['controlCount'])
        self.assertEqual(fourth['summary']['new']['trial']['points'], 0)
        self.assertEqual(len(fourth['checks']), len(third['checks']))
        for earlier, later in zip(third['checks'], fourth['checks']):
            for field in ['id', 'satellitePx', 'scenePx', 'current']:
                self.assertEqual(earlier[field], later[field])
            self.assertEqual(later['previousTrial'], earlier['trial'])
        self.assertEqual(fourth['modelSelection']['observedControlCount'], fourth['controlCount'])
        self.assertGreater(fourth['modelSelection']['refinement'][-1]['meshNodes'], fourth['controlCount'])
