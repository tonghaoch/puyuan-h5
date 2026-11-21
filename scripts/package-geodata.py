"""Package only the park boundary needed by the location dialog, retaining OSM attribution."""
from pathlib import Path
from shutil import copyfile

root = Path(__file__).resolve().parents[1]
output = root / 'public/geodata/boundary.geojson'
output.parent.mkdir(parents=True, exist_ok=True)
copyfile(root / 'references/geodata/boundary.geojson', output)
