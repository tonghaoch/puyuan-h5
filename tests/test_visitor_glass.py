from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.site_details import glass_hall, visitor


class VisitorGlass(unittest.TestCase):
    def test_long_hall_splices_both_rails_at_each_projected_bent(self):
        def hall(bays, run):
            return ElementTree.fromstring('<svg>' + glass_hall((0, 0), (12, -9), (24, 0), run, 5, bays, True) + '</svg>')
        ordinary = hall(9, (-9, -45))
        compact = hall(6, (-9, -45))
        skewed = hall(9, (-3, -45))
        rows = ordinary.findall('.//g[@data-east-roof-bent]')
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(compact.findall('.//g[@data-east-roof-bent]')), 5)
        for node in rows:
            self.assertEqual(len(node.findall('polygon')), 2)
        self.assertNotEqual(ElementTree.tostring(rows[0]), ElementTree.tostring(skewed.find('.//g[@data-east-roof-bent]')))
        for model in (compact, skewed):
            self.assertEqual(ElementTree.tostring(ordinary.find('.//g[@data-part="east-end-truss"]')),
                             ElementTree.tostring(model.find('.//g[@data-part="east-end-truss"]')))

    def test_link_meets_the_west_hall_without_replacing_the_small_hall(self):
        small = glass_hall((0, 0), (4, -3), (9, 0), (-1, -8), 3, 3)
        self.assertNotIn('east-roof-bent', small)
        parts = [node.get('data-part') for node in ElementTree.fromstring(visitor())]
        self.assertLess(parts.index('west-link-frame'), parts.index('west-glass-elevation'))
        self.assertLess(parts.index('west-glass-elevation'), parts.index('west-pitched-frames'))
