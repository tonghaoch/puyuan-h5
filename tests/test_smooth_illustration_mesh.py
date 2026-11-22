import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from calibrate_illustration import cross, train
from smooth_illustration_mesh import build_smooth_candidate, sample_mesh
from trial_illustration_registration import transfer


class SmoothIllustrationMeshTest(unittest.TestCase):
    def points(self):
        return [dict(id=str(index), satellitePx=source, scenePx=target)
                for index, (source, target) in enumerate([
                    ([0, 0], [0, 0]), ([100, 0], [100, 0]),
                    ([100, 100], [100, 100]), ([0, 100], [0, 100]),
                    ([50, 50], [60, 50]),
                ])]

    def test_shared_edges_stay_continuous_and_inverse_uses_the_same_mesh(self):
        points = self.points()
        mesh, audit = sample_mesh(points, train(points, 0), 3)
        self.assertEqual(mesh['supportSites'], [point['satellitePx'] for point in points])
        self.assertGreater(len(mesh['controls']), len(mesh['supportSites']))
        self.assertTrue(all(step['foldedTriangles'] == 0 for step in audit))
        for query in [[25, 25], [13, 71], [64, 29], [0, 100]]:
            projected = transfer(query, mesh['controls'], mesh['targets'], mesh['triangles'])
            inverse = transfer(projected, mesh['targets'], mesh['controls'], mesh['triangles'])
            for actual, expected in zip(inverse, query):
                self.assertAlmostEqual(actual, expected, places=7)
        left = transfer([25-1e-6, 25+1e-6], mesh['controls'], mesh['targets'], mesh['triangles'])
        right = transfer([25+1e-6, 25-1e-6], mesh['controls'], mesh['targets'], mesh['triangles'])
        self.assertLess(sum((a-b)**2 for a, b in zip(left, right)), 1e-8)

    def test_reflection_is_rejected_instead_of_publishing_an_ambiguous_inverse(self):
        points = self.points()
        for point in points:
            point['scenePx'] = [-point['satellitePx'][0], point['satellitePx'][1]]
        with self.assertRaisesRegex(ValueError, 'folds'):
            sample_mesh(points, train(points, 0), 2)

    def test_selection_cannot_raise_the_established_control_displacement_gate(self):
        with self.assertRaisesRegex(ValueError, 'four-pixel'):
            build_smooth_candidate(self.points(), dict(kind='control-loo-spline-mesh', maxAnchorPx=5, subdivisionLevels=2))
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            build_smooth_candidate(self.points(), dict(kind='unsupported', maxAnchorPx=4, subdivisionLevels=2))

    def test_positive_triangles_do_not_admit_a_boundary_that_wraps_twice(self):
        points = [dict(id='center', satellitePx=[0, 0], scenePx=[0, 0])]
        for index in range(9):
            angle = index*2*math.pi/9
            points.append(dict(id=str(index), satellitePx=[100*math.cos(angle), 100*math.sin(angle)],
                               scenePx=[100*math.cos(2*angle), 100*math.sin(2*angle)]))
        with self.assertRaisesRegex(ValueError, 'boundary'):
            sample_mesh(points, train(points, 0), 0)
