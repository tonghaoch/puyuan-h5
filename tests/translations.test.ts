import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { days, dinnerSpots, experiences, quests, tools, wanderers } from '../src/data/offsite.ts'

function json(relativePath: string) {
  return JSON.parse(readFileSync(new URL(relativePath, import.meta.url), 'utf8'))
}
const english: Record<string, string> = Object.assign(
  {},
  ...['ui', 'catalog', 'offsite'].map((name) => json(`../src/i18n/${name}.json`)),
)

test('every encounter, photo, workshop, meal, schedule and mapped place has English copy', () => {
  function check(value: unknown) {
    if (typeof value === 'string' && /\p{Script=Han}/u.test(value)) {
      assert.ok(english[value] && !/\p{Script=Han}/u.test(english[value]!), value)
    } else if (value && typeof value === 'object') {
      Object.values(value).forEach(check)
    }
  }
  check([days, dinnerSpots, experiences, quests, tools, wanderers])
  for (const place of json('../src/data/reference-map.json').landmarks)
    check([place.name, place.subtitle])
})

test('English messages retain the same named placeholders as their source', () => {
  const placeholders = (value: string) => (value.match(/\{\w+\}/g) ?? []).sort()
  for (const [source, translation] of Object.entries(english)) {
    assert.deepEqual(placeholders(translation), placeholders(source), source)
  }
})
