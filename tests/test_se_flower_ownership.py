import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.surface_finishes import sampled_shape


class SoutheastFlowerOwnership(unittest.TestCase):
    def test_only_the_south_garden_tree_yields_to_the_registered_eave(self):
        landscape = json.loads((ROOT / 'src/data/native-landscape.json').read_text())
        data = json.loads((ROOT / 'src/data/town-architecture.json').read_text())
        roof, = [item for item in data['features'] if item['id'] == 'roof-707']
        self.assertEqual(roof['kind'], 'roof')
        owned = {}
        for tile in landscape['tiles']:
            painting = ET.parse(ROOT / ('public' + tile['sourceAsset']))
            for tree in painting.findall('.//*[@data-rooted-flower]'):
                ident = tree.get('data-rooted-flower')
                masks = tree.findall('.//{*}mask')
                owned.setdefault(ident, set()).add(len(masks))
                for mask in masks:
                    self.assertEqual(ident, 'flowering-987-1194')
                    self.assertEqual(mask.get('maskUnits'), 'userSpaceOnUse')
                    self.assertEqual(mask.find('{*}rect').get('fill'), 'white')
                    expected = ET.fromstring(sampled_shape(roof, 'black'))
                    self.assertEqual(mask.find('{*}path').attrib, expected.attrib)
                    content = tree.find('{*}g')
                    self.assertEqual(content.get('mask'), f"url(#{mask.get('id')})")
                    self.assertTrue(content.findall('.//*[@data-flower-scaffold]'))
        self.assertEqual(owned, {'flowering-1030-916': {0}, 'flowering-1230-1004': {0},
                                 'flowering-987-1194': {1}, 'flowering-1302-1187': {0}})
