# 濮院漫游 H5

具有微信小程序布局的 H5：紧凑顶部栏、固定底部三 tab、下拉关闭的底部详情。手机直接使用，电脑居中预览同一套手机界面。

已覆盖18个原图标注地点，寺塔单列后形成19个独立建筑组团，并细化其余街巷建筑。右侧“细看古建”可打开目录选择；外围为连续的无建筑草地，支持拖出古镇范围并一键返回。

地图现有三种视图：

默认视野按窗口大小适配。从默认视野可缩小一次或放大八次；达到边界时对应按钮变灰，滚轮与双指缩放也遵循相同范围。

- **手绘导览**：以可编辑几何和绘制代码生成水系、驳岸、铺装、桥梁、植物及建筑，叠加动画与18处地点。底图、遮罩和详情场景均独立于原图像素。
- **原图对照**：全景使用轻量原色底图；放大后按缩放比例与屏幕像素密度，加载可视区域附近的 2 倍保真、4 倍 AI 或 8 倍近看图块。8 倍层直接从原始裁切生成，而非连续放大。各档共用相同坐标，AI 增强不代表新增真实建筑细节。
- **真实路网**：OSM 的道路、桥梁、水道、园区边界和具名地标。

原图对照以地图本身为输入，用 AI 补画镇外河岸与草地，保留镇内原稿。补画结果已写入概览及各档图块，不依赖页面贴图；镇外景观是插画延展，不代表实地地形。

原图的 18 处地点名和竖排「濮院古镇」由独立文字层按原位绘制。底图及所有高清档都使用去字补绘，标签下的景物是 AI 推断，不是实测资料。

地图按地点分类浏览，餐厅和活动页保留搜索、筛选与收藏。运营内容为演示数据；手绘图未进行地理配准，GPS 显示在真实路网中。

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

    npm run art:landscape
    npm run art:models
    npm run art:meadow
    npm run art:scenes
    npm run art:generate
    npm run geo:package
    npm run format

日常重绘需要 Python 3、Pillow、Playwright 与 Chrome/Chromium，`art:generate` 直接使用保存的几何数据，无需原图或网络。只有可选的原始资料导入与 `art:trace` 需要 NumPy/OpenCV；`art:reference` 单独重建原图对照。原始图片不被覆盖。

目标是原生手绘的完整度与细腻程度超过原图；当前已替换地形与景观底稿、补画被标签遮挡的院落，建筑体量、河岸与装饰仍需逐区精修。范围与验收标准见 [原生手绘目标](docs/native-map.md)。

- src/data/reference-map.json：18处参考图地点、范围与坐标变换。
- src/data/town-landscape.json：独立地形、水系、铺装、桥梁与植物实例。
- src/data/town-architecture.json：独立建筑轮廓及原生材质。
- src/data/town-completions.json：标签遮挡区域的原生建筑设计。
- src/data/landmark-models.json：独立建筑范围、资产和局部灯光。
- src/data/architecture-tiles.json：未命名街巷的建筑细节图块。
- src/data/street-houses.json、src/data/street-observations.json：逐栋檐线、院墙和可见木面等原生构件；核对方法见 [街屋精修](docs/street-houses.md)。
- src/data/meadow-tiles.json：外围草地景观块，按视野加载。
- src/data/catalog.ts：演示餐厅、活动与场次。
- src/data/geographic-pois.json：保存原始来源的地理地标，与插画地点分开。
- public/art：原生 SVG、预渲染图层、原生水面遮罩、卡片插画与可选原图对照。
- public/geodata：真实路网和来源信息。已下线的核对影像仅保存在 references/geodata，不随应用发布。
- references：原图、上版原型地图、原始地理资料和研究参考。

收藏只保存在当前浏览器。位置不会上传或保存轨迹。微信 JS-SDK/签名服务尚未配置，当前定位使用浏览器能力；尚未生产部署或微信真机验收。

## 文档

- [独立原生手绘导览目标与验收](docs/native-map.md)
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
