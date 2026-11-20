"""Compose the native illustration using the same painter order as ParkMap.vue."""
from pathlib import Path
import json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]

def scene_layers(root):
    reference=json.loads((root/'src/data/reference-map.json').read_text())
    models=json.loads((root/'src/data/landmark-models.json').read_text())['models']
    blocks=json.loads((root/'src/data/architecture-tiles.json').read_text())['tiles']
    landscape=json.loads((root/'src/data/native-landscape.json').read_text())
    dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']
    width,height=reference['scene']['width'],reference['scene']['height']
    layers=[('land',landscape['ground'].replace('.svg','.webp'),(0,0,width,height)),
            ('waterfront',landscape['waterfronts'].replace('.svg','.webp'),(0,0,width,height))]
    for tile in blocks:
        layers.append(('street',tile['asset'],(tile['x'],tile['y'],tile['width'],tile['height'])))
    for model in sorted(models,key=lambda m:m['sourceBounds'][1]+m['sourceBounds'][3]):
        x,y,w,h=model['sourceBounds']
        layers.append(('landmark',model['asset'],(x+dx,y+dy,w,h)))
    for tile in landscape['tiles']:
        layers.append(('plant',tile['asset'],(tile['x'],tile['y'],tile['width'],tile['height'])))
    return (width,height),layers


def compose_scene(scale=3,root=ROOT,omit=()):
    (width,height),layers=scene_layers(root)
    scene=Image.new('RGBA',(width*scale,height*scale),'#e4e6cc')
    for kind,asset,(left,top,wide,tall) in layers:
        if kind in omit:continue
        with Image.open(root/'public'/asset.lstrip('/')) as image:
            painting=image.convert('RGBA').resize((wide*scale,tall*scale),Image.Resampling.LANCZOS)
        scene.alpha_composite(painting,(left*scale,top*scale))
    return scene
