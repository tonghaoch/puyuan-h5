import copy
import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.courtyard_details import details, ground
from art.landscape import shape


class LongwanPublicCourt(unittest.TestCase):
    def test_only_the_dining_floor_yields_to_the_public_stone(self):
        sites = json.loads((ROOT / 'src/data/town-completions.json').read_text())['sites']
        landscape = json.loads((ROOT / 'src/data/town-landscape.json').read_text())
        owners = [(name, index, court['yieldFloorToPlaza']) for name, site in sites.items()
                  for index, court in enumerate(site.get('courts', [])) if 'yieldFloorToPlaza' in court]
        self.assertEqual(owners, [('longwan-dining', 0, 'longwan-limestone-yard')])
        name, index, plaza_id = owners[0]
        plaza, = [item for item in landscape['plazas'] if item['id'] == plaza_id]
        site = sites[name]
        private_site = copy.deepcopy(site)
        del private_site['courts'][index]['yieldFloorToPlaza']
        self.assertEqual(details(site), details(private_site))
        floor = ET.fromstring('<svg>' + ground(site) + '</svg>')
        old = ET.fromstring('<svg>' + ground(private_site) + '</svg>')
        parent = floor.find('./g[@mask="url(#courtyard-land)"]')
        mask = parent.find('./defs/mask')
        self.assertEqual(mask.get('maskUnits'), 'userSpaceOnUse')
        self.assertEqual(mask.find('rect').get('fill'), 'white')
        self.assertEqual(mask.find('path').get('d'), shape(plaza))
        self.assertEqual(mask.find('path').get('fill'), 'black')
        self.assertEqual(mask.find('path').get('fill-rule'), 'evenodd')
        private = parent.find('g')
        self.assertEqual(private.get('mask'), f"url(#{mask.get('id')})")
        self.assertEqual([ET.tostring(child) for child in private],
                         [ET.tostring(child) for child in old.find('g')])
        self.assertEqual(ET.tostring(floor.find('defs')), ET.tostring(old.find('defs')))
