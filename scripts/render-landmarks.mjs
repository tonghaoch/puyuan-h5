import { chromium } from '@playwright/test'
import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { spawnSync } from 'node:child_process'
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
const selection = process.argv
  .find((arg) => arg.startsWith('--only='))
  ?.slice(7)
  .split(',')
const jobs = [
  ...models.map((model) => ({ ...model, factor: 8, preview: 2 })),
  ...tiles.map((tile) => ({ ...tile, factor: 4, preview: 2 })),
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
      .update(`raster-v2:${job.factor}:${job.preview}:92:85:4`)
      .digest('hex')
    if (cache[job.id] === hash && existsSync(target) && existsSync(preview)) {
      process.stdout.write(`Unchanged ${job.id}\n`)
      continue
    }
    const page = await browser.newPage({
      viewport: { width: Number(w), height: Number(h) },
      deviceScaleFactor: job.factor,
    })
    await page.setContent(
      `<style>html,body{margin:0;background:transparent}svg{display:block}</style>${source}`,
    )
    const input = new URL(`${job.id}.png`, temporary).pathname
    await page.screenshot({ path: input, omitBackground: true })
    await page.close()
    const convert = spawnSync(
      process.env.PUYUAN_ART_PYTHON || 'python3',
      [
        '-c',
        `from PIL import Image
image=Image.open(${JSON.stringify(input)})
image.save(${JSON.stringify(target)},quality=92,method=4)
image.resize((${Number(w) * job.preview},${Number(h) * job.preview}),Image.Resampling.LANCZOS).save(${JSON.stringify(preview)},quality=85,method=4)`,
      ],
      { stdio: 'inherit' },
    )
    if (convert.status !== 0) throw new Error(`Could not render ${job.id}`)
    cache[job.id] = hash
    await writeFile(cachePath, JSON.stringify(cache, null, 2))
    process.stdout.write(`Rendered ${job.id}\n`)
  }
} finally {
  await browser.close()
}
