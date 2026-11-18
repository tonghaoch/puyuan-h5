# 街屋精修：按可见檐线还原建筑群

翔云观的斜殿曾被画成单个平直长屋；濮家大院和龙湾街有些相邻的屋顶、端墙和木铺面被归入同一块深色轮廓。这轮按檐线区分瓦坡与立面，保留可辨认的外轮廓，不把标签遮挡区内的设计解释为实测。

| 地标 | 集中核对的区域 | 屋面构件 |
| --- | --- | ---: |
| 翔云观 | 北院、斜向主殿及西门、南院与东岸 | 28 |
| 濮家大院 | 西巷排屋、东侧围院、南沿河三排 | 34 |
| 龙湾街美食广场 | 西侧长屋与沿街连续铺面 | 19 |
| 濮驸马第 | 南门及沿河小屋 | 7 |
| 大有桥建筑群 | 西院、东岸、东侧回巷 | 39 |
| 濮商会馆 | 西翼山墙与东侧柱廊 | 19 |
| 美食中心 | 四排铺面、后侧短檐与临水附屋 | 12 |
| 梅泾剧场 | 西侧连院、北排与回廊、南侧临街铺面 | 32 |
| 深夜食堂 | 街口小棚、南排店院、东侧双列附屋 | 24 |
| 书场 | 正厅与后场小院、西侧斜巷 | 20 |
| 福善寺建筑群 | 双层金瓦主殿、东西廊亭、临河山墙、双檐南门与南院 | 31 |
| 禅意酒店 | 临水外廊、院内木屋和内侧围廊 | 11 |
| 禅美术馆 | 西院、三排木屋、东翼和南厅 | 14 |
| 游客中心 | 白山墙排屋、配殿、跨水廊及南门屋（不含玻璃厅） | 46 |
| 设计师之家 | 北排双厅、西返廊、临河窄屋及三组铺排 | 33 |
| 妆楼 | 低屋、木楼、东院及东侧白山墙 | 17 |
| 北更楼 | 下檐横窗木架和上层短阁（不把垛墙、桥面算成屋面） | 2 |

十七处地标的 59 组共 388 个屋面。八片无名街巷的 15 组另有 77 个屋面，合计 **465 个屋面构件**，不是实地建筑栋数：主殿和门楼的叠檐分别建模。每条记录包含前檐两端、后坡偏移、脊高、墙高、立面类型。灰瓦沿坡向分垄，墙柱保持竖直；庭院的低墙和铺地与屋体分别绘制。可见的灰瓦与木面用于校准檐线位置；主殿叠层以及被标签遮挡过多的构件不做自动拟合。

全园另有 118 块带可见下沿的白墙、339 块原误作灰瓦的木立面、246 条墨线以可编辑的矢量几何保存。它们不依赖参考图运行。编辑依据为图面资料而非 GPS 或建筑测绘。

## 桥头与临水街屋

大有桥东侧回巷南端改成斜交的两段屋脊。会馆以每栋独立的瓦口、木横枋和边柱处理前后遮挡，不把整块深色底形再盖回白墙。`eaveEnds` 的键是本组屋面在 `houses` 中的零起始序号；`tileLips` 每段的上下沿点数相等，`timber` 为可见木框折线。美食中心原先的标签占位厅遮住了能辨认的铺面，现改绘四排长屋、短后檐与岸侧小屋；完整重画的长屋组用 `retainObservedSurfaces: false` 关闭粗轮廓叠绘，避免瓦片浮在巷中。

深夜食堂、梅泾剧场、龙湾街、濮驸马第四处普通补绘房屋挪回干岸，驸马第的厢房缩短留出邻房间距。单元测试按每个原图坐标单位采样全部 22 处普通补绘房屋的投影（含旋转、侧墙），对照带洞的原生水域；游船和水台另测。`artifacts/quay-review/shore-footprints.jpg` 最右栏红线为调整前、绿线为调整后，蓝色是项目的水域。它验证的是图面关系，不能据此推断标签下建筑的实地位置。

## 剧场、食堂与书场

剧场西侧原属一块跨街巷图层的大轮廓，现区分北排短屋、前后相接的纵向厢房和南街白墩铺面。食堂街角的小棚只有棚顶、梁和柱，棚下仍能看到地面；东院的两列附屋用独立后檐和屋脊描出不对称的山墙。书场正厅与内院围出小天井，旧的标签补绘厅缩回遮挡范围，不再被侧屋切断。两处花冠按可见的色块定位，前排屋面遮去后方枝叶；这些点位依然是插画坐标。

- `roofForms` 可覆盖后檐或屋脊的两个端点；已有人工端点的屋面不参与自动拟合。`roofTones` 描述瓦色，`pavingAngle` 为院内石缝方向，院墙记录第三个可选值为瓦帽宽度。
- `behindEaves` 记录树的实例 ID 与其前方的屋面序号。调整这些屋面的形状、排序或相关树木后须同时重建景观和建筑。透空棚的遮挡只使用屋面，而不把柱间视作一堵墙。
- 三处街区都越出了旧版详情卡的裁切范围。本轮用前后两版完整原生图层比较：`python3 scripts/review-street-houses.py --baseline /path/to/previous-full-build --full-scene --out artifacts/lane-review --site meijing-theater --site night-dining --site storytelling-house`。`overview.jpg` 为原图、改前、当前三列；同目录有八张局部对照、六张手机和桌面实际放大截图。
- 八处可见深色形状 IoU 等权平均 **0.697 → 0.725**。书场正厅和西巷 0.760 → 0.840、0.722 → 0.749；食堂街口、南排和东院 0.493 → 0.575、0.714 → 0.730、0.676 → 0.712。剧场北排 0.735 → 0.751，但西院 0.764 → 0.742、南街 0.712 → 0.701，仍应复核局部檐宽、屋体衔接与铺面开间。不能把六处提升解释成全园验收。

## 重建与复核

- 正常重建：`npm run art:landscape && npm run art:models && npm run art:scenes`。应用只加载原生素材；建筑源数据为 `src/data/street-houses.json` 和 `src/data/street-observations.json`。
- 视觉复核：`python3 scripts/review-street-houses.py --baseline /path/to/previous-build`。基线需有 `src/data/landmark-models.json` 和 `public/art/landmarks/`；省略基线时只对照原图。使用 `scripts/requirements-art.txt` 的依赖。
- `artifacts/street-review/overview.jpg` 保留前四处地标的九张局部对照；本轮三处地标的七张新对照、手机放大截图和 `alignment.json` 在 `artifacts/quay-review/`。复查本轮：`python3 scripts/review-street-houses.py --baseline /path/to/previous-build --out artifacts/quay-review --site dayou-bridge-quarter --site merchant-hall --site food-center`。
- 数值仅检查未被印刷标签遮住的深色形状：同一原图分辨率、灰度阈值 145，逐区计算 IoU（交集面积/并集面积）；另报容许两像素误差的精确率和召回率。九处等权平均 IoU 从约 0.66 增至 0.71。它不衡量瓦纹质量，也不能证明全园已与原图高度一致。
- 本轮以已有上述九处街屋的版本为基线，只比较两版详情图都有像素的区域，避免把裁图外的黑边算作屋面。七处等权平均 IoU 为 0.674 → 0.701。大有桥西院、东岸、回巷分别为 0.737 → 0.752、0.621 → 0.627、0.696 → 0.709；会馆西翼、东廊为 0.650 → 0.685、0.686 → 0.731；美食中心排屋、临水附屋为 0.668 → 0.715、0.657 → 0.685。
- `scripts/import-street-facades.py` 是一次性观察工具；`scripts/fit-street-eaves.py <候选.json>` 会把候选数据另存，不覆盖作者文件。它只做以当前檐线为基准的有限微调，不应反复应用。两者都不在日常构建链中。

## 无名河岛与图题边缘

东侧河岛北端临桥围院 4 个屋面、中段树庭 5 个、南端两间木屋，加上隔水西岸的长瓦屋和禅美术馆以南图题边的 4 个屋面，共 16 个。河岛一轮结束时为十处地标 234 个构件、三片无名街巷 16 个构件。后者写在 `street-houses.json` 的 `background`，只进入相交的街巷瓦块，不增加地标、图钉或详情卡。东岸另有一排店屋沿导览范围边缘伸向范围外，没有把它移到河岛上凑数。

河岛不是游船，也不与西岸连成一块。西侧实为短石桥：河道外环从桥下通过，岛身由同一水域的内环留出；岛石铺地与立面砌缝沿同一个内环绘制。原图竖题的四个字与白边另做排除范围，不再把其右侧露出的瓦坡、木面和白墙一起排掉。该组按 `visibleOnly` 在已辨认的区域收笔，没有从字下推断整院的平面或归属。

`artifacts/island-review/overview.jpg` 从左到右为原图、上轮原生图、本轮原生图。五组深色轮廓 IoU：桥头 `0.055 → 0.482`、树庭 `0.035 → 0.429`、南端双屋 `0.566 → 0.590`、西岸长屋 `0.635 → 0.688`、图题边附屋 `0.000 → 0.716`。五组等权 `0.258 → 0.581`，其中前两组仍不能算逐栋吻合。用 `python3 scripts/review-street-houses.py --full-scene --baseline /path/to/previous-build --out artifacts/island-review --site east-islet --site east-west-bank --site gallery-south-lane` 复查。在本地 H5 开着时，`node scripts/capture-background-streets.mjs` 会从真实导览放大到三片街区，生成手机和桌面截图；不用原图，也不需要临时添加景点。

## 福善寺与图题南端环院

福善寺以 7 组 31 个屋面替代旧殿模板和连片轮廓。金瓦主殿依前后檐分别起坡，西边的两亭和河边的六座山墙各自收檐；南门上层的柱枋与下层屋面之间真正露空，透出后方地面。寺前移除没有图面依据的直路，保留能辨出的庭中石缝。三段石驳岸沿水域外环生成，原先像假屋顶的七片瓦木轮廓不再绘入建筑；桥头陆路和南河水段分别保留。

图题以南的两座小院、内院、题字边返廊和沿河排屋另有 4 组 31 个屋面，不增加地标。竖题及印刷标签不作为檐线依据。两处一共精修 62 个屋面。

| 区域 | 可见深色轮廓 IoU（河岛版 → 本轮） |
| --- | --- |
| 金瓦主殿、东廊、西亭 | 0.418 → 0.406；0.579 → 0.524；0.670 → 0.632 |
| 河边山墙、双檐南门 | 0.838 → 0.794；0.721 → 0.625 |
| 寺南小院、东南附屋 | 0.680 → 0.762；0.520 → 0.579 |
| 图题南双院、内院 | 0.715 → 0.685；0.515 → 0.699 |
| 题字边返廊、沿河排屋 | 0.563 → 0.649；0.472 → 0.550 |

十一组等权平均 **0.608 → 0.628**，五组上升、六组下降。单独检查主殿琉璃色域，IoU 为 **0.534 → 0.636**，两像素容差精确率 0.821 → 0.924、召回率 1.000 → 0.994。金瓦铺得更准，不等于深色檐口也更准。门楼虽然恢复了透空，柱脚与檐角轮廓仍应优先复查；不能用整个组团的均值验收。

本机河岛基线 `/private/tmp/puyuan-islet-rebuild.zXu3i1` 用于复查此轮变化；福善寺终稿的独立重建 `/private/tmp/puyuan-temple-release.tCAGBB` 留作下一轮基线。三列图从左到右为原图、河岛版、福善寺版。坐标均为插画坐标，不用于导航。

```sh
python3 scripts/review-street-houses.py --full-scene --baseline /private/tmp/puyuan-islet-rebuild.zXu3i1 --out artifacts/temple-court-review --site temple-hall --site title-south-courts
node scripts/capture-background-streets.mjs --out artifacts/temple-court-review temple-gold-hall temple-east-cloister temple-double-gate temple-river-gables south-lane-inner-court
```

第一条只做离线对照；第二条在 H5 预览运行时以桌面和手机视口各拍五处，不进入原图视图。输出同目录含 `overview.jpg`、逐组数值、十张浏览器截图与 `rebuild.json`。

## 禅意酒店、北巷与寺门复查

酒店的三组 11 个屋面不再套用矩形环廊模板。外廊与内廊的南檐、屋脊和后檐分别与东西侧屋面斜接；两廊之间留出白石露台。内院木屋分开绘制，东侧短厅与窄檐相接，不把草庭切成旧模型的 L 形。浅色墙帽、暗瓦、木隔扇和窗下矮板可独立调整。北侧标签遮住的区域留作简化设计，不把它当作实测。酒店以北的小街另有 2 组 8 个屋面，包括印刷标签边确实露出的三段短檐；均归背景，不增景点。被完整替换的旧窗墙不再从新屋下方露出。

酒店西水道与南水道现在属于同一个水形。原本在插画坐标 `y=573` 附近收窄至零的夹点已修复；测试每 0.25 个坐标单位检查西檐外的水隙连续，同时要求西侧人行道、露台与墙基保持干燥。主图、详情图与动画共用该水形。

| 可见区域 | 深色轮廓 IoU（福善寺版 → 酒店版） |
| --- | ---: |
| 酒店临水外廊 | 0.799 → 0.830 |
| 内院木屋及东侧短檐 | 0.485 → 0.835 |
| 内侧围廊 | 0.716 → 0.837 |
| 北巷排屋 | 0.672 → 0.754 |
| 图签旁露出的短檐 | 0.448 → 0.788 |

五组等权 **0.624 → 0.809**，不包括印刷区。另行复查旧版下降项：福善寺南门按两列实际可辨的柱脚收梁，用完整的弯曲侧坡封合原模型檐角不该透光的三角缝，保留上下檐夹缝；南门 **0.625 → 0.754**，高于更早河岛版的 0.721。西配殿恢复白色小山墙、门洞及后侧低木桥，**0.632 → 0.665**，仍略低于河岛版的 0.670。寺南小院也有约 0.001 的回落，不能说所有轮廓都已还原。各组完整数值在 `artifacts/zen-review/temple/alignment.json`。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-temple-release.tCAGBB --full-scene --out artifacts/zen-review --site zen-courtyard --site zen-north-lane
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-temple-release.tCAGBB --full-scene --out artifacts/zen-review/temple --site temple-hall
node scripts/capture-background-streets.mjs --out artifacts/zen-review --fit zen-courtyard
node scripts/capture-background-streets.mjs --out artifacts/zen-review zen-inner-lodges zen-court-galleries zen-lane-north-row temple-double-gate temple-west-pavilions
```

`artifacts/zen-review/overview.jpg` 三列为原图、福善寺版、酒店版。`--fit` 通过 H5 的缩放键使两岸全宽进入视口；其余局部固定三倍缩放。六个取景各有桌面和手机截图，均未调用原图视图。下一轮可用 `/private/tmp/puyuan-zen-release.CDAHm5` 作独立基线；不要覆盖之前的基线。

## 禅美术馆与游客中心

相对酒店独立基线，本轮增加 63 个屋面。禅美术馆保留西院的两道矮墙、三排木屋间露出的白山墙、连续的东翼和南厅。撤掉压在可见木屋上的设计性占位院落。游客中心保留三座大小不同的玻璃厅和一段玻璃连廊；南排山墙之间另画矮檐，跨水廊的局部白石墩之间可见水面，南端门屋分出两排窗。东岸的三间沿河屋面属于背景，不新增景点。位置来自可见檐线；标签下方没有能据以还原的细节。

游客中心原先三块绕着房檐走的水形改为同一条河；草岸和南岸石面沿河形生成。四片假岸墙与一片假瓦面（`wood-662/663/664`、`wall-273`、`roof-976`）退出建筑，西侧石阶泊岸单独由景观绘制。`partialTraceReplacements` 只遮去 `roof-1017` 在游客中心范围内的旧底形与立面，东侧不在范围内的构件仍在原图块内。全园 851 个建筑表面；265 个可生成体积的屋形包含 3472 个面。

同一坐标比较原图、酒店版和本版，排除印刷标签后，深色形状的交并比（IoU）为：

| 区域 | 上版 → 本版 | 区域 | 上版 → 本版 |
| --- | ---: | --- | ---: |
| 美术馆西院 | 0.564 → 0.591 | 美术馆三排木屋 | 0.808 → 0.906 |
| 美术馆东翼 | 0.861 → 0.886 | 美术馆南厅 | 0.832 → 0.926 |
| 游客中心西返廊 | 0.638 → 0.663 | 后排小厅 | 0.622 → 0.601 |
| 东配殿 | 0.737 → 0.715 | 南排山墙 | 0.641 → 0.587 |
| 北岸木铺 | 0.786 → 0.757 | 西跨水廊 | 0.740 → 0.747 |
| 东跨水廊 | 0.698 → 0.657 | 南端门屋 | 0.646 → 0.612 |
| 东岸无名小铺 | 0.640 → 0.788 | | |

美术馆四组都提高；游客中心八组中只有西返廊和西跨水廊超过上版。六组下降不可用背景东岸小铺的提升抵消。原来成片黑瓦虽不是完整房屋，但覆盖了不少原图暗部；新山墙和跨廊可辨认，仍有檐口错位、暗纹过整齐、后厅木框和南门屋窗脚粗细不合。此数值既不等于建筑数量，也不是全园视觉验收。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-zen-release.CDAHm5 --full-scene --out artifacts/gallery-visitor-review --site visitor-court --site zen-gallery --site visitor-east-bank
node scripts/capture-background-streets.mjs --out artifacts/gallery-visitor-review --fit zen-gallery visitor-court
node scripts/capture-background-streets.mjs --out artifacts/gallery-visitor-review museum-timber-courts visitor-front-gables visitor-west-water-walk visitor-south-gatehouses visitor-bank-shops
python3 scripts/survey-remaining-streets.py --out artifacts/gallery-visitor-review/remaining
```

三列图 `artifacts/gallery-visitor-review/overview.jpg`，每组局部与数值在同目录。另有七个取景、各一张桌面和手机截图；它们来自运行中的 H5，不是离线拼图。无参考图重建基线 `/private/tmp/puyuan-gallery-release.sMZZfI` 与旧酒店基线分开保留。详情图逐对校验见 `artifacts/gallery-visitor-review/rebuild.json`。

### 美术馆版本的剩余区域（历史）

`artifacts/gallery-visitor-review/remaining/remaining-landmarks.jpg` 将尚未按小建筑分组的五处地标与原图并排绘制。优先看设计师之家北部两栋长屋和岸边小铺：现有地标位置在，白色端墙和两列之间的巷隙仍画成瓦块。其次看妆楼两岸附屋。北更楼砖石台基、水上舞台背侧花木和寺塔也要复查。寺塔须区分官方照片的石构材质与地图中的墨色，不宜仅追黑白分数。

`remaining/survey.json` 另列 125 个有足够瓦木证据的未复核网格，以及两格疑似漏绘；树影、桥和驳岸也会命中，不能当作确认漏楼。已经建模的游客中心南排与东跨水廊、福善寺西配殿、剧场西院和南街也仍在人工精修队列中。

## 设计师之家、妆楼与两岸小铺

新增 58 个屋面：设计师之家 33、妆楼 17、无名对岸小铺 8。替换两处旧占位厅；木楼按楼层和开间画木板窗与柱脚，瓦坡、脊线按固定种子画磨损旧瓦。两处水带接回邻水域，岸线共用水面几何。补四座石板桥，两座旧桥移至跨水处；设计师之家北桥去除两块假瓦，换灰石栏、双墩与干岸桥台。只校准插画的裁切边，不移动点位或 GPS。

`artifacts/designer-loft-review/overview.jpg` 按原图 / 美术馆版 / 本版排列。对前后版应用同一校正后的印刷标签遮罩。深色轮廓 IoU（前→本）：

| 区域 | 分组 |
| --- | --- |
| 设计师之家 | 双厅 .877→.939；内巷 .701→.713；临河窄屋 **.736→.729**；西返廊 .000→.723；西铺 .706→.713；南院 .603→.687；岸铺 .729→.812 |
| 妆楼 | 低屋 .658→.731；高木楼 .818→.862；东院 .746→.818；东端山墙 .507→.537 |
| 对岸街巷 | 无名小铺 .573→.676 |

12 组等权 .638→.745，11 升 1 降。两列临河窄屋的端墙和墨瓦口仍错位，妆楼东端也比原图整齐；数值不是全园验收。`north-bridge.jpg` 单列桥体前后；八个取景（两个整体、五组屋和北桥）各有手机及桌面实屏。独立重建保存在 `/private/tmp/puyuan-designer-quay-release.Dj3II6`，详情图逐对结果见 `rebuild.json`。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-gallery-release.sMZZfI --full-scene --out artifacts/designer-loft-review --site designer-quarter --site dressing-house --site dressing-south-bank
node scripts/capture-background-streets.mjs --out artifacts/designer-loft-review --fit designer-quarter dressing-house
node scripts/capture-background-streets.mjs --out artifacts/designer-loft-review designer-twin-halls designer-canal-gables designer-quay-shops dressing-timber-loft dressing-opposite-shops bridge-1
python3 scripts/survey-remaining-streets.py --out artifacts/designer-loft-review/remaining
```

此版的 `remaining/remaining-landmarks.jpg` 并列寺塔、水上舞台、北更楼。113 个可比网格中，寺塔 (862,500)、舞台 (990,308) 两格疑似漏灰瓦，不是新景点。先对照北更楼两层深木框、石台和河边树带；寺塔须区分官方照片材质和插画墨色。

## 北更楼、两岸街屋与东南小桥

拆开两道灰瓦檐、上层矮阁与下层木框，增加横窗、脊饰和白墙；把误作瓦屋的门洞过梁归还给垛墙，删除石台两端无依据的灯笼和中央长梯。侧栏、垛口、墙缝、门洞和低门槛分开画。西岸八个屋面以斜檐和朝南白墙留出中间巷道；东岸三段木铺在桥台北端，不加点位。扩回两侧可见水面，东南小桥下水流连续，不把桥面当作陆地。标签后方只做连续补绘。

`artifacts/watchtower-review/overview.jpg` 是原图 / 设计师之家版 / 北更楼版，四个视窗同一印刷标签遮罩。深色轮廓 IoU：门楼及石台 .310→.520，上阁 .730→.734，西院 .616→.660，东岸木楼 .548→.638。初稿把西屋排成横向铺面，立面对照显示应朝南出山墙；纠正后西院较前版提高，但邻墙转折和白墙轻重仍有差别。上阁提高很小，垛墙灰砖的明暗仍比原图规整。四组分数不代表整个园区的还原度。

两个整体和五个局部各有手机、桌面取景；`watch-inspection-*` 与 `watch-detail-*` 是从古建目录进入后的画面。`remaining/remaining-landmarks.jpg` 留有水上舞台、寺塔两处对照；111 个剩余网格里，(862,500) 和 (990,308) 匹配到的是暗色，不一定是漏绘灰瓦。下一处先看舞台外弧后面的花木、侧檐与湖中木台，寺塔材质另核。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-designer-quay-release.Dj3II6 --full-scene --out artifacts/watchtower-review --site north-watchtower --site watchtower-bank-houses
node scripts/capture-background-streets.mjs --out artifacts/watchtower-review --fit north-watchtower watchtower-bank-houses
node scripts/capture-background-streets.mjs --out artifacts/watchtower-review watch-upper-pavilion watch-gate-and-parapet watch-west-courts watch-east-timber watch-east-footbridge
python3 scripts/survey-remaining-streets.py --out artifacts/watchtower-review/remaining
python3 scripts/compare-art-rebuild.py --rebuild /private/tmp/puyuan-watchtower-release.iqc3Ra --out artifacts/watchtower-review/rebuild.json
```

## 水上舞台：扇形棚与湖中木台

旧棚将玻璃分成 24 个均匀窄格。现按可见的梁位拆成六跨，主梁、断续细框、内弧深木檐、浅色西端面分开绘制；后排花木按屋盖边缘遮挡。删除误作建筑的五块碎片；屋檐下是连到岸边的干地，独立木台的深色板面、浅裙板和两侧小件都在湖中。印刷标签挡住的细框与岸线是连贯补绘，不是实测。此项是专用结构，不重复计入 465 个街屋屋面。

| 原图可见区域 | 深色轮廓 IoU（北更楼版 → 舞台版） | 材质色域 IoU（同一可见掩膜） |
| --- | --- | --- |
| 玻璃棚 | .202 → .257 | 浅蓝玻璃 .449 → .900 |
| 内弧深檐 | .321 → .589 | 深木 .271 → .704 |
| 湖中木台 | .787 → .824 | 深木 .008 → .883 |
| 后排花带 | .099 → .131 | 不测 |

前一列比较暗像素位置；后一列比较相应玻璃或木色像素，不是细框对准率。花树的疏密、墨色与棚框断线仍与原图不同。`artifacts/stage-arc-review/` 有三列总览、四组对照与 14 张手机／桌面截图（目录细赏、详情、整体和四处放大）。剩余调查的 111 个可比格里只提示寺塔 (862,500)；原舞台 (990,308) 不再命中。这不是全园视觉验收。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-watchtower-release.iqc3Ra --full-scene --out artifacts/stage-arc-review --site waterside-stage
node scripts/capture-background-streets.mjs --out artifacts/stage-arc-review --details waterside-stage
node scripts/capture-background-streets.mjs --out artifacts/stage-arc-review --fit waterside-stage
node scripts/capture-background-streets.mjs --out artifacts/stage-arc-review stage-glass-fan stage-lake-eave stage-floating-platform stage-flower-belt
python3 scripts/compare-art-rebuild.py --rebuild /private/tmp/puyuan-stage-release.I1Vq2b --out artifacts/stage-arc-review/rebuild.json
```

## 寺塔密檐与临湖石台

`scripts/art/pagoda.py` 用插画坐标绘制不规则的深灰上部剪影、短顶缘、紧密的赭褐檐带及多边形石台。插画西侧的窄水道和东侧干地已经分开，桥头铺地不再直接并入湖面。绘制的檐带不是实测楼层；官方码头照片中的浅石色塔和细刹是对现状外形的另一份证据，官方寺门照、魔方塔照均不用于推断插画深灰形体的身份。参见[两类证据](architecture-reference-review.md#寺塔原图与现状照片应分别处理)。

| 可见形状 | 深色轮廓 IoU（舞台版 → 寺塔版） |
| --- | --- |
| 上部剪影与小顶缘 | .330 → .845 |
| 紧密层檐 | .234 → .647 |
| 赭褐塔座 | .143 → .576 |
| 浅石台周边，不含中央塔身 | .052 → .067 |

`artifacts/pagoda-review/overview.jpg` 为原图、舞台版和寺塔版；四组离线对照与手机、桌面目录细赏、详情、整体和四处放大均在同目录。台阶的灰缝、东端收口仍偏规则；深色掩膜不直接衡量浅石材质。寺塔详情 `#map/place/temple/temple-pagoda` 可刷新；普通地点 `#map/place/temple` 仍打开寺院。收藏和地理点位都以福善寺为单位。

`remaining/survey.json` 在未屏蔽的同一批 111 个可比格里不再提示 (862,500) 等疑似漏灰瓦；`remaining/shortlist.jpg` 的 8 格仍有明显差异，可能是檐脚、植物或水岸，不等于缺 8 座建筑。下一处以游客中心南排和东侧跨水廊为主，保留窗间水面及桥墩；妆楼东端、设计师之家临河屋仍留在返工清单。此轮不会改变 465 个街屋屋面计数。

```sh
python3 scripts/review-street-houses.py --baseline /private/tmp/puyuan-stage-release.I1Vq2b --full-scene --out artifacts/pagoda-review --site temple-pagoda
node scripts/capture-background-streets.mjs --out artifacts/pagoda-review --details temple-pagoda
node scripts/capture-background-streets.mjs --out artifacts/pagoda-review --fit temple-pagoda
node scripts/capture-background-streets.mjs --out artifacts/pagoda-review pagoda-upper-silhouette pagoda-tight-eaves pagoda-ochre-base pagoda-stone-terrace
python3 scripts/survey-remaining-streets.py --out artifacts/pagoda-review/remaining
python3 scripts/compare-art-rebuild.py --rebuild /private/tmp/puyuan-pagoda-release.sndsUb --out artifacts/pagoda-review/rebuild.json
```
