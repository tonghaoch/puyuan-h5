from copy import deepcopy
from pathlib import Path
import json,sys,unittest
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from art.east_quarter_materials import earth_court


class EastQuarterMaterials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=json.loads((ROOT/'src/data/street-houses.json').read_text());cls.groups={g['id']:g for groups in data['sites'].values() for g in groups}

    def test_earth_court_keeps_binding_and_inset(self):
        grid=self.groups['south-courts-and-east-bank'];self.assertEqual(grid['courtLayers']['0'],self.groups['main-sanctuary-and-west-gate']['courtBeforeHouse']['4'])
        ring=deepcopy(grid['courts'][0]);svg=earth_court('fixture',ring);self.assertEqual(svg,earth_court('fixture',ring));self.assertNotEqual(svg,earth_court('fixture',grid['courts'][1]));self.assertEqual(ring,grid['courts'][0]);self.assertNotIn('<image',svg)
