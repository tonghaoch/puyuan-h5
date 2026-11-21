import { expect, test } from '@playwright/test'

test('the map and game book show the same illustrated quest, including the personal reward', async ({
  page,
}) => {
  for (const tab of ['map', 'games']) {
    await page.goto(`/#${tab}/task/cuju`)
    const detail =
      tab === 'map' ? page.getByRole('dialog') : page.getByRole('region', { name: '游戏详情' })
    await expect(detail.getByRole('heading', { name: '蹴鞠达人' })).toBeVisible()
    await expect(detail).not.toContainText('一锤定音')
    await expect(detail).toContainText('32 分')
    const photo = detail.getByRole('img')
    await expect(photo).toHaveAttribute('src', /cuju-1\.webp$/)
    await detail.getByRole('button', { name: '地点' }).click()
    await expect(photo).toHaveAttribute('src', /cuju-2\.webp$/)
    await expect
      .poll(() => photo.evaluate((img: HTMLImageElement) => img.naturalWidth))
      .toBeGreaterThan(0)
    await expect(detail.locator('figcaption')).toContainText('大草坪')
    if (tab === 'map') {
      await detail.getByText('额外机缘').scrollIntoViewIfNeeded()
      await expect(detail.getByText('额外机缘')).toBeInViewport()
      await expect(detail.getByRole('button', { name: '关闭弹窗' })).toBeInViewport()
      await detail.getByRole('button', { name: '关闭弹窗' }).click()
      await expect(detail).toHaveCount(0)
    }
  }
})

test('the handbook includes roaming-only characters and the full three-plate encounter', async ({
  page,
}) => {
  await page.goto('/#games/roaming')
  const constable = page.getByRole('link', { name: /巡捕/ })
  await constable.click()
  const detail = page.getByRole('region', { name: '人物手札' })
  await expect(detail).toContainText('至少半数')
  await expect(detail.getByRole('button', { name: '查看活动范围' })).toHaveCount(0)
  await detail.getByRole('button', { name: '返回游戏手册' }).click()
  await expect(constable).toBeFocused()
  await page.getByRole('link', { name: /蒙面大侠/ }).click()
  await detail.getByRole('button', { name: '对局' }).click()
  await expect(detail.getByRole('img')).toHaveAttribute('src', /masked-3\.webp$/)
  await page.reload()
  await expect(detail.getByRole('heading', { name: '蒙面大侠' })).toBeVisible()
  await detail.getByRole('button', { name: '查看活动范围' }).click()
  const pin = page.getByRole('button', { name: /游走 NPC：蒙面大侠/ })
  await pin.click()
  const sheet = page.getByRole('dialog', { name: '蒙面大侠' })
  await sheet.getByRole('button', { name: '对局' }).click()
  await expect(sheet.getByRole('img')).toHaveAttribute('src', /masked-3\.webp$/)
  await page.keyboard.press('Escape')
  await expect(pin).toBeFocused()
})

test('the merchant has a single portrait and a keyboard-accessible card price list', async ({
  page,
}) => {
  await page.goto('/#map/npc/trader')
  const sheet = page.getByRole('dialog', { name: '黑市商人' })
  await expect(sheet.getByRole('group', { name: '选择图版' })).toHaveCount(0)
  await expect(sheet.getByRole('img')).toHaveAttribute('src', /trader-1\.webp$/)
  await sheet.focus()
  await page.keyboard.press('Shift+Tab')
  await expect(sheet.locator('summary')).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(sheet.getByText('改命卡 · 500 交子')).toBeVisible()
})

test('folio tabs sit outside the picture and work with the keyboard on a narrow screen', async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 640 })
  await page.goto('/#games/npc/masked')
  const plate = page.getByRole('figure', { name: '蒙面大侠图录' })
  const choices = page.getByRole('group', { name: '选择图版' })
  await expect(choices.getByRole('button')).toHaveCount(3)
  const art = (await plate.boundingBox())!
  for (const choice of await choices.getByRole('button').all()) {
    const box = (await choice.boundingBox())!
    expect(box.y).toBeGreaterThanOrEqual(art.y + art.height - 1)
    expect(box.height).toBeGreaterThanOrEqual(44)
    expect(box.x + box.width).toBeLessThanOrEqual(320)
  }
  const next = choices.getByRole('button', { name: '落子' })
  await next.focus()
  await page.keyboard.press('Enter')
  await expect(next).toHaveAttribute('aria-pressed', 'true')
  await expect(plate.getByRole('img')).toHaveAttribute('src', /masked-2\.webp$/)
  await expect(plate.getByRole('img')).toHaveCSS('object-fit', 'contain')
})

test('swiping turns a leaf but vertical reading gestures do not', async ({
  page,
  context,
  isMobile,
}) => {
  test.skip(!isMobile, 'Touch gestures use the mobile viewport')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/#map/npc/masked')
  const photo = page.getByRole('dialog').getByRole('img')
  const session = await context.newCDPSession(page)
  const swipe = async (deltaX: number, deltaY: number) => {
    const bounds = (await page.locator('.plate-mount').boundingBox())!
    const startX = bounds.x + bounds.width / 2
    const startY = bounds.y + bounds.height / 2
    await session.send('Input.dispatchTouchEvent', {
      type: 'touchStart',
      touchPoints: [{ x: startX, y: startY }],
    })
    await session.send('Input.dispatchTouchEvent', {
      type: 'touchMove',
      touchPoints: [{ x: startX + deltaX, y: startY + deltaY }],
    })
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
  }
  await swipe(-85, 3)
  await expect(photo).toHaveAttribute('src', /masked-2\.webp$/)
  await swipe(85, 2)
  await expect(photo).toHaveAttribute('src', /masked-1\.webp$/)
  await swipe(-3, -95)
  await expect(photo).toHaveAttribute('src', /masked-1\.webp$/)
  await expect
    .poll(() => page.locator('.dialog-content').evaluate((element) => element.scrollTop))
    .toBeGreaterThan(0)
})
