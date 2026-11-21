import { expect, test } from '@playwright/test'

test('the walk preview moves the seal, not the camera, and recenters only on request', async ({
  page,
}) => {
  await page.addInitScript(() => {
    for (const method of ['getCurrentPosition', 'watchPosition']) {
      Object.defineProperty(navigator.geolocation, method, {
        value: () => {
          document.documentElement.dataset.locationRequested = 'yes'
        },
      })
    }
  })
  await page.goto('/?preview=walk')
  const seal = page.getByRole('img', { name: '我的位置（模拟）' })
  const scene = page.locator('.map-scene')
  const viewport = page.locator('.map-viewport')
  await expect(seal.locator('span')).toBeInViewport()
  const initial = await scene.getAttribute('style')
  const start = await seal.getAttribute('style')
  await expect(seal).not.toHaveAttribute('style', start!)
  await expect(scene).toHaveAttribute('style', initial!)
  await page.getByRole('button', { name: '暂停模拟步行' }).click()
  await viewport.press('=')
  await viewport.press('ArrowLeft')
  const before = await scene.getAttribute('style')
  const scale = () =>
    scene.evaluate((element) => new DOMMatrix(getComputedStyle(element).transform).a)
  const beforeScale = await scale()
  await page.getByRole('button', { name: '回到我的位置' }).click()
  await expect(scene).not.toHaveAttribute('style', before!)
  expect(await scale()).toBe(beforeScale)
  const bounds = (await viewport.boundingBox())!
  await expect
    .poll(async () => {
      const mark = (await seal.locator('span').boundingBox())!
      return Math.hypot(
        mark.x + mark.width / 2 - bounds.x - bounds.width / 2,
        mark.y + mark.height / 2 - bounds.y - bounds.height / 2,
      )
    })
    .toBeLessThan(2)
  await page.locator('.language-button').click()
  await expect(page.getByRole('img', { name: 'My location (simulated)' })).toHaveText('Me')
  await page.getByRole('button', { name: 'Resume demo walk' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('html')).not.toHaveAttribute('data-location-requested', 'yes')
})

test('a reduced-motion preview steps manually; the regular map has no fake location', async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/?preview=walk')
  const seal = page.getByRole('img', { name: '我的位置（模拟）' })
  const start = await seal.getAttribute('style')
  await page.getByRole('button', { name: '模拟走一步' }).click()
  await expect(seal).not.toHaveAttribute('style', start!)
  await page.goto('/')
  await expect(page.locator('.walk-preview-control, .walker-anchor')).toHaveCount(0)
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.getByRole('dialog', { name: '我的位置' })).toBeVisible()
})
