# 地图参考

puyuan-reference.jpg 是用户于 2026-11-17 提供的原始参考图，尺寸 2363 × 1672。

用于识别古镇范围、建筑风格和候选设施，也是当前手绘导览的细节底稿。图中包含周边住宅与产业区；最终地图聚焦确认后的古镇游览范围。

这是一张带透视的导览插画，不是测绘底图。图上的建筑、名称与开放范围仍需对照当前园区资料确认；不能从图片推断精确经纬度。

原图保留完整，不覆盖、不裁改；正式地图资产另行制作。本目录不会被 Vite 自动打包到产品中。

2026-11-18：scripts/prepare-reference-map.py 按 src/data/reference-map.json 选取古镇范围，生成 public/art 下的配色版、原色对照和水面动画遮罩。仅做平移、遮罩与配色，原图不覆盖。

`npm run art:reference` 重建 1520 × 1240 的原色概览图和 2 倍保真图块（Lanczos 插值、轻度锐化）。使用 `npm run art:reference -- --ai-master /path/to/puyuan-AI-4x.webp` 可同时切分已对齐的 6080 × 4960 AI 母图；不提供时保留随项目发布的 4 倍图块。两层均为 512 像素无损 WebP，边界图块按实际尺寸裁切。原始 JPG 与手绘导览素材不变。

高清层在切块前统一增强明暗边缘，对每个像素的修正量设限，避免地名笔画和屋脊出现过重的亮边。缩放比例乘屏幕像素比超过 1.7 时切入 4 倍层，不必等到 2 倍图已被拉大才加载。

近看档（缩放 ≥ 2.7 或缩放 × 屏幕像素比 > 4）用 8 倍层。它与 4 倍层采用同一图块网格，每块最多 1024 像素。`npm run art:reference -- --lapsrn-x8 /path/to/LapSRN_x8.pb` 可从原始裁切直接重建，需 NumPy、opencv-contrib-python-headless 4.11 和 [LapSRN 模型](https://github.com/fannymonori/TF-LapSRN/blob/master/export/LapSRN_x8.pb)。不提供模型时保留随项目发布的近看层。
