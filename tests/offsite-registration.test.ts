import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { quests, wanderers } from '../src/data/offsite.ts'

type Point = [number, number]
type Control = [number, number, number, number]

test('all mapped encounters project from the marked tips using their local landmarks', async () => {
  const manifest: {
    regions: { controls: [Control, Control, Control]; tips: Record<string, Point> }[]
  } = JSON.parse(
    await readFile(new URL('../references/offsite-registration.json', import.meta.url), 'utf8'),
  )
  const registered = new Map<string, Point>()
  for (const {
    controls: [origin, east, north],
    tips,
  } of manifest.regions) {
    const eastX = east[0] - origin[0],
      eastY = east[1] - origin[1]
    const northX = north[0] - origin[0],
      northY = north[1] - origin[1]
    const determinant = eastX * northY - eastY * northX
    assert.notEqual(determinant, 0)
    for (const [key, [tipX, tipY]] of Object.entries(tips)) {
      const eastWeight = ((tipX - origin[0]) * northY - (tipY - origin[1]) * northX) / determinant
      const northWeight = (eastX * (tipY - origin[1]) - eastY * (tipX - origin[0])) / determinant
      const project = (axis: 2 | 3) =>
        Math.round(
          origin[axis] +
            eastWeight * (east[axis] - origin[axis]) +
            northWeight * (north[axis] - origin[axis]),
        )
      registered.set(key, [project(2), project(3)])
    }
  }
  const actual = new Map<string, Point>()
  for (const quest of quests) actual.set(quest.id, quest.point)
  for (const npc of wanderers) if (npc.point) actual.set(npc.id, npc.point)
  assert.equal(registered.size, 13)
  assert.deepEqual(actual, registered)
})
