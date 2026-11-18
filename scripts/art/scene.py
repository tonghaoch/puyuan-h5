"""Compose the native illustration using the same painter order as ParkMap.vue."""
from pathlib import Path
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]

def compose_scene(scale=3,root=ROOT):
    reference=json.loads((root/'src/data/reference-map.json').read_text())
    models=json.loads((root/'src/data/landmark-models.json').read_text())['models']
    blocks=json.loads((root/'src/data/architecture-tiles.json').read_text())['tiles']
    landscape=json.loads((root/'src/data/native-landscape.json').read_text())
    dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']
    size=(reference['scene']['width']*scale,reference['scene']['height']*scale)
    scene=Image.new('RGBA',size,'#e4e6cc')
    ground=Image.open(root/'public/art/native/ground.webp').convert('RGBA')
    scene.alpha_composite(ground.resize(size,Image.Resampling.LANCZOS))
    waterfront=Image.open(root/'public'/landscape['waterfronts'].lstrip('/').replace('.svg','.webp')).convert('RGBA')
    scene.alpha_composite(waterfront.resize(size,Image.Resampling.LANCZOS))
    for tile in blocks:
        asset=Image.open(root/'public'/tile['asset'].lstrip('/')).convert('RGBA')
        scene.alpha_composite(asset.resize((tile['width']*scale,tile['height']*scale),Image.Resampling.LANCZOS),(tile['x']*scale,tile['y']*scale))
    for model in sorted(models,key=lambda m:m['sourceBounds'][1]+m['sourceBounds'][3]):
        x,y,w,h=model['sourceBounds']
        asset=Image.open(root/'public'/model['asset'].lstrip('/')).convert('RGBA')
        scene.alpha_composite(asset.resize((w*scale,h*scale),Image.Resampling.LANCZOS),((x+dx)*scale,(y+dy)*scale))
    for tile in landscape['tiles']:
        asset=Image.open(root/'public'/tile['asset'].lstrip('/')).convert('RGBA')
        scene.alpha_composite(asset.resize((tile['width']*scale,tile['height']*scale),Image.Resampling.LANCZOS),(tile['x']*scale,tile['y']*scale))
    return scene
