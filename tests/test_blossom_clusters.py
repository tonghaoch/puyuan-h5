from pathlib import Path
from random import Random
import sys
import unittest
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from art.blossom_clusters import blossom_clusters
from art.plantings import planting


class FlowerFrameTest(unittest.TestCase):
    stem = dict(species='blooming-bough', paint='leaf', root=[3, 1], size=[32, 40], bloom='pink',
                flowerFrame=dict(fork=8, bare=.47, tuft=1, span=1))

    def frame(self, **changes):
        stem = dict(self.stem, flowerFrame={**self.stem['flowerFrame'], **changes})
        return ElementTree.fromstring(blossom_clusters(Random(27), stem))

    def test_sprays_and_openings_can_change_without_moving_the_wood(self):
        original = self.frame()
        wood = lambda crown: ElementTree.tostring(crown.find("g[@data-part='wood']"))
        spray = lambda crown: crown.find("g[@data-part='flower-spray']")
        for changed in (self.frame(tuft=1.6), self.frame(bare=.66)):
            self.assertEqual(wood(original), wood(changed))
            self.assertNotEqual(ElementTree.tostring(spray(original)), ElementTree.tostring(spray(changed)))
        self.assertEqual(spray(original).find('path').get('d'), spray(self.frame(tuft=1.6)).find('path').get('d'))
        self.assertNotEqual(spray(original).find('path').get('d'), spray(self.frame(bare=.66)).find('path').get('d'))
        self.assertNotEqual(wood(original), wood(self.frame(fork=4)))

    def test_frame_uses_authored_leaders_and_root_only_inside_opted_in_stem(self):
        stem = dict(self.stem, leaders=[[-9, -35], [8, -31]])
        model = dict(id='specimen', x=20, y=30, stems=[stem])
        drawing = ElementTree.fromstring(planting(model))
        self.assertIn('translate(3 1)', drawing.find('g').get('transform'))
        self.assertEqual(len(drawing.findall(".//g[@data-part='flower-spray']")), 6)
        self.assertIn('8 -31', drawing.find(".//g[@data-part='wood']")[-1].get('d'))
        del stem['flowerFrame']
        self.assertNotIn('flower-frame', planting(model))
        self.assertIn('flower-spurs', planting(model))
