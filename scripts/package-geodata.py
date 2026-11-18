"""Package the saved OSM snapshot, preserving provenance. Does not fetch or alter geometry."""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
features = []
for filename, layer in [('boundary.geojson', 'boundary'), ('roads.geojson', 'road'), ('waterways.geojson', 'water'), ('buildings.geojson', 'building'), ('named-pois.geojson', 'poi')]:
    obj = json.loads((root / 'references' / 'geodata' / filename).read_text())
    for feature in obj['features']:
        feature['properties']['layer'] = layer
        features.append(feature)
result = {
    'type': 'FeatureCollection',
    'attribution': '© OpenStreetMap contributors',
    'license': 'https://www.openstreetmap.org/copyright',
    'source': 'https://www.openstreetmap.org/way/1283631045',
    'retrieved': '2026-11-17',
    'crs_note': 'WGS84 longitude,latitude; public data, not field-surveyed',
    'features': features,
}
out = root / 'public' / 'geodata' / 'puyuan.geojson'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
print(f'Packaged {len(features)} attributed features.')

(root / 'src/data/geographic-pois.json').write_text((root / 'references/geodata/named-pois.geojson').read_text())
