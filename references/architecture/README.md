# 建筑参考资料

整理日期：2026-11-18。全部资料用于本地外观研究，未加入 `public/` 或其他发布资产。没有取得建筑测绘尺寸、完整层数、原始设计图或照片拍摄日期。

## 用户原图裁图

原文件：`../puyuan-reference.jpg`，2363 × 1672。

| 文件 | 原图裁框 `[left,top,right,bottom]` |
| --- | --- |
| source-tower.png | [865,440,975,615]，3 倍放大 |
| source-zen-hotel.png | [1100,450,1320,640]，3 倍放大 |
| source-visitor-center.png | [610,300,905,515]，3 倍放大 |
| source-temple.png | [795,590,1025,845]，3 倍放大 |

另有 18 个 `source-group-*.png`，坐标见 `source-crops.json`；`source-groups-contact-sheet.jpg` 是便于比较的排版表。裁框不是建筑 footprint，也不是地面控制点。

## 景区第一方资料

入口：<https://www.puyuantown.com/>；指南：<https://www.puyuantown.com/guide>。`/home` 页脚标明桐乡市濮院旅游有限公司及备案号。已保存首页、主页面、指南 HTML 和公开页面脚本，以说明资料与照片确实来自该站公开内容。

`puyuantown-official-guide.json` 是官方页面调用的公开内容响应：

```text
POST https://bookingapi.puyuantown.com/api/pcContent/no_auth/getList
{"module_code":"puyuan_play_guide","module_index":0}
```

| 本地文件 | 官方正文标签 | 原始图片 URL |
| --- | --- | --- |
| official-visitor-wharf.jpg | 宝藏出片打卡地图 → 游客中心码头，sqlid=13 | https://newguanwan.oss-cn-hangzhou.aliyuncs.com/config/pcContent/2026-05-06/54bd7810-2e81-4751-be6d-50d387227d0e.jpg |
| official-fushan-temple.jpg | 宝藏出片打卡地图 → 福善寺，sqlid=13 | https://newguanwan.oss-cn-hangzhou.aliyuncs.com/config/pcContent/2026-05-06/d7531069-71b1-473c-be5b-06416d53aafd.JPG |
| official-meishang-hotel.jpg | 古镇住宿打卡地图 → 梅尚度假酒店，sqlid=34 | https://newguanwan.oss-cn-hangzhou.aliyuncs.com/config/pcContent/2026-05-06/a428244a-ef58-4839-8a4f-bd25665d8e31.jpg |
| official-magic-tower.jpg | 表演体验打卡地图 → 魔方塔，地点美术馆广场，sqlid=33 | https://newguanwan.oss-cn-hangzhou.aliyuncs.com/config/pcContent/2026-05-08/0278c7a1-e731-4b0a-8651-cf9253f450c6.JPG |
| official-home-carousel-2.png | 官网首页轮播，未标注建筑身份，不用于认定具体建筑 | https://cdn.puyuantown.com/config/pcContent/2026-11-09/7005b551-619c-439f-bd2b-0db927f1af9c.png |

`puyuantown-official-carousel.json` 与 `puyuantown-official-guide-images.json` 保留其公开图片出处。图片版权仍归原权利人；保存用于参考，不表示取得重新发布或制作衍生资产的授权。URL 中的日期是路径信息，不能认定为照片拍摄日期。

`tongxiang-official-introduction.html` 记录的政府网页正文请求返回 403，不作为内容证据。其他未读到正文的搜索结果不作为已核实的建筑事实。

分析结论与 18 个组团的外观观察见 [architecture-reference-review.md](../../docs/architecture-reference-review.md)。
