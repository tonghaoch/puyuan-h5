import { expect, test } from '@playwright/test'
import { readFileSync } from 'node:fs'
import { createGeoFrame, type LngLat } from '../src/lib/geography'

test('the live illustrated fix appears without interaction, tracks, and falls back without moving the map', async ({
  page,
  context,
}) => {
  await context.grantPermissions(['geolocation'])
  await context.setGeolocation({ longitude: 120.63138012, latitude: 30.682173, accuracy: 10 })
  await page.goto('/')
  const marker = page.getByRole('img', { name: '我的大致位置' })
  await expect(marker).toBeAttached()
  await expect(page.locator('.illustrated-radius')).toHaveCount(1)
  await expect(page.locator('.geo-overview')).toHaveCount(0)
  const camera = await page.locator('.map-scene').getAttribute('style')
  const first = await marker.getAttribute('style')
  await context.setGeolocation({ longitude: 120.63090338, latitude: 30.68130516, accuracy: 10 })
  await expect(marker).not.toHaveAttribute('style', first!)
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.getByText('手绘图圈出大致位置，不作导航。')).toBeVisible()
  await context.setGeolocation({ longitude: 120.62882956, latitude: 30.67995213, accuracy: 10 })
  await expect(marker).toHaveCount(0)
  await expect(page.locator('.illustrated-radius')).toHaveCount(0)
  await expect(page.locator('.geo-user')).toBeVisible()
  await expect(page.getByText(/仅显示园区小图/)).toBeVisible()
  await expect(page.locator('.map-scene')).toHaveAttribute('style', camera!)
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('watch only the foreground guide; discard late and expired fixes; recover without polling', async ({
  page,
}) => {
  await page.clock.install()
  await page.addInitScript(() => {
    const subscriptions: { update: PositionCallback; fail: PositionErrorCallback }[] = []
    Object.defineProperty(navigator, 'geolocation', {
      value: {
        watchPosition(update: PositionCallback, fail: PositionErrorCallback) {
          const id = subscriptions.push({ update, fail }) - 1
          document.documentElement.dataset.starts = String(subscriptions.length)
          return id
        },
        clearWatch(id: number) {
          document.documentElement.dataset.lastStop = String(id)
        },
      },
    })
    window.addEventListener('test-position', (event) => {
      const { id, age = 0, error } = (event as CustomEvent).detail
      if (error) subscriptions[id]!.fail({ code: error } as GeolocationPositionError)
      else
        subscriptions[id]!.update({
          timestamp: Date.now() - age,
          coords: { latitude: 30.6828, longitude: 120.6293, accuracy: 12 },
        } as GeolocationPosition)
    })
  })
  const sample = (id: number, age = 0, error = 0) =>
    page.evaluate(
      (detail) => {
        window.dispatchEvent(new CustomEvent('test-position', { detail }))
      },
      { id, age, error },
    )
  const visible = (hidden: boolean) =>
    page.evaluate((hidden) => {
      Object.defineProperty(document, 'hidden', { value: hidden, configurable: true })
      document.dispatchEvent(new Event('visibilitychange'))
    }, hidden)
  await page.goto('/#games')
  const html = page.locator('html')
  await expect(page.getByRole('button', { name: '地图', exact: true })).toBeVisible()
  await expect(html).not.toHaveAttribute('data-starts', /.+/)
  await page.getByRole('button', { name: '地图', exact: true }).click()
  await expect(html).toHaveAttribute('data-starts', '1')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await sample(0)
  await page.getByRole('button', { name: '获取我的位置' }).click()
  const dot = page.locator('.geo-user')
  await expect(dot).toBeVisible()
  await expect(html).toHaveAttribute('data-starts', '1')
  await visible(true)
  await expect(html).toHaveAttribute('data-last-stop', '0')
  await sample(0)
  await expect(dot).toHaveCount(0)
  await visible(false)
  await expect(html).toHaveAttribute('data-starts', '2')
  await sample(0)
  await expect(dot).toHaveCount(0)
  await sample(1, 0, 3)
  await expect(page.getByText(/定位暂时超时/)).toBeVisible()
  await sample(1, 61000)
  await expect(page.getByText(/位置已过期/)).toBeVisible()
  await sample(1)
  await expect(dot).toBeVisible()
  await page.clock.fastForward(61000)
  await expect(dot).toHaveCount(0)
  await expect(page.getByText(/位置已过期/)).toBeVisible()
  await sample(1)
  await expect(dot).toBeVisible()
  await expect(html).toHaveAttribute('data-starts', '2')
  await page.getByRole('button', { name: '游戏', exact: true }).click()
  await expect(html).toHaveAttribute('data-last-stop', '1')
})

test('an unsupported geolocation API leaves the guide usable', async ({ page }) => {
  await page.addInitScript(() =>
    Object.defineProperty(navigator, 'geolocation', { value: undefined }),
  )
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.getByText(/当前环境暂不支持定位/)).toBeVisible()
  await expect(page.getByRole('button', { name: '手动请求定位' })).toHaveCount(0)
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.locator('.geo-overview')).toHaveCount(0)
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('the live marker uses smoothing for jitter and accepts a corrected distant fix immediately', async ({
  page,
}) => {
  await page.clock.install()
  await page.addInitScript(() => {
    let update: PositionCallback
    Object.defineProperty(navigator, 'geolocation', {
      value: {
        watchPosition(callback: PositionCallback) {
          update = callback
          return 1
        },
        clearWatch() {},
      },
    })
    window.addEventListener('smoothing-position', (event) => {
      update({
        timestamp: Date.now(),
        coords: (event as CustomEvent).detail,
      } as GeolocationPosition)
    })
  })
  const origin = { longitude: 120.63138012, latitude: 30.682173 }
  const point = (meters: number) => ({
    ...origin,
    longitude:
      origin.longitude +
      ((meters / (6378137 * Math.cos((origin.latitude * Math.PI) / 180))) * 180) / Math.PI,
    accuracy: 8,
  })
  const emit = (meters: number) =>
    page.evaluate(
      (coords) => window.dispatchEvent(new CustomEvent('smoothing-position', { detail: coords })),
      point(meters),
    )
  const boundary = JSON.parse(
    readFileSync(new URL('../public/geodata/boundary.geojson', import.meta.url), 'utf8'),
  )
  const frame = createGeoFrame(boundary.features[0].geometry.coordinates[0] as LngLat[])
  const expected = (meters: number) => frame.project([point(meters).longitude, origin.latitude])
  const distance = (a: readonly number[], b: readonly number[]) =>
    Math.hypot(a[0] - b[0], a[1] - b[1])
  await page.goto('/')
  await emit(4)
  await page.getByRole('button', { name: '获取我的位置' }).click()
  const marker = page.locator('.geo-user')
  await expect(marker).toBeVisible()
  const camera = await page.locator('.map-scene').getAttribute('style')
  const position = async () =>
    (await marker.getAttribute('transform'))!.match(/[-\d.]+/g)!.map(Number)
  await page.clock.runFor(1000)
  await emit(-4)
  await expect
    .poll(async () => distance(await position(), expected(0)))
    .toBeLessThan(distance(expected(-4), expected(0)) * 0.8)
  await page.clock.runFor(1000)
  await emit(50)
  await expect.poll(async () => distance(await position(), expected(50))).toBeLessThan(0.001)
  await expect(page.locator('.map-scene')).toHaveAttribute('style', camera!)
  await expect(page.getByRole('dialog')).toHaveCount(0)
})
