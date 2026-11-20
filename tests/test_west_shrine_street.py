from copy import deepcopy
import json
import math
from pathlib import Path
import re
import sys
import unittest
from xml.etree import ElementTree as ET

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.street_houses import detail_body, house, roof_faces, roof_frame


def drawing(groups):
    return ET.fromstring('<site>' + detail_body(groups, []) + '</site>')


def building(parent, index):
    roof_id = f'{parent.get("id")}-roof-{index}'
    return next(node for node in parent if node.get('data-front') and node.find(f'.//*[@id="{roof_id}"]') is not None)


class WestShrineStreetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = json.loads((ROOT / 'src/data/street-houses.json').read_text())['sites']['xiangyun-temple']
        cls.sanctuary, cls.street = cls.groups[-2:]
        cls.rendered = drawing(cls.groups)

    def test_return_has_joined_bearing_faces_between_old_wall_and_gate(self):
        sections = self.sanctuary['cappedGateReturn']['sections']
        self.assertLess(min(math.dist(point, self.street['walls'][0][0][0]) for point in sections[1]), 1)
        self.assertLess(math.dist(sections[-1][-1], self.sanctuary['houses'][4][:2]), 1)
        parent = self.rendered.find(f'./g[@id="{self.sanctuary["id"]}"]')
        cap = parent.find('./g[@id="west-gate-capped-return"]')
        self.assertLess(list(parent).index(cap), list(parent).index(building(parent, 4)))
        self.assertEqual(len(cap), 3 * (len(sections) - 1))
        for index, (start, end) in enumerate(zip(sections, sections[1:])):
            for offset, (upper, lower) in enumerate(((2, 3), (0, 1), (1, 2))):
                path = cap[3 * index + offset].get('d')
                actual = [[float(number) for number in point] for point in re.findall(r'(-?[\d.]+),(-?[\d.]+)', path)]
                self.assertEqual(actual, [start[upper], end[upper], end[lower], start[lower]])
                self.assertTrue(cv2.isContourConvex(np.float32(actual)))

    def test_three_separate_pitched_wings_have_founded_gables_and_open_roof_gaps(self):
        wings = self.street['courtWingVolumes']
        self.assertEqual(set(wings), {'0', '1', '2'})
        parent = self.rendered.find(f'./g[@id="{self.street["id"]}"]')
        footprints = []
        for index in range(3):
            wing = wings[str(index)]
            model, form, feet = wing['model'], wing['roof'], wing['feet']
            frame = roof_frame(model, form)
            slopes = roof_faces(model, frame, form)
            self.assertEqual(len(slopes), 2)
            areas = [cv2.contourArea(np.float32(points), oriented=True) for points in slopes]
            self.assertLess(areas[0] * areas[1], 0)
            self.assertTrue(all(cv2.isContourConvex(np.float32(points)) for points in slopes))
            self.assertEqual(form['endFace'], 'limewash')
            for eave, foot in zip((frame[1], frame[3]), feet['gable']['ends']):
                self.assertGreater(foot[1], eave[1] + 1)
            walls, roof = house(model, None, form, None, feet)
            roof_id = f'{self.street["id"]}-roof-{index}'
            expected = ET.fromstring(f'<g data-front="{model[-1]}">{walls}<g id="{roof_id}">{roof}</g></g>')
            self.assertEqual(ET.tostring(building(parent, index)), ET.tostring(expected))
            footprints.append(cv2.convexHull(np.float32(frame)))
        for first, following in zip(footprints, footprints[1:]):
            self.assertTrue(all(cv2.pointPolygonTest(following, tuple(map(float, point[0])), True) < -.5 for point in first))
            self.assertEqual(cv2.intersectConvexConvex(first, following)[0], 0)

    def test_six_gate_and_hall_bodies_court_and_cross_street_stay_in_order(self):
        old = deepcopy(self.groups)
        old[-2].pop('cappedGateReturn')
        old[-1].pop('courtWingVolumes')
        original, revised = drawing(old), drawing(self.groups)
        revised[-2].remove(revised[-2].find('./g[@id="west-gate-capped-return"]'))
        self.assertEqual(sum(bool(node.get('data-front')) for node in revised[-2]), 6)
        self.assertIsNotNone(revised[-2].find('./use[@href="#court-layer-xiangyun-west-gate-apron"]'))
        for index in range(3):
            body = building(revised[-1], index)
            pos = list(revised[-1]).index(body)
            revised[-1].remove(body)
            revised[-1].insert(pos, building(original[-1], index))
        self.assertEqual(ET.tostring(revised), ET.tostring(original))
