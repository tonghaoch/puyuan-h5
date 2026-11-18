"""Create review artifacts from saved OSM data and one Esri map export.

No feature coordinates are invented or moved. Pillow is required for the image.
Run from any directory. Outputs are research references, not app map assets.
"""

import json
import math
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
raw = json.loads((ROOT / "osm-area-raw.json").read_text())
all_nodes = {e["id"]: e for e in raw["elements"] if e["type"] == "node"}
all_ways = [e for e in raw["elements"] if e["type"] == "way"]
graphs = {}
for graph_name, tag in [("roads", "highway"), ("waterways", "waterway")]:
    ways = [e for e in all_ways if tag in e.get("tags", {})]
    edge_ways = defaultdict(set)
    adjacent = defaultdict(set)
    for way in ways:
        for a, b in zip(way["nodes"], way["nodes"][1:]):
            edge_ways[tuple(sorted((a, b)))].add(way["id"])
            adjacent[a].add(b)
            adjacent[b].add(a)
    unseen = set(adjacent)
    components = []
    while unseen:
        pending = [unseen.pop()]
        component = []
        while pending:
            node_id = pending.pop()
            component.append(node_id)
            new = adjacent[node_id] & unseen
            unseen -= new
            pending.extend(new)
        components.append(sorted(component))
    components.sort(key=len, reverse=True)
    graphs[graph_name] = {
        "nodes": [{"osm_id": node_id,
                   "coordinates": [all_nodes[node_id]["lon"], all_nodes[node_id]["lat"]]}
                  for node_id in sorted(adjacent)],
        "edges": [{"nodes": list(pair), "way_ids": sorted(way_ids)}
                  for pair, way_ids in sorted(edge_ways.items())],
        "ways": [{"osm_id": way["id"], "tags": way.get("tags", {})} for way in ways],
        "components": components,
        "statistics": {
            "node_count": len(adjacent),
            "edge_count": len(edge_ways),
            "component_node_counts": list(map(len, components)),
            "junction_count_degree_ge_3": sum(len(v) >= 3 for v in adjacent.values()),
            "bridge_way_count": sum(w.get("tags", {}).get("bridge") == "yes" for w in ways),
        },
    }
graph_output = {
    "coordinate_system": "WGS84 longitude,latitude",
    "attribution": "© OpenStreetMap contributors",
    "license": "https://opendatacommons.org/licenses/odbl/1-0/",
    "method": "Undirected edges join consecutive original OSM nodes only; geometric crossings do not add nodes.",
    "limitations": "Unclipped snapshot. No access, one-way, pedestrian routing, polygon interior or opening-status interpretation. Not a navigation graph.",
    "graphs": graphs,
}
(ROOT / "osm-connectivity-review.json").write_text(json.dumps(graph_output, ensure_ascii=False, indent=2) + "\n")

roads = json.loads((ROOT / "roads.geojson").read_text())
bridges = {**roads, "name": "Puyuan OSM bridge ways: review only",
           "features": [f for f in roads["features"] if f["properties"].get("bridge") == "yes"]}
(ROOT / "bridges.geojson").write_text(json.dumps(bridges, ensure_ascii=False, indent=2) + "\n")

metadata = json.loads((ROOT / "esri-world-imagery-export.json").read_text())
extent = metadata["extent"]
width, height = metadata["width"], metadata["height"]
image = Image.open(ROOT / "esri-world-imagery-reference.jpg").convert("RGBA")
if image.size != (width, height):
    raise ValueError("Export metadata and image dimensions disagree")


def project(point):
    longitude, latitude = point
    radius = 6378137
    x = radius * math.radians(longitude)
    y = radius * math.log(math.tan(math.pi / 4 + math.radians(latitude) / 2))
    return ((x - extent["xmin"]) / (extent["xmax"] - extent["xmin"]) * width,
            (extent["ymax"] - y) / (extent["ymax"] - extent["ymin"]) * height)


overlay = Image.new("RGBA", image.size)
draw = ImageDraw.Draw(overlay)
for filename, color, line_width in [
    ("waterways.geojson", (50, 220, 255, 190), 3),
    ("roads.geojson", (255, 246, 183, 170), 2),
    ("boundary.geojson", (255, 95, 155, 230), 4),
    ("bridges.geojson", (255, 145, 50, 255), 5),
]:
    for feature in json.loads((ROOT / filename).read_text())["features"]:
        geometry = feature["geometry"]
        paths = [geometry["coordinates"]] if geometry["type"] == "LineString" else geometry["coordinates"]
        for path in paths:
            draw.line([project(p) for p in path], fill=color, width=line_width)

font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 20)
for feature in json.loads((ROOT / "named-pois.geojson").read_text())["features"]:
    x, y = project(feature["geometry"]["coordinates"])
    draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    label = feature["properties"]["name"]
    text_box = draw.textbbox((x + 9, y + 1), label, font=font)
    draw.rectangle((text_box[0] - 3, text_box[1] - 3, text_box[2] + 3, text_box[3] + 3), fill=(0, 0, 0, 190))
    draw.text((x + 9, y + 1), label, font=font, fill=(255, 255, 255, 255))
image = Image.alpha_composite(image, overlay).convert("RGB")
captioned = Image.new("RGB", (width, height + 80), (20, 26, 28))
captioned.paste(image)
draw = ImageDraw.Draw(captioned)
caption_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
captions = [
    "Research comparison only. Pink: OSM boundary; cyan: canal centerlines; pale yellow: roads; orange: bridges.",
    "Imagery: Esri, Vantor, Earthstar Geographics, GIS User Community. OSM: (c) OpenStreetMap contributors / ODbL.",
    "Source-date metadata at park center: 2025-05-27. Not a survey or proof of positional accuracy.",
]
for index, text in enumerate(captions):
    draw.text((12, height + 8 + index * 23), text, font=caption_font, fill=(235, 239, 240))
captioned.save(ROOT / "esri-osm-comparison.jpg", quality=92)

# World file for the original uncaptioned imagery, using returned EPSG:3857 extent.
x_size = (extent["xmax"] - extent["xmin"]) / width
y_size = -(extent["ymax"] - extent["ymin"]) / height
world_file = [x_size, 0, 0, y_size, extent["xmin"] + x_size / 2, extent["ymax"] + y_size / 2]
(ROOT / "esri-world-imagery-reference.jgw").write_text("\n".join(f"{v:.12f}" for v in world_file) + "\n")
print(json.dumps({name: graph["statistics"] for name, graph in graphs.items()}, ensure_ascii=False))
