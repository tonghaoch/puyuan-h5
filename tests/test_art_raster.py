from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys
import unittest

from PIL import Image, ImageChops, ImageStat

ENCODER = Path(__file__).resolve().parents[1]/'scripts/encode-art-asset.py'


class PublishedRaster(unittest.TestCase):
    def test_neighbouring_wharf_crowns_retain_comparable_ink_detail(self):
        art = ENCODER.parents[1]/'public/art/reference-tiles'
        # Both crowns share a tile. Measure changes one scene pixel apart,
        # not WebP noise or single display pixels at a particular zoom.
        for level in (4,8):
            with Image.open(art/f'{level}/10-1.webp') as image:
                def ink(box):
                    crop = image.crop(tuple(n*level for n in box)).convert('L')
                    w,h = crop.size
                    delta = ImageChops.difference(crop.crop((0,0,w-level,h)),
                                                  crop.crop((level,0,w,h)))
                    return ImageStat.Stat(delta).rms[0]
                ratio = ink((0,79,18,99)) / ink((25,87,45,107))
                with self.subTest(level=level):
                    self.assertGreater(ratio,0.72)
                    self.assertLess(ratio,1.4)

    def test_food_centre_callout_is_gone_at_every_zoom(self):
        art = ENCODER.parents[1]/'public/art'
        # Two interior-only cutouts of the printed scroll: its white rim in
        # the trees and its tail above the roof. Neither includes paving.
        for level in (1, 2, 4, 8):
            for left,top,right,bottom in ((1281,227,1311,244),(1297,235,1312,249)):
                crop = Image.new('RGB',((right-left)*level,(bottom-top)*level))
                if level == 1:
                    with Image.open(art/'puyuan-original-scope.webp') as image:
                        crop = image.crop((left,top,right,bottom))
                else:
                    step = 256 if level == 2 else 128
                    for y in range(top//step,(bottom-1)//step+1):
                        for x in range(left//step,(right-1)//step+1):
                            with Image.open(art/f'reference-tiles/{level}/{x}-{y}.webp') as tile:
                                crop.paste(tile, ((x*step-left)*level,(y*step-top)*level))
                with self.subTest(level=level,window=(left,top)):
                    r,g,b = crop.split()
                    darkest = ImageChops.darker(r,ImageChops.darker(g,b))
                    self.assertLess(sum(darkest.histogram()[236:]),4*level**2)

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
