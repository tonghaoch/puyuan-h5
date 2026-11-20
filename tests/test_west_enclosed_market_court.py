import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from art.street_houses import detail_body


class WestEnclosedMarketCourt(unittest.TestCase):
    def setUp(self):
        self.key='sw-west-enclosed-market-court'
        self.streets=json.loads((ROOT/'src/data/street-houses.json').read_bytes())
        self.group,=self.streets['background'][self.key]
        features=json.loads((ROOT/'src/data/town-architecture.json').read_bytes())['features']
        self.body=detail_body([self.group],features)
        self.tile=Path('public/art/architecture/block-1-3.svg')

    def test_only_named_group_paints_before_both_roofs_and_retained_timber(self):
        enabled=[group['id'] for section in ('sites','background') for groups in self.streets[section].values() for group in groups if group.get('swCourtUnderlay')]
        self.assertEqual(enabled,[self.key])
        drawing=(ROOT/self.tile).read_text()
        self.assertEqual(drawing.count(self.body),1)
        end=drawing.index(self.body)+len(self.body)
        for surface in ('roof-824','roof-815','wood-494','wood-496','wood-499'):
            self.assertLess(end,drawing.index(f'id="finish-{surface}"'),surface)

    def test_drawn_planes_leave_the_open_inner_yard_unpainted(self):
        faces=ElementTree.fromstring(self.body).findall('g/g[@data-elevation-face]')
        self.assertEqual(len(faces),8)
        mask=Image.new('1',(440,420));pen=ImageDraw.Draw(mask)
        for face in faces:
            paths=face.findall('path');self.assertTrue(paths)
            for path in paths:
                outline=path.get('d')
                self.assertTrue(outline.startswith('M') and outline.endswith('Z'))
                vertices=[tuple(map(float,pair.split(','))) for pair in outline[1:-1].split('L')]
                pen.polygon([((east-425)*4,(south-940)*4) for east,south in vertices],fill=1)
        self.assertIsNotNone(mask.getbbox())
        self.assertIsNone(mask.crop(((457-425)*4,(980-940)*4,(485-425)*4,(1006-940)*4)).getbbox())

    def test_without_this_group_every_other_generated_street_is_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            other=Path(directory)
            shutil.copytree(ROOT/'scripts',other/'scripts')
            shutil.copytree(ROOT/'src/data',other/'src/data')
            del self.streets['background'][self.key]
            (other/'src/data/street-houses.json').write_text(json.dumps(self.streets,ensure_ascii=False))
            subprocess.run([sys.executable,'scripts/generate-landmarks.py'],cwd=other,check=True,stdout=subprocess.DEVNULL)
            for folder in ('public/art/architecture','public/art/landmarks'):
                released={file.relative_to(ROOT) for file in (ROOT/folder).glob('*.svg')}
                generated={file.relative_to(other) for file in (other/folder).glob('*.svg')}
                self.assertEqual(released,generated)
                for rel in released:
                    expected=(ROOT/rel).read_text()
                    self.assertEqual((other/rel).read_text(),expected.replace(self.body,'') if rel==self.tile else expected,str(rel))
