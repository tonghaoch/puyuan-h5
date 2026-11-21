import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { encounterImage, quests, wanderers } from '../src/data/offsite.ts'

test('all eight quests and six characters have their own captioned local PPT plates and thumbnail', async () => {
  assert.equal(quests.length, 8)
  assert.equal(wanderers.length, 6)
  const entries = [...quests, ...wanderers]
  assert.equal(new Set(entries.map((entry) => entry.id)).size, entries.length)
  assert.equal(
    entries.reduce((count, entry) => count + entry.photos.length, 0),
    28,
  )
  for (const entry of entries) {
    assert.ok(entry.description && entry.setup && entry.goal)
    for (const [label, caption] of entry.photos) assert.ok(label && caption)
    for (const plate of ['thumb' as const, ...entry.photos.map((_, index) => index + 1)]) {
      const path = encounterImage(entry.id, plate)
      const data = await readFile(new URL(`../public${path}`, import.meta.url))
      assert.equal(data.toString('ascii', 8, 12), 'WEBP', path)
      assert.ok(data.length < (plate === 'thumb' ? 10000 : 160000), path)
    }
  }
})
