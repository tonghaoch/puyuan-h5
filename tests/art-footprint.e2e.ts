import { expect, test, type Page } from '@playwright/test'
import { rasterizeArt } from '../scripts/art-raster.mjs'

async function maskColumn(
  page: Page,
  source: string,
  id: string,
  left: number,
  top: number,
  rows: number,
) {
  return page.evaluate(
    async ({ source, id, left, top, rows }) => {
      const fragment = new DOMParser().parseFromString(source, 'image/svg+xml')
      const footprint = fragment.getElementById(id)!
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1" height="${rows}" viewBox="${left} ${top} 1 ${rows}"><defs>${footprint.outerHTML}</defs><rect x="${left}" y="${top}" width="1" height="${rows}" mask="url(#${id})"/></svg>`
      const image = new Image()
      image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
      await image.decode()
      const canvas = document.createElement('canvas')
      canvas.width = image.width
      canvas.height = image.height
      const context = canvas.getContext('2d')!
      context.drawImage(image, 0, 0)
      return Array.from({ length: rows }, (_, row) => context.getImageData(0, row, 1, 1).data[3])
    },
    { source, id, left, top, rows },
  )
}

test('the Fuma eave retains both tile edges around its open court', async ({ page, request }) => {
  const asset = await request.get('/art/landmarks/fuma-residence.svg')
  expect(asset.ok()).toBe(true)
  const alpha = await maskColumn(page, await asset.text(), 'finish-roof-935', 740, 633, 10)
  expect(alpha[0]).toBe(0)
  expect(alpha[4]).toBe(255)
  expect(alpha.slice(5, 7)).toEqual([0, 0])
  expect(alpha[7]).toBeGreaterThan(200)
  expect(alpha[9]).toBe(0)
})

test('the measured east quay slate admits the light opening between the timber eaves', async ({
  page,
  request,
}) => {
  const asset = await request.get('/art/architecture/block-4-3.svg')
  expect(asset.ok()).toBe(true)
  const alpha = await maskColumn(
    page,
    await asset.text(),
    'east-quay-timber-row-measured-slate',
    1160,
    998,
    8,
  )
  expect(alpha[0]).toBe(255)
  expect(alpha.slice(2, 4)).toEqual([0, 0])
  expect(alpha[7]).toBe(255)
})

test('asset pixels come from the decoded vector, independent of the display viewport', async ({
  page,
}) => {
  const source =
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="10"><defs><mask id="m"><rect x="3" y="2" width="6" height="5" fill="white"/><rect x="5" y="3" width="2" height="2"/></mask></defs><rect width="12" height="10" fill="#b14d65" mask="url(#m)"/></svg>'
  const raster = await rasterizeArt(page, source, 36, 30)
  expect([raster.readUInt32BE(16), raster.readUInt32BE(20)]).toEqual([36, 30])
  await page.setViewportSize({ width: 170, height: 110 })
  expect(await rasterizeArt(page, source, 36, 30)).toEqual(raster)
  const samples = await page.evaluate(async (data) => {
    const image = new Image()
    image.src = `data:image/png;base64,${data}`
    await image.decode()
    const canvas = document.createElement('canvas')
    canvas.width = image.width
    canvas.height = image.height
    const context = canvas.getContext('2d')!
    context.drawImage(image, 0, 0)
    return [
      [0, 0],
      [12, 12],
      [18, 12],
    ].map(([x, y]) => Array.from(context.getImageData(x!, y!, 1, 1).data))
  }, raster.toString('base64'))
  expect(samples).toEqual([
    [0, 0, 0, 0],
    [177, 77, 101, 255],
    [0, 0, 0, 0],
  ])
})
