import json
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from art import surface_finishes
from art.landscape import poly
from art.native_roofs import planes
from art.nw_court_roofs import COURTS, court_roof
from art.nw_pool_fronts import FRAMES


POOL_FACES = (
    ('pool-north-cross-shop', 'wood-634', ((720,547.8),(751.4,546.6),(751.3,552.2),(720.1,553.35)), 'd6948fdb0b8802e210518ba9bb347f6a879768fd917bd2a6303374d9a284d87d'),
    ('pool-middle-west-front', 'wood-630', ((719.8,559.4),(735.3,559.2),(735.3,564.55),(719.9,565)), 'd58aac033396b8d71caa967d23c81b450dba53ed18556b800ee8ee55bec61067'),
    ('pool-middle-east-front', 'wood-629', ((739.1,559.3),(747.5,559.05),(747.5,564.7),(739.1,564.85)), '6a598cc6d00dc788d9ccf20cadee49130d4086684e96de58283db6438a2d3670'),
    ('pool-south-recessed-front', 'wood-619', ((725,582.7),(751,582.4),(751.1,588.3),(725.1,589.05)), 'ad7c2282f553c141465f34abf1ab62fb09d1ea5b0ff220ae85492aa9014c572b'),
)
RAW_SHA = {
    'roof-973':'382e06df5d65dc14c3112d2dde006f9140e09832a83d595a06edcfb5b52cf3f3',
    'wood-634':'4babf70165f9b2191b2b03ba2472b3d32d104abc841767cefb2ef21dc0284114',
    'wood-630':'894203ce192ffe09868f4d5c84db195fcf77b1b7fb2c60c040349b918e12a5b1',
    'wood-629':'2c7fc13d1b6bab63c7479dd478e09a2c87f0f5e97f99b3dac481d72c088b5de1',
    'wood-619':'8acc85075d2a2ba6596f3ba9ad05a87ffb1ef34aeb9e39b417e9e66e4b96e90a',
}


def cut_footprint(footprint, rings):
    return footprint.removesuffix('</mask>') + ''.join(poly(ring,'black') for ring in rings) + '</mask>'


class NorthwestCourtRoofs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def data(name):
            return json.loads((ROOT / 'src' / 'data' / (name + '.json')).read_bytes())
        observations = data('street-observations')['surfaces']
        volumes = data('roof-volumes')['roofs']
        cls.features = {feature['id']: dict(feature,
                            streetObservation=observations.get(feature['id'], {}),
                            roofVolume=volumes.get(feature['id'], {}))
                        for feature in data('town-architecture')['features']}
        cls.owners = {
            'roof-973': ('landmarks/fuma-residence', 'nw12-fuma-cross-halls', 6, 2,
                         ('wood-619', 'wood-620', 'wood-629', 'wood-630', 'wood-634')),
            'roof-866': ('architecture/block-2-2', 'nw12-fork-island-ranges', 3, 0,
                         ('wood-537', 'wood-538', 'wood-539')),
        }

    def test_only_the_two_registered_mothers_bypass_ordinary_planes(self):
        self.assertEqual(set(COURTS), set(self.owners))
        with patch.object(surface_finishes, 'planes', wraps=planes) as ordinary, \
             patch.object(surface_finishes, 'court_roof', wraps=court_roof) as registered:
            for feature in self.features.values():
                surface_finishes.render_surface(feature)
        self.assertCountEqual([call.args[0]['id'] for call in registered.call_args_list], self.owners)
        self.assertCountEqual([call.args[0]['id'] for call in ordinary.call_args_list],
                              self.features.keys() - self.owners.keys())

    def test_replacing_wings_is_the_only_change_inside_the_original_material_mask(self):
        for key, (_, _, _, hole_count, _) in self.owners.items():
            with self.subTest(key=key):
                feature = self.features[key]
                actual = surface_finishes.render_surface(feature)
                with patch.dict(COURTS, clear=True):
                    standard = surface_finishes.render_surface(feature)
                wings = court_roof(feature)
                self.assertEqual(actual.count(wings), 1)
                self.assertEqual(actual.replace(wings, planes(feature)), standard)
                footprint, _ = surface_finishes.sample_footprint(feature)
                rings = [ring for _,_,ring,_ in POOL_FACES] if key == 'roof-973' else []
                self.assertEqual(actual.count(cut_footprint(footprint,rings)), 1)
                self.assertEqual(len(feature['holes']), hole_count)
                svg = ET.fromstring('<svg>' + actual + '</svg>')
                mask_group = svg.find(f'g[@mask="url(#finish-{key})"]')
                self.assertIsNotNone(mask_group.find(f'g[@id="{COURTS[key][0]}"]'))

    def test_only_the_four_named_faces_transfer_between_the_registered_parents(self):
        self.assertEqual([(name,parents,(*head,*reversed(foot))) for name,parents,head,foot,*_ in FRAMES],
                         [(name,('roof-973',wood),ring) for name,wood,ring,_ in POOL_FACES])
        for key, digest in RAW_SHA.items():
            with self.subTest(key=key):
                self.assert_transferred_material(key, digest)

    def assert_transferred_material(self, key, digest):
        feature = self.features[key]
        body = surface_finishes.render_surface(feature)
        expected = surface_finishes.render_surface(dict(feature,nwRawFront=True))
        self.assertEqual(hashlib.sha256(expected.encode()).hexdigest(), digest)
        faces = [row for row in POOL_FACES if key in ('roof-973',row[1])]
        rings = [row[2] for row in faces]
        footprint, _ = surface_finishes.sample_footprint(feature)
        live = cut_footprint(footprint, rings)
        self.assertEqual(body.count(live), 1)
        document = ET.fromstring('<svg>'+body+'</svg>')
        self.assertEqual(len(document.findall(f'.//*[@id="finish-{key}"]')), 1)
        masked = document.findall(f'g[@mask="url(#finish-{key})"]')
        self.assertEqual(len(masked), 1)
        if key == 'roof-973':
            self.assertIsNotNone(masked[0].find('g[@id="nw12-fuma-cross-halls"]'))
        frames = [node for node in document if node.get('id','').startswith('pool-')]
        self.assertEqual([(node.get('id'),hashlib.sha256(ET.tostring(node)).hexdigest()) for node in frames],
                         [(name,stamp) for name,_,_,stamp in faces] if key == 'roof-973' else [])
        if frames:
            body, marker, tail = body.partition('<g id="pool-north-cross-shop">')
            self.assertTrue(marker)
            self.assertEqual(len(ET.fromstring('<svg>'+marker+tail+'</svg>')),len(frames))
        restored = body.replace(live,footprint)
        outside = 'M0,0H2363V1672H0Z' + ''.join('M'+'L'.join(f'{x},{y}' for x,y in ring)+'Z' for ring in rings)
        clip = f'<defs><clipPath id="single-face-{key}"><path d="{outside}" clip-rule="evenodd"/></clipPath></defs>'
        self.assertTrue(restored.startswith(clip))
        restored = restored[len(clip):]
        timber = feature['streetObservation'].get('timber', [])
        self.assertEqual(len(timber), 4 if key == 'roof-973' else 0)
        for panel in timber:
            leaf = surface_finishes.sampled_shape(panel,f'url(#surface-timber-{key})')
            wrapper = f'<g clip-path="url(#single-face-{key})">{leaf}</g>'
            self.assertEqual(restored.count(wrapper), 1)
            restored = restored.replace(wrapper,leaf)
        self.assertEqual(restored, expected)

    def test_recorded_wings_and_original_plaster_and_timber_reach_the_generated_asset(self):
        for key, (asset, author, wing_count, _, wood_ids) in self.owners.items():
            with self.subTest(key=key):
                svg = (ROOT / 'public' / 'art' / (asset + '.svg')).read_text()
                feature = self.features[key]
                body = surface_finishes.render_surface(feature)
                self.assertEqual(svg.count(body), 1)
                assembly = ET.fromstring(court_roof(feature))
                self.assertEqual(assembly.get('id'), author)
                self.assertEqual(len(assembly), wing_count)
                self.assertEqual([wing.get('id') for wing in assembly],
                                 [author + '-' + unit[0] for unit in COURTS[key][1]])
                for wing in assembly:
                    self.assertEqual(svg.count(f'id="{wing.get("id")}"'), 1)
                    self.assertEqual(len(wing.findall('.//pattern')), 4)
                for panel in feature['streetObservation']['plaster']:
                    plaster = surface_finishes.sampled_shape(panel, '#eeebe2')
                    self.assertLess(svg.index(plaster), svg.index(body))
                for wood_id in wood_ids:
                    timber = surface_finishes.render_surface(self.features[wood_id])
                    self.assertIn(timber, svg)


if __name__ == '__main__':
    unittest.main()
