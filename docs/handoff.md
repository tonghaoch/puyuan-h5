# 开发交接

更新：2026-11-18。从原 session `01a1e9bb-9ea0-7dc1-835c-395cbedf41ec` 的消息、工作区与生成结果恢复；原 session 最后几次请求因 `413 Payload Too Large` 失败。

## 当前接续点

最新目标已升级为「手绘导览完全取代原图，全部原生实现且总体细腻程度更高」。这取代下面历史交接中保留原始标签和依赖原图底稿的决定。当前进展、输入数据、验证证据与剩余视觉任务以 [独立原生手绘导览](native-map.md) 为准；目标仍在进行。

**当前版本：寺塔与临湖石台。** [直接看寺塔](http://127.0.0.1:5174/#map/place/temple/temple-pagoda) 或从古建目录进入。按插画而非实景照片复原深灰上部剪影、赭褐密檐和多边形浅石台；塔后留出干地和西侧窄水道。寺塔、寺院详情现在显示各自的插画，仍属同一福善寺地点，不增加 POI，也不改变 GPS。

- [原图／舞台版／寺塔版](../artifacts/pagoda-review/overview.jpg)、[手机详情](../artifacts/pagoda-review/temple-pagoda-detail-mobile.png)及[已绘区域待查索引](../artifacts/pagoda-review/remaining/shortlist.jpg)。上部剪影改善明显；石台暗部重合度仅 .067，不能视为通过。深灰量体的真实身份未知。
- 24 项单测、63 项浏览器检查通过，1 项桌面双指按配置跳过；类型检查与构建通过。`/private/tmp/puyuan-pagoda-release.sndsUb` 是新的无参考图基线；`artifacts/pagoda-review/rebuild.json` 中 100 个 SVG、5 份 JSON 清单和 19 张详情图逐字节相同。保留舞台、北更楼等前版，不覆盖。
- 19 处地标都有分组或专用结构，但不等于高相似度验收。下一轮优先复查游客中心南排与东跨水廊，与两岸檐脚、窗间留白和石墩逐一对齐；之后回到妆楼东端、设计师之家临河窄屋。[寺塔核对与复现](street-houses.md#寺塔密檐与临湖石台)。未提交、未推送。

### 水上舞台（前版）

在 `http://127.0.0.1:5174/` 选择「细看古建」→「选择要细看的建筑」→「水上舞台」。[原图／北更楼版／舞台版](../artifacts/stage-arc-review/overview.jpg) 与[手机详情](../artifacts/stage-arc-review/waterside-stage-detail-mobile.png)可直接比较。棚下不再透出假水面，木台两侧小件中间保留湖水；印刷标签后的部分是补绘。舞台不增加民居屋面数。

- 23 项单测、59 项浏览器检查通过；1 项桌面双指按配置跳过。类型检查与构建通过。`/private/tmp/puyuan-stage-release.I1Vq2b` 是独立舞台基线；100 个 SVG、5 份 JSON 清单、19 张详情 WebP 全部逐字节一致。
- [分组数值与复现](street-houses.md#水上舞台扇形棚与湖中木台)。花带树冠与玻璃细框仍不像原图；余区筛选不等于验证全部街屋。下一处寺塔须区分插画墨色与现状照片，不将不明深灰量体认作魔方塔。

### 北更楼与两岸街屋（前版）

在「细看古建」目录选择「北更楼」。原图能辨认双檐间的矮阁、下层横窗木架、石台垛口和中央门洞，不支持旧版画出的贯通长梯；现已按这些差异重画。两岸屋群新增 11 个屋面，仍不进景点目录。

- 前后对照 `artifacts/watchtower-review/overview.jpg`，不遮住门楼的详情实屏 `artifacts/watchtower-review/watch-detail-mobile.png`；同目录有四组独立对照、两片水岸与东南桥的手机/桌面放大实屏。上阁只提高 .004，不能视为美术验收。
- 22 项单测、57 项浏览器检查通过，1 项桌面双指按配置跳过；类型检查与生产构建通过。新的无参考图重建 `/private/tmp/puyuan-watchtower-release.iqc3Ra` 是下轮独立基线；100 个 SVG、5 份清单及 19 张详情图与工作区逐字节相同。`artifacts/watchtower-review/rebuild.json` 留有逐对结果。
- [街屋精修](street-houses.md) 列出本轮数值和重现命令。下轮先核水上舞台的后排树带、盖檐下的空隙、临水小台；寺塔须区分原图暗色层檐和官方照片材质。另留北更楼和游客中心等已绘区域的返工项。未提交、未推送。

### 设计师之家与妆楼（前版）

两地标与无名街屋新增 58 个屋面，对岸街屋不进目录。12 组轮廓重合度有 11 组提高；设计师之家两列临河窄屋回退，妆楼东端仍太整齐。四座石板短桥、两处水带与北桥桥台见 `artifacts/designer-loft-review/`。

- 前后对照 `overview.jpg`，石栏和桥下水道 `north-bridge.jpg`；同目录有两处整体与六处局部的手机、桌面实屏。
- 21 项单测、55 项浏览器检查通过，1 项桌面双指按配置跳过；生产构建通过。独立重建的 100 个 SVG、5 份 JSON 和 17/19 张详情图逐字节相同，其余两张的解码差值见 `rebuild.json`。
- 下一轮用 `/private/tmp/puyuan-designer-quay-release.Dj3II6` 作前版，不覆盖。剩余寺塔、水上舞台、北更楼三处成组对照见 `artifacts/designer-loft-review/remaining/remaining-landmarks.jpg`。优先核北更楼木框、白墙、石台与水岸；[街屋精修](street-houses.md) 列出旧区待返工项。未提交、未推送。

### 美术馆与游客中心（前版）

原生 H5 的「细看古建」→「选择要细看的建筑」可直接看这两个地标。东岸无名小铺只在地图中绘制，不进目录。相对酒店版新建 63 个屋面；游客中心两道跨水廊之间不再是假陆地。

- 原图 / 酒店版 / 本版：`artifacts/gallery-visitor-review/overview.jpg`；实屏 `zen-gallery-fit-mobile.png`、`visitor-court-fit-mobile.png` 及五组放大图在同目录。
- 20 项单测、51 项浏览器检查通过，1 项桌面触屏检查按配置跳过，生产构建通过。19 张详情图重新合成；无原图独立重建对照见 `artifacts/gallery-visitor-review/rebuild.json`。
- 下一轮独立基线 `/private/tmp/puyuan-gallery-release.sMZZfI`。酒店基线保留以便比较，勿覆盖。未提交、未推送。
- 不要以测试通过代替建筑验收：美术馆四组提高，游客中心南排、东廊等六组仍低于酒店版。剩余五个地标的成组核对索引为 `artifacts/gallery-visitor-review/remaining/remaining-landmarks.jpg`；先看设计师之家北排长屋与岸边小铺。逐组数值及重现命令见[街屋精修](street-houses.md)。

### 先前轮次

2026-11-18 接续 `01a1ec8f-494e-72d0-9ed9-636bcdbdf969`。该会话因 413 中断时，游客中心玻璃厅仍像高塔，新拆出的河岸 SVG 已生成但合成详情所需的 WebP 尚不存在。本轮已重画游客中心和水上舞台，修复湖岸与船体重影，重建 19 张详情图；原有未提交工作保留在 `main`，未推送。

从本地预览点「细看古建」→「选择要细看的建筑」即可核对各组团。游客中心与水上舞台的上轮对照在 `artifacts/handoff-stage-and-visitor.jpg`；四处街屋的本轮对照在 `artifacts/street-review/overview.jpg`；全园在 `artifacts/full-town-finished.jpg`。舞台背侧的花木带仍偏稀疏。不要把功能检查当作全园美术验收。

桥头一轮又逐栋核对大有桥（39 个屋面）、濮商会馆（19 个）与美食中心（12 个）。三列图按「原图 / 接手前 / 当前」排列：`artifacts/quay-review/overview.jpg`。四处标签区临水补绘的墙脚已移回干岸，另见 `artifacts/quay-review/shore-footprints.jpg`。

上一轮梅泾剧场、深夜食堂、书场新增 76 个屋面，含露柱小棚、四坡厅和白墩铺面。`artifacts/lane-review/overview.jpg` 与八张局部图使用完整地图而非旧卡片的裁切范围；六处轮廓更接近原图，剧场西院与南街仍偏低。该版的独立重建基线仍在本机临时目录 `/private/tmp/puyuan-lane-final.YzxwDR`。

河岛一轮完成两座围院、南端双屋、西岸长瓦屋和禅美术馆以南图题边的附屋，5 组 16 个原生屋面均归背景，不增景点。连通桥下水道，用同一条岸线画石壁、岸顶和岛上铺地。`artifacts/island-review/overview.jpg` 为当时的三列对照；五组局部轮廓 IoU 等权 `0.258 → 0.581`。无原图完整重建基线 `/private/tmp/puyuan-islet-rebuild.zXu3i1` 保留，供比较福善寺修改前的版本。

现已完成福善寺东廊和桥头小屋所在的整个院群，以及图题南端的匿名街院：共 11 组、62 个屋面；寺门双檐留出透光带，七片误作建筑的驳岸移回景观。`artifacts/temple-court-review/overview.jpg` 从左到右为原图、河岛版、福善寺版；同目录有五处各两种视口的 H5 截图。11 组可见深色轮廓等权 IoU `0.608 → 0.628`，五升六降。主殿金瓦范围更准，南门、东西配殿及沿河山墙不能据此算通过。

福善寺终稿的无原图独立基线 `/private/tmp/puyuan-temple-release.tCAGBB` 保留，用于本轮前后对照。

酒店版记录：两道临水围廊之间保留白石露台，院内木屋分开，东侧窄檐与短厅相接。酒店与无名北巷共 19 个屋面，五组可见深色形状 IoU 等权 `0.624 → 0.809`。西檐下水道已与南河相通，不切穿墙基。寺门双檐侧坡和前柱、西配殿山墙与低木桥也已复查。`artifacts/zen-review/overview.jpg` 是原图 / 福善寺版 / 酒店版；`zen-courtyard-fit-mobile.png` 为同目录的手机全院画面。完整清单及复查命令见[街屋精修](street-houses.md)。

当时的基线 `/private/tmp/puyuan-zen-release.CDAHm5` 从无原图、无素材、无缓存的目录重建。18 项单测、47 项浏览器检查通过，1 项桌面双指检查跳过，生产构建通过。当时建议先看 `artifacts/zen-review/remaining-landmarks.jpg` 的禅美术馆：可见内院木屋与东翼尚未连好；游客中心的沿河围院仍是大片粗轮廓。寺门已高于河岛版的轮廓分数，西配殿尚未超过，不能以酒店五组都提升来结案。

## 较早交接（历史）

用户最后一项开发要求是「很好，继续打磨剩下所有的建筑？」。随后两条消息是针对请求错误重试，没有改变开发范围。

这轮代码和素材已经落盘，原 session 中断在最终交付之前。全园细化内容见 [全园构件细化](architecture-finishing.md)；19 个地标组团和 24 块街巷图层已有输出，北更楼与妆楼做了单独绘制。继续美术迭代时从这些现有资产对照原图检查；还原度仍需用户看图反馈，自动化通过只说明功能和数据约束通过。

接手后用户已要求继续开发。已完成一轮形体与材质修正：北更楼恢复源图的木构楼阁和石台，妆楼高立面移回右侧，全园增加源图明暗分区与长墨线。具体修改和对照图见上述构件细化文档。

手机截图另确认了 CSS 阴影滤镜导致的放大变软，已移除建筑图片和细赏状态的滤镜。此改动后再次通过 10 项建筑专项浏览器检查；键盘焦点边框和素材内的明暗保留。

## 已保留的产品决定

- 交付为具有小程序布局的微信 H5：手机界面、底部三 tab、地图点位详情、餐厅与活动列表。
- 视觉方向为中式复古、精细的 2.5D 建筑与局部动画，布局遵循用户原图和可核对的地理资料。
- 古镇外围延伸为连续草地，放大后仍有拖拽余量，可以返回古镇。
- 原图只保留在对照视图；手绘图以可编辑形体补全标签遮挡区。早期细化依据见 [建筑参考核对](architecture-reference-review.md)。

## 早期接手验证

`npm test`：9 项通过。`npm run build`：类型检查与生产构建通过。`npm run test:e2e`：41 项通过；桌面配置跳过 1 项仅适用于触屏设备的双指缩放测试，手机配置中该测试通过。

浏览器验证覆盖全部建筑目录选择、图层细节切换、建筑点击与拖动、外围探索、三 tab、弹层、收藏、地图模式与模拟定位。接续细化后已重新输出全园合成预览 `artifacts/full-town-finished.jpg`，以及 19 处原图/接手时/本轮修正对照 `artifacts/relief-*.jpg`。

接手后已运行 `node scripts/capture.mjs` 更新桌面和手机截图，覆盖全部手机建筑细赏、四种地图视图、列表、详情和模拟定位。现有本地预览地址为 `http://127.0.0.1:5174/`，服务工作目录已核对为本仓库。

## 后续工作及依赖

1. 建筑视觉验收：在「细看古建」中检查各组团，与「原图对照」比较，再按反馈局部修整。生成流程和资产职责见 [全园建筑](whole-town-architecture.md)。
2. 手绘主图与 GPS 整合：先确认分布于全园的地面控制点及独立检验点，再拟合并报告误差。当前 GPS 只在真实路网、影像视图显示；配准资料缺口见 [地图核对](map-reconciliation.md)。
3. 微信接入：需要可访问的 HTTPS 环境、JS-SDK 所需配置与签名服务，再进行 iOS/Android 微信真机验收。
4. 运营内容：餐厅、价格、营业时间及活动场次仍为演示数据，需要真实资料。

## Git 状态

仓库为 `tonghaoch/puyuan-h5`。交接时分支为 `main`，基线提交为 `f723d42`；当时尚未提交的建筑图层和细化文件已完整保留，并在接续开发中继续完善。代码、生成素材与来源资料一并纳入版本控制。最新提交与工作区状态通过 `git log -1 --oneline` 和 `git status --short --branch` 查看。当前实现全貌见 [实现记录](implementation.md)。
