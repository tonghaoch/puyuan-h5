import json
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.street_houses import detail_body, replace_traces
from art.surface_finishes import sampled_shape


class StandaloneElevation(unittest.TestCase):
    def setUp(self):
        background=json.loads((ROOT/'src/data/street-houses.json').read_bytes())['background']
        self.group=next(group for group in background['east-west-bank'] if group['id']=='east-bend-standalone-returns')
        self.features=json.loads((ROOT/'src/data/town-architecture.json').read_bytes())['features']

    def test_elevation_extent_selects_a_tile_without_cutting_the_old_scene(self):
        box=(1054,692,1310,948);original='<g id="unchanged-street"/>'
        self.assertEqual(replace_traces(original,box,[self.group]),original)
        normal={'id':'normal','houses':[],'replace':[[[1157,935],[1160,935],[1160,938]]],'retainObservedSurfaces':False}
        self.assertEqual(replace_traces(original,box,[self.group,normal]),replace_traces(original,box,[normal]))
        self.assertEqual(detail_body([normal,self.group],self.features),detail_body([normal],self.features)+detail_body([self.group],self.features))

    def test_all_registered_slopes_use_the_original_footprints_as_occluders(self):
        drawing=ElementTree.fromstring(detail_body([self.group],self.features));mask=drawing.find('defs/mask');self.assertIsNotNone(mask)
        self.assertEqual(drawing.find('g').get('mask'),f'url(#{mask.get("id")})')
        atlas={feature['id']:feature for feature in self.features}
        self.assertEqual([node.attrib for node in mask.findall('path')],[ElementTree.fromstring(sampled_shape(atlas[key],'black')).attrib for key in self.group['standaloneElevation']['behind']])
        self.assertEqual(len(drawing.findall('.//g[@data-front]')),0)

    def test_lowering_one_wall_foot_does_not_move_its_roof_or_its_neighbours(self):
        def draw(group):return ElementTree.fromstring(detail_body([group],self.features))
        original=draw(self.group);changed=deepcopy(self.group);face=changed['standaloneElevation']['faces'][0]
        face['foot'][0][1]+=1;edited=draw(changed)
        self.assertEqual(ElementTree.tostring(original.find('defs')),ElementTree.tostring(edited.find('defs')))
        self.assertEqual([before.get('data-elevation-face') for before,after in zip(original.find('g'),edited.find('g')) if ElementTree.tostring(before)!=ElementTree.tostring(after)],[face['id']])


if __name__=='__main__':unittest.main()
