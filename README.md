# 濮院漫游 H5

具有微信小程序布局的 H5：地图、行程、游戏、餐厅四个底部入口。手机直接使用，电脑居中预览同一套手机界面。

导览覆盖 18 个标注地点，点击地名可查看详情。外围为连续草地，可以自由拖动探索。

导览中的 8 条游船分布在不同河段，错开航行。船身使用从原图中抠出的竹篷船和深色篷船；系统开启「减少动态效果」时，游船和水纹保持静止。

默认视野按窗口大小适配。手机上单指拖动、双指缩放；桌面也支持滚轮缩放。地图右下角仅保留定位按钮，位于底部导航上方。

导览全景使用轻量原色底图；放大后按缩放比例与屏幕像素密度，加载可视区域附近的 2 倍保真、4 倍 AI 或 8 倍近看图块。8 倍层直接从原始裁切生成，而非连续放大。各档共用相同坐标，AI 增强不代表新增真实建筑细节。

导览以地图本身为输入，用 AI 补画镇外河岸与草地，保留镇内原稿。补画结果已写入概览及各档图块，不依赖页面贴图；镇外景观是插画延展，不代表实地地形。

原图的 18 处地点名和竖排「濮院古镇」由独立文字层按原位绘制。底图及所有高清档都使用去字补绘，标签下的景物是 AI 推断，不是实测资料。

导览顶部有三枚图层牌签：江湖令牌和行走 NPC 默认点亮，古镇地点默认熄灭。点按牌签可显示或隐藏对应标记。全部熄灭时只看底图。从手册定位时只会点亮目标所在的图层。

首次打开默认中文，点右上角的「文 / En」图标即可切换语言，朱砂色标出当前语言。切换不会重置地图视野、筛选、正在阅读的手册或收藏；浏览器允许本地存储时会记住选择。餐厅和活动搜索同时匹配中英文。译文位于 `src/i18n/`，地图和图录沿用原始画作及照片。

令牌与 NPC 图标固定在各自落点正上方，跟随底图同比缩放，不因视口边缘、工具栏或地名而换位。

SOX 活动手册按 v1119 行程资料整理。`src/data/offsite.ts` 保存两天时间线、可选体验、餐厅、挑战与角色。导览图按活动参考图标出了 8 枚挑战令及 5 个斗笠侠客标记。每枚令牌只打开自己的底部卡片；同在大草坪的「蹴鞠达人」和「一锤定音」各有落点和手册入口，旧的大草坪详情链接仍可使用。放大可见标记名称；引线末端的小圆点才是配准位置。NPC 点代表活动区域，不是实时追踪；巡捕游走全镇，不设固定点。配准依据见 `references/offsite-registration.json`，这些插画坐标不是 GPS。演艺 Tab 提供景区小程序码，不发布推测场次；体验价格及名额以现场为准。旧演示活动深链保留，不作为团队安排。GPS 只在「我的位置」的园区边界概览中显示。

## 本地运行

使用 Node.js 24 LTS：

    npm install
    npm run dev

打开终端显示的 Local 地址。H5 和微信小程序是两个入口：网页可直接分享，小程序用 `miniprogram/` 中的 `web-view` 加载它。[微信开发者工具真机测试与 GitHub Pages 审阅](docs/phone-review.md)。

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

日常重绘需要 Python 3、Pillow、Playwright 与 Chrome/Chromium，`art:generate` 直接使用保存的几何数据，无需原图或网络。只有可选的原始资料导入与 `art:trace` 需要 NumPy/OpenCV；`art:reference` 单独重建导览。原始图片不被覆盖。

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
- public/art：原生 SVG、预渲染图层、原生水面遮罩、卡片插画与可选导览。
- public/geodata：定位概览使用的园区边界及来源信息。原始路网、地标和核对影像保存在 references/geodata，不随应用发布。
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
