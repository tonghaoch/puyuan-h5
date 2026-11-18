import { chromium } from '@playwright/test'
import { existsSync, mkdirSync } from 'node:fs'
mkdirSync('artifacts', { recursive: true })
const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const browser = await chromium.launch({
  executablePath:
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ||
    (existsSync(localChrome) ? localChrome : undefined),
  headless: true,
})
for (const [name, viewport] of [
  ['desktop', { width: 1440, height: 1000 }],
  ['mobile', { width: 390, height: 844 }],
]) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1, reducedMotion: 'reduce' })
  page.on('pageerror', (error) => console.error('PAGE ERROR:', error.message))
  await page.goto('http://127.0.0.1:5174', { waitUntil: 'networkidle' })
  await page.screenshot({ path: `artifacts/${name}-map.png` })
  for (const [view, label] of [
    ['reference', '原图对照'],
    ['geographic', '真实路网'],
    ['imagery', '影像核对'],
  ]) {
    await page.getByRole('button', { name: label, exact: true }).click()
    if (view !== 'reference') await page.locator('.real-road').first().waitFor({ state: 'visible' })
    await page.waitForTimeout(300)
    await page.screenshot({ path: `artifacts/${name}-${view}.png` })
  }
  await page.getByRole('button', { name: '手绘导览', exact: true }).click()
  await page.getByRole('button', { name: /^寻味濮院/ }).click()
  await page.screenshot({ path: `artifacts/${name}-food.png` })
  await page.getByRole('button', { name: /^风雅之约/ }).click()
  await page.waitForTimeout(300)
  await page.screenshot({ path: `artifacts/${name}-activities.png` })
  await page.getByRole('button', { name: '查看水岸听曲详情' }).click()
  await page.getByRole('dialog').waitFor({ state: 'visible' })
  await page.waitForTimeout(300)
  await page.screenshot({ path: `artifacts/${name}-detail.png` })
  await page.getByRole('button', { name: '关闭弹窗' }).click()
  await page.getByRole('dialog').waitFor({ state: 'hidden' })
  await page.getByRole('button', { name: /^游园地图/ }).click()
  await page.context().grantPermissions(['geolocation'])
  // Synthetic device position for the screenshot only, not the developer's location.
  await page
    .context()
    .setGeolocation({ latitude: 30.6828922, longitude: 120.6296382, accuracy: 10 })
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await page.locator('.geo-user').waitFor({ state: 'visible' })
  await page.locator('.geo-overview').scrollIntoViewIfNeeded()
  await page.screenshot({ path: `artifacts/${name}-location-simulated.png` })
  await page.getByRole('button', { name: '在真实路网中查看位置' }).click()
  await page.locator('.main-user-position').waitFor({ state: 'visible' })
  await page.screenshot({ path: `artifacts/${name}-real-gps-simulated.png` })
  await page.close()
}
await browser.close()
