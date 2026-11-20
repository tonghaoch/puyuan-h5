import json
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.native_roofs import facade
from art.surface_finishes import render_surface


def dataset(name):
    return json.loads((ROOT / 'src/data' / (name + '.json')).read_bytes())


class FumaMeasuredFrontTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        observations = dataset('street-observations')['surfaces']
        volumes = dataset('roof-volumes')['roofs']
        cls.owners = {item['id']: dict(item, streetObservation=observations.get(item['id'], {}),
                                      roofVolume=volumes.get(item['id'], {}))
                      for item in dataset('town-architecture')['features']}

    def test_north_storefront_has_no_second_eave_storey(self):
        roof = self.owners['roof-978']
        self.assertEqual(facade(roof), '')
        self.assertIn('id="finish-roof-978"', render_surface(roof))
        for timber in ('wood-638', 'wood-639'):
            self.assertIn(f'id="finish-{timber}"', render_surface(self.owners[timber]))

    def test_four_pool_fronts_are_owned_once_in_their_measured_row(self):
        body = ElementTree.fromstring('<svg>' + render_surface(self.owners['roof-973']) + '</svg>')
        for front, wood in [('pool-north-cross-shop', 'wood-634'), ('pool-middle-west-front', 'wood-630'),
                            ('pool-middle-east-front', 'wood-629'), ('pool-south-recessed-front', 'wood-619')]:
            with self.subTest(front=front):
                self.assertEqual(len(body.findall(f".//g[@id='{front}']")), 1)
                material = render_surface(self.owners[wood])
                self.assertNotIn(f'id="{front}"', material)
                self.assertIn(f'id="finish-{wood}"', material)
