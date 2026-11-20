import random
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.landscape import tree
from art.upright_broadleaf import crown_rim


class UprightBroadleaf(unittest.TestCase):
    def test_silhouette_has_a_wider_belly_and_room_for_an_exposed_stem(self):
        for seed in range(32):
            rim = crown_rim(random.Random(seed))
            shoulder = [across for across, level in rim if level < -31]
            belly = [across for across, level in rim if -21 < level < -13]
            self.assertGreater(max(belly) - min(belly), max(shoulder) - min(shoulder) + 7)
            self.assertLess(max(level for across, level in rim), -7)

    def test_opt_in_changes_only_one_stem_not_its_sibling_or_placement(self):
        for species in ('clipped-oval', 'pear-crown'):
            rear = dict(species=species, root=[-4, -2], size=[11, 18], paint='leaf')
            front = dict(species=species, root=[3, 2], size=[12, 21], paint='lime')
            model = dict(id='sample-pair', x=470, y=924, stems=[rear, front])
            previous = tree(model)
            before = ElementTree.fromstring(previous)
            front['habit'] = 'upright-broadleaf'
            after = ElementTree.fromstring(tree(model))
            self.assertEqual(ElementTree.tostring(before[0]), ElementTree.tostring(after[0]))
            self.assertEqual(before[1].attrib, after[1].attrib)
            self.assertEqual(len(after.findall('.//g[@data-bearing-stem]')), 1)
            rear['habit'] = 'upright-broadleaf'
            pair = ElementTree.fromstring(tree(model))
            for planted in pair:
                self.assertEqual(len(planted.findall('.//g[@data-bearing-stem]')), 1)
                self.assertEqual(len(planted.findall('.//g[@data-broad-crown]')), 1)
            self.assertNotEqual(pair[0].get('transform'), pair[1].get('transform'))
            del rear['habit'], front['habit']
            self.assertEqual(tree(model), previous)

    def test_colour_does_not_change_the_silhouette_or_branch_structure(self):
        stem = dict(species='pear-crown', root=[0, 0], size=[11, 17], paint='leaf', habit='upright-broadleaf')
        model = dict(id='solitary', x=0, y=0, stems=[stem])
        first = tree(model)
        self.assertEqual(tree(model), first)
        stem['paint'] = 'lime'
        second = tree(model)
        self.assertNotEqual(first, second)
        def paths(svg):
            return [element.get('d') for element in ElementTree.fromstring(svg).iter('path')]
        self.assertEqual(paths(first), paths(second))
