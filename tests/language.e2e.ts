import { expect, test } from '@playwright/test'

test('language toggles in place without resetting the map, quest photos or dining search', async ({
  page,
}) => {
  await page.goto('/#map')
  const toggle = page.locator('.language-button')
  const scene = page.locator('.map-scene')
  await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN')
  await expect(toggle).toHaveAccessibleName('切换到英文 · English')
  await expect(toggle.locator('svg[aria-hidden="true"]')).toBeVisible()
  await expect(page.getByText('游园手帖')).toHaveCount(0)
  await page.getByRole('button', { name: '古镇地点', exact: true }).click()
  await page.locator('.map-viewport').press('=')
  const camera = await scene.getAttribute('style')
  await toggle.click()
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  await expect(toggle).toHaveAccessibleName('Switch to Chinese · 中文')
  await expect(page).toHaveTitle('Puyuan Wanderer · Discover Jiangnan')
  await expect(scene).toHaveAttribute('style', camera!)
  await expect(page.getByRole('button', { name: 'Places', exact: true })).toHaveAttribute(
    'aria-pressed',
    'true',
  )
  await page.getByRole('button', { name: 'Quest: Grand Lawn · Cuju Kickoff' }).click()
  const sheet = page.getByRole('dialog', { name: 'Cuju Kickoff' })
  await expect(sheet).toContainText('Score more than 250 points as a team.')
  await sheet.getByRole('button', { name: 'Location' }).click()
  await expect(
    sheet.getByRole('img', { name: 'The Grand Lawn beside the old town buildings.' }),
  ).toBeVisible()
  await sheet.getByRole('button', { name: 'Close dialog' }).click()
  await expect(scene).toHaveAttribute('style', camera!)
  await page.getByRole('button', { name: 'Dining', exact: true }).click()
  const search = page.getByRole('searchbox')
  await search.fill('hot pot')
  await expect(page.locator('.dinner-row')).toHaveCount(1)
  await page.getByRole('button', { name: 'Save North Arcade Sichuan Hot Pot' }).click()
  await toggle.click()
  await expect(search).toHaveValue('hot pot')
  await expect(page.getByRole('button', { name: '取消收藏北廊棚川式火锅' })).toHaveAttribute(
    'aria-pressed',
    'true',
  )
  await search.fill('川式')
  await toggle.click()
  await expect(page.getByRole('heading', { name: 'North Arcade Sichuan Hot Pot' })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('navigation', { name: 'Main navigation' })).toBeVisible()
  await page.goto('/#map/favorites')
  await expect(page.getByRole('dialog')).toContainText('North Arcade Sichuan Hot Pot')
})

test('all book chapters, map labels and legacy dialogs render English on a narrow phone', async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 740 })
  await page.goto('/#map/guide')
  await expect(page).toHaveURL(/#map$/)
  await page.locator('.language-button').click()
  for (const [route, expected] of [
    ['map', 'Roaming NPCs'],
    ['itinerary', 'Two Days in Puyuan'],
    ['itinerary/walk', 'Shufang Zen Garden'],
    ['itinerary/studio', 'Ginkgo bookmark'],
    ['itinerary/shows', 'Check today’s curtain times'],
    ['games', 'The Scattered Poem'],
    ['games/roaming', 'The Caravan Guard'],
    ['games/tokens', '500 jiaozi'],
    ['games/npc/trader', 'The Black Market Trader'],
    ['games/task/relay', 'The Cloth Relay'],
    ['food', 'Old Well Restaurant'],
    ['activities', 'Opera by the Water'],
    ['activities/activity/waterside-opera', 'Tomorrow'],
    ['map/place/water-stage', 'where Water Stage stands'],
    ['map/place/temple/temple-pagoda', 'Temple Pagoda'],
    ['map/restaurant/r-tea', 'Canal Lane Tea House'],
    ['map/restaurant/late-supper', 'About 50 seats'],
    ['map/location', 'Location overview'],
    ['map/favorites', 'Nothing saved yet.'],
  ]) {
    await page.goto(`/#${route}`)
    await expect(page.locator('body')).toContainText(expected)
    const missed = await page.evaluate(() => {
      const attributes = Array.from(
        document.querySelectorAll('[aria-label],[placeholder],[title],[alt]'),
      )
        .filter((el) => el.getClientRects().length && !el.closest('.language-button'))
        .flatMap((el) =>
          ['aria-label', 'placeholder', 'title', 'alt'].map((key) => el.getAttribute(key) || ''),
        )
      return (
        [document.body.innerText, ...attributes]
          .join('\n')
          .replaceAll('濮院时尚古镇', '')
          .replaceAll('中文', '')
          .match(/\p{Script=Han}+/gu) || []
      )
    })
    expect(missed, route).toEqual([])
    expect(await page.evaluate(() => document.documentElement.scrollWidth), route).toBe(320)
  }
})
