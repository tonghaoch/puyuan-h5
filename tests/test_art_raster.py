from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys
import unittest

from PIL import Image

ENCODER = Path(__file__).resolve().parents[1]/'scripts/encode-art-asset.py'


class PublishedRaster(unittest.TestCase):
    def test_meadow_keeps_small_tufts_without_mirrored_flowering_shrubs(self):
        root = ENCODER.parents[1]
        with Image.open(root/'public/art/reference-meadow.webp') as grass, \
             Image.open(root/'references/reference-outpaint.webp') as painting:
            sample = painting.crop((61,62,253,254))
            for box in ((144,64,192,108),(0,8,40,50)):
                self.assertEqual(grass.crop(box).tobytes(),sample.crop(box).tobytes())
            for box in ((0,102,62,167),(0,217,62,282)):
                self.assertGreater(grass.crop(box).convert('L').getextrema()[0],145)
            self.assertEqual(grass.crop((0,0,1,384)).tobytes(),grass.crop((383,0,384,384)).tobytes())
            self.assertEqual(grass.crop((0,0,384,1)).tobytes(),grass.crop((0,383,384,384)).tobytes())
            for y in (141,227):
                expected = grass.getpixel((1,y))
                for level in (1,2,4,8):
                    path = root/'public/art/puyuan-original-scope.webp'
                    x, row = level+level//2, y*level+level//2
                    if level != 1:
                        size = 1024 if level == 8 else 512
                        path = root/f'public/art/reference-tiles/{level}/0-{row//size}.webp'
                        row %= size
                    with Image.open(path) as scene, self.subTest(y=y,level=level):
                        actual = scene.getpixel((x,row))
                        self.assertLess(max(abs(a-b) for a,b in zip(actual,expected)),16)

    def test_boundary_roads_survive_meadow_at_every_zoom(self):
        root = ENCODER.parents[1]
        art = root/'public/art'
        with Image.open(root/'references/puyuan-reference.jpg') as source:
            for sx,sy in ((255,544),(500,487),(553,464),(611,398),(591,273),
                          (1154,265),(1155,247),(169,1120),(240,1354)):
                expected = source.getpixel((sx,sy))
                for level in (1,2,4,8):
                    x,y = (sx-30)*level,(sy-180)*level
                    size = 1024 if level == 8 else 512
                    path = art/'puyuan-original-scope.webp'
                    if level != 1:
                        path = art/f'reference-tiles/{level}/{x//size}-{y//size}.webp'
                        x,y = x%size,y%size
                    with Image.open(path) as image, self.subTest(point=(sx,sy),level=level):
                        actual = image.getpixel((x,y))
                        self.assertLess(max(abs(a-b) for a,b in zip(actual,expected)),16)

    def test_reference_enhancement_preserves_scene_alignment_and_source(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('scripts','src/data','references','public/art'):
                (root/folder).mkdir(parents=True)
            script = root/'scripts/prepare-reference-map.py'
            shutil.copyfile(ENCODER.with_name('prepare-reference-map.py'),script)
            layout = {
                'source':'references/source.png',
                'scene':{'width':160,'height':120},
                'sourceOffset':{'x':-20,'y':-10},
                'scope':[[40,30],[160,30],[160,110],[40,110]],
            }
            (root/'src/data/reference-map.json').write_text(json.dumps(layout))
            source = root/layout['source']
            drawing = Image.new('RGB',(200,140),(70,100,130))
            drawing.paste((180,140,100),(80,50,120,90))
            drawing.save(source)
            Image.new('RGB',(160,120),(91,135,75)).save(root/'references/reference-outpaint.webp',lossless=True)
            repair=Image.new('RGBA',(160,120))
            repair.paste((50,85,40,255),(50,40,65,55))
            repair.save(root/'references/reference-label-repairs.webp',lossless=True)
            before = source.read_bytes()
            subprocess.run([sys.executable,str(script)],check=True)
            self.assertEqual(source.read_bytes(),before)
            with Image.open(root/'public/art/reference-tiles/2/0-0.webp') as result:
                self.assertEqual(result.size,(320,240))
                # Source (100,70) maps to scene (80,60), now at twice the density.
                self.assertEqual(result.getpixel((160,120)),(180,140,100))
                self.assertEqual(result.getpixel((80,120)),(70,100,130))
                self.assertEqual(result.getpixel((0,0)),(91,135,75))
                self.assertEqual(result.getpixel((114,94)),(50,85,40))

    def test_blank_landmark_cannot_replace_the_last_good_asset(self):
        with TemporaryDirectory() as directory:
            source,asset,preview = [Path(directory)/name for name in ('render.png','model.webp','preview.webp')]
            drawing = Image.new('RGBA',(8,8)); drawing.putpixel((4,5),(100,70,42,255)); drawing.save(source)
            command = [sys.executable,str(ENCODER),str(source),str(asset),str(preview),'4','4']
            subprocess.run([*command,'--landmark'],check=True)
            before = [file.read_bytes() for file in (asset,preview)]
            Image.new('RGBA',(8,8)).save(source)
            self.assertEqual(subprocess.run([*command,'--landmark'],capture_output=True).returncode,3)
            self.assertEqual(before,[file.read_bytes() for file in (asset,preview)])
            subprocess.run(command,check=True)
            with Image.open(asset) as empty_tile:self.assertIsNone(empty_tile.getchannel('A').getbbox())
