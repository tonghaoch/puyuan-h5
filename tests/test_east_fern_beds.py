import json,sys,unittest
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from art.landscape import tree


class EastFernBeds(unittest.TestCase):
    def test_only_the_selected_fern_changes_and_keeps_its_transform(self):
        rows=json.loads((ROOT/'src/data/town-landscape.json').read_bytes())['trees'];original=deepcopy(next(row for row in rows if row['id']=='tree-58'))
        original['stems'][4].pop('fernFan',None);model=deepcopy(original);model['stems'][4]['fernFan']={'shoulders':[-15,14],'backLift':29,'frontReach':10}
        marker='<g data-species="';before=tree(original)[:-4].split(marker);after=tree(model)[:-4].split(marker)
        self.assertEqual(len(before),len(after));self.assertEqual(sum(a!=b for a,b in zip(before,after)),1)
        edited=next((a,b) for a,b in zip(before,after) if a!=b);self.assertEqual(edited[0].partition('>')[0],edited[1].partition('>')[0]);self.assertEqual(edited[1].count('data-fern-axis'),4)
        model['stems'][4]['fernFan']['backLift']+=2;self.assertNotEqual(tree(model)[:-4].split(marker),after)
        self.assertIsNotNone(ET.fromstring(tree(model)))
