import { writeFile } from 'node:fs/promises'
import { networkInterfaces } from 'node:os'
import { build } from 'vite'
import { startPhonePreview } from './wechat-local-server.mjs'

const [target] = process.argv.slice(2)
let url
if (target && target !== '--lan') {
  url = new URL(target)
  if (url.protocol !== 'https:' || url.username || url.password) {
    throw new Error('请提供不含凭据的 HTTPS 审阅地址。')
  }
} else {
  const addresses = Object.values(networkInterfaces())
    .flat()
    .filter(
      (entry) =>
        entry &&
        !entry.internal &&
        entry.family === 'IPv4' &&
        /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(entry.address),
    )
  const host = target === '--lan' ? process.env.WECHAT_LAN_IP || addresses[0]?.address : '127.0.0.1'
  if (target === '--lan' && !addresses.some((entry) => entry.address === host)) {
    throw new Error('未找到指定的局域网 IPv4。请连接 Wi-Fi，或传入 HTTPS 地址。')
  }
  await build()
  await import('./package-review.mjs')
  ;({ url } = await startPhonePreview(host, 4174))
  console.log(
    target === '--lan'
      ? '手机须连接同一可信 Wi-Fi。完整预览链接相当于访问凭据，请勿转发；按 Ctrl-C 停止。'
      : '仅本机开发者工具可访问。手机同网测试请先退出，再显式使用 --lan。',
  )
}
await writeFile(
  new URL('../miniprogram/preview-url.js', import.meta.url),
  `module.exports = ${JSON.stringify(url.href)}\n`,
)
console.log(
  `H5 地址：${url.href}\n在微信开发者工具中导入仓库根目录，重新编译后点「预览」或「真机调试」，用手机微信扫码。`,
)
