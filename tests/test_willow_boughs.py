import copy
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from art.plantings import planting


class BearingBoughTest(unittest.TestCase):
    model = {'id':'garden', 'x':200, 'y':140, 'stems':[
        {'species':'willow','root':[-2,-3],'size':[19,22],'paint':'lime','habit':'pendant-curtains'},
        {'species':'pear-crown','root':[7,1],'size':[10,18],'paint':'leaf'}]}
    frame = {'fork':[-1,-10],'arms':[[-6,-31,7,14],[7,-28,8,16],[0,-36,8,14]]}

    def test_selected_stem_keeps_its_foot_and_neighbors(self):
        model = copy.deepcopy(self.model)
        old = ElementTree.fromstring(planting(model))
        model['stems'][0]['bearingCrown'] = copy.deepcopy(self.frame)
        new = ElementTree.fromstring(planting(model))
        self.assertEqual(old[0].attrib, new[0].attrib)
        self.assertEqual(ElementTree.tostring(old[1]), ElementTree.tostring(new[1]))
        self.assertEqual([g.get('data-bough-depth') for g in new.findall('.//g[@data-bough-depth]')], ['0','1','2'])

    def test_reaching_side_arm_does_not_move_other_boughs_or_bole(self):
        model = copy.deepcopy(self.model)
        frame = copy.deepcopy(self.frame)
        model['stems'][0]['bearingCrown'] = frame
        def pieces():
            frame_node = ElementTree.fromstring(planting(model)).find('.//g[@data-willow-frame]')
            return [ElementTree.tostring(item) for item in frame_node]
        before = pieces()
        frame['arms'][1][0] += 3
        after = pieces()
        self.assertEqual([index for index in range(len(before)) if before[index] != after[index]], [3])
