import assert from 'node:assert/strict'
import test from 'node:test'
import { createLocationSmoother, fixDistance } from '../src/lib/location-smoothing.ts'
import type { GeographicFix } from '../src/lib/geography.ts'

const origin = { longitude: 120.63, latitude: 30.68 }
export function deviceFix(x: number, y: number, timestamp: number, accuracy = 8): GeographicFix {
  return {
    longitude:
      origin.longitude +
      ((x / (6378137 * Math.cos((origin.latitude * Math.PI) / 180))) * 180) / Math.PI,
    latitude: origin.latitude + ((y / 6378137) * 180) / Math.PI,
    timestamp,
    accuracy,
  }
}

test('stationary alternating noise is reduced without claiming a smaller confidence region', () => {
  const smoother = createLocationSmoother()
  const truth = deviceFix(0, 0, 0)
  let rawSquared = 0
  let filteredSquared = 0
  for (let i = 0; i < 30; i++) {
    const raw = deviceFix(i % 2 ? 4 : -4, i % 3 ? 2 : -2, i * 1000)
    const filtered = smoother.update(raw)
    rawSquared += fixDistance(raw, truth) ** 2
    filteredSquared += fixDistance(filtered, truth) ** 2
    assert.ok(fixDistance(filtered, raw) <= 3.001)
    assert.ok(filtered.accuracy + 0.001 >= raw.accuracy + fixDistance(filtered, raw))
    assert.equal(filtered.timestamp, raw.timestamp)
  }
  assert.ok(filteredSquared < rawSquared * 0.65)
})

test('walking starts immediately, keeps turns, and resets after a large change or sampling gap', () => {
  const smoother = createLocationSmoother()
  for (let i = 0; i <= 20; i++) {
    const x = Math.min(i, 10) * 1.4
    const y = Math.max(0, i - 10) * 1.4
    const raw = deviceFix(x, y, i * 1000)
    const filtered = smoother.update(raw)
    assert.ok(fixDistance(filtered, raw) < 1)
    if (i === 1) assert.ok(filtered.longitude > origin.longitude)
    if (i === 11) assert.ok(filtered.latitude > origin.latitude)
  }
  const relocated = deviceFix(100, 30, 21000)
  assert.ok(fixDistance(smoother.update(relocated), relocated) < 0.001)
  const afterGap = deviceFix(101, 30, 30000)
  assert.ok(fixDistance(smoother.update(afterGap), afterGap) < 0.001)
  smoother.reset()
  const restarted = deviceFix(0, 0, 31000)
  assert.ok(fixDistance(smoother.update(restarted), restarted) < 0.001)
})

test('duplicates and late readings do not shift the estimate or make it fresher', () => {
  const smoother = createLocationSmoother()
  smoother.update(deviceFix(0, 0, 1000))
  const last = smoother.update(deviceFix(2, 0, 2000))
  assert.deepEqual(smoother.update(deviceFix(8, 0, 2000)), last)
  assert.deepEqual(smoother.update(deviceFix(4, 0, 1500)), last)
})

test('smoothing cannot remove a persistent bias or distinguish a corrected position from a spike', () => {
  const smoother = createLocationSmoother()
  const truth = deviceFix(0, 0, 0)
  for (let i = 0; i < 10; i++) {
    const filtered = smoother.update(deviceFix(12, 0, i * 1000, 5))
    assert.ok(fixDistance(filtered, truth) > 11.9)
  }
  const raw = deviceFix(80, 0, 10000, 5)
  const result = smoother.update(raw)
  assert.ok(fixDistance(result, raw) < 0.001)
  assert.ok(fixDistance(result, truth) > 79)
})

test('nearby coordinates across the longitude seam stay nearby', () => {
  const smoother = createLocationSmoother()
  smoother.update({ longitude: 179.99999, latitude: 0, accuracy: 8, timestamp: 0 })
  const raw = { longitude: -179.99999, latitude: 0, accuracy: 8, timestamp: 1000 }
  assert.ok(fixDistance(smoother.update(raw), raw) < 3)
})
