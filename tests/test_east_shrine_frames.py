import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from art.east_shrine_frames import terraced_wall
from art.street_houses import house


class SanctuaryFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sites = json.loads((ROOT/'src/data/street-houses.json').read_text())['sites']
        cls.owners = [group for groups in sites.values() for group in groups if 'terracedTimberFrames' in group]
        cls.group, = cls.owners
        cls.frames = cls.group['terracedTimberFrames']

    def test_only_main_sanctuary_tiers_are_selected(self):
        self.assertEqual(self.group['id'], 'main-sanctuary-and-west-gate')
        self.assertEqual(set(self.frames), {'0','1','2','3'})
        self.assertEqual([self.frames[str(index)]['profile'] for index in range(4)], ['backed-porch']+['closed-drum']*3)

    def test_original_walls_stay_unclipped_behind_each_timber_frame(self):
        for index, frame in self.frames.items():
            model = self.group['houses'][int(index)]
            original = house(model)[0]
            drawing = terraced_wall(original, model, frame, 'fixture')
            node = ET.fromstring(drawing)
            self.assertIn('<g data-original-walls="1">'+original+'</g>', drawing)
            self.assertEqual(len(node.findall('defs/clipPath')), 1)
            self.assertEqual(node[-1].get('clip-path'), 'url(#inset-fixture)')

    def test_post_stations_control_the_bays_and_must_be_ordered(self):
        model = self.group['houses'][0]; original = house(model)[0]; frame = self.frames['0']
        self.assertNotEqual(terraced_wall(original, model, frame, 'fixture'), terraced_wall(original, model, dict(frame,posts=[.15,.88]), 'fixture'))
        with self.assertRaises(ValueError):
            terraced_wall(original, model, dict(frame,posts=[.8,.4]), 'fixture')
