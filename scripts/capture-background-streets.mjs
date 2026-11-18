import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { chromium } from '@playwright/test'
import { parseArgs } from 'node:util'

const root = new URL('../', import.meta.url)
const read = async (path) => JSON.parse(await readFile(new URL(path, root), 'utf8'))
const { sites, background } = await read('src/data/street-houses.json')
const { sourceOffset } = await read('src/data/reference-map.json')
const { bridges } = await read('src/data/town-landscape.json')
const { values, positionals } = parseArgs({
  options: {
    out: { type: 'string', default: 'artifacts/island-review' },
    fit: { type: 'boolean', default: false },
    details: { type: 'boolean', default: false },
  },
  allowPositionals: true,
})
const out = new URL(values.out.replace(/\/?$/, '/'), root)
const { sites: structures } = await read('src/data/landmark-structures.json')
const { models } = await read('src/data/landmark-models.json')
const areas = {
  ...sites,
  ...background,
  ...Object.fromEntries(Object.entries(structures).map(([id, model]) => [id, model.review])),
}
const named = {
  ...Object.fromEntries(
    bridges.map(({ id, x, y, length, width, angle }) => {
      const radians = (angle * Math.PI) / 180
      const dx = (Math.abs(length * Math.cos(radians)) + Math.abs(width * Math.sin(radians))) / 2
      const dy = (Math.abs(length * Math.sin(radians)) + Math.abs(width * Math.cos(radians))) / 2
      return [
        id,
        [
          {
            replace: [
              [
                [x - dx, y - dy - 4],
                [x + dx, y + dy + 4],
              ],
            ],
          },
        ],
      ]
    }),
  ),
  ...Object.fromEntries(
    Object.values(areas)
      .flat()
      .map((group) => [group.id, [group]]),
  ),
  ...areas,
}
const selected = positionals.length
  ? positionals.map((name) => {
      assert.ok(Object.hasOwn(named, name), name)
      return [name, named[name]]
    })
  : Object.entries(background)
if (values.details) assert.ok(positionals.length && !values.fit, 'Specify landmarks for --details')
const shots = []
await mkdir(out, { recursive: true })
const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const browser = await chromium.launch({
  executablePath:
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ||
    (existsSync(localChrome) ? localChrome : undefined),
})
try {
  for (const [device, viewport] of Object.entries({
    mobile: { width: 390, height: 844 },
    desktop: { width: 1440, height: 1000 },
  })) {
    const page = await browser.newPage({
      viewport,
      deviceScaleFactor: device === 'mobile' ? 2 : 1,
      reducedMotion: 'reduce',
    })
    const requests = []
    page.on('request', (request) => requests.push(request.url()))
    await page.goto(process.env.PUYUAN_PREVIEW_URL || 'http://127.0.0.1:5174/', {
      waitUntil: 'networkidle',
    })
    const map = page.getByRole('region', { name: /古镇示意地图/ })
    const scene = page.locator('.map-scene')
    for (const [area, groups] of selected) {
      if (values.details) {
        const model = models.find(({ id }) => id === area)
        assert.ok(model, `No place card for ${area}`)
        await page.getByRole('button', { name: '细看古建', exact: true }).click()
        await page.getByRole('button', { name: '选择要细看的建筑' }).click()
        await page
          .getByRole('region', { name: '古建目录' })
          .getByRole('button', { name: new RegExp(model.name) })
          .click()
        await page.locator(`[data-model-id="${area}"] img`).evaluate((image) => image.decode())
        await page.waitForLoadState('networkidle')
        shots.push([new URL(`${area}-inspection-${device}.png`, out), await page.screenshot()])
        await page.getByRole('button', { name: `查看${model.name}建筑详情` }).click()
        const hero = page.getByRole('dialog').locator('.detail-hero img')
        await hero.evaluate((image) => image.decode())
        assert.equal(await hero.getAttribute('src'), model.heroAsset)
        shots.push([new URL(`${area}-detail-${device}.png`, out), await page.screenshot()])
        await page.goto(process.env.PUYUAN_PREVIEW_URL || 'http://127.0.0.1:5174/', {
          waitUntil: 'networkidle',
        })
        continue
      }
      for (let step = 0; step < 16; step++) await map.press('=')
      const points = groups.flatMap((group) => group.replace.flat())
      const center = (axis) =>
        (Math.min(...points.map((point) => point[axis])) +
          Math.max(...points.map((point) => point[axis]))) /
        2
      const [x, y] = [center(0) + sourceOffset.x, center(1) + sourceOffset.y]
      const box = await map.boundingBox()
      const readScale = () => scene.evaluate((element) => new DOMMatrix(element.style.transform).a)
      let scaleToCheck = 3
      if (values.fit) {
        const extent = (axis) =>
          Math.max(...points.map((point) => point[axis])) -
          Math.min(...points.map((point) => point[axis]))
        const limit = Math.min(
          (box.width - 80) / extent(0),
          Math.max(100, box.height - 350) / extent(1),
        )
        for (let step = 0; step < 16 && (await readScale()) > limit; step++) await map.press('-')
        scaleToCheck = await readScale()
        assert.ok(scaleToCheck <= limit, `Cannot fit ${device}/${area}`)
      }
      const offset = async () => {
        const [left, top, scale] = await scene.evaluate((element) => {
          const matrix = new DOMMatrix(element.style.transform)
          return [matrix.e, matrix.f, matrix.a]
        })
        assert.equal(scale, scaleToCheck)
        return [left + x * scale - box.width / 2, top + y * scale - box.height * 0.53]
      }
      const [dx, dy] = await offset()
      for (const [delta, next, previous] of [
        [dx, 'ArrowRight', 'ArrowLeft'],
        [dy, 'ArrowDown', 'ArrowUp'],
      ]) {
        for (let step = 0; step < Math.round(Math.abs(delta) / 70); step++)
          await map.press(delta > 0 ? next : previous)
      }
      const remainder = await offset()
      assert.ok(
        remainder.every((delta) => Math.abs(delta) <= 36),
        `${device}/${area}: ${remainder}`,
      )
      if (remainder.some((delta) => Math.abs(delta) > 1)) {
        const start = await map.evaluate((viewport) => {
          const box = viewport.getBoundingClientRect()
          for (const down of [0.47, 0.6, 0.4]) {
            for (const across of [0.3, 0.55, 0.72]) {
              const x = box.left + box.width * across
              const y = box.top + box.height * down
              const hit = document.elementFromPoint(x, y)
              const button = hit?.closest('button')
              if (hit && viewport.contains(hit) && (!button || button.matches('.landmark-model')))
                return { x, y }
            }
          }
        })
        assert.ok(start, `No draggable map surface: ${device}/${area}`)
        await page.mouse.move(start.x, start.y)
        await page.mouse.down()
        await page.mouse.move(start.x + 12, start.y)
        await page.mouse.move(start.x - remainder[0], start.y - remainder[1])
        await page.mouse.up()
        const centered = await offset()
        assert.ok(
          centered.every((delta) => Math.abs(delta) <= 1),
          `${device}/${area}: ${centered}`,
        )
      }
      await page.waitForFunction(() => {
        const element = document.querySelector('.map-scene')
        const intended = new DOMMatrix(element.style.transform)
        const painted = new DOMMatrix(getComputedStyle(element).transform)
        return Math.abs(intended.e - painted.e) + Math.abs(intended.f - painted.f) < 1
      })
      await page.waitForLoadState('networkidle')
      const tiles = page.locator('.architecture-context-layer img, .native-landscape-layer img')
      assert.ok(await tiles.count())
      await tiles.evaluateAll(async (images) => {
        await Promise.all(images.map((image) => image.decode()))
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))
      })
      let frame = await page.screenshot()
      let settled = false
      for (let attempt = 0; attempt < 8 && !settled; attempt++) {
        await page.waitForTimeout(250)
        const next = await page.screenshot()
        settled = frame.equals(next)
        frame = next
      }
      assert.ok(settled, `Map did not finish painting: ${device}/${area}`)
      shots.push([new URL(`${area}${values.fit ? '-fit' : ''}-${device}.png`, out), frame])
    }
    assert.ok(!requests.some((url) => url.includes('puyuan-original-scope')))
    await page.close()
  }
} finally {
  await browser.close()
}
for (const [file, image] of shots) await writeFile(file, image)
