import copy
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from art.street_houses import detail_body
from art.courtyard_occlusion import court_bindings


class CourtyardDepth(unittest.TestCase):
    def setUp(self):
        self.front={'id':'gate','replace':[],'retainObservedSurfaces':False,'houses':[[2,7,10,7,0,-3,2,4,'gable']]}
        self.back={'id':'yard','replace':[],'retainObservedSurfaces':False,'houses':[], 'courtFinish':'silver-setts','courts':[[[1,9],[10,9],[12,17],[2,18]]]}

    def test_move_one_paint_not_another_copy_of_the_house(self):
        parse=lambda:ET.fromstring('<svg>'+detail_body([self.front,self.back],[])+'</svg>')
        before=parse(); surface=ET.tostring(before[1].find('path')); house=ET.tostring(before[0].find('g[@data-front]'))
        self.front['courtBeforeHouse']={'0':'test-apron'}; self.back['courtLayers']={'0':'test-apron'}; after=parse()
        self.assertEqual(after[0][0].get('href'),'#court-layer-test-apron')
        self.assertEqual(house,ET.tostring(after[0][1])); self.assertEqual(len(after.findall('.//g[@data-front]')),1)
        self.assertEqual(surface,ET.tostring(after[1].find('defs/g[@id="court-layer-test-apron"]/path')))
        self.assertIsNone(after[1].find('path')); self.assertEqual(len(after.findall('.//use[@href="#court-layer-test-apron"]')),1)

    def test_unmatched_duplicate_or_clipped_bindings_are_rejected(self):
        self.front['courtBeforeHouse']={'0':'test-apron'}
        with self.assertRaises(ValueError):court_bindings([self.front,self.back])
        self.back['courtLayers']={'0':'test-apron'}
        for groups in ([self.back,self.front],[self.front,self.back,copy.deepcopy(self.back)],[self.front,dict(self.back,visibleOnly=True)]):
            with self.assertRaises(ValueError):court_bindings(groups)
