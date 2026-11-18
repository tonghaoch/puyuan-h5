"""Fast, exact native scene previews for visual authoring; no reference images required."""
from pathlib import Path
import json,sys
from art.scene import compose_scene

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'artifacts/native-detail-reviews';out.mkdir(parents=True,exist_ok=True)
reference=json.loads((ROOT/'src/data/reference-map.json').read_text())
models=json.loads((ROOT/'src/data/landmark-models.json').read_text())['models']
selected=next((arg[7:].split(',') for arg in sys.argv[1:] if arg.startswith('--only=')),None)
dx,dy=reference['sourceOffset']['x'],reference['sourceOffset']['y'];scale=3
scene=compose_scene(scale).convert('RGB')
preview=scene.copy();preview.thumbnail((2280,1860));preview.save(out/'whole-town.jpg',quality=95)
for m in models:
    if selected and m['id'] not in selected:continue
    x,y,w,h=m['sourceBounds']
    scene.crop(((x+dx)*scale,(y+dy)*scale,(x+w+dx)*scale,(y+h+dy)*scale)).save(out/f'{m["id"]}.jpg',quality=96)
print(f'Native scene review: {out}')
