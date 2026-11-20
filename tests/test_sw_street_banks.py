import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.landscape import path, shape
from art.sw_street_banks import ACTIVE, BANKS, bank_returns, dry_shoulders


class SouthwestStreetBanksTest(unittest.TestCase):
    def test_only_three_named_dry_receivers_are_enabled(self):
        self.assertEqual(ACTIVE, ('longwan','island','elbow'))
        self.assertEqual(set(ACTIVE),set(BANKS))
        for suffix,fragment in (('dry-shoulder',dry_shoulders()),('bank-return',bank_returns())):
            groups=ElementTree.fromstring('<svg>'+fragment+'</svg>')
            self.assertEqual([group.get('id') for group in groups],[f'sw-{name}-{suffix}' for name in ACTIVE])
            for group in groups:
                self.assertTrue(all(face.get('d','').endswith('Z') and face.get('stroke')=='none' for face in group))

    def test_exposed_return_is_a_face_between_distinct_lips(self):
        for name in ACTIVE:
            for rim,toe,color in BANKS[name]['returns']:
                self.assertEqual(len(rim),len(toe));self.assertGreaterEqual(len(rim),3)
                self.assertTrue(all(foot[1]>edge[1] for edge,foot in zip(rim,toe)))
                self.assertTrue(color.startswith('#'))

    def test_routes_and_existing_water_are_in_front_of_dry_work(self):
        town=json.loads((ROOT/'src/data/town-landscape.json').read_bytes())
        ground=(ROOT/'public/art/native/ground.svg').read_text()
        first_walk=f'<g id="{town["walks"][0]["id"]}">'
        first_water=path(shape(town['water'][0]),'url(#water)','url(#quay)',2.8,'fill-rule="evenodd" paint-order="stroke fill"')
        self.assertLess(ground.index(dry_shoulders()),ground.index(first_walk))
        self.assertLess(ground.index(first_walk),ground.index(bank_returns()))
        self.assertLess(ground.index(bank_returns()),ground.index(first_water))
        self.assertLess(ground.index(first_water),ground.index('<g id="visible-canal-banks">'))
