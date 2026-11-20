import json
import re
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.landscape import quay_edge


class ShorelineEnsemblesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.town = json.loads((ROOT / 'src/data/town-landscape.json').read_bytes())
        cls.ground = (ROOT / 'public/art/native/ground.svg').read_text()

    def test_pool_seats_join_four_existing_stone_sections(self):
        region = self.town['water'][0]
        arc = next(face for face in region['bankFaces'] if face['id'] == 'stage-arc-quay')
        east, south = quay_edge(region, arc)[0]
        toe = (east, round(south - arc['toeLift'], 2))
        top = (east, round(toe[1] - arc['height'], 2))
        courses = self.town['visibleBankCourses']
        group = ElementTree.fromstring(self.ground).find('.//*[@id="pool-turn-stone-seats"]')
        self.assertIsNotNone(group, 'The low coping must bridge both gaps, not replace the middle course')
        faces = []
        for wall in list(group)[::2]:
            coords = list(map(float, re.findall(r'-?[\d.]+', wall.get('d'))))
            faces.append(list(zip(coords[::2], coords[1::2])))
        def starts(face):
            return (face[0], face[3])
        def ends(face):
            return (face[1], face[2])
        def section(course, index):
            return tuple(tuple(course[key][index]) for key in ('toe', 'cap'))
        self.assertEqual(starts(faces[0]), (toe, top))
        self.assertEqual(ends(faces[1]), section(courses[68], -1))
        self.assertEqual(starts(faces[2]), section(courses[68], 0))
        self.assertEqual(ends(faces[-1]), section(courses[67], -1))
        self.assertLess(self.ground.index('id="pool-turn-stone-seats"'), self.ground.index('id="visible-canal-banks"'))

    def test_temple_bridge_pair_stays_behind_the_willow_and_leaves_the_bank_open(self):
        trees = {row['id']: row for row in self.town['trees']}
        pair, willow = trees['east-walk-bamboo'], trees['tree-15']
        self.assertEqual(len({tuple(stem['root']) for stem in pair.get('stems', [])}), 2)
        self.assertLess(pair['y'], willow['y'])
        self.assertEqual(willow['stems'][0]['species'], 'willow')
        self.assertNotIn('tree-304', trees)
        self.assertEqual(self.town['retiredPlantInstances'].count('tree-304'), 1)

    def test_merchant_embankment_supports_the_dry_top_without_hiding_the_walk(self):
        top, support = 'id="sw21-merchant-grass-shelf-top"', 'id="sw21-merchant-grass-shelf-return"'
        self.assertEqual(self.ground.count(top), 1, 'Expected one dry merchant shelf')
        self.assertEqual(self.ground.count(support), 1, 'Expected one joined stone return')
        first_walk = f'id="{self.town["walks"][0]["id"]}"'
        self.assertLess(self.ground.index(top), self.ground.index(first_walk))
        self.assertLess(self.ground.index('id="visible-canal-banks"'), self.ground.index(support))
        self.assertLess(self.ground.index(support), self.ground.index('id="canal-currents"'))
        from art.sw_quay_tables import retired_traces
        self.assertEqual(retired_traces(), {'wood-497'})
