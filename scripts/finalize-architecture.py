"""Overview LOD and complete place-card scenes from all reconstructed architecture layers."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
models=json.loads((ROOT/'src/data/landmark-models.json').read_text())['models']
tiles=json.loads((ROOT/'src/data/architecture-tiles.json').read_text())['tiles']
reference=json.loads((ROOT/'src/data/reference-map.json').read_text())
dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y']
scale=3
size=(reference['scene']['width']*scale,reference['scene']['height']*scale)
scene=Image.new('RGBA',size,'#e4e6cc')
ground=Image.open(ROOT/'public/art/puyuan-layered-ground.webp').convert('RGBA')
scene.alpha_composite(ground.resize(size,Image.Resampling.LANCZOS))
# Match the page's painter order, including anonymous buildings which cross named-group bounds.
for tile in tiles:
    asset=Image.open(ROOT/'public'/tile['asset'].lstrip('/')).convert('RGBA')
    scene.alpha_composite(asset.resize((tile['width']*scale,tile['height']*scale),Image.Resampling.LANCZOS),(tile['x']*scale,tile['y']*scale))
for model in sorted(models,key=lambda m:m['sourceBounds'][1]+m['sourceBounds'][3]):
    x,y,w,h=model['sourceBounds']
    asset=Image.open(ROOT/'public'/model['asset'].lstrip('/')).convert('RGBA')
    asset.resize((w*2,h*2),Image.Resampling.LANCZOS).save(ROOT/'public'/model['overviewAsset'].lstrip('/'),quality=88,method=6)
    scene.alpha_composite(asset.resize((w*scale,h*scale),Image.Resampling.LANCZOS),((x+dx)*scale,(y+dy)*scale))
for model in models:
    x,y,w,h=model['sourceBounds']
    crop=scene.crop(((x+dx)*scale,(y+dy)*scale,(x+dx+w)*scale,(y+dy+h)*scale))
    crop.convert('RGB').save(ROOT/'public'/model['heroAsset'].lstrip('/'),quality=92,method=6)
artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
review=scene.convert('RGB');review.thumbnail((2280,1860));review.save(artifacts/'full-town-finished.jpg',quality=94)
print(f'Finalized {len(models)} overview assets and complete place-card scenes.')
