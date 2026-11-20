import { chromium } from '@playwright/test'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { spawnSync } from 'node:child_process'
import { rasterizeArt } from './art-raster.mjs'
const root = new URL('../', import.meta.url)
const temporary = new URL('../artifacts/architecture-renders/', import.meta.url)
await mkdir(temporary, { recursive: true })
const cachePath = new URL('render-cache.json', temporary)
let cache = {}
try {
  cache = JSON.parse(await readFile(cachePath, 'utf8'))
} catch {
  /* First render. */
}
const models = JSON.parse(
  await readFile(new URL('src/data/landmark-models.json', root), 'utf8'),
).models
const tiles = JSON.parse(
  await readFile(new URL('src/data/architecture-tiles.json', root), 'utf8'),
).tiles
let landscapeJobs = []
const landscapePath = new URL('src/data/native-landscape.json', root)
if (existsSync(landscapePath)) {
  const landscape = JSON.parse(await readFile(landscapePath, 'utf8'))
  landscapeJobs = [
    { id: 'native-ground', asset: landscape.ground, sourceAsset: landscape.ground },
    { id: 'native-waterfronts', asset: landscape.waterfronts, sourceAsset: landscape.waterfronts },
    ...landscape.tiles,
  ].map((tile) => ({
    id: tile.id,
    sourceAsset: tile.sourceAsset,
    asset: tile.asset.replace('.svg', '.webp'),
    overviewAsset: tile.overviewAsset || tile.asset.replace('.svg', '.preview.webp'),
    factor: tile.id.startsWith('native-') ? 4 : 6,
    preview: tile.id.startsWith('native-') ? 1 : 2,
  }))
}
const selection = process.argv
  .find((arg) => arg.startsWith('--only='))
  ?.slice(7)
  .split(',')
const jobs = [
  ...models.map((model) => ({ ...model, factor: 8, preview: 2 })),
  ...tiles.map((tile) => ({ ...tile, factor: 4, preview: 2 })),
  ...landscapeJobs,
].filter((job) => !selection || selection.includes(job.id))
const localChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const browser = await chromium.launch({
  executablePath:
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ||
    (existsSync(localChrome) ? localChrome : undefined),
  headless: true,
})
try {
  for (const job of jobs) {
    const source = await readFile(new URL(`public${job.sourceAsset}`, root), 'utf8')
    const [, w, h] = source.match(/width="(\d+)" height="(\d+)"/)
    const target = new URL(`public${job.asset}`, root).pathname
    const preview = new URL(`public${job.overviewAsset}`, root).pathname
    const hash = createHash('sha256')
      .update(source)
      .update(`decoded-srgb-canvas-v1:${job.factor}:${job.preview}:92:85:4`)
      .update(job.heroAsset ? ':painted-landmark-v1' : '')
      .digest('hex')
    if (cache[job.id] === hash && existsSync(target) && existsSync(preview)) {
      process.stdout.write(`Unchanged ${job.id}\n`)
      continue
    }
    const page = await browser.newPage()
    const input = new URL(`${job.id}.png`, temporary).pathname
    let encoded = false
    for (let attempt = 0; attempt < 3; attempt++) {
      await writeFile(
        input,
        await rasterizeArt(page, source, Number(w) * job.factor, Number(h) * job.factor),
      )
      const convert = spawnSync(
        process.env.PUYUAN_ART_PYTHON || 'python3',
        [
          new URL('scripts/encode-art-asset.py', root).pathname,
          input,
          target,
          preview,
          String(Number(w) * job.preview),
          String(Number(h) * job.preview),
          ...(job.heroAsset ? ['--landmark'] : []),
        ],
        { stdio: 'inherit' },
      )
      if (convert.status === 0) {
        encoded = true
        break
      }
      if (convert.status !== 3) throw new Error(`Could not encode ${job.id}`)
    }
    await page.close()
    if (!encoded) throw new Error(`Landmark ${job.id} is still transparent after three captures`)
    cache[job.id] = hash
    await writeFile(cachePath, JSON.stringify(cache, null, 2))
    process.stdout.write(`Rendered ${job.id}\n`)
  }
} finally {
  await browser.close()
}
