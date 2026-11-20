import random
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.landscape import tree
from art.plantings import open_spire


class BankEvergreen(unittest.TestCase):
    def test_only_opted_in_stems_acquire_needle_sprays(self):
        stem = dict(species='spire', root=[0, 0], size=[32, 40], paint='sage', habit='open-spire')
        model = dict(id='sample-pair', x=502, y=602, stems=[stem, dict(stem, root=[10, 3])])
        before = tree(model)
        self.assertIn(open_spire(random.Random('sample-pair-stem-0'), 'sage'), before)
        original = ElementTree.fromstring(before)
        stem['habit'] = 'bank-needle-forks'
        changed = ElementTree.fromstring(tree(model))
        self.assertEqual(original[0].attrib, changed[0].attrib)
        self.assertEqual(ElementTree.tostring(original[1]), ElementTree.tostring(changed[1]))
        sprays = changed[0].findall('.//g[@data-needle-spray]')
        self.assertGreater(len(sprays), 2)
        self.assertEqual(len({spray.find('path').get('d') for spray in sprays}), len(sprays))
        stem['habit'] = 'open-spire'
        self.assertEqual(tree(model), before)

    def test_pigment_changes_do_not_move_branches_or_close_the_forks(self):
        stem = dict(species='spire', root=[-2, 1], size=[10, 20], paint='leaf', habit='bank-needle-forks')
        model = dict(id='colour-pair', x=512, y=508, stems=[stem])
        def drawing():
            paths = ElementTree.fromstring(tree(model)).findall('.//path')
            return [(node.get('d'), node.get('fill'), node.get('stroke')) for node in paths]
        original = drawing()
        stem['paint'] = 'lime'
        changed = drawing()
        self.assertEqual([row[0] for row in original], [row[0] for row in changed])
        self.assertNotEqual(original, changed)
