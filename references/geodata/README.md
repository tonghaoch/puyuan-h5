# 濮院时尚古镇地理参考数据

OSM 数据取得日期：2026-11-17。以下 OSM 数据及其派生 GeoJSON 的坐标为 WGS84，经度在前、纬度在后。© OpenStreetMap contributors，适用 [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)，来源与署名说明见 <https://www.openstreetmap.org/copyright>。后续加入的 Esri 影像有独立来源和使用条款，见文末，不能套用 OSM 许可。

这些数据的**公开来源已核实，现场位置、开放状态和测量精度未核实**。它们尚未与当前应用的美术示意图完成配准，不应据此直接在示意图上展示用户位置。

## 原始资料

| 文件 | 来源 |
| --- | --- |
| `nominatim-attraction.json` | [Nominatim 查询“濮院时尚古镇”](https://nominatim.openstreetmap.org/search?q=%E6%BF%AE%E9%99%A2%E6%97%B6%E5%B0%9A%E5%8F%A4%E9%95%87&format=jsonv2&addressdetails=1) |
| `nominatim-ancient-town.json` | [Nominatim 查询“濮院古镇”](https://nominatim.openstreetmap.org/search?q=%E6%BF%AE%E9%99%A2%E5%8F%A4%E9%95%87&format=jsonv2&addressdetails=1) |
| `osm-boundary-full.json` | [OSM way 1283631045 完整几何](https://api.openstreetmap.org/api/0.6/way/1283631045/full.json) |
| `osm-area-raw.json` | [OSM 单次小范围矢量导出](https://api.openstreetmap.org/api/0.6/map.json?bbox=120.6240,30.6785,120.6347,30.6867) |

查询 bbox 为 `(west=120.6240, south=30.6785, east=120.6347, north=30.6867)`。它只是数据请求范围，**不是景区边界**。OSM API 会保留与范围相交的 way 的完整节点，返回的 geometry 可能延伸到请求范围以外；包含的 relation 也不保证完整。原始导出约 355 KB，含 988 nodes、150 ways、41 relations。

## 派生 GeoJSON

执行 `python3 references/geodata/derive.py` 可从保存的快照重建：

| 文件 | 数量 | 内容与限制 |
| --- | --- | --- |
| `boundary.geojson` | 1 | OSM 标为濮院时尚古镇的闭合 polygon，62 个不同顶点；不等于已实测/官方确认的运营边界。 |
| `roads.geojson` | 125 | highway ways；包括园内步行街、桥、园外道路和一处 area=yes 广场。没有按景区 polygon 裁剪。 |
| `waterways.geojson` | 15 | canal 中心线；无河岸宽度、无水面 polygon。 |
| `buildings.geojson` | 1 | 原范围仅一栋已标记建筑的 polygon；无法代表园区建筑全量。 |
| `named-pois.geojson` | 8 | 非公交的具名节点，保留名称、标签、时间戳和 OSM 链接。不是活动地点或营业信息的官方确认。 |

脚本不补点、不偏移、不投影、不裁剪、不组装 relation，也不依据照片猜测几何。保留 OSM ID、版本和原始标签。只有原本闭合且明确为面积的对象才输出 Polygon；其它 way 输出 LineString。

完整发现及下一步见 [地理数据调查](../../docs/geodata-research.md)。

## 影像与连接关系核对资料（2026-11-17 至 18 补充）

- `esri-world-imagery-reference.jpg`：通过官方 World Imagery MapServer 单次 export 取得的 1400 × 1200 影像，仅供研究核对，未集成到应用。
- `esri-world-imagery-export.json`：原始 export 响应，含实际 EPSG:3857 范围；服务器调整过宽高比，应使用该返回范围而不是请求 bbox。
- `esri-world-imagery-reference.jgw`：上图的 world file，采用 EPSG:3857 投影米及像素中心约定。
- `esri-world-imagery-service.json` / `esri-world-imagery-local-metadata.json`：服务版权、图层说明及中心点来源元数据。中心点元数据日期为 2025-05-27；整张图是否同一采集日期未核实。
- `esri-osm-comparison.jpg`：OSM 边界、道路、水道、桥与具名点叠加影像，附说明条，供目视核对。因为加了说明条，不能套用原影像 world file。
- `bridges.geojson`：29 个原始 OSM `bridge=yes` highway ways，包含园外桥梁，未裁剪。
- `osm-connectivity-review.json`：根据 way 相邻原始 node ID 构建的道路与水系独立无向图。没有补点或按视觉相交连接，不是可上线的步行导航图。
- `reconcile-references.py`：从已保存快照重建以上派生核对资料，使用 Python 和 Pillow，不访问网络。

影像来源：**Esri, Vantor, Earthstar Geographics, and the GIS User Community**。服务地址：<https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer>；服务所链接的使用范围说明：<https://goto.arcgisonline.com/maps/World_Imagery>。公开 export 可调用不等于任意再分发或制作衍生资产的授权；本目录的影像作为研究参考保存。

完整对应分析与缺口见 [原图与地理资料核对](../../docs/map-reconciliation.md)。
