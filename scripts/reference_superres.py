"""Offline illustration super-resolution. The browser only loads the encoded tiles."""
from hashlib import sha256

import numpy as np
from PIL import Image
from spandrel import ModelLoader
import torch


def render_detail_tiles(scene, rim, weights, directory):
    if sha256(weights.read_bytes()).hexdigest() != 'b8a8376811077954d82ca3fcf476f1ac3da3e8a68a4f4d71363008000a18b75d':
        raise ValueError('Expected the official Real-ESRGAN v0.2.5.0 realesr-animevideov3.pth')
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    model = ModelLoader().load_from_file(weights).to(device).eval()
    lanczos = Image.Resampling.LANCZOS

    @torch.inference_mode()
    def enhance(image):
        pixels = torch.from_numpy(np.array(image)).permute(2, 0, 1).unsqueeze(0)
        output = model(pixels.to(device, dtype=torch.float32) / 255)
        rgb = output[0].permute(1, 2, 0).clamp(0, 1).mul(255).round().byte().cpu().numpy()
        return Image.fromarray(rgb)

    for level in (4, 8):
        (directory / str(level)).mkdir(parents=True, exist_ok=True)
    w, h = scene.size
    for y in range(0, h, 128):
        for x in range(0, w, 128):
            # Run past the tile boundary so the convolutions see the adjacent roofs.
            box = max(0, x-24), max(0, y-24), min(w, x+128+24), min(h, y+128+24)
            patch = scene.crop(box)
            four = enhance(patch)
            # Mix native-scale contours with a second pass on the finer sampling grid.
            # Both passes start from the registered painting, not a compressed tile.
            fine = enhance(patch.resize((patch.width*2, patch.height*2), lanczos))
            eight = Image.blend(four.resize(fine.size, lanczos), fine, 0.35)
            for level, detail in ((4, four), (8, eight)):
                paper = patch.resize(detail.size, lanczos)
                mask = rim.crop(box).resize(detail.size, Image.Resampling.BILINEAR)
                image = Image.composite(Image.blend(paper, detail, 0.86), paper, mask)
                bounds = (x-box[0], y-box[1], min(w, x+128)-box[0], min(h, y+128)-box[1])
                image.crop(tuple(n*level for n in bounds)).save(
                    directory / str(level) / f'{x//128}-{y//128}.webp', quality=94, method=5)
