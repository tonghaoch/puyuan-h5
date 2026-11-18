"""Overview LOD and complete place-card scenes from all reconstructed architecture layers."""
from pathlib import Path
import json
from PIL import Image
from art.scene import compose_scene
ROOT=Path(__file__).resolve().parents[1]
models=json.loads((ROOT/'src/data/landmark-models.json').read_text())['models']
tiles=json.loads((ROOT/'src/data/architecture-tiles.json').read_text())['tiles']
reference=json.loads((ROOT/'src/data/reference-map.json').read_text())
dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']
scale=3
size=(reference['scene']['width']*scale,reference['scene']['height']*scale)
scene=compose_scene(scale)
for model in sorted(models,key=lambda m:m['sourceBounds'][1]+m['sourceBounds'][3]):
    x,y,w,h=model['sourceBounds']
    asset=Image.open(ROOT/'public'/model['asset'].lstrip('/')).convert('RGBA')
    asset.resize((w*2,h*2),Image.Resampling.LANCZOS).save(ROOT/'public'/model['overviewAsset'].lstrip('/'),quality=88,method=6)
for model in models:
    x,y,w,h=model['sourceBounds']
    crop=scene.crop(((x+dx)*scale,(y+dy)*scale,(x+dx+w)*scale,(y+dy+h)*scale))
    crop.convert('RGB').save(ROOT/'public'/model['heroAsset'].lstrip('/'),quality=92,method=6)
artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
review=scene.convert('RGB');review.thumbnail((2280,1860));review.save(artifacts/'full-town-finished.jpg',quality=94)
print(f'Finalized {len(models)} overview assets and complete place-card scenes.')
