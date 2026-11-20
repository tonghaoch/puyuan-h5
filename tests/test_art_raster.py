from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

from PIL import Image

ENCODER = Path(__file__).resolve().parents[1]/'scripts/encode-art-asset.py'


class PublishedRaster(unittest.TestCase):
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
