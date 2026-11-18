import { test, expect } from '@playwright/test'

test('all three views work, restaurant search and categories filter actual results', async ({
  page,
}) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await page.goto('/')
  await expect(page.getByRole('region', { name: /古镇示意地图/ })).toBeVisible()
  await page.getByRole('button', { name: /^寻味濮院/ }).click()
  await expect(page.locator('.food-card')).toHaveCount(4)
  await page.getByRole('button', { name: '茶馆', exact: true }).click()
  await expect(page.locator('.food-card')).toHaveCount(1)
  await page.getByRole('textbox', { name: '搜索餐厅' }).fill('不存在的餐厅')
  await expect(page.getByText('这一味，还在寻找中')).toBeVisible()
  await page.getByRole('button', { name: '查看全部餐厅', exact: true }).click()
  await expect(page.locator('.food-card')).toHaveCount(4)
  await page.getByRole('button', { name: /^风雅之约/ }).click()
  await expect(page.locator('.activity-card')).toHaveCount(5)
  await page.getByRole('button', { name: '水乡演艺', exact: true }).click()
  await expect(page.locator('.activity-card')).toHaveCount(2)
  await page.getByRole('button', { name: /^明天/ }).click()
  await expect(page.locator('.activity-card')).toHaveCount(2)
  expect(errors).toEqual([])
})

test('pins filter, open a real detail and link through to restaurant content', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '美食', exact: true }).click()
  await expect(page.locator('.map-pin')).toHaveCount(3)
  await page.getByRole('button', { name: '查看深夜食堂', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('heading', { name: '深夜食堂' })).toBeVisible()
  await dialog.getByRole('button', { name: /水巷茶事.*茶馆/ }).click()
  await expect(dialog.getByText('示例营业时间')).toBeVisible()
  await dialog.getByRole('button', { name: '在地图中查看', exact: true }).click()
  await expect(dialog).toHaveCount(0)
  await expect(page.locator('.map-pin')).toHaveCount(18)
  await expect(page.getByRole('button', { name: '查看深夜食堂', exact: true })).toBeVisible()
})

test('zoom and camera survive tab changes and pan responds to pointer drag', async ({ page }) => {
  await page.goto('/')
  const scene = page.locator('.map-scene')
  const initial = await scene.getAttribute('style')
  await page.getByRole('button', { name: '放大地图', exact: true }).click()
  await expect(scene).not.toHaveAttribute('style', initial!)
  const zoomed = await scene.getAttribute('style')
  await page.getByRole('button', { name: /^寻味濮院/ }).click()
  await page.getByRole('button', { name: /^游园地图/ }).click()
  await expect(scene).toHaveAttribute('style', zoomed!)
  const viewport = page.getByRole('region', { name: /古镇示意地图/ })
  const bounds = (await viewport.boundingBox())!
  const x = bounds.x + bounds.width * 0.55,
    y = bounds.y + bounds.height * 0.55
  await page.mouse.move(x, y)
  await page.mouse.down()
  await page.mouse.move(x + 60, y + 40, { steps: 6 })
  await page.mouse.up()
  await expect(scene).not.toHaveAttribute('style', zoomed!)
  await page.getByRole('button', { name: '重置地图视野' }).click()
  await expect(scene).toHaveAttribute('style', initial!)
})

test('favorites persist after reload and can be removed in the collection', async ({ page }) => {
  await page.goto('/#food')
  await page.getByRole('button', { name: '收藏水巷茶事', exact: true }).click()
  await expect(page.getByRole('button', { name: '取消收藏水巷茶事', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  )
  await page.reload()
  await page.getByRole('button', { name: '我的收藏', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByText('水巷茶事', { exact: true })).toBeVisible()
  await dialog.getByRole('button', { name: '取消收藏水巷茶事', exact: true }).click()
  await expect(dialog.getByText(/还没有收藏/)).toBeVisible()
})

test('direct detail links close locally, browser Back closes an opened detail', async ({
  page,
}) => {
  await page.goto('/#activities/activity/waterside-opera')
  await expect(page.getByRole('dialog', { name: '水岸听曲' })).toBeVisible()
  await page.getByRole('button', { name: '关闭弹窗' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page).toHaveURL(/#activities$/)
  await page.getByRole('button', { name: '查看水岸听曲详情', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.goBack()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.getByRole('navigation', { name: '主要导航' })).toBeVisible()
})

test('device geolocation remains separate from the uncalibrated scene', async ({
  page,
  context,
}) => {
  await context.grantPermissions(['geolocation'])
  await context.setGeolocation({ latitude: 30, longitude: 120, accuracy: 18 })
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await expect(page.getByRole('dialog').getByText('已获取设备位置', { exact: true })).toBeVisible()
  await expect(page.getByText(/设备报告精度约 18 米/)).toBeVisible()
  await expect(page.getByText(/暂不在示意图上显示定位点/)).toBeVisible()
  await expect(page.locator('.map-pin')).toHaveCount(18)
})

test('permission denial stops prompting and keeps browsing available', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'geolocation', {
      configurable: true,
      value: {
        getCurrentPosition: (_success: unknown, failure: (error: { code: number }) => void) =>
          failure({ code: 1 }),
      },
    })
  })
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await expect(page.getByText(/定位权限未开启/)).toBeVisible()
  await expect(page.getByRole('button', { name: '重新获取位置' })).toHaveCount(0)
  await page.getByRole('button', { name: '继续浏览地图' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('reduced motion is respected and viewport never overflows horizontally', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/')
  await expect(page.getByRole('button', { name: '开启动效' })).toHaveAttribute(
    'aria-pressed',
    'false',
  )
  await expect(page.locator('.map-viewport')).toHaveClass(/motion-paused/)
  for (const name of [/^游园地图/, /^寻味濮院/, /^风雅之约/]) {
    await page.getByRole('button', { name }).click()
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    )
    expect(overflow).toBe(false)
  }
})

test('two-finger touch zooms the scene on mobile', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Touch gesture is exercised in the mobile browser project')
  await page.goto('/')
  const scene = page.locator('.map-scene')
  const before = await scene.getAttribute('style')
  const client = await page.context().newCDPSession(page)
  const point = (id: number, x: number) => ({ id, x, y: 420, radiusX: 2, radiusY: 2 })
  await client.send('Input.dispatchTouchEvent', {
    type: 'touchStart',
    touchPoints: [point(0, 150), point(1, 230)],
  })
  for (let distance = 10; distance <= 50; distance += 10) {
    await client.send('Input.dispatchTouchEvent', {
      type: 'touchMove',
      touchPoints: [point(0, 150 - distance), point(1, 230 + distance)],
    })
  }
  await client.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
  await expect(scene).not.toHaveAttribute('style', before!)
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('detail keyboard focus stays in the dialog and Escape restores the opener', async ({
  page,
}) => {
  await page.goto('/#activities')
  const opener = page.getByRole('button', { name: '查看水岸听曲详情', exact: true })
  await opener.click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press('Tab')
    expect(await page.evaluate(() => !!document.activeElement?.closest('[role="dialog"]'))).toBe(
      true,
    )
  }
  await page.keyboard.press('Escape')
  await expect(dialog).toHaveCount(0)
  await expect(opener).toBeFocused()
})

test('near-park GPS is plotted only on the attributed geographic overview', async ({
  page,
  context,
}) => {
  await context.grantPermissions(['geolocation'])
  await context.setGeolocation({ latitude: 30.6828922, longitude: 120.6296382, accuracy: 10 })
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.locator('.geo-map')).toBeVisible()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await expect(page.locator('.geo-user')).toBeVisible()
  await expect(page.getByText('你的位置在公开资料记录的园区范围内。')).toBeVisible()
  await expect(page.getByRole('link', { name: '© OpenStreetMap contributors' })).toBeVisible()
  expect(Number(await page.locator('.geo-accuracy').getAttribute('r'))).toBeGreaterThan(0)
  await expect(page.locator('.map-scene .geo-user')).toHaveCount(0)
})

test('close button stays available when a long dialog is scrolled', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await expect(page.locator('.geo-map')).toBeVisible()
  await page.locator('.dialog-content').evaluate((el) => {
    el.scrollTop = el.scrollHeight
  })
  await expect(page.getByRole('button', { name: '关闭弹窗' })).toBeInViewport()
  await page.getByRole('button', { name: '关闭弹窗' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('navigation is at the bottom in both desktop preview and mobile', async ({ page }) => {
  await page.goto('/')
  const shell = (await page.locator('.app-shell').boundingBox())!
  const nav = (await page.getByRole('navigation', { name: '主要导航' }).boundingBox())!
  expect(shell.width).toBeLessThanOrEqual(480)
  expect(Math.abs(nav.x - shell.x)).toBeLessThan(3)
  expect(Math.abs(nav.y + nav.height - shell.y - shell.height)).toBeLessThan(3)
  expect(nav.y).toBeGreaterThan(shell.height * 0.8)
  await page.getByRole('button', { name: /^寻味濮院/ }).click()
  await expect(page.getByRole('navigation', { name: '主要导航' })).toBeInViewport()
})

test('reference and illustration share geometry, real map and imagery share georeferenced geometry', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('.map-art')).toHaveAttribute('src', '/art/puyuan-layered-ground.webp')
  const initial = await page.locator('.map-scene').getAttribute('style')
  await page.getByRole('button', { name: '原图对照', exact: true }).click()
  await expect(page.locator('.map-art')).toHaveAttribute('src', '/art/puyuan-original-scope.webp')
  await expect(page.locator('.map-scene')).toHaveAttribute('style', initial!)
  await page.getByRole('button', { name: '真实路网', exact: true }).click()
  await expect(page.locator('.real-road').first()).toBeVisible()
  await expect(page.locator('.geo-landmark')).toHaveCount(8)
  await page.getByRole('textbox', { name: '搜索地图地点或活动' }).fill('福山塔')
  await expect(page.locator('.geo-landmark')).toHaveCount(1)
  await page.getByRole('button', { name: '查看地图资料：福山塔', exact: true }).click()
  await expect(page.getByRole('dialog').getByRole('heading', { name: '福山塔' })).toBeVisible()
  await page.getByRole('button', { name: '继续看地图' }).click()
  await page.getByRole('button', { name: '影像核对', exact: true }).click()
  await expect(page.locator('.real-map-scene image')).toHaveAttribute(
    'href',
    '/geodata/imagery-reference.jpg',
  )
  expect(Number(await page.locator('.real-map-scene image').getAttribute('width'))).toBeGreaterThan(
    500,
  )
  await expect(page.locator('.geo-landmark')).toHaveCount(8)
  await page.getByRole('button', { name: '手绘导览', exact: true }).click()
  await expect(page.locator('.map-scene')).toHaveAttribute('style', initial!)
})

test('acquired GPS can be opened on the main real map without placing it on the illustration', async ({
  page,
  context,
}) => {
  await context.grantPermissions(['geolocation'])
  await context.setGeolocation({ latitude: 30.6828922, longitude: 120.6296382, accuracy: 10 })
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await page.getByRole('button', { name: '在真实路网中查看位置' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('.main-user-position')).toBeVisible()
  await expect(page.getByRole('button', { name: '真实路网', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  )
  await page.getByRole('button', { name: '影像核对', exact: true }).click()
  await expect(page.locator('.main-user-position')).toBeVisible()
  await page.getByRole('button', { name: '手绘导览', exact: true }).click()
  await expect(page.locator('.main-user-position')).toHaveCount(0)
})

test('bottom sheet can be dragged down to dismiss', async ({ page }) => {
  await page.goto('/#activities/activity/waterside-opera')
  const handle = (await page.getByRole('button', { name: '收起弹层' }).boundingBox())!
  await page.mouse.move(handle.x + handle.width / 2, handle.y + 12)
  await page.mouse.down()
  await page.mouse.move(handle.x + handle.width / 2, handle.y + 125, { steps: 8 })
  await page.mouse.up()
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('detailed buildings are independent, inspectable and selectable', async ({ page }) => {
  await page.goto('/')
  expect(await page.locator('.landmark-model').count()).toBeGreaterThan(0)
  expect(await page.locator('.landmark-model').count()).toBeLessThanOrEqual(19)
  await page.getByRole('button', { name: '细看古建', exact: true }).click()
  await expect(page.locator('.building-inspection')).toContainText('游客中心')
  const model = page.getByRole('button', { name: '查看游客中心建筑详情', exact: true })
  await expect(model).toBeInViewport()
  await model.click({ position: { x: 35, y: 100 } })
  await expect(
    page.getByRole('dialog').getByRole('heading', { name: '游客中心', exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: '关闭弹窗' }).click()
  await page.getByRole('button', { name: '下一处建筑' }).click()
  await expect(page.locator('.building-inspection')).toContainText('寺塔')
  const camera = await page.locator('.map-scene').getAttribute('style')
  await page.getByRole('button', { name: '原图对照', exact: true }).click()
  await expect(page.locator('.landmark-model')).toHaveCount(0)
  await expect(page.locator('.map-scene')).toHaveAttribute('style', camera!)
  await page.getByRole('button', { name: '手绘导览', exact: true }).click()
  expect(await page.locator('.landmark-model').count()).toBeGreaterThan(0)
  expect(await page.locator('.landmark-model').count()).toBeLessThanOrEqual(19)
})

test('dragging on a large building pans the map without opening its detail', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '细看古建', exact: true }).click()
  const model = (await page
    .getByRole('button', { name: '查看游客中心建筑详情', exact: true })
    .boundingBox())!
  const scene = page.locator('.map-scene')
  const before = await scene.getAttribute('style')
  const x = model.x + 35,
    y = model.y + 100
  await page.mouse.move(x, y)
  await page.mouse.down()
  await page.mouse.move(x + 65, y + 30, { steps: 8 })
  await page.mouse.up()
  await expect(scene).not.toHaveAttribute('style', before!)
  await expect(page.getByRole('dialog')).toHaveCount(0)
})

test('panning beyond the former crop reveals meadow and can return to town', async ({ page }) => {
  await page.goto('/')
  const scene = page.locator('.map-scene')
  const initial = await scene.getAttribute('style')
  await page.getByRole('region', { name: /古镇示意地图/ }).focus()
  for (let i = 0; i < 22; i++) await page.keyboard.press('ArrowRight')
  await expect(page.getByRole('button', { name: '回到古镇', exact: true })).toBeVisible()
  await expect(page.locator('.meadow-backdrop')).toHaveCSS('background-image', /meadow-tile\.svg/)
  const view = (await page.locator('.map-viewport').boundingBox())!
  const image = (await page.locator('.map-art').boundingBox())!
  expect(image.x + image.width).toBeLessThan(view.x + 35)
  expect(await page.locator('.meadow-layer img').count()).toBeLessThan(25)
  await page.getByRole('button', { name: '回到古镇', exact: true }).click()
  await expect(scene).toHaveAttribute('style', initial!)
  await page.getByRole('button', { name: '真实路网', exact: true }).click()
  await expect(page.locator('.meadow-backdrop')).toHaveCount(0)
  await expect(page.locator('.landmark-model')).toHaveCount(0)
})

test('all landmark groups can be selected from the architecture directory', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '细看古建', exact: true }).click()
  await page.getByRole('button', { name: '选择要细看的建筑' }).click()
  const directory = page.getByRole('region', { name: '古建目录' })
  await expect(directory.locator('div > button')).toHaveCount(19)
  await directory.getByRole('button', { name: /龙湾街美食广场/ }).click()
  await expect(directory).toHaveCount(0)
  await expect(page.locator('.building-inspection')).toContainText('龙湾街美食广场')
  await expect(page.locator('[data-model-id="longwan-dining"]')).toBeInViewport()
  await expect(page.locator('[data-model-id="longwan-dining"] img')).toHaveAttribute(
    'src',
    '/art/landmarks/longwan-dining.webp',
  )
  await page.getByRole('button', { name: '选择要细看的建筑' }).click()
  await directory.getByRole('button', { name: /北更楼/ }).click()
  await expect(page.locator('.building-inspection')).toContainText('北更楼')
  await expect(page.locator('[data-model-id="north-watchtower"]')).toBeInViewport()
})

test('background architecture changes detail level and stays out of geographic views', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('.architecture-context-layer img').first()).toBeVisible()
  expect(await page.locator('.architecture-context-layer img').count()).toBeLessThanOrEqual(24)
  await expect(page.locator('.architecture-context-layer img').first()).toHaveAttribute(
    'src',
    /preview\.webp$/,
  )
  await page.getByRole('button', { name: '细看古建', exact: true }).click()
  const images = page.locator('.architecture-context-layer img')
  await expect(images.first()).toHaveAttribute('src', /(?<!preview)\.webp$/)
  await page.getByRole('button', { name: '真实路网', exact: true }).click()
  await expect(page.locator('.architecture-context-layer')).toHaveCount(0)
  await expect(page.locator('.landmark-layer')).toHaveCount(0)
  await page.getByRole('button', { name: '手绘导览', exact: true }).click()
  await expect(page.locator('.architecture-context-layer')).toBeVisible()
})
