import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.canal_groves import roof_shapes
from art.landscape import tree
from art.surface_finishes import sampled_shape


class CanalGroves(unittest.TestCase):
    def setUp(self):
        self.trees={t['id']:t for t in json.loads((ROOT/'src/data/town-landscape.json').read_bytes())['trees']}

    def test_open_bed_keeps_unselected_stems_byte_identical_at_the_same_depth(self):
        original=deepcopy(self.trees['tree-58']);original.pop('canalGrove',None);model=deepcopy(original)
        model['canalGrove']={'form':'open-bed','stems':[0,1],'leader':[-1.85,-37.4],'shoulder':[16.4,24]}
        marker='<g data-species="';before=tree(original)[:-4].split(marker);after=tree(model)[:-4].split(marker)
        order=sorted(range(len(model['stems'])),key=lambda index:model['stems'][index]['root'][1]);self.assertEqual(len(before),len(after));self.assertEqual(before[0],after[0])
        for index,first,second in zip(order,before[1:],after[1:]):
            if index not in (0,1):self.assertEqual(first,second)
            else:self.assertEqual(first.partition('>')[0],second.partition('>')[0]);self.assertIn('data-open-bed-crown',second)
        self.assertEqual(len(ET.fromstring(tree(model))),len(order))

    def test_legacy_mask_reuses_registered_surface_and_keeps_crown_parts_editable(self):
        model=deepcopy(self.trees['tree-146']);model['canalGrove']={'form':'eave-thicket','behind':'roof-829','shoulders':[[-.26,.55,.81],[.25,.52,.86]],'front':[-.035,.66,.57]}
        drawing=tree(model);self.assertIn(sampled_shape(roof_shapes()['roof-829'],'black'),drawing);self.assertEqual(drawing.count('data-outer-shoulder'),2)
        model['canalGrove']['front'][0]+=.09;changed=tree(model)
        self.assertEqual(drawing.split('data-front-crown')[0],changed.split('data-front-crown')[0]);self.assertNotEqual(drawing,changed)
        self.assertNotIn('<image',drawing);ET.fromstring('<svg>'+drawing+'</svg>')

    def test_no_other_species_can_be_replaced_by_a_bed(self):
        model=deepcopy(self.trees['tree-36']);model['canalGrove']={'form':'open-bed','stems':[3],'leader':[0,-37],'shoulder':[16,24]}
        with self.assertRaises(ValueError):tree(model)

    def test_removing_the_open_habit_returns_only_that_stem_to_its_original_renderer(self):
        model=deepcopy(self.trees['tree-36']);model['canalGrove']={'form':'open-bed','stems':[0,1],'leader':[0,-37],'shoulder':[16,24]}
        model['stems'][0].pop('habit');untouched=deepcopy(model);untouched.pop('canalGrove')
        expected=ET.fromstring(tree(untouched));actual=ET.fromstring(tree(model));self.assertEqual(ET.tostring(actual[0]),ET.tostring(expected[0]))
        self.assertEqual(len(actual.findall('.//g[@data-open-bed-crown]')),1)
