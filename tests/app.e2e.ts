import { test, expect, type Locator } from '@playwright/test'

test('four event sections, dinner search, and day two programme', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))
  await page.goto('/')
  await expect(page.getByRole('region', { name: /古镇导览/ })).toBeVisible()
  await expect(page.locator('.main-nav button')).toHaveCount(4)
  await page.getByRole('button', { name: '餐厅', exact: true }).click()
  await expect(page.locator('.dinner-row')).toHaveCount(10)
  await page.getByRole('button', { name: '特色风味' }).click()
  await expect(page.locator('.dinner-row')).toHaveCount(3)
  await expect(page.getByRole('status')).toContainText('3 家推荐')
  await page.getByRole('searchbox', { name: '搜索餐厅' }).fill('不存在的餐厅')
  await expect(page.getByText('没有找到这家餐厅')).toBeVisible()
  await page.getByRole('button', { name: /查看全部餐厅/ }).click()
  await expect(page.getByRole('searchbox', { name: '搜索餐厅' })).toBeFocused()
  await expect(page.locator('.dinner-row')).toHaveCount(10)
  await page.getByRole('button', { name: '行程', exact: true }).click()
  await page.getByRole('button', { name: /看第二天/ }).click()
  await expect(page.getByRole('heading', { name: '慢游水乡，返程' })).toBeInViewport()
  await page.getByRole('button', { name: /回第一天/ }).click()
  await expect(page.getByRole('heading', { name: '到濮院，入戏' })).toBeInViewport()
  await page.getByRole('button', { name: /看第二天/ }).click()
  await page.getByRole('link', { name: '查看体验' }).click()
  await expect(page.locator('.directory-row')).toHaveCount(12)
  await page.getByRole('link', { name: '演出', exact: true }).click()
  await expect(page.getByAltText(/演艺时间表微信小程序码/)).toBeVisible()
  expect(errors).toEqual([])
})

test('separate lawn tokens open the indicated challenge without leaving the map', async ({
  page,
}) => {
  await page.goto('/')
  const flag = page.getByRole('button', { name: '游戏：大草坪 · 蹴鞠达人' })
  const hammer = page.getByRole('button', { name: '游戏：大草坪 · 一锤定音' })
  await expect(page.locator('.quest-pin')).toHaveCount(8)
  const scene = page.locator('.map-scene')
  await page.getByRole('button', { name: '放大地图' }).click()
  await expect(flag).toBeInViewport()
  const camera = await scene.getAttribute('style')
  const flagIcon = flag.locator('svg')
  const originalBounds = await flagIcon.boundingBox()
  await flag.hover()
  expect(await flagIcon.boundingBox()).toEqual(originalBounds)
  await flag.click()
  const sheet = page.getByRole('dialog')
  await expect(sheet.getByRole('heading', { name: '蹴鞠达人' })).toBeVisible()
  await expect(sheet).toContainText('全队总分超过 250 分')
  await expect(sheet).not.toContainText('一锤定音')
  await expect(page).toHaveURL(/#map\/task\/cuju$/)
  expect(await flagIcon.boundingBox()).toEqual(originalBounds)
  await expect(page.locator('.app-shell')).toHaveJSProperty('inert', true)
  await expect(page.locator('.map-page')).toBeVisible()
  await expect(sheet).toBeFocused()
  const height = page.viewportSize()!.height
  await expect
    .poll(async () => {
      const bounds = (await sheet.boundingBox())!
      return Math.abs(bounds.y + bounds.height - height)
    })
    .toBeLessThan(2)
  expect((await sheet.boundingBox())!.y).toBeGreaterThan(height * 0.25)
  await page.goBack()
  await expect(sheet).toHaveCount(0)
  await expect(flag).toBeFocused()
  await expect(scene).toHaveAttribute('style', camera!)
  await expect(flag).toBeInViewport()
  await hammer.click()
  await expect(sheet.getByRole('heading', { name: '一锤定音' })).toBeVisible()
  await expect(sheet).toContainText('全队合计敲破超过 12 个气球。')
  await expect(sheet).not.toContainText('蹴鞠达人')
  await expect(page).toHaveURL(/#map\/task\/hammer$/)
  await page.keyboard.press('Escape')
  await expect(hammer).toBeFocused()
  await page.goto('/#games/task/treasure')
  await page.getByRole('button', { name: '在导览中查看' }).click()
  const pin = page.getByRole('button', { name: /^游戏：珍宝馆/ })
  await expect(pin).toBeInViewport()
  const viewport = (await page.locator('.map-viewport').boundingBox())!
  const anchor = (await page.locator('[data-marker="quest:treasure"]').boundingBox())!
  expect(Math.abs(viewport.x + viewport.width / 2 - anchor.x)).toBeLessThan(1)
  await page.getByRole('button', { name: '路网', exact: true }).click()
  await expect(page.locator('.quest-pin')).toHaveCount(0)
})

test('legacy lawn links open only the original game and dismiss locally', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  const sheet = page.getByRole('dialog')
  for (const [suffix, name] of [
    ['', '蹴鞠达人'],
    ['/0', '蹴鞠达人'],
    ['/1', '一锤定音'],
  ] as const) {
    await page.goto(`/#map/task/lawn${suffix}`)
    await expect(sheet).toHaveAccessibleName(name)
    await expect(sheet.getByRole('heading', { name, exact: true })).toBeVisible()
    await expect(sheet).not.toContainText(name === '蹴鞠达人' ? '一锤定音' : '蹴鞠达人')
  }
  await page.reload()
  await expect(sheet.getByRole('heading', { name: '一锤定音' })).toBeVisible()
  await sheet.getByRole('button', { name: '关闭弹窗' }).click()
  await expect(page).toHaveURL(/#map$/)
  await expect(sheet).toHaveCount(0)
  await expect(page.getByRole('button', { name: '游戏：大草坪 · 一锤定音' })).toBeVisible()
})

test('each lawn game has its own handbook entry and locates its own pin', async ({ page }) => {
  await page.goto('/#games')
  for (const [id, name, number, other] of [
    ['cuju', '蹴鞠达人', '03', '一锤定音'],
    ['hammer', '一锤定音', '04', '蹴鞠达人'],
  ] as const) {
    await expect(page.locator('.quest-row')).toHaveCount(8)
    const entry = page.getByRole('link', { name: new RegExp(name) })
    await expect(entry).toHaveAccessibleName(`${number} 大草坪 ${name}`)
    await entry.click()
    await expect(page).toHaveURL(new RegExp(`#games/task/${id}$`))
    const detail = page.getByRole('region', { name: '游戏详情' })
    await expect(detail.getByRole('heading', { name, exact: true })).toBeVisible()
    await expect(detail).not.toContainText(other)
    await detail.getByRole('button', { name: '在导览中查看' }).click()
    const viewport = (await page.locator('.map-viewport').boundingBox())!
    const anchor = (await page.locator(`[data-marker="quest:${id}"]`).boundingBox())!
    expect(Math.abs(viewport.x + viewport.width / 2 - anchor.x)).toBeLessThan(1)
    expect(Math.abs(viewport.y + viewport.height * 0.45 - anchor.y)).toBeLessThan(1)
    await page.getByRole('button', { name: '游戏', exact: true }).click()
  }
})

test('quest and NPC artwork scales in proportion to the map', async ({ page }) => {
  await page.goto('/')
  const artwork = page.locator('.map-art, .field-pin > svg')
  await expect(artwork).toHaveCount(14)
  const firstIcon = page.locator('.field-pin > svg').first()
  await expect.poll(async () => (await firstIcon.boundingBox())?.width ?? 0).toBeCloseTo(26, 1)
  const sizes = () =>
    artwork.evaluateAll((elements) =>
      elements.map((element) => {
        const { width, height } = element.getBoundingClientRect()
        return { width, height }
      }),
    )
  const initial = await sizes()
  for (const [action, ratio] of [
    ['放大地图', 1.25],
    ['放大地图', 1.25 ** 2],
    ['缩小地图', 1.25],
    ['重置地图视野', 1],
    ['缩小地图', 0.8],
  ] as const) {
    await page.getByRole('button', { name: action }).click()
    const current = await sizes()
    for (const [index, original] of initial.entries()) {
      expect(current[index]!.width / original.width).toBeCloseTo(ratio, 2)
      expect(current[index]!.height / original.height).toBeCloseTo(ratio, 2)
    }
  }
})

test('all thirteen pins stay directly above their map points during pan, zoom and layer changes', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  const markers = page.locator('.field-marker')
  await expect(markers).toHaveCount(13)
  const checkPins = async () => {
    await expect
      .poll(() =>
        markers.evaluateAll((elements) => {
          const scene = document.querySelector<HTMLElement>('.map-scene')!
          const rect = scene.getBoundingClientRect()
          const scale = rect.width / scene.offsetWidth
          return elements.flatMap((element) => {
            const marker = element as HTMLElement
            const anchor = marker.getBoundingClientRect()
            const expectedX = rect.x + parseFloat(marker.style.left) * scale
            const expectedY = rect.y + parseFloat(marker.style.top) * scale
            if (Math.hypot(anchor.x - expectedX, anchor.y - expectedY) > 0.1)
              return [marker.dataset.marker]
            const button = marker.querySelector('button')!
            const icon = button.querySelector('svg')!.getBoundingClientRect()
            if (Math.abs(icon.x + icon.width / 2 - expectedX) > 0.1 || icon.bottom > expectedY)
              return [marker.dataset.marker]
            const bounds = button.getBoundingClientRect()
            const x = bounds.x + bounds.width / 2,
              y = bounds.y + bounds.height / 2
            const hit = document.elementFromPoint(x, y)?.closest('.field-pin')
            return hit && hit !== button ? [marker.dataset.marker] : []
          })
        }),
      )
      .toEqual([])
  }
  const gaps = () =>
    markers.evaluateAll((elements) =>
      elements.map((element) => {
        const icon = element.querySelector('.field-pin > svg')!.getBoundingClientRect()
        return (element.getBoundingClientRect().y - icon.bottom) / icon.height
      }),
    )
  const initialGaps = await gaps()
  const viewport = page.getByRole('region', { name: /古镇导览/ })
  for (let step = 0; step < 5; step++) {
    await viewport.press('ArrowRight')
    await viewport.press('ArrowUp')
    await page.getByRole('button', { name: '古镇地点', exact: true }).click()
    await checkPins()
    for (const [index, gap] of (await gaps()).entries())
      expect(gap).toBeCloseTo(initialGaps[index]!, 2)
    await page.getByRole('button', { name: '放大地图' }).click()
  }
})

test('five NPC markers show roaming areas; the roaming constable has no invented pin', async ({
  page,
}) => {
  await page.goto('/')
  const layers = page.getByRole('group', { name: '地图图层' })
  await layers.getByRole('button', { name: '江湖令牌' }).click()
  await layers.getByRole('button', { name: '行走 NPC' }).click()
  await page.getByRole('button', { name: '游戏', exact: true }).click()
  await page.getByRole('link', { name: '游走 NPC' }).click()
  await expect(page.getByRole('button', { name: '查看活动范围' })).toHaveCount(5)
  await page
    .locator('article')
    .filter({ has: page.getByRole('heading', { name: '蒙面大侠' }) })
    .getByRole('button')
    .click()
  await expect(page.locator('.npc-pin')).toHaveCount(5)
  await expect(layers.getByRole('button', { pressed: true })).toHaveText(['行走 NPC'])
  await expect(page.getByRole('button', { name: /游走 NPC：巡捕/ })).toHaveCount(0)
  const pin = page.getByRole('button', { name: /游走 NPC：蒙面大侠/ })
  await expect(pin).toBeInViewport()
  await pin.click()
  const card = page.getByRole('dialog', { name: '蒙面大侠' })
  await expect(card.getByText('ID 设计公寓附近')).toBeVisible()
  await expect(card.getByText(/不是实时位置/)).toBeVisible()
  await page.goBack()
  await expect(pin).toBeFocused()
  await page.getByRole('button', { name: '路网', exact: true }).click()
  await expect(page.locator('.field-marker')).toHaveCount(0)
})

test('three independent map toggles control markers in every combination', async ({ page }) => {
  await page.goto('/')
  const layers = page.getByRole('group', { name: '地图图层' })
  const names = ['江湖令牌', '行走 NPC', '古镇地点']
  await expect(layers.getByRole('button')).toHaveText(names)
  const check = async (quest: boolean, npc: boolean, places: boolean) => {
    const enabled = [quest, npc, places]
    await expect(layers.getByRole('button', { pressed: true })).toHaveText(
      names.filter((_, index) => enabled[index]),
    )
    await expect(page.locator('.quest-pin')).toHaveCount(quest ? 8 : 0)
    await expect(page.locator('.npc-pin')).toHaveCount(npc ? 5 : 0)
    await expect(page.locator('.reference-labels button')).toHaveCount(places ? 18 : 0)
    await expect(page.locator('.quest-legend')).toHaveCount(Number(quest) + Number(npc))
  }
  const toggle = (name: string) => layers.getByRole('button', { name }).click()
  await check(true, true, false)
  await toggle('古镇地点')
  await check(true, true, true)
  await toggle('江湖令牌')
  await check(false, true, true)
  await toggle('行走 NPC')
  await check(false, false, true)
  await toggle('古镇地点')
  await check(false, false, false)
  await expect(page.locator('.map-art')).toBeVisible()
  await page.getByRole('button', { name: '路网', exact: true }).click()
  await expect(layers).toHaveCount(0)
  await page.getByRole('button', { name: '导览', exact: true }).click()
  await check(false, false, false)
  await toggle('行走 NPC')
  await check(false, true, false)
  await toggle('江湖令牌')
  await check(true, true, false)
  await toggle('行走 NPC')
  await check(true, false, false)
  await toggle('古镇地点')
  await check(true, false, true)
})

test('town places open restaurant content and retain the other layer choices', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '古镇地点', exact: true }).click()
  await page.getByRole('button', { name: '江湖令牌', exact: true }).click()
  await page.getByRole('button', { name: '行走 NPC', exact: true }).click()
  await page.getByRole('button', { name: '查看深夜食堂', exact: true }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('heading', { name: '深夜食堂' })).toBeVisible()
  await dialog.getByRole('button', { name: /深夜食堂.*自由晚餐推荐/ }).click()
  await expect(dialog.getByText(/约 50 个餐位/)).toBeVisible()
  await dialog.getByRole('button', { name: '在地图中查看', exact: true }).click()
  await expect(dialog).toHaveCount(0)
  await expect(page.locator('.reference-labels button')).toHaveCount(18)
  await expect(page.locator('.field-marker')).toHaveCount(0)
  await expect(page.getByRole('button', { name: '查看深夜食堂', exact: true })).toBeVisible()
})

test('zoom and camera survive tab changes and pan responds to pointer drag', async ({ page }) => {
  await page.goto('/')
  const scene = page.locator('.map-scene')
  const initial = await scene.getAttribute('style')
  await page.getByRole('button', { name: '放大地图', exact: true }).click()
  await expect(scene).not.toHaveAttribute('style', initial!)
  const zoomed = await scene.getAttribute('style')
  await page.getByRole('button', { name: /^餐厅$/ }).click()
  await page.getByRole('button', { name: /^地图$/ }).click()
  await expect(scene).toHaveAttribute('style', zoomed!)
  const viewport = page.getByRole('region', { name: /古镇导览/ })
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

test('favorites persist after reload and can be removed from the card', async ({ page }) => {
  await page.goto('/#food')
  await page.getByRole('button', { name: '收藏蚬子滩客栈', exact: true }).click()
  await expect(
    page.getByRole('button', { name: '取消收藏蚬子滩客栈', exact: true }),
  ).toHaveAttribute('aria-pressed', 'true')
  await page.reload()
  await expect(page.getByRole('button', { name: '我的收藏', exact: true })).toHaveCount(0)
  await page.getByRole('button', { name: '取消收藏蚬子滩客栈', exact: true }).click()
  await expect(page.getByRole('button', { name: '收藏蚬子滩客栈', exact: true })).toBeVisible()
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
  await page.getByRole('button', { name: '古镇地点', exact: true }).click()
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await expect(page.getByRole('dialog').getByText('已获取设备位置', { exact: true })).toBeVisible()
  await expect(page.getByText(/设备报告精度约 18 米/)).toBeVisible()
  await expect(page.getByText(/暂不在示意图上显示定位点/)).toBeVisible()
  await expect(page.locator('.reference-labels button')).toHaveCount(18)
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
  await expect(page.getByRole('button', { name: /开启动效|减少动态效果/ })).toHaveCount(0)
  const boats = page.locator('.guide-boat')
  await expect(boats).toHaveCount(8)
  for (const boat of await boats.all())
    await expect(boat).toHaveCSS('animation-play-state', 'paused')
  await expect(page.locator('.map-viewport')).toHaveClass(/motion-paused/)
  for (const name of [/^地图$/, /^餐厅$/, /^行程$/, /^游戏$/]) {
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
  const npcIcon = page.locator('.npc-pin > svg').first()
  await expect.poll(async () => (await npcIcon.boundingBox())?.width ?? 0).toBeCloseTo(26, 1)
  const sceneWidth = (await scene.boundingBox())!.width
  const iconWidth = (await npcIcon.boundingBox())!.width
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
  const sceneRatio = (await scene.boundingBox())!.width / sceneWidth
  expect(sceneRatio).toBeGreaterThan(1)
  expect((await npcIcon.boundingBox())!.width / iconWidth).toBeCloseTo(sceneRatio, 2)
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
  await page.getByRole('button', { name: /^餐厅$/ }).click()
  await expect(page.getByRole('navigation', { name: '主要导航' })).toBeInViewport()
})

test('narrow navigation keeps one current destination and chapter or filter', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 })
  await page.goto('/#itinerary/walk')
  const main = page.getByRole('navigation', { name: '主要导航' })
  const trip = page.getByRole('navigation', { name: '行程内容' })
  const games = page.getByRole('navigation', { name: '游戏内容' })
  const dining = page.getByRole('group', { name: '餐厅分类' })

  async function checkTargets(controls: Locator) {
    for (const control of await controls.all()) {
      const box = (await control.boundingBox())!
      expect(box.width).toBeGreaterThanOrEqual(44)
      expect(box.height).toBeGreaterThanOrEqual(44)
      expect(box.x).toBeGreaterThanOrEqual(0)
      expect(box.x + box.width).toBeLessThanOrEqual(320)
    }
  }

  await expect(main.locator('[aria-current="page"]')).toHaveText('行程')
  await expect(trip.locator('a[aria-current="page"]')).toHaveText('游览')
  await checkTargets(main.getByRole('button'))
  await checkTargets(trip.getByRole('link'))
  await trip.getByRole('link', { name: '演出', exact: true }).press('Enter')
  await expect(trip.locator('a[aria-current="page"]')).toHaveText('演出')
  await page.goBack()
  await expect(trip.locator('a[aria-current="page"]')).toHaveText('游览')

  await main.getByRole('button', { name: '游戏' }).click()
  await expect(main.locator('[aria-current="page"]')).toHaveText('游戏')
  await checkTargets(games.getByRole('link'))
  await games.getByRole('link', { name: '游走 NPC' }).click()
  await expect(games.locator('a[aria-current="page"]')).toHaveText('游走 NPC')
  await main.getByRole('button', { name: '餐厅' }).click()
  await expect(main.locator('[aria-current="page"]')).toHaveText('餐厅')
  await checkTargets(dining.getByRole('button'))
  await expect(dining.getByRole('button', { pressed: true })).toHaveText('全部')
  await dining.getByRole('button', { name: '水乡家常' }).click()
  await expect(dining.getByRole('button', { pressed: true })).toHaveText('水乡家常')
  await expect(page.getByRole('status')).toContainText('7 家推荐')
})

test('zooming the reference map loads local AI tiles and panning replaces them', async ({
  page,
}) => {
  await page.goto('/')
  const tiles = page.locator('.reference-tiles img[src*="/8/"]')
  await expect(tiles).toHaveCount(0)
  const plus = page.getByRole('button', { name: '放大地图' })
  const minus = page.getByRole('button', { name: '缩小地图' })
  await minus.click()
  await expect(minus).toBeDisabled()
  await plus.click()
  await expect(minus).toBeEnabled()
  for (let i = 0; i < 8; i++) await plus.click()
  await expect(plus).toBeDisabled()
  await expect(tiles.first()).toBeVisible()
  await expect(tiles.first()).toHaveJSProperty('naturalWidth', 1024)
  const firstTile = await tiles.first().getAttribute('src')
  expect(await tiles.count()).toBeLessThan(30)
  const viewport = page.locator('.map-viewport')
  await viewport.focus()
  for (let i = 0; i < 10; i++) await viewport.press('ArrowRight')
  await expect(page.locator(`.reference-tiles img[src="${firstTile}"]`)).toHaveCount(0)
  await expect(tiles.first()).toBeVisible()
  await viewport.press('Home')
  await expect(plus).toBeEnabled()
  await expect(minus).toBeEnabled()
  await expect(tiles).toHaveCount(0)
})

test('the reference map is the default and switching to real roads preserves its camera', async ({
  page,
}) => {
  await page.goto('/')
  const views = page.locator('.map-view-switch button')
  await expect(views).toHaveText(['导览', '路网'])
  const reference = page.getByRole('button', { name: '导览', exact: true })
  await expect(reference).toHaveAttribute('aria-pressed', 'true')
  await expect(page.locator('.map-art')).toHaveAttribute('src', '/art/puyuan-original-scope.webp')
  await expect
    .poll(() =>
      page.locator('.map-art').evaluate((image: HTMLImageElement) => ({
        pixels: [image.naturalWidth, image.naturalHeight],
        scene: [image.width, image.height],
      })),
    )
    .toEqual({ pixels: [1520, 1240], scene: [1520, 1240] })
  await page.getByRole('button', { name: '放大地图' }).click()
  const zoomed = await page.locator('.map-scene').getAttribute('style')
  await page.getByRole('button', { name: '路网', exact: true }).click()
  await expect(page.locator('.real-road').first()).toBeVisible()
  await expect(page.locator('.geo-landmark')).toHaveCount(8)
  await expect(page.getByRole('textbox', { name: '搜索地图地点或活动' })).toHaveCount(0)
  await page.getByRole('button', { name: '查看地图资料：福山塔', exact: true }).click()
  await expect(page.getByRole('dialog').getByRole('heading', { name: '福山塔' })).toBeVisible()
  await page.getByRole('button', { name: '继续看地图' }).click()
  await expect(page.getByRole('button', { name: '影像核对', exact: true })).toHaveCount(0)
  await expect(page.locator('.geo-landmark')).toHaveCount(8)
  await reference.click()
  await expect(page.locator('.map-scene')).toHaveAttribute('style', zoomed!)
})

test('acquired GPS can be opened on the main real map without placing it on the reference map', async ({
  page,
  context,
}) => {
  await context.grantPermissions(['geolocation'])
  await context.setGeolocation({ latitude: 30.6828922, longitude: 120.6296382, accuracy: 10 })
  await page.goto('/')
  await page.getByRole('button', { name: '获取我的位置' }).click()
  await page.getByRole('button', { name: '获取设备位置', exact: true }).click()
  await page.getByRole('button', { name: '在路网中查看位置' }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('.main-user-position')).toBeVisible()
  await expect(page.getByRole('button', { name: '路网', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  )
  await page.getByRole('button', { name: '导览', exact: true }).click()
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

test('panning beyond the former crop reveals meadow and can return to town', async ({ page }) => {
  await page.goto('/')
  const scene = page.locator('.map-scene')
  const initial = await scene.getAttribute('style')
  await page.getByRole('region', { name: /古镇导览/ }).focus()
  for (let i = 0; i < 22; i++) await page.keyboard.press('ArrowRight')
  await expect(page.getByRole('button', { name: '回到古镇', exact: true })).toBeVisible()
  await expect(page.locator('.meadow-backdrop')).toHaveCSS(
    'background-image',
    /reference-meadow\.webp/,
  )
  const view = (await page.locator('.map-viewport').boundingBox())!
  const image = (await page.locator('.map-art').boundingBox())!
  expect(image.x + image.width).toBeLessThan(view.x + 35)
  await page.getByRole('button', { name: '回到古镇', exact: true }).click()
  await expect(scene).toHaveAttribute('style', initial!)
  await page.getByRole('button', { name: '路网', exact: true }).click()
  await expect(page.locator('.meadow-backdrop')).toHaveCount(0)
})

test('the tower link survives reload without changing the temple place or its default card', async ({
  page,
}) => {
  await page.goto('/#map/place/temple/temple-pagoda')
  const dialog = page.getByRole('dialog')
  await page.reload()
  await expect(dialog.getByRole('heading', { name: '寺塔', exact: true })).toBeVisible()
  await expect(dialog.locator('.detail-facts')).toContainText('福善寺')
  for (const suffix of ['', '/waterside-stage']) {
    await page.goto(`/#map/place/temple${suffix}`)
    await expect(dialog.getByRole('heading', { name: '福善寺', exact: true })).toBeVisible()
    await expect(dialog.locator('.detail-hero img')).toHaveAttribute(
      'src',
      '/art/landmarks/temple-hall.scene.webp',
    )
  }
})
