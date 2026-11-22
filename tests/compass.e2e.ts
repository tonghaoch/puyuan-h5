import { expect, test, type Page } from '@playwright/test'

async function pointPhone(
  page: Page,
  values: { alpha?: number; absolute?: boolean; webkitCompassHeading?: number },
) {
  await page.evaluate((values) => {
    window.dispatchEvent(
      Object.assign(new Event('deviceorientation'), { beta: 0, gamma: 0, ...values }),
    )
  }, values)
}

const fixed = { longitude: 120.63138012, latitude: 30.682173, accuracy: 10 }
test.use({ permissions: ['geolocation'], geolocation: fixed })

test('rotate at a fixed GPS position: both fans follow the phone, not the camera or a walking course', async ({
  page,
  context,
}) => {
  await page.clock.install()
  await page.addInitScript(() => {
    Object.defineProperty(DeviceOrientationEvent, 'requestPermission', { value: undefined })
    Object.defineProperty(screen.orientation, 'angle', { value: 0, configurable: true })
  })
  await page.goto('/')
  const marker = page.locator('.walker-anchor')
  const fan = marker.locator('.compass-fan')
  await expect(marker).toBeAttached()
  const camera = await page.locator('.map-scene').getAttribute('style')
  const position = await marker.getAttribute('style')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  const mini = page.locator('.geo-user .compass-fan')
  await pointPhone(page, { alpha: 0, absolute: false })
  await expect(fan).toHaveCount(0)
  await pointPhone(page, { alpha: 0, absolute: true })
  await expect(mini).toHaveAttribute('transform', 'rotate(0)')
  const north = await fan.getAttribute('transform')
  await pointPhone(page, { alpha: 270, absolute: true })
  await expect(mini).toHaveAttribute('transform', 'rotate(90)')
  await expect(fan).not.toHaveAttribute('transform', north!)
  await pointPhone(page, { alpha: 30, absolute: false })
  await expect(mini).toHaveAttribute('transform', 'rotate(90)')
  await expect(marker).toHaveAttribute('style', position!)
  await expect(page.locator('.map-scene')).toHaveAttribute('style', camera!)
  await page.evaluate(() => {
    Object.defineProperty(screen.orientation, 'angle', { value: 90, configurable: true })
    screen.orientation.dispatchEvent(new Event('change'))
  })
  await expect(mini).toHaveAttribute('transform', 'rotate(180)')
  await page.clock.fastForward(21_000)
  await expect(fan).toHaveCount(0)
  await expect(marker).toBeAttached()
  await context.setGeolocation({ longitude: 120.62882956, latitude: 30.67995213, accuracy: 10 })
  await expect(marker).toHaveCount(0)
  await expect(page.getByText(/仅显示园区小图/)).toBeVisible()
  await pointPhone(page, { alpha: 270, absolute: true })
  await expect(mini).toHaveAttribute('transform', 'rotate(180)')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await pointPhone(page, { alpha: 20, absolute: true })
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.locator('.geo-user')).toBeVisible()
  await expect(mini).toHaveCount(0)
})

for (const decision of ['granted', 'denied'] as const) {
  test(`permission is requested only on tap; ${decision} does not affect the location`, async ({
    page,
  }) => {
    await page.addInitScript((decision) => {
      DeviceOrientationEvent.requestPermission = async () => {
        document.documentElement.dataset.compassGesture = String(navigator.userActivation.isActive)
        return decision
      }
    }, decision)
    await page.goto('/')
    const marker = page.locator('.walker-anchor')
    await expect(marker).toBeAttached()
    await page.getByRole('button', { name: '获取我的位置' }).click()
    await pointPhone(page, { webkitCompassHeading: 25 })
    await expect(marker.locator('.compass-fan')).toHaveCount(0)
    await expect(page.locator('html')).not.toHaveAttribute('data-compass-gesture')
    await page.getByRole('button', { name: '开启手机朝向' }).click()
    await expect(page.locator('html')).toHaveAttribute('data-compass-gesture', 'true')
    await pointPhone(page, { webkitCompassHeading: 25 })
    if (decision === 'granted') {
      await expect(page.locator('.geo-user .compass-fan')).toHaveAttribute(
        'transform',
        'rotate(25)',
      )
      await expect(marker.locator('.compass-fan')).toBeAttached()
    } else {
      await expect(page.getByText('未获朝向权限，仍可查看位置。')).toBeVisible()
      await expect(page.locator('.compass-fan')).toHaveCount(0)
    }
    await expect(marker).toBeAttached()
    await expect(page.getByRole('dialog')).toHaveCount(0)
  })
}
