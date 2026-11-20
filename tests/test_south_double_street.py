import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art.landscape import ground_bed, path, rounded_ring, shape


class SouthDoubleStreet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'src/data/town-landscape.json').read_text())
        cls.svg = (ROOT / 'public/art/native/ground.svg').read_text()
        cls.nodes = ET.fromstring(cls.svg.replace(' xmlns="http://www.w3.org/2000/svg"', ''))
        cls.bed, = [bed for bed in cls.data['groundBeds'] if bed['id'] == 'southwest-avenue-verge']

    def test_existing_lane_paving_and_planted_surface_reach_the_ground_in_order(self):
        paving, = [region for region in self.data['paving'] if region.get('material') == 'lane-setts' and len(region.get('holes', [])) == 117]
        source = path(shape(paving), 'url(#lane-setts)', '#dfe0c8', .55, 'fill-rule="evenodd"')
        self.assertEqual(self.svg.count(source), 1)
        laying = ground_bed(self.bed)
        self.assertEqual(self.svg.count(laying), 1)
        opening, = [node for node in self.nodes.iter('g') if node.get('clip-path') == 'url(#sw34-public-ground-parallel)']
        planted = ET.fromstring('<g>'+laying+'</g>')
        self.assertEqual([ET.tostring(child) for child in opening], [ET.tostring(child) for child in planted])
        self.assertLess(self.svg.index(source), self.svg.index(laying))
        self.assertLess(self.svg.index(laying), self.svg.index('<g id="sw34-parallel-slope">'))
        self.assertLess(self.svg.index('<g id="sw34-parallel-slope">'), self.svg.index('<g id="sw34-parallel-apron">'))

    def test_pavement_opens_the_turf_only_between_its_registered_shoulders(self):
        street = json.loads((ROOT / 'src/data/sw34-floor-parallel.json').read_text())
        self.assertEqual(street['bed'], self.bed['id'])
        stations = street['apron']
        self.assertEqual((stations[0], stations[-1]), ([368.4,1240.8,1247.1,1248.4], [557.9,1207.1,1216.7,1218.7]))
        self.assertTrue(all(left[0] < right[0] for left,right in zip(stations,stations[1:])))
        self.assertTrue(all(near < edge < far for _,near,edge,far in stations))
        strip = rounded_ring([(across, near) for across,near,_,_ in stations]+[(across, far) for across,_,_,far in reversed(stations)])
        cut, = self.nodes.findall('.//clipPath[@id="sw34-public-ground-parallel"]/path')
        self.assertEqual(cut.attrib, {'d':'M0 0H2363V1672H0Z'+strip, 'clip-rule':'evenodd'})
        border, = self.nodes.findall('.//clipPath[@id="sw34-planted-ground-parallel"]/path')
        self.assertEqual(border.get('d'), shape(self.bed))
        self.assertEqual(len(self.nodes.findall('.//g[@clip-path="url(#sw34-planted-ground-parallel)"]/g[@id="sw34-parallel-slope"]')), 1)
        apron, = self.nodes.findall('.//g[@id="sw34-parallel-apron"]')
        self.assertEqual(apron[0].get('d'),strip)


if __name__ == '__main__':
    unittest.main()
