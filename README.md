# 濮院漫游 H5

具有微信小程序布局的 H5：紧凑顶部栏、固定底部三 tab、下拉关闭的底部详情。手机直接使用，电脑居中预览同一套手机界面。

已覆盖18个原图标注地点，寺塔单列后形成19个独立建筑组团，并细化其余街巷建筑。右侧“细看古建”可打开目录选择；外围为连续的无建筑草地，支持拖出古镇范围并一键返回。

地图现有四种视图：

- **手绘导览**：沿用原图的古镇水系、桥梁和地标布局，按实际可见轮廓重建全园建筑图层，外围衔接草地，叠加动画与18处地点。
- **原图对照**：同一范围与坐标的原始配色，可直接检查还原位置。
- **真实路网**：OSM 的道路、桥梁、水道、园区边界和具名地标。
- **影像核对**：带准确投影范围的地图服务影像，与路网和 GPS 叠加。

支持餐厅和活动列表、搜索筛选、场次状态、收藏及地图联动。运营内容为演示数据；手绘图未进行地理配准，GPS 显示在真实路网和影像视图中。

## 本地运行

使用 Node.js 24 LTS：

    npm install
    npm run dev

打开终端显示的 Local 地址。手机与微信测试需要可访问的 HTTPS 地址；本项目是网页，不是小程序工程。

## 验证

    npm test
    npm run test:e2e
    npm run build

浏览器测试默认使用本机 Chrome（macOS）。其他环境可先运行 npx playwright install chromium，或通过 PLAYWRIGHT_CHROMIUM_EXECUTABLE 指定 Chromium 路径。测试服务固定使用 5174 端口。

## 维护

    npm run art:trace
    npm run art:models
    npm run art:meadow
    npm run art:reference
    npm run art:generate
    npm run geo:package
    npm run format

原图和建筑处理脚本需要 Python 3、Pillow、NumPy 和 OpenCV（scripts/requirements-art.txt）；建筑预渲染另使用 Playwright 与 Chrome/Chromium。开发无需重生成素材，已提交工作区内的生成结果可直接使用。原始图片不被覆盖。

- src/data/reference-map.json：18处参考图地点、范围与坐标变换。
- src/data/landmark-models.json：独立建筑范围、资产和局部灯光。
- src/data/architecture-tiles.json：未命名街巷的建筑细节图块。
- src/data/meadow-tiles.json：外围草地景观块，按视野加载。
- src/data/catalog.ts：演示餐厅、活动与场次。
- src/data/geographic-pois.json：保存原始来源的地理地标，与插画地点分开。
- public/art：原图衍生地图、原色对照、水面遮罩和卡片插画。
- public/geodata：真实路网、地图服务影像及其投影范围、来源信息。
- references：原图、上版原型地图、原始地理资料和研究参考。

收藏只保存在当前浏览器。位置不会上传或保存轨迹。微信 JS-SDK/签名服务尚未配置，当前定位使用浏览器能力；尚未生产部署或微信真机验收。

## 文档

- [开发接续与剩余事项](docs/handoff.md)：恢复会话或接续本轮建筑细化时先读。
- [当前实现](docs/implementation.md)
- [本轮构件细化](docs/architecture-finishing.md)
- [全园建筑与实景校正](docs/whole-town-architecture.md)
- [精细建筑与连续外围](docs/building-layers.md)
- [原图与实际地图核对](docs/map-reconciliation.md)
- [地理数据来源与覆盖缺口](docs/geodata-research.md)
- [技术方案](docs/technical-plan.md)
- [美术与动画方向](docs/art-direction.md)
- [微信与地图官方资料核查](docs/platform-research.md)
