import assert from 'node:assert/strict'
import test from 'node:test'
import { deviceBearing, type CompassSample } from '../src/lib/device-bearing.ts'

const flat: CompassSample = {
  type: 'deviceorientation',
  absolute: true,
  alpha: 0,
  beta: 0,
  gamma: 0,
}

test('stationary phones point the screen top towards compass north, east, south and west', () => {
  for (const heading of [0, 90, 180, 270, 359, 1]) {
    assert.equal(deviceBearing({ ...flat, alpha: (360 - heading) % 360 }, 0), heading)
    assert.equal(
      deviceBearing({ ...flat, absolute: false, webkitCompassHeading: heading }, 0),
      heading,
    )
  }
  assert.equal(
    deviceBearing({ ...flat, absolute: false, type: 'deviceorientationabsolute' }, 90),
    90,
  )
  assert.equal(deviceBearing({ ...flat, webkitCompassHeading: 90 }, -90), 0)
})

test('project the visible top edge onto the ground in tilted landscape and inverted portrait', () => {
  const tilt = { ...flat, alpha: 10, beta: 45, gamma: 30 }
  assert.ok(Math.abs(deviceBearing(tilt, 90)! - 57.7923) < 0.001)
  assert.ok(Math.abs(deviceBearing({ ...tilt, webkitCompassHeading: 350 }, 90)! - 57.7923) < 0.001)
  assert.equal(deviceBearing({ ...flat, beta: 150 }, 0), 180)
  assert.equal(deviceBearing({ ...flat, beta: 90 }, 0), null)
  assert.equal(deviceBearing({ ...flat, gamma: 90 }, 90), null)
})

test('ignore relative yaw, reject missing or unreliable compass data rather than assuming north', () => {
  assert.equal(deviceBearing({ ...flat, absolute: false }, 0), undefined)
  for (const sample of [
    { alpha: null },
    { alpha: NaN },
    { beta: null },
    { webkitCompassHeading: -1 },
    { webkitCompassHeading: NaN },
    { webkitCompassHeading: 0, webkitCompassAccuracy: -1 },
    { webkitCompassHeading: 10, webkitCompassAccuracy: 55 },
  ])
    assert.equal(deviceBearing({ ...flat, ...sample }, 0), null)
})
