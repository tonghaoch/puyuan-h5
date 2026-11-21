# 手机测试与分享审阅

## 用自己的手机先测，不需要 GitHub Pages

1. 手机和 Mac 连同一可信 Wi-Fi；在仓库根目录运行 `npm ci`（已装依赖可跳过），再运行 `npm run wechat:preview -- --lan`。这会构建 H5，将网页成品绑定到一个局域网 IPv4 的 4174 端口，并把含随机访问码的地址写入本机小程序壳。不带 `--lan` 时仅监听本机，供开发者工具模拟器使用。
2. 将终端显示的**完整链接**发给自己的微信，在手机里点开。没有随机路径会返回 404；链接持有人在同一网络可查看行程和活动照片，HTTP 不加密，请不要转发或在公共 Wi-Fi 使用。终端须保持运行，结束时按 Ctrl-C；重新启动会换码。手机里的 `localhost` 是手机自己，不是电脑。如果连不上，检查 Wi-Fi 设备隔离、macOS 防火墙和 VPN；多网卡可用 `WECHAT_LAN_IP=实际的Wi-Fi地址 npm run wechat:preview -- --lan`。
3. 打开**微信开发者工具 → 小程序 → 导入**，选仓库根目录（有 `project.config.json`），不是 `src/`、`dist/` 或 `miniprogram/`。用该 AppID 的开发者微信登录；若不属于该项目，请换成有权限的非个人主体小程序 AppID。`miniprogramRoot` 只打包轻量壳，不会打包整套地图。
4. 临时局域网调试可在**详情 → 本地设置**勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」。点**编译 → 真机调试**（或「预览」），用同一开发者微信扫码。若开发版提示域名不可用，可在手机开发版菜单开启调试、退出并重新进入；不同客户端/账号仍可能拒绝局域网 HTTP。这是调试手段，不是发布配置。
5. 局域网打不开 `web-view`、需要验证定位，或要跨网络测试时，**改用已配置业务域名的 HTTPS 站点**：运行 `npm run wechat:preview -- https://你的域名/站点路径/`，再编译、重新扫码。此模式不启动本机服务器。退出本地「不校验」后再验证一次。

**正式版与体验版**：在小程序管理后台的开发设置配置 **业务域名**（不是 request 合法域名），按微信要求完成域名资质与校验文件验证。个人类型小程序不支持 `web-view`。GitHub Pages 可用于普通微信网页审阅，但 `github.io` 地址不等于已获准的小程序业务域名。真机扫码及定位授权需本人完成；定位使用浏览器 Geolocation，未接入微信 JS-SDK，HTTP 局域网页面不能用来验收定位能力。

[微信官方 web-view 说明](https://developers.weixin.qq.com/miniprogram/dev/component/web-view.html) · [网络与开发调试说明](https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html)

## 给同事一个 GitHub Pages 链接

- `npm run build:review` 生成 `dist-review/`。它是可独立部署的静态站点，支持仓库子路径和 `#map` 等深链接。不要上传整个源码仓库、原 PPT、参考图目录或个人开发者工具配置。**成品仍包含行程、集合地点和活动图片**，公开审阅前需确认这些可对外展示。
- 在 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**。推送到 `main` 后会自动运行测试、构建和网页检查；全部通过才会部署到 Pages。也可在 **Actions → Publish H5 review to Pages → Run workflow** 手动重新部署。成功后分享部署返回的网址或其普通二维码，微信扫一扫即可打开，无需安装开发者工具。
- 若私有仓库因套餐限制不能开启 Pages，不必改源码可见性。获得公开成品的授权后，可将 `dist-review/` **的内容**放到单独的公开审阅仓库，Pages 选择 **Deploy from a branch → main → /(root)**。这种方式需要在更新版本时重新发布成品。普通 Pages 不是邀请制，拿到链接的人可能继续转发；如内容限内部，应使用带访问控制的托管。
