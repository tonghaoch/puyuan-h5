import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { chromium } from '@playwright/test'
import { parseArgs } from 'node:util'

const root = new URL('../', import.meta.url)
const read = async (path) => JSON.parse(await readFile(new URL(path, root), 'utf8'))
const { sites, background } = await read('src/data/street-houses.json')
const { sourceOffset, scene: sceneSize } = await read('src/data/reference-map.json')
const { bridges, groundBeds } = await read('src/data/town-landscape.json')
const { paleBlocks } = await read('src/data/town-completions.json')
const { values, positionals } = parseArgs({
  options: {
    out: { type: 'string', default: 'artifacts/island-review' },
    fit: { type: 'boolean', default: false },
    details: { type: 'boolean', default: false },
    box: { type: 'string', multiple: true, default: [] },
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
  ...Object.fromEntries(groundBeds.map(({ id, points }) => [id, [{ replace: [points] }]])),
  ...Object.fromEntries(
    paleBlocks.map(({ id, units }) => [id, [{ replace: units.map(({ top }) => top) }]]),
  ),
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
const selected =
  positionals.length || values.box.length
    ? positionals.map((name) => {
        assert.ok(Object.hasOwn(named, name), name)
        return [name, named[name]]
      })
    : Object.entries(background)
if (values.details)
  assert.ok(
    positionals.length && !values.fit && !values.box.length,
    'Specify landmarks for --details',
  )
for (const value of values.box) {
  assert.match(
    value,
    /^\d+,\d+,\d+,\d+$/,
    'Use --box left,top,right,bottom in illustration coordinates',
  )
  const [left, top, right, bottom] = value.split(',').map(Number)
  assert.ok(
    left < right &&
      top < bottom &&
      left + sourceOffset.x >= 0 &&
      top + sourceOffset.y >= 0 &&
      right + sourceOffset.x <= sceneSize.width &&
      bottom + sourceOffset.y <= sceneSize.height,
    `Box outside the scene: ${value}`,
  )
  selected.push([
    `cell-${[left, top, right, bottom].join('-')}`,
    [
      {
        replace: [
          [
            [left, top],
            [right, bottom],
          ],
        ],
      },
    ],
  ])
}
const shots = []
async function stableFrame(page, name) {
  let previous = await page.screenshot()
  for (let attempt = 0; attempt < 8; attempt++) {
    await page.waitForTimeout(250)
    const next = await page.screenshot()
    if (previous.equals(next)) return next
    previous = next
  }
  assert.fail(`View did not finish painting: ${name}`)
}
await mkdir(out, { recursive: true })
const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const browser = await chromium.launch({
  args: values.details ? ['--disable-gpu'] : [],
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
        await page.waitForFunction(() => {
          const scene = document.querySelector('.map-scene')
          const target = new DOMMatrix(scene.style.transform)
          const actual = new DOMMatrix(getComputedStyle(scene).transform)
          return Math.abs(target.e - actual.e) + Math.abs(target.f - actual.f) < 1
        })
        await page.waitForLoadState('networkidle')
        shots.push([
          new URL(`${area}-inspection-${device}.png`, out),
          await stableFrame(page, `${device}/${area}/inspection`),
        ])
        await page.getByRole('button', { name: `查看${model.name}建筑详情` }).click()
        const hero = page.getByRole('dialog').locator('.detail-hero img')
        await hero.evaluate((image) => image.decode())
        assert.equal(await hero.getAttribute('src'), model.heroAsset)
        await page.waitForFunction(() => {
          const hero = document.querySelector('[role="dialog"] .detail-hero img')
          if (!hero) return false
          const box = hero.getBoundingClientRect()
          const foreground = document.elementFromPoint(
            box.x + box.width / 2,
            box.y + box.height / 2,
          )
          return (
            box.height > 0 &&
            foreground?.closest('.detail-hero') === hero.closest('.detail-hero') &&
            Number(getComputedStyle(hero.closest('.dialog-backdrop')).opacity) >= 0.99
          )
        })
        shots.push([
          new URL(`${area}-detail-${device}.png`, out),
          await stableFrame(page, `${device}/${area}/detail`),
        ])
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
      const frame = await stableFrame(page, `${device}/${area}`)
      shots.push([new URL(`${area}${values.fit ? '-fit' : ''}-${device}.png`, out), frame])
    }
    assert.ok(!requests.some((url) => url.includes('puyuan-original-scope')))
    await page.close()
  }
} finally {
  await browser.close()
}
for (const [file, image] of shots) await writeFile(file, image)
