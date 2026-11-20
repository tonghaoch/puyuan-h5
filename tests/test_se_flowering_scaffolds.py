import json,sys,unittest
from pathlib import Path
from xml.etree import ElementTree as XML

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from art.se_flowering_scaffolds import load_family,rooted_flower

class PaperFlowerFamily(unittest.TestCase):
    def setUp(self):
        self.family,self.roofs=load_family(ROOT);self.trees={t['id']:t for t in json.loads((ROOT/'src/data/town-landscape.json').read_bytes())['trees']}

    def test_exact_stock_and_foot(self):
        for key,design in self.family.items():
            with self.assertRaises(ValueError):rooted_flower(dict(self.trees[key],x=self.trees[key]['x']+1),design,self.roofs)
        self.assertNotIn('story-lane-blossom',self.family)

    def test_every_registered_scaffold_carries_separate_flowers_and_wood(self):
        for key,design in self.family.items():
            tree=XML.fromstring(rooted_flower(self.trees[key],design,self.roofs));self.assertEqual(tree.get('data-rooted-flower'),key);limbs=tree.findall('.//*[@data-flower-scaffold]');self.assertEqual(len(limbs),len(design['limbs']))
            for limb in limbs:
                for part in ('wood','bloom'):self.assertTrue(any(len(node) for node in limb.findall('.//*[@data-flower-part="'+part+'"]')))
            self.assertEqual(tree.find('.//mask') is not None,'frontRoof' in design)
