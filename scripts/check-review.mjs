import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { chromium } from '@playwright/test'
import { preview } from 'vite'

const base = '/puyuan-review-check/'
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const server = await preview({
  configFile: false,
  base,
  appType: 'mpa',
  build: { outDir: 'dist-review' },
  preview: { host: '127.0.0.1', port: 0 },
})
let browser
try {
  browser = await chromium.launch({
    executablePath:
      process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || (existsSync(chrome) ? chrome : undefined),
  })
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
  const root = `http://127.0.0.1:${server.httpServer.address().port}${base}`
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('response', (response) => {
    if (response.status() >= 400 || !response.url().startsWith(root))
      errors.push(`${response.status()} ${response.url()}`)
  })
  const decode = async (selector) => {
    const image = page.locator(selector).first()
    await image.waitFor({ state: 'attached' })
    await image.evaluate((element) => element.decode())
  }
  await page.goto(`${root}#map`)
  await decode('.map-art')
  for (let step = 0; step < 10; step++) await page.locator('.map-viewport').press('=')
  await decode('.reference-tiles img[src*="/8/"]')
  for (const [route, selector] of [
    ['games/task/relay', '.plate-leaf img'],
    ['itinerary/shows', '.show-code img'],
    ['food', '.dining-art'],
    ['map/place/temple/temple-pagoda', '.detail-hero img'],
  ]) {
    await page.goto(`${root}#${route}`)
    await decode(selector)
  }
  const boundary = page.waitForResponse(
    (response) => response.url() === `${root}geodata/boundary.geojson`,
  )
  await page.goto(`${root}#map/location`)
  assert.equal((await (await boundary).json()).type, 'FeatureCollection')
  assert.deepEqual(errors, [])
  console.log(
    '审阅包子路径验证通过：底图、高清瓦片、游戏图录、演艺码、餐厅插画、地点详情及定位边界。',
  )
} finally {
  await browser?.close()
  await server.close()
}
