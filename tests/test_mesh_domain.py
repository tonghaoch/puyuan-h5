import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from calibrate_illustration import Mesh, cross


class MeshDomainTest(unittest.TestCase):
    def test_nearly_collinear_valid_controls_cover_their_entire_triangle(self):
        points = [dict(satellitePx=point, scenePx=point) for point in [[259, 1044], [893, 960], [948, 953]]]
        for ordered in itertools.permutations(points):
            mesh = Mesh(list(ordered))
            self.assertEqual(len(mesh.triangles), 1, 'A valid thin triangle was omitted')
            self.assertEqual(sum(cross(*[mesh.sites[index] for index in tri]) for tri in mesh.triangles), 182)
            query = [sum(point['satellitePx'][axis] for point in points)/3 for axis in (0, 1)]
            result = mesh.project(query)
            for actual, expected in zip(result, query):
                self.assertAlmostEqual(actual, expected, places=7)

    def test_invalid_collinear_domain_fails_explicitly(self):
        points = [dict(satellitePx=[index, index], scenePx=[index, index]) for index in range(4)]
        with self.assertRaisesRegex(ValueError, 'nondegenerate'):
            Mesh(points)
