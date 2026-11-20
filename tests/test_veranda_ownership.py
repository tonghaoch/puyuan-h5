import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.street_houses import detail_body


class VerandaOwnershipTest(unittest.TestCase):
    def test_only_the_four_surveyed_fronts_reveal_existing_timber(self):
        survey = json.loads((ROOT / 'src/data/street-houses.json').read_bytes())
        features = json.loads((ROOT / 'src/data/town-architecture.json').read_bytes())['features']
        group, = (group for groups in survey['sites'].values() for group in groups
                  if group['id'] == 'guild-east-veranda')
        timber = {'2': 'wood-505', '3': 'wood-508', '4': 'wood-495', '5': 'wood-498'}
        self.assertEqual(group.get('frontTimberSources'), timber)
        xml = ElementTree.fromstring('<svg>' + detail_body([group], features) + '</svg>')
        houses = xml.findall("./g/*[@data-front]")
        self.assertEqual(len(houses), 6)
        for index, house in enumerate(houses):
            key = f'guild-east-veranda-roof-{index}'
            with self.subTest(house=index):
                self.assertIsNotNone(house.find(f"./*[@id='{key}']"))
                reserves = house.findall(f"./g[@mask='url(#{key}-timber-reserve)']")
                self.assertEqual(len(reserves), int(str(index) in timber))
                if reserves:
                    source = timber[str(index)]
                    self.assertIsNotNone(xml.find(f".//g[@mask='url(#finish-guild-east-veranda-{source})']"))
                    self.assertTrue(len(reserves[0]) > 0)
                    self.assertIsNone(reserves[0].find(f".//*[@id='{key}']"))
