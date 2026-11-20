import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from art.north_gallery import eaved_shutters
from art.street_houses import colonnade


class NorthGalleryTests(unittest.TestCase):
    def setUp(self):
        self.frame = {'infill':'stained-shutters','beam':[(0,10),(25,9)],'columns':[0,.4,1],
                      'soffit':{'eave':[(-1,9),(26,8.5)],'recess':.28}}

    def test_existing_shutters_and_feet_are_preserved(self):
        def verify(front, height):
            self.assertNotIn('soffit',front)
            self.assertEqual(front['columns'],self.frame['columns'])
            for (east, head),(original_east,original_head) in zip(front['beam'],self.frame['beam']):
                self.assertEqual(east,original_east)
                self.assertAlmostEqual(head+height,original_head+4)
            return colonnade(front,height)
        svg=ElementTree.fromstring('<svg>'+eaved_shutters(self.frame,4,verify)+'</svg>')
        self.assertIsNotNone(svg.find(".//g[@data-infill='stained-shutters']"))
        self.assertEqual(len(svg.findall(".//g[@data-soffit]/path")),2)
        self.assertEqual(len(svg.findall(".//g[@data-eave-bearing]")),len(self.frame['columns']))

    def test_lining_is_opt_in_and_cannot_cross_the_beam(self):
        legacy=dict(self.frame); del legacy['soffit']
        self.assertNotIn('data-soffit',colonnade(legacy,4))
        self.assertIn('data-soffit',colonnade(self.frame,4))
        with self.assertRaises(ValueError):
            colonnade(dict(self.frame,soffit={'eave':[(0,15),(25,8)],'recess':.1}),4)
