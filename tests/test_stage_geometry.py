import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.stage import fan, platform


class StageGeometry(unittest.TestCase):
    def setUp(self):
        self.stage = json.loads((ROOT / 'src/data/landmark-structures.json').read_text())['sites']['waterside-stage']

    def test_pier_belongs_to_the_two_eave_faces_not_the_glass(self):
        canopy = self.stage['canopy']
        before = ElementTree.fromstring(fan(canopy))
        canopy['pierWidths'][2] += .5
        after = ElementTree.fromstring(fan(canopy))
        changed = [part.attrib for part, other in zip(before, after) if ElementTree.tostring(part) != ElementTree.tostring(other)]
        self.assertEqual(changed, [{'data-eave-bay': '1'}, {'data-eave-bay': '2'}])

    def test_bearer_is_below_the_deck_and_sized_independently(self):
        deck = self.stage['deck']
        before = ElementTree.fromstring(platform(deck))
        deck['bearer']['depth'] += .5
        after = ElementTree.fromstring(platform(deck))
        self.assertNotEqual(before[0].get('d'), after[0].get('d'))
        self.assertEqual([ElementTree.tostring(part) for part in before[1:]], [ElementTree.tostring(part) for part in after[1:]])
