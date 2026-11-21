import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import test from 'node:test'

test('each registered mini program page has a JSON configuration', async () => {
  const { miniprogramRoot } = JSON.parse(await readFile('project.config.json', 'utf8'))
  const { pages } = JSON.parse(await readFile(join(miniprogramRoot, 'app.json'), 'utf8'))
  for (const page of pages) {
    const file = join(miniprogramRoot, `${page}.json`)
    const config = JSON.parse(await readFile(file, 'utf8'))
    assert.ok(config !== null && typeof config === 'object' && !Array.isArray(config), file)
  }
})
