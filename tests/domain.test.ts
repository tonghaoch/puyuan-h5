import test from 'node:test'
import assert from 'node:assert/strict'
import { shanghaiDate, shiftDay, sessionStatus } from '../src/lib/time.ts'
import { zoomAt, clampCamera, MIN_SCALE, MAX_SCALE } from '../src/lib/map-camera.ts'

test('Shanghai day changes at UTC 16:00 rather than the device local midnight', () => {
  assert.equal(shanghaiDate(new Date('2026-11-17T15:59:59Z')), '2026-11-17')
  assert.equal(shanghaiDate(new Date('2026-11-17T16:00:00Z')), '2026-11-18')
  assert.equal(shiftDay('2026-12-31', 1), '2027-01-01')
  assert.equal(shiftDay('2028-02-28', 1), '2028-02-29')
})
test('sessions become ongoing at start and ended at end, regardless of an upcoming session', () => {
  const session = { start: '2026-11-17T19:00:00+08:00', end: '2026-11-17T19:30:00+08:00' }
  const next = { start: '2026-11-18T19:00:00+08:00', end: '2026-11-18T19:30:00+08:00' }
  assert.equal(sessionStatus([session], Date.parse(session.start) - 1), 'upcoming')
  assert.equal(sessionStatus([session, next], Date.parse(session.start)), 'ongoing')
  assert.equal(sessionStatus([session], Date.parse(session.end)), 'ended')
  assert.equal(sessionStatus([session, next], Date.parse(session.end)), 'upcoming')
  assert.equal(sessionStatus([], Date.parse(session.start)), 'ended')
})
test('zoom preserves the world point beneath the pointer until scene limits intervene', () => {
  const camera = { x: -180, y: -120, scale: 0.8 }
  const point = { x: 300, y: 200 }
  const before = { x: (point.x - camera.x) / camera.scale, y: (point.y - camera.y) / camera.scale }
  const next = zoomAt(camera, 1.3, point.x, point.y, 1000, 700)
  assert.ok(Math.abs((point.x - next.x) / next.scale - before.x) < 1e-8)
  assert.ok(Math.abs((point.y - next.y) / next.scale - before.y) < 1e-8)
})
test('extreme zoom and pan cannot lose the scene', () => {
  const zoomIn = zoomAt({ x: 0, y: 0, scale: 0.7 }, 1000, 200, 300, 390, 700)
  const zoomOut = zoomAt(zoomIn, 0.0001, 200, 300, 390, 700)
  assert.equal(zoomIn.scale, MAX_SCALE)
  assert.equal(zoomOut.scale, MIN_SCALE)
  const clamped = clampCamera({ x: 1e9, y: -1e9, scale: 1 }, 390, 700)
  assert.ok(clamped.x < 390)
  assert.ok(clamped.y > -1400)
})

test('geographic location distinguishes inside, outside, uncertainty and stale fixes', async () => {
  const { classifyFix, createGeoFrame } = await import('../src/lib/geography.ts')
  const ring: [number, number][] = [
    [120, 30],
    [120.01, 30],
    [120.01, 30.01],
    [120, 30.01],
    [120, 30],
  ]
  const now = 100000
  const fix = { longitude: 120.005, latitude: 30.005, accuracy: 10, timestamp: now }
  assert.equal(classifyFix(fix, ring, now), 'inside')
  assert.equal(classifyFix({ ...fix, longitude: 120.02 }, ring, now), 'outside')
  assert.equal(classifyFix({ ...fix, longitude: 120.01001, accuracy: 100 }, ring, now), 'uncertain')
  assert.equal(classifyFix({ ...fix, timestamp: now - 60001 }, ring, now), 'stale')
  const frame = createGeoFrame(ring)
  const southwest = frame.project(ring[0]!)
  const northeast = frame.project(ring[2]!)
  assert.ok(southwest[0] < northeast[0] && southwest[1] > northeast[1])
})

test('published park data has an attributed WGS84 polygon and matches the recorded place', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const data = JSON.parse(
    await readFile(new URL('../public/geodata/puyuan.geojson', import.meta.url), 'utf8'),
  )
  const feature = data.features.find(
    (f: { properties: { layer: string } }) => f.properties.layer === 'boundary',
  )
  const ring = feature.geometry.coordinates[0]
  assert.equal(feature.geometry.type, 'Polygon')
  assert.deepEqual(ring[0], ring.at(-1))
  assert.ok(pointInRing([120.6296382, 30.6828922], ring))
  assert.match(data.attribution, /OpenStreetMap/)
  assert.ok(
    data.features.some((f: { properties: { layer: string } }) => f.properties.layer === 'water'),
  )
})

test('source-aligned map retains reference landmark order and exact image-space translation', async () => {
  const { readFile } = await import('node:fs/promises')
  const manifest = JSON.parse(
    await readFile(new URL('../src/data/reference-map.json', import.meta.url), 'utf8'),
  )
  const get = (id: string) => manifest.landmarks.find((p: { id: string }) => p.id === id)
  assert.ok(get('visitor').anchor[0] < get('water-stage').anchor[0])
  assert.ok(get('north-gate').anchor[1] < get('guildhall').anchor[1])
  assert.ok(get('guildhall').anchor[1] > get('temple').anchor[1])
  assert.ok(get('designer-house').anchor[0] > get('zen-hotel').anchor[0])
  assert.ok(get('zhuanglou').anchor[1] > get('dayou').anchor[1])
  for (const landmark of manifest.landmarks) {
    const x = landmark.anchor[0] + manifest.sourceOffset.x
    const y = landmark.anchor[1] + manifest.sourceOffset.y
    assert.ok(x > 0 && x < manifest.scene.width && y > 0 && y < manifest.scene.height)
  }
  const audit = JSON.parse(
    await readFile(new URL('../docs/map-asset-manifest.json', import.meta.url), 'utf8'),
  )
  assert.equal(audit.georeferenced, false)
  assert.deepEqual(audit.translation, manifest.sourceOffset)
})

test('satellite image uses service-returned projected extent in the same frame as GPS', async () => {
  const { readFile } = await import('node:fs/promises')
  const { createGeoFrame, mercator } = await import('../src/lib/geography.ts')
  const data = JSON.parse(
    await readFile(new URL('../public/geodata/puyuan.geojson', import.meta.url), 'utf8'),
  )
  const boundary = data.features.find(
    (f: { properties: { layer: string } }) => f.properties.layer === 'boundary',
  ).geometry.coordinates[0]
  const frame = createGeoFrame(boundary, 1520, 1240, 100)
  const metadata = JSON.parse(
    await readFile(new URL('../public/geodata/imagery-extent.json', import.meta.url), 'utf8'),
  )
  const extent = metadata.extent
  const topLeft = frame.projectMeters([extent.xmin, extent.ymax])
  const bottomRight = frame.projectMeters([extent.xmax, extent.ymin])
  const point: [number, number] = [120.6296382, 30.6828922]
  const meters = mercator(point)
  const imagePosition = [
    topLeft[0] +
      ((meters[0] - extent.xmin) / (extent.xmax - extent.xmin)) * (bottomRight[0] - topLeft[0]),
    topLeft[1] +
      ((extent.ymax - meters[1]) / (extent.ymax - extent.ymin)) * (bottomRight[1] - topLeft[1]),
  ]
  const expected = frame.project(point)
  assert.ok(Math.hypot(imagePosition[0]! - expected[0], imagePosition[1]! - expected[1]) < 1e-8)
})
