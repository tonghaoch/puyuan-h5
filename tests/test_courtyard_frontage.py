import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from art.street_houses import colonnade


class CourtyardFrontageTests(unittest.TestCase):
    def test_front_keeps_a_solid_end_behind_the_last_post(self):
        frame = dict(beam=[[0, 3], [10, 2]], columns=[0, .4, 1], infill='courtyard-front', limePiers=[.4])
        ordinary = ElementTree.fromstring(colonnade(frame, 5))
        extended = ElementTree.fromstring(colonnade(dict(frame, limeEnd=[16, 1.8]), 5))
        self.assertEqual(extended[0].get('d'), 'M10,2L16,1.8L16,6.8L10,7Z')
        self.assertEqual([item.attrib for item in extended[2:]], [item.attrib for item in ordinary])
        self.assertEqual([item.get('stroke') for item in ordinary[-3:]], ['#443530', '#dfd5c9', '#443530'])

    def test_window_apron_does_not_add_a_second_row_of_openings(self):
        frame = dict(beam=[[0, 0], [20, 0]], infill='lime-casements', openings=[[.1, .4, .3, .56]],
                     apronLevel=.64, apronJoints=[.3])
        front = ElementTree.fromstring(colonnade(frame, 10))
        self.assertEqual(front[0].get('data-windows'), '1')
        self.assertEqual(front[-2].get('d'), 'M6,6.4L6,9.4')

    def test_sloping_foot_does_not_move_the_eave(self):
        frame = dict(beam=[[0, 0], [10, 0]], infill='courtyard-front', columns=[0, .5, 1], footDepths=[5, 3])
        front = ElementTree.fromstring(colonnade(frame, 5))
        self.assertEqual(front[0].get('d'), 'M0,0L10,0L10,3L0,5Z')
