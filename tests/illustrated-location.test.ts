import assert from 'node:assert/strict'
import test from 'node:test'
import {
  createIllustrationProjector,
  illustratedBearing,
  projectIllustratedFix,
} from '../src/lib/illustrated-location.ts'
import registration from '../src/data/illustration-registration.json' with { type: 'json' }
import baseline from '../references/geodata/illustration-registration-baseline.json' with { type: 'json' }

function sample(east: number, south: number, accuracy = 10) {
  const world = registration.world
  return projectIllustratedFix({
    longitude: (((world[4] + east * world[0]) / 6378137) * 180) / Math.PI,
    latitude: (Math.atan(Math.sinh((world[5] + south * world[3]) / 6378137)) * 180) / Math.PI,
    accuracy,
    timestamp: 0,
  })
}

test('Yu Bridge is a control, distinct from the independent east bridge', () => {
  const bridge = sample(816, 688)!
  assert.ok(Math.hypot(bridge.x - 947, bridge.y - 726) < 0.001)
  const independent = sample(955, 662)!
  assert.ok(Math.hypot(independent.x - 1086, independent.y - 701) < 3)
  assert.ok(sample(816, 688, 30)!.radius > bridge.radius)
  assert.ok(bridge.radius > 10)
})

test('continuous across triangle edges, never snaps a walker to a pin or road', () => {
  const left = sample(816 - 0.001, 688)!
  const right = sample(816 + 0.001, 688)!
  assert.ok(Math.hypot(left.x - right.x, left.y - right.y) < 0.01)
  assert.notEqual(left.x, right.x)
})

test('the painted bearing follows a geographic displacement in the local triangle, not screen north', () => {
  for (const [east, south] of [
    [817, 690],
    [954, 663],
  ]) {
    const origin = sample(east, south)!
    for (const heading of [0, 45, 90, 180, 270, 359]) {
      const angle = (heading * Math.PI) / 180
      const end = sample(east + 0.01 * Math.sin(angle), south - 0.01 * Math.cos(angle))!
      const expected =
        (360 + (Math.atan2(end.x - origin.x, origin.y - end.y) * 180) / Math.PI) % 360
      assert.ok(Math.abs(illustratedBearing(origin, heading) - expected) < 0.0001)
    }
  }
})

test('unreliable regions, footprint edges, sparse or coarse fixes have no illustrated marker', () => {
  for (const [east, south] of [
    [1164, 557],
    [634, 987],
    [50, 100],
    [1289, 197],
    [984, 360],
  ])
    assert.equal(sample(east, south), null)
  for (const accuracy of [-1, 51, Infinity, NaN]) assert.equal(sample(816, 688, accuracy), null)
})

test('confirmed bridge corrections improve the separate west-temple bridge without widening visibility', () => {
  const before = createIllustrationProjector(baseline)
  const world = registration.world
  const fix = (east: number, south: number, accuracy: number) => ({
    longitude:
      ((world[4] / 6378137) * 180) / Math.PI + (((east * world[0]) / 6378137) * 180) / Math.PI,
    latitude: (Math.atan(Math.sinh((world[5] + south * world[3]) / 6378137)) * 180) / Math.PI,
    accuracy,
    timestamp: 0,
  })
  const previous = before(fix(475, 666, 10))!
  const corrected = projectIllustratedFix(fix(475, 666, 10))!
  assert.ok(
    Math.hypot(corrected.x - 570, corrected.y - 712) <
      Math.hypot(previous.x - 570, previous.y - 712) * 0.7,
  )
  for (const accuracy of [0, 10, 30]) {
    for (let east = 0; east < 1400; east += 20) {
      for (let south = 0; south < 1200; south += 20) {
        const position = fix(east, south, accuracy)
        if (projectIllustratedFix(position))
          assert.ok(before(position), `new unsupported marker at ${east},${south}`)
      }
    }
  }
})
