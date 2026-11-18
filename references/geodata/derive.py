"""Derive review-only GeoJSON from the accompanying OSM API snapshot.

No coordinate conversion, snapping, clipping, inference or relation assembly.
Run with Python 3; no dependencies. Output coordinates remain WGS84 lon/lat.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent
raw = json.loads((ROOT / "osm-area-raw.json").read_text())
elements = raw["elements"]
nodes = {e["id"]: e for e in elements if e["type"] == "node"}


def feature(element):
    tags = element.get("tags", {})
    if element["type"] == "node":
        geometry = {"type": "Point", "coordinates": [element["lon"], element["lat"]]}
    else:
        missing = [node_id for node_id in element["nodes"] if node_id not in nodes]
        if missing:
            raise ValueError(f"Incomplete way {element['id']}: missing {missing}")
        coordinates = [[nodes[node_id]["lon"], nodes[node_id]["lat"]]
                       for node_id in element["nodes"]]
        is_area = (tags.get("area") == "yes" or "building" in tags
                   or element["id"] == 1283631045)
        if is_area:
            if coordinates[0] != coordinates[-1]:
                raise ValueError(f"Area way {element['id']} is not closed")
            geometry = {"type": "Polygon", "coordinates": [coordinates]}
        else:
            geometry = {"type": "LineString", "coordinates": coordinates}
    return {
        "type": "Feature",
        "id": f"{element['type']}/{element['id']}",
        "properties": {
            **tags,
            "osm_type": element["type"],
            "osm_id": element["id"],
            "osm_version": element["version"],
            "osm_timestamp": element["timestamp"],
            "source_url": f"https://www.openstreetmap.org/{element['type']}/{element['id']}",
            "verification": "osm-source-only; not field-surveyed",
        },
        "geometry": geometry,
    }


layers = {
    "boundary": [e for e in elements if e["type"] == "way" and e["id"] == 1283631045],
    "roads": [e for e in elements if e["type"] == "way" and "highway" in e.get("tags", {})],
    "waterways": [e for e in elements if e["type"] == "way" and "waterway" in e.get("tags", {})],
    "buildings": [e for e in elements if e["type"] == "way" and "building" in e.get("tags", {})],
    "named-pois": [e for e in elements if e["type"] == "node"
                   and e.get("tags", {}).get("name")
                   and not e["tags"].get("public_transport")],
}
for name, selected in layers.items():
    output = {
        "type": "FeatureCollection",
        "name": f"Puyuan OSM reference: {name}",
        "attribution": "© OpenStreetMap contributors",
        "license": "https://opendatacommons.org/licenses/odbl/1-0/",
        "features": [feature(e) for e in selected],
    }
    (ROOT / f"{name}.geojson").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"{name}: {len(selected)} features")
