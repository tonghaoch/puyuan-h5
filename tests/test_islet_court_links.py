import json,sys,unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from art.islet_court_links import court_link


class BridgeCourtLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=json.loads((ROOT/'src/data/street-houses.json').read_text())
        cls.owners=[group for groups in [*data['sites'].values(),*data['background'].values()] for group in groups if 'isletCourtLinks' in group]
        cls.owner,=cls.owners;cls.model=cls.owner['houses'][2];cls.spec=cls.owner['isletCourtLinks']['2']

    def test_only_the_bridge_court_link_is_selected(self):
        self.assertEqual(self.owner['id'],'islet-bridge-court');self.assertEqual(set(self.owner['isletCourtLinks']),{'2'});self.assertEqual(self.spec['build'],'quay-timber-link')

    def test_body_and_capping_follow_all_joint_stations(self):
        body,cap=map(ET.fromstring,court_link(self.model,self.spec,'unit'))
        self.assertEqual(body.get('data-islet-link-body'),'unit');self.assertEqual(cap.get('data-islet-link-cap'),'unit');self.assertEqual(len(body),8*(len(self.spec['joints'])-1));self.assertGreater(len(cap),2*(len(self.spec['joints'])-1))
        simpler=dict(self.spec,joints=[0,.55,1]);self.assertNotEqual(court_link(self.model,self.spec,'unit'),court_link(self.model,simpler,'unit'))

    def test_caps_must_fit_the_range_and_joints_must_be_ordered(self):
        for spec in (dict(self.spec,joints=[0,.7,.5,1]),dict(self.spec,capDepth=1.1)):
            with self.assertRaises(ValueError):court_link(self.model,spec,'unit')
