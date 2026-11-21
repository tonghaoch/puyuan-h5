import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'

const built = new URL('../dist/', import.meta.url)
const output = new URL('../dist-review/', import.meta.url)
const { models } = JSON.parse(
  await readFile(new URL('../src/data/landmark-models.json', import.meta.url), 'utf8'),
)
const files = [
  'index.html',
  'favicon.svg',
  'assets',
  'geodata/boundary.geojson',
  'geodata/README.txt',
  'art/puyuan-original-scope.webp',
  'art/reference-meadow.webp',
  'art/reference-tiles',
  'art/native/water-mask.svg',
  'art/meadow-tile.svg',
  'art/boat-covered.webp',
  'art/boat-bamboo.webp',
  'art/encounters',
  'art/journal-journey.svg',
  'art/journal-dining.svg',
  'art/offsite-shows.png',
  ...['stage', 'temple', 'market', 'tea', 'food', 'noodles', 'dessert'].map(
    (name) => `art/${name}.svg`,
  ),
  ...models.map((model) => (model.heroAsset || model.asset).replace(/^\//, '')),
]

await rm(output, { force: true, recursive: true })
await mkdir(output, { recursive: true })
for (const file of new Set(files)) {
  await cp(new URL(file, built), new URL(file, output), { recursive: true })
}
await writeFile(new URL('.nojekyll', output), '')
console.log(
  '审阅站点已生成：dist-review/（仅网页运行资源，无原始参考资料、小程序配置或源码映射）。',
)
