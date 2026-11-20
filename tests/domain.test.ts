import test from 'node:test'
import assert from 'node:assert/strict'
import { shanghaiDate, shiftDay, sessionStatus } from '../src/lib/time.ts'
import {
  zoomAt,
  clampCamera,
  MIN_SCALE,
  MAX_SCALE,
  cameraBounds,
  visibleScene,
} from '../src/lib/map-camera.ts'

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
test('expanded camera retains a bounded meadow and gives geography its own limits', () => {
  const zoomIn = zoomAt({ x: 0, y: 0, scale: 0.7 }, 1000, 200, 300, 390, 700)
  const zoomOut = zoomAt(zoomIn, 0.0001, 200, 300, 390, 700)
  assert.equal(zoomIn.scale, MAX_SCALE)
  assert.equal(zoomOut.scale, MIN_SCALE)
  const clamped = clampCamera({ x: 1e9, y: -1e9, scale: 1 }, 390, 700)
  const world = cameraBounds('illustration')
  assert.ok(clamped.x + world.left <= 0)
  assert.ok(clamped.x + world.right >= 390)
  assert.ok(clamped.y + world.top <= 0)
  assert.ok(clamped.y + world.bottom >= 700)
  assert.ok(clamped.x > 390, 'the town may leave the viewport so the meadow can be explored')
  const real = clampCamera({ x: 1e9, y: -1e9, scale: 8 }, 390, 700, 'geographic')
  assert.equal(real.scale, 1.8)
  assert.ok(real.x < 390, 'decorative margins do not alter the geographic map')
  const view = visibleScene({ x: -300, y: -200, scale: 2 }, 400, 600, 0)
  assert.deepEqual(view, { left: 150, top: 100, right: 350, bottom: 400 })
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

test('architecture coverage owns each visible surface once and includes every reference location', async () => {
  const { readFile, access } = await import('node:fs/promises')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  const reference = await read('../src/data/reference-map.json')
  const models = (await read('../src/data/landmark-models.json')).models
  const atlas = await read('../src/data/architecture-tiles.json')
  const surfaces = (await read('../src/data/town-architecture.json')).features
  const owners = new Set(models.map((m: { id: string }) => m.id))
  assert.equal(models.length, 19)
  for (const landmark of reference.landmarks)
    assert.ok(
      models.some((m: { placeId: string }) => m.placeId === landmark.id),
      landmark.name,
    )
  const named = surfaces.filter((f: { owner: string | null }) => f.owner !== null)
  for (const surface of named) assert.ok(owners.has(surface.owner))
  assert.equal(
    models.reduce((sum: number, m: { surfaceCount: number }) => sum + m.surfaceCount, 0),
    named.length,
  )
  assert.equal(atlas.surfaceCount, surfaces.length - named.length)
  assert.equal(new Set(surfaces.map((f: { id: string }) => f.id)).size, surfaces.length)
  for (const model of models) {
    for (const key of ['asset', 'overviewAsset', 'sourceAsset', 'heroAsset'])
      await access(new URL(`../public${model[key]}`, import.meta.url))
  }
  for (const tile of atlas.tiles)
    for (const key of ['asset', 'overviewAsset', 'sourceAsset'])
      await access(new URL(`../public${tile[key]}`, import.meta.url))
})

test('street-house eaves are drawn in their own landmark and every roof reference resolves locally', async () => {
  const { readFile } = await import('node:fs/promises')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  type Point = [number, number]
  type EaveEnd = { tileLips?: [Point[], Point[]][]; timber?: Point[][] }
  type Group = {
    id: string
    houses: unknown[][]
    eaveEnds?: Record<string, EaveEnd>
    roofTones?: Record<string, string>
    roofForms?: Record<string, { rear?: [Point, Point]; ridge?: [Point, Point]; sag?: number }>
    frontFrames?: Record<
      string,
      {
        beam: [Point, Point]
        columns: number[]
        recess?: Point
        infill?: string
        openings?: [number, number, number, number][]
        floors?: number[]
        pierFeet?: [number, number, number][]
      }
    >
    platforms?: {
      rim: Point[]
      rise: number
      flight: [Point, Point, Point, Point]
      steps: number
    }[]
    walls?: [Point[], number, number?, number?][]
    pavingAngle?: number
  }
  const { sites }: { sites: Record<string, Group[]> } = await read('../src/data/street-houses.json')
  const { models } = await read('../src/data/landmark-models.json')
  const groupIds = new Set<string>()
  for (const [site, groups] of Object.entries(sites)) {
    const model = models.find((entry: { id: string }) => entry.id === site)
    assert.ok(model, site)
    const svg = await readFile(new URL(`../public${model.sourceAsset}`, import.meta.url), 'utf8')
    const ids = [...svg.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1])
    const uniqueIds = new Set(ids)
    assert.equal(uniqueIds.size, ids.length, site)
    for (const link of svg.matchAll(/url\(#([^)]+)\)/g)) assert.ok(uniqueIds.has(link[1]), link[1])
    assert.equal(
      [...svg.matchAll(/data-front="/g)].length,
      groups.reduce((count, group) => count + group.houses.length, 0),
      site,
    )
    for (const group of groups) {
      assert.ok(!groupIds.has(group.id) && uniqueIds.has(group.id), group.id)
      groupIds.add(group.id)
      assert.ok(group.pavingAngle === undefined || Number.isFinite(group.pavingAngle))
      for (const [index, form] of Object.entries(group.roofForms ?? {})) {
        assert.ok(Object.hasOwn(group.houses, index) && (form.rear || form.ridge))
        assert.ok(form.sag === undefined || (Number.isFinite(form.sag) && form.sag >= 0))
        for (const edge of [form.rear, form.ridge]) {
          if (edge)
            assert.ok(
              edge.length === 2 &&
                edge.every((point) => point.length === 2 && point.every(Number.isFinite)) &&
                (edge[0][0] !== edge[1][0] || edge[0][1] !== edge[1][1]),
            )
        }
      }
      for (const [points, height, cap, skirt] of group.walls ?? []) {
        assert.ok(skirt === undefined || (Number.isFinite(skirt) && skirt > 0 && skirt < height))
        assert.ok(
          points.length >= 2 &&
            height > 0 &&
            (cap === undefined ||
              (cap > 0 &&
                points
                  .slice(1)
                  .every(
                    ([x, y], offset) => x !== points[offset]![0] || y !== points[offset]![1],
                  ))),
        )
      }
      for (const [index, tone] of Object.entries(group.roofTones ?? {})) {
        assert.ok(
          Object.hasOwn(group.houses, index) &&
            [
              'river-grey',
              'warm-tile',
              'ochre-glaze',
              'smoke-tile',
              'ink-slate',
              'aged-pan',
            ].includes(tone),
        )
      }
      for (const [index, frame] of Object.entries(group.frontFrames ?? {})) {
        assert.ok(Object.hasOwn(group.houses, index))
        assert.ok(
          [...frame.beam, ...(frame.recess ? [frame.recess] : [])].every(
            (point) => point.length === 2 && point.every(Number.isFinite),
          ),
        )
        const roof = svg.indexOf(`id="${group.id}-roof-${index}"`)
        const facade = svg.slice(svg.lastIndexOf('<g data-front=', roof), roof)
        if (frame.infill === 'lime-casements') {
          assert.ok(Array.isArray(frame.openings))
          assert.ok(facade.includes(`data-windows="${frame.openings.length}"`))
          for (const [start, end, head, sill] of frame.openings) {
            assert.ok(0 <= start && start < end && end <= 1)
            assert.ok(0 <= head && head < sill && sill <= 1)
          }
        } else {
          assert.ok(
            frame.columns.length >= 2 &&
              frame.columns.every(
                (at, i) => at >= 0 && at <= 1 && (!i || frame.columns[i - 1]! < at),
              ),
          )
          assert.ok(facade.includes(`data-bays="${frame.columns.length - 1}"`))
        }
        if (frame.infill === 'storeyed-shutters') {
          const floors = frame.floors!
          assert.ok(floors.length >= 3 && floors[0] === 0 && floors.at(-1) === 1)
          assert.ok(floors.slice(1).every((level, floor) => level > floors[floor]!))
          assert.ok(facade.includes(`data-storeys="${floors.length - 1}"`))
        }
        for (const [position, depth, width] of frame.pierFeet ?? [])
          assert.ok(position >= 0 && position <= 1 && depth > 0 && width > 0)
      }
      for (const platform of group.platforms ?? []) {
        assert.ok(platform.rim.length >= 3 && platform.rise > 0 && platform.flight.length === 4)
        assert.ok(
          [...platform.rim, ...platform.flight].every(
            (point) => point.length === 2 && point.every(Number.isFinite),
          ),
        )
        assert.ok(
          Number.isInteger(platform.steps) &&
            platform.steps > 0 &&
            svg.includes(`data-stair-treads="${platform.steps}"`),
        )
      }
      for (const [index, detail] of Object.entries(group.eaveEnds ?? {})) {
        assert.ok(Object.hasOwn(group.houses, index), `${group.id} eave end ${index}`)
        for (const [crest, drip] of detail.tileLips ?? []) {
          assert.ok(crest.length >= 2 && crest.length === drip.length)
          assert.ok(
            [...crest, ...drip].every(
              (point) => point.length === 2 && point.every(Number.isFinite),
            ),
          )
        }
        for (const frame of detail.timber ?? [])
          assert.ok(
            frame.length >= 2 &&
              frame.every((point) => point.length === 2 && point.every(Number.isFinite)),
          )
      }
      for (const [index, house] of group.houses.entries()) {
        assert.ok(uniqueIds.has(`${group.id}-roof-${index}`))
        assert.ok(house.slice(0, 8).every(Number.isFinite))
        assert.ok(
          [
            'plaster',
            'gable',
            'blind-wall',
            'temple',
            'temple-portico',
            'shop',
            'gallery',
            'arcade',
            'canopy',
            'hall',
            'pier-shop',
          ].includes(String(house[8])),
        )
      }
    }
  }
})

test('north gate has two timber levels on masonry and its west bank gables face the lane ends', async () => {
  const { readFile } = await import('node:fs/promises')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const read = async (path: string) => JSON.parse(await text(path))
  const { sites, background } = await read('../src/data/street-houses.json')
  const [base, upper] = sites['north-watchtower']
  const svg = await text('../public/art/landmarks/north-watchtower.svg')
  assert.ok(base.gateTerrace && svg.includes('data-masonry="gate-parapet"'))
  assert.ok(base.frontFrames[0].transom[0] < base.houses[0][7])
  assert.ok(upper.houses[0][7] < base.houses[0][7])
  assert.equal(svg.match(/data-infill="lime-timber"/g)?.length, 2)
  const terrain = await read('../src/data/town-architecture.json')
  const { roofs } = await read('../src/data/roof-volumes.json')
  for (const id of terrain.gateMasonryReplacedByTerrace) {
    assert.ok(!terrain.features.some((surface: { id: string }) => surface.id === id))
    assert.ok(!(id in roofs))
  }
  const court = background['watchtower-bank-houses'].find(
    (group: { id: string }) => group.id === 'watch-west-courts',
  )
  for (const [index, house] of court.houses.entries()) {
    if (house[8] !== 'gable') continue
    const form = court.roofForms[index]
    assert.equal(form.endFace, 'limewash')
    assert.ok(form.ridge[0][1] < form.ridge[1][1])
    assert.ok(form.ridge[1][1] < Math.min(house[3], form.rear[1][1]))
  }
})

test('anonymous street roofs stay in their intersecting background tiles across seams', async () => {
  const { readFile } = await import('node:fs/promises')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const read = async (path: string) => JSON.parse(await text(path))
  type Group = { id: string; replace: [number, number][][]; houses: unknown[][] }
  const { background }: { background: Record<string, Group[]> } = await read(
    '../src/data/street-houses.json',
  )
  const { models } = await read('../src/data/landmark-models.json')
  const { tiles } = await read('../src/data/architecture-tiles.json')
  const { sourceOffset } = await read('../src/data/reference-map.json')
  const groups = Object.values(background).flat()
  const copies = new Map<string, string>()
  for (const model of models) {
    const svg = await text(`../public${model.sourceAsset}`)
    for (const group of groups) assert.ok(!svg.includes(`id="${group.id}"`), model.id)
  }
  for (const tile of tiles) {
    const svg = await text(`../public${tile.sourceAsset}`)
    const ids = [...svg.matchAll(/\bid="([^"]+)"/g)].map((hit) => hit[1])
    const unique = new Set(ids)
    assert.equal(unique.size, ids.length, tile.id)
    for (const link of svg.matchAll(/url\(#([^)]+)\)/g)) assert.ok(unique.has(link[1]), link[1])
    const left = tile.x - sourceOffset.x,
      top = tile.y - sourceOffset.y
    let fronts = 0
    for (const group of groups) {
      const intersects = group.replace.some((ring) => {
        const xs = ring.map(([x]) => x),
          ys = ring.map(([, y]) => y)
        return (
          Math.max(...xs) > left &&
          Math.min(...xs) < left + tile.width &&
          Math.max(...ys) > top &&
          Math.min(...ys) < top + tile.height
        )
      })
      assert.equal(unique.has(group.id), intersects, `${tile.id}: ${group.id}`)
      if (!intersects) continue
      fronts += group.houses.length
      for (const index of group.houses.keys()) {
        const id = `${group.id}-roof-${index}`
        const roof = svg.match(new RegExp(`<g id="${id}">(.+?)</g>`))?.[1]
        assert.ok(roof, id)
        if (copies.has(id)) assert.equal(roof, copies.get(id), id)
        copies.set(id, roof)
      }
    }
    assert.equal([...svg.matchAll(/data-front="/g)].length, fronts, tile.id)
  }
  assert.equal(
    copies.size,
    groups.reduce((count, group) => count + group.houses.length, 0),
  )
  for (const column of [4, 5]) {
    const tile = tiles.find((item: { id: string }) => item.id === `block-${column}-2`)
    assert.match(await text(`../public${tile.sourceAsset}`), /id="west-bank-long-roofs-roof-0"/)
  }
})

test('temple stone banks follow water edges without roofs, join the canal, and keep the causeway dry', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const read = async (path: string) => JSON.parse(await text(path))
  type Point = [number, number]
  type Bank = { id: string; from: Point; to: Point; height: number; hole?: number }
  type Water = { points: Point[]; holes: Point[][]; bankFaces?: Bank[] }
  const { water, walks }: { water: Water[]; walks: { id: string }[] } = await read(
    '../src/data/town-landscape.json',
  )
  const { features, quayFragmentsMovedToLandscape } = await read(
    '../src/data/town-architecture.json',
  )
  const { roofs } = await read('../src/data/roof-volumes.json')
  const { surfaces } = await read('../src/data/street-observations.json')
  const ground = await text('../public/art/native/ground.svg')
  assert.ok(
    !walks.some((walk) => walk.id === 'temple-court') &&
      ground.includes('id="temple-stone-forecourt"'),
  )
  const banks = water.flatMap((region) =>
    (region.bankFaces ?? []).map((bank) => ({ bank, region })),
  )
  for (const id of [
    'temple-west-stone-bank',
    'temple-south-stone-bank',
    'temple-east-stone-bank',
  ]) {
    const matches = banks.filter(({ bank }) => bank.id === id)
    assert.equal(matches.length, 1, id)
    const { bank, region } = matches[0]!
    assert.ok(bank.height > 0 && ground.includes(`<g id="${id}">`))
    const ring = bank.hole === undefined ? region.points : region.holes[bank.hole]!
    for (const [x, y] of [bank.from, bank.to])
      assert.ok(ring.some(([xx, yy]) => x === xx && y === yy))
  }
  const wet = (point: Point) =>
    water.some(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((ring) => pointInRing(point, ring)),
    )
  for (const point of [
    [836, 849],
    [878, 847],
    [911, 843],
    [945, 839.8],
    [956, 838.5],
    [972, 837],
    [988, 836],
    [970, 751],
    [985, 749],
  ] as Point[])
    assert.ok(wet(point), String(point))
  for (const point of [
    [865, 846],
    [939, 833],
    [925, 836],
    [977, 830],
    [984, 743],
    [927, 706],
    [943, 759],
  ] as Point[])
    assert.ok(!wet(point), String(point))
  for (const id of quayFragmentsMovedToLandscape)
    assert.ok(
      !features.some((f: { id: string }) => f.id === id) && !(id in roofs) && !(id in surfaces),
      id,
    )
})

test('canal forks and projected bridge decks have one water mask and dry abutments', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][]; bankFaces?: { id: string }[] }
  type Deck = {
    id: string
    sections?: [Point, Point][]
    x: number
    y: number
    length: number
    angle: number
  }
  const town: { water: Water[]; bridges: Deck[] } = JSON.parse(
    await text('../src/data/town-landscape.json'),
  )
  const at = (point: Point) =>
    town.water.filter(
      ({ points, holes }) =>
        pointInRing(point, points) && !holes.some((hole) => pointInRing(point, hole)),
    )
  const channels: [string, Point[]][] = [
    [
      'watch-west-quay',
      [
        [498, 700],
        [497.5, 706],
        [497.5, 716],
        [501, 735],
        [502, 758],
        [503, 789],
        [503, 825],
        [504.1, 847],
        [505.5, 869],
        [509, 889],
        [514, 908],
        [517, 929],
      ],
    ],
    [
      'merchant-bend-quay',
      [
        [609.2, 744],
        [610, 752],
        [610.5, 759],
      ],
    ],
    [
      'merchant-bend-quay',
      [
        [561, 805],
        [569, 804],
        [574, 802],
        [582, 802],
        [593, 799],
        [602, 796],
        [613, 794],
      ],
    ],
    [
      'fuma-grass-quay',
      [
        [648, 724],
        [664, 721],
        [683, 718],
        [702, 713],
        [723, 712],
        [745, 713],
        [753, 716],
        [763, 720],
        [778, 722],
        [788, 724.1],
        [797, 719.5],
        [805.7, 710.9],
      ],
    ],
    [
      'merchant-bend-quay',
      [
        [631, 960],
        [634, 980],
        [635, 990],
      ],
    ],
    [
      'merchant-bend-quay',
      [
        [645, 990],
        [651, 996.1],
        [666, 996],
        [685, 993],
        [705, 990],
        [714, 988],
        [738, 984],
      ],
    ],
    [
      'stage-arc-quay',
      [
        [1218, 383],
        [1241, 384],
        [1263, 383],
      ],
    ],
    [
      'watch-point-south-course',
      [
        [616, 519],
        [623, 522],
        [633, 525],
        [639, 527],
        [650, 530],
        [661, 528],
        [670, 523],
        [677, 516],
        [681, 513.4],
      ],
    ],
  ]
  for (const [bank, spine] of channels) {
    const region = town.water.find((entry) => entry.bankFaces?.some(({ id }) => id === bank))
    assert.ok(region, bank)
    for (const [index, [endX, endY]] of spine.slice(1).entries()) {
      const [x, y] = spine[index]!
      const steps = Math.ceil(Math.hypot(endX - x, endY - y))
      for (let step = 0; step <= steps; step++) {
        const point: Point = [x + ((endX - x) * step) / steps, y + ((endY - y) * step) / steps]
        const layers = at(point)
        assert.ok(layers.length === 1 && layers[0] === region, `${bank}: ${point}`)
      }
    }
  }
  for (const point of [
    [645, 511],
    [652, 541],
    [625, 715],
    [713, 700],
    [667, 732],
    [647, 965],
    [680, 985],
    [717, 980],
    [955, 540],
    [961, 537],
    [966, 535],
    [971, 533],
    [975, 531],
    [502, 705],
    [510, 840],
    [517, 934],
    [578, 792],
    [584, 814],
    [605, 763],
  ] as Point[])
    assert.equal(at(point).length, 0, String(point))
  const layer = await text('../public/art/native/waterfronts.svg')
  for (const id of [
    'bridge-0',
    'fuma-west-garden-slab',
    'fuma-east-garden-slab',
    'merchant-canal-slab',
    'merchant-east-slab',
    'pagoda-west-slab',
    'lake-east-stone-slab',
    'teahouse-north-timber',
    'east-residence-slab',
    'west-boathouse-footbridge',
    'west-island-bank-slab',
    'west-ditch-plankstone',
    'family-west-footbridge',
    'family-quay-footbridge',
    'south-east-quay-slab',
  ])
    assert.ok(town.bridges.find((deck) => deck.id === id)?.sections?.length, id)
  for (const deck of town.bridges) {
    const { id } = deck
    assert.equal(at([deck.x, deck.y]).length, 1, `${id}: water below deck`)
    if (deck.sections) {
      assert.ok(layer.includes(`id="${id}"`), id)
      for (const [left, right] of [deck.sections[0]!, deck.sections.at(-1)!])
        assert.equal(at([(left[0] + right[0]) / 2, (left[1] + right[1]) / 2]).length, 0, id)
    } else {
      const radians = (deck.angle * Math.PI) / 180
      for (const side of [-0.5, 0.5])
        assert.equal(
          at([
            deck.x + side * deck.length * Math.cos(radians),
            deck.y + side * deck.length * Math.sin(radians),
          ]).length,
          0,
          id,
        )
    }
  }
})

test('one continuous southern canal serves both Pu family footbridges without flooding the gables', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  type Region = { points: Point[]; holes: Point[][] }
  const { water }: { water: Region[] } = JSON.parse(
    await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'),
  )
  const covering = (point: Point) =>
    water.filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  const channel: Point[] = [
    [1046, 1145.7],
    [1061.25, 1144.4],
    [1076.4, 1141.2],
    [1096.6, 1137.7],
    [1110, 1135.6],
    [1117.2, 1133.2],
    [1122, 1131.0],
  ]
  const [river] = covering(channel[0]!)
  assert.ok(river)
  for (const [index, start] of channel.slice(0, -1).entries()) {
    const end = channel[index + 1]!
    for (let step = 0; step <= 16; step++) {
      const location: Point = [
        start[0] + ((end[0] - start[0]) * step) / 16,
        start[1] + ((end[1] - start[1]) * step) / 16,
      ]
      const hit = covering(location)
      assert.equal(hit.length, 1)
      assert.equal(hit[0], river)
    }
  }
  for (const point of [
    [1068, 1123],
    [1079.4, 1119],
    [1090, 1131],
    [1106, 1128],
  ] as Point[])
    assert.equal(covering(point).length, 0)
})

test('merchant bend masonry stays on the dry island after opening the western channel', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  type Face = { id: string; from: Point; to: Point; hole?: number }
  type Region = { points: Point[]; holes: Point[][]; bankFaces?: Face[]; islandQuays?: Face[] }
  const { water }: { water: Region[] } = JSON.parse(
    await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'),
  )
  const matches = water.flatMap((region) =>
    (region.bankFaces ?? [])
      .filter(({ id }) => id === 'merchant-bend-quay')
      .map((face) => ({ region, face })),
  )
  assert.equal(matches.length, 1)
  const { region, face } = matches[0]!
  assert.notEqual(face.hole, undefined)
  const island = region.holes[face.hole!]!
  for (const point of [
    [644, 763],
    [655, 843],
    [660, 902],
  ] as Point[])
    assert.ok(pointInRing(point, island))
  for (const point of [
    [610, 752],
    [574, 802],
  ] as Point[]) {
    assert.ok(pointInRing(point, region.points))
    assert.ok(!region.holes.some((ring) => pointInRing(point, ring)))
  }
  for (const body of water) {
    for (const bank of [...(body.bankFaces ?? []), ...(body.islandQuays ?? [])]) {
      const ring = bank.hole === undefined ? body.points : body.holes[bank.hole]!
      for (const [x, y] of [bank.from, bank.to])
        assert.ok(
          ring.some(([east, south]) => x === east && y === south),
          bank.id,
        )
    }
  }
})

test('one visitor canal passes under both galleries and leaves their landings on dry ground', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][]; bankFaces?: { id: string }[] }
  const { water }: { water: Water[] } = JSON.parse(await text('../src/data/town-landscape.json'))
  const at = (point: Point) =>
    water.filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((ring) => pointInRing(point, ring)),
    )
  const [canal] = at([809, 476])
  assert.ok(canal)
  for (const id of ['visitor-grassy-quay', 'visitor-south-gallery-quay'])
    assert.ok(canal.bankFaces?.some((bank) => bank.id === id))
  for (const northing of [472, 478]) {
    for (let easting = 735; easting <= 889; easting++) {
      const covering = at([easting, northing])
      assert.equal(covering.length, 1, `${easting},${northing}`)
      assert.equal(covering[0], canal)
    }
  }
  for (const point of [
    [759, 443],
    [810, 443],
    [790, 514],
    [844, 509],
  ] as Point[])
    assert.equal(at(point).length, 0, String(point))
  const waterfront = await text('../public/art/native/waterfronts.svg')
  assert.ok(waterfront.includes('id="museum-stone-landing"'))
})

test('visitor trace replacement clips only its own part of the shared roof in every tile', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const { partialTraceReplacements } = JSON.parse(await text('../src/data/street-houses.json'))
  const [ring] = partialTraceReplacements['roof-1017']
  assert.ok(pointInRing([790, 475], ring) && !pointInRing([920, 443], ring))
  const { tiles } = JSON.parse(await text('../src/data/architecture-tiles.json'))
  const copies = new Set<string>()
  let count = 0
  for (const tile of tiles) {
    const svg = await text(`../public${tile.sourceAsset}`)
    if (!svg.includes('id="finish-roof-1017"')) continue
    const mask = svg.match(/<mask id="clear-roof-1017"[^>]*>.*?<\/mask>/)?.[0]
    assert.ok(
      mask?.includes(ring.map(([x, y]: number[]) => `${x!.toFixed(2)},${y!.toFixed(2)}`).join(' ')),
    )
    assert.ok(svg.includes('<g mask="url(#clear-roof-1017)">'))
    copies.add(mask!)
    count++
  }
  assert.ok(count > 1)
  assert.equal(copies.size, 1)
})

test('street and watchtower canals flow below crossings without flooding either bank', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  type Point = [number, number]
  type Region = { points: Point[]; holes: Point[][]; bankFaces?: { id: string }[] }
  type Bridge = { id: string; x: number; y: number; length: number; angle: number }
  const { water, bridges, scope }: { water: Region[]; bridges: Bridge[]; scope: Point[] } =
    await read('../src/data/town-landscape.json')
  assert.deepEqual(scope, (await read('../src/data/reference-map.json')).scope)
  const at = (point: Point) =>
    water.filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((ring) => pointInRing(point, ring)),
    )
  const channels: [string, Point[], string[]][] = [
    [
      'teahouse-east-grass-quay',
      [
        [869.7, 931],
        [875, 934],
        [884, 937.2],
        [893, 936.4],
        [906, 934],
        [917.5, 930],
        [931, 925.5],
        [945, 920.4],
        [956, 915.4],
        [969.7, 910],
        [981.2, 905.8],
      ],
      ['bridge-11'],
    ],
    [
      'watch-willow-quay',
      [
        [590, 524],
        [586, 539],
        [572, 551],
        [575, 561],
        [585, 571],
        [586.3, 585.2],
        [586, 599],
        [588, 610],
      ],
      ['watch-east-footbridge'],
    ],
    [
      'watch-west-quay',
      [
        [530, 513],
        [525, 530],
        [521, 546],
        [519, 558],
        [518.5, 575],
        [517, 585],
        [515, 594],
        [513, 602],
      ],
      [],
    ],
    [
      'designer-shop-bank',
      [
        [1270, 633.5],
        [1269.7, 643.5],
        [1269.9, 671],
        [1269.5, 682.5],
        [1272, 685],
        [1282, 686],
        [1287, 686.5],
        [1295, 689],
        [1305, 690],
        [1312, 692],
        [1320.7, 695.1],
        [1328, 699],
        [1336, 703],
        [1346, 708],
      ],
      ['designer-lane-slab', 'designer-west-slab', 'designer-fork-slab', 'bridge-1'],
    ],
    [
      'dressing-timber-bank',
      [
        [607, 1181],
        [613, 1180],
        [616.5, 1180.5],
        [618.6, 1186.2],
        [622.3, 1188.5],
        [633.5, 1188.7],
        [644, 1188.7],
        [651.1, 1187.6],
        [662, 1183],
        [670, 1181],
        [683, 1178.7],
        [704, 1178.4],
        [723, 1175.5],
        [738, 1173.4],
        [748.5, 1177.2],
        [757.3, 1179],
        [775, 1176.3],
      ],
      ['bridge-12', 'dressing-garden-slab', 'bridge-16'],
    ],
  ]
  for (const [bank, spine, crossings] of channels) {
    const region = water.find((entry) => entry.bankFaces?.some((face) => face.id === bank))
    assert.ok(region, bank)
    for (const [index, [x, y]] of spine.slice(1).entries()) {
      const start = spine[index]!
      const count = Math.ceil(2 * Math.hypot(x - start[0], y - start[1]))
      for (let step = 0; step <= count; step++) {
        const covers = at([
          start[0] + ((x - start[0]) * step) / count,
          start[1] + ((y - start[1]) * step) / count,
        ])
        assert.equal(covers.length, 1, `${bank}: ${index}/${step}`)
        assert.equal(covers[0], region)
      }
    }
    for (const id of crossings) {
      const bridge = bridges.find((entry) => entry.id === id)!
      assert.equal(at([bridge.x, bridge.y])[0], region, id)
      const angle = (bridge.angle * Math.PI) / 180
      for (const side of [-0.5, 0.5]) {
        const abutment: Point = [
          bridge.x + side * bridge.length * Math.cos(angle),
          bridge.y + side * bridge.length * Math.sin(angle),
        ]
        assert.ok(pointInRing(abutment, scope), id)
        assert.equal(at(abutment).length, 0, id)
      }
      if (id === 'bridge-1') {
        for (let northing = 448; northing <= 516; northing++)
          assert.equal(at([1413, northing])[0], region, `north bridge: ${northing}`)
      }
    }
  }
  for (const point of [
    [1377, 681],
    [890, 929.9],
    [931, 917.1],
    [956, 910],
    [630.1, 492],
    [648.8, 499.6],
    [656.3, 498.4],
    [525, 577],
    [568, 579],
    [545, 580],
    [598, 575],
    [1325, 674],
    [1391, 582],
    [716, 1167],
    [670, 1172],
    [724, 1186],
    [747, 1169],
  ] as Point[])
    assert.equal(at(point).length, 0, String(point))
  const { features, plantFragmentsMovedToLandscape } = await read(
    '../src/data/town-architecture.json',
  )
  const { roofs } = await read('../src/data/roof-volumes.json')
  for (const retired of plantFragmentsMovedToLandscape)
    assert.ok(
      !features.some((entry: { id: string }) => entry.id === retired) && !(retired in roofs),
      retired,
    )
})

test('east quay timber eaves and post feet sit on the dry side of the two stone landings', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][] }
  const { water, plazas }: { water: Water[]; plazas: { id: string; points: Point[] }[] } =
    await read('../src/data/town-landscape.json')
  const { background } = await read('../src/data/street-houses.json')
  const row = background['east-west-bank'].find(
    (group: { id: string }) => group.id === 'east-quay-timber-row',
  )
  const wet = (point: Point) =>
    water.some(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  for (const [left, top, right, end, , , , height] of row.houses) {
    for (const fraction of [0, 0.25, 0.5, 0.75, 1]) {
      assert.equal(
        wet([left + (right - left) * fraction, top + (end - top) * fraction + height]),
        false,
      )
    }
  }
  for (const [id, point] of [
    ['east-quay-upper-landing', [1167.5, 1024]],
    ['east-quay-lower-landing', [1161, 1039]],
  ] as [string, Point][]) {
    assert.ok(pointInRing(point, plazas.find((plaza) => plaza.id === id)!.points) && !wet(point))
  }
  for (const point of [
    [1173, 1041],
    [1179, 1031],
    [1195, 990],
  ] as Point[])
    assert.ok(wet(point))
})

test('both hotel gallery roofs meet at their mitres and the open western moat reaches the south canal', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][] }
  const { water }: { water: Water[] } = await read('../src/data/town-landscape.json')
  const wet = (point: Point, region: Water) =>
    pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole))
  const moat = water.find((region) => wet([1206, 615], region))!
  assert.ok(moat && wet([1278, 606], moat) && wet([1136, 533], moat))
  for (let northing = 559; northing <= 602; northing += 0.25) {
    const channel = Array.from({ length: 53 }, (_, index) => 1126 + index * 0.25).filter(
      (easting) => wet([easting, northing], moat),
    )
    assert.ok(channel.length >= 3, `pinched western water at ${northing}`)
    assert.ok(channel.at(-1)! - channel[0]! === (channel.length - 1) * 0.25)
  }
  for (const point of [
    [1125.5, 584],
    [1133, 584],
    [1206, 577],
    [1206, 605],
  ] as Point[])
    assert.ok(!water.some((region) => wet(point, region)), String(point))
  type Gallery = {
    id: string
    houses: unknown[][]
    roofForms: Record<string, { rear: Point[]; ridge: Point[] }>
  }
  const { sites }: { sites: Record<string, Gallery[]> } = await read(
    '../src/data/street-houses.json',
  )
  for (const name of ['zen-water-galleries', 'zen-court-galleries']) {
    const group = sites['zen-courtyard']!.find((item) => item.id === name)!
    const front = group.houses[2]!
    for (const wing of [0, 1]) {
      assert.deepEqual(group.houses[wing]!.slice(2, 4), front.slice(2 * wing, 2 * wing + 2))
      for (const edge of ['rear', 'ridge'] as const)
        assert.deepEqual(group.roofForms[wing]![edge][1], group.roofForms[2]![edge][wing])
    }
  }
})

test('measured roof accents reference editable surfaces and resolve inside each published street tile', async () => {
  const { readFile } = await import('node:fs/promises')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const read = async (path: string) => JSON.parse(await text(path))
  type Group = { id: string; surfaceFinish?: string[]; slateOutlines?: string[] }
  type Areas = Record<string, Group[]>
  const { sites, background }: { sites: Areas; background: Areas } = await read(
    '../src/data/street-houses.json',
  )
  const { features } = await read('../src/data/town-architecture.json')
  const groups = Object.values({ ...sites, ...background })
    .flat()
    .filter((group) => group.surfaceFinish || group.slateOutlines)
  for (const group of groups)
    for (const surface of [...(group.surfaceFinish ?? []), ...(group.slateOutlines ?? [])])
      assert.ok(
        features.some(
          (f: { id: string; kind: string }) =>
            f.id === surface && ['roof', 'gold'].includes(f.kind),
        ),
        surface,
      )
  const { models } = await read('../src/data/landmark-models.json')
  const { tiles } = await read('../src/data/architecture-tiles.json')
  const published = new Set<string>()
  for (const { sourceAsset } of [...models, ...tiles]) {
    const svg = await text(`../public${sourceAsset}`)
    for (const group of groups) {
      if (!svg.includes(`id="${group.id}"`)) continue
      published.add(group.id)
      if (group.slateOutlines)
        assert.ok(svg.includes(`mask="url(#${group.id}-measured-slate)"`), group.id)
      if (group.surfaceFinish)
        assert.ok(
          svg.includes(`id="${group.id}-tile-accents"`) &&
            svg.includes(`<use href="#${group.id}-tile-accents"`),
          group.id,
        )
    }
  }
  assert.equal(published.size, groups.length)
})

test('street eaves mask the specified trees in their published canopy tiles', async () => {
  const { readFile } = await import('node:fs/promises')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  const { trees } = await read('../src/data/town-landscape.json')
  const { tiles } = await read('../src/data/native-landscape.json')
  type Areas = Record<string, { houses: unknown[][]; behindEaves?: Record<string, number[]> }[]>
  const { sites, background }: { sites: Areas; background: Areas } = await read(
    '../src/data/street-houses.json',
  )
  const canopies = await Promise.all(
    tiles.map(async ({ sourceAsset }: { sourceAsset: string }) =>
      readFile(new URL(`../public${sourceAsset}`, import.meta.url), 'utf8'),
    ),
  )
  for (const group of Object.values({ ...sites, ...background }).flat()) {
    for (const [treeId, indices] of Object.entries(group.behindEaves ?? {})) {
      assert.equal(trees.filter((tree: { id: string }) => tree.id === treeId).length, 1, treeId)
      assert.ok(
        indices.length &&
          indices.every(
            (index) => Number.isInteger(index) && index >= 0 && index < group.houses.length,
          ),
      )
      const key = `tree-depth-${treeId}`
      assert.ok(
        canopies.some(
          (svg) => svg.includes(`<mask id="${key}"`) && svg.includes(`mask="url(#${key})"`),
        ),
        treeId,
      )
    }
  }
})

test('street joinery belongs to active elevations and its plaster sits behind the original windows', async () => {
  const { readFile } = await import('node:fs/promises')
  const read = async (name: string) =>
    JSON.parse(await readFile(new URL(`../src/data/${name}.json`, import.meta.url), 'utf8'))
  type Point = [number, number]
  type Detail = {
    id: string
    plasterReturns?: Point[][]
    pieces: { beam?: Point[]; height?: number }[]
  }
  const streets = await read('street-houses')
  const surfaces: { id: string; bounds: number[] }[] = (await read('town-architecture')).features
  const tiles: { sourceAsset: string }[] = (await read('architecture-tiles')).tiles
  const artwork = await Promise.all(
    tiles.map((tile) => readFile(new URL(`../public${tile.sourceAsset}`, import.meta.url), 'utf8')),
  )
  for (const [key, detail] of Object.entries(streets.joinery as Record<string, Detail>)) {
    const surface = surfaces.find((item) => item.id === key)
    assert.ok(surface, key)
    const [left, top, width, height] = surface.bounds as [number, number, number, number]
    const group = `id="${detail.id}"`
    const copies = artwork.filter((svg) => svg.includes(group))
    assert.ok(copies.length, key)
    for (const piece of detail.pieces) {
      for (const [x, y] of piece.beam ?? []) {
        assert.ok(x >= left - 1 && x <= left + width + 1, key)
        assert.ok(y >= top - 1 && y + (piece.height ?? 0) <= top + height + 7, key)
      }
    }
    for (const svg of copies) {
      const body = svg.indexOf(`id="finish-${key}"`)
      assert.ok(body >= 0 && body < svg.indexOf(group), key)
      if (detail.plasterReturns) {
        const plaster = svg.indexOf(`id="${detail.id}-plaster"`)
        assert.ok(plaster >= 0 && plaster < body, key)
      }
    }
  }
})

test('the southwest spring ends at the stone bank without wetting the west path', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][] }
  const { water }: { water: Water[] } = JSON.parse(
    await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'),
  )
  const wet = (point: Point) =>
    water.filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  const spring = wet([172, 1252])
  assert.equal(spring.length, 1)
  for (const point of [
    [170, 1256],
    [166, 1263],
    [165, 1272],
  ] as Point[])
    assert.deepEqual(wet(point), spring)
  for (const point of [
    [171, 1244],
    [164, 1256],
    [175, 1252],
  ] as Point[])
    assert.equal(wet(point).length, 0)
})

test('native map assets contain editable drawing commands without embedded raster imagery', async () => {
  const { readFile, access } = await import('node:fs/promises')
  const { createHash } = await import('node:crypto')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  const landscape = await read('../src/data/native-landscape.json')
  const town = await read('../src/data/town-landscape.json')
  const models = (await read('../src/data/landmark-models.json')).models
  const blocks = (await read('../src/data/architecture-tiles.json')).tiles
  const volumes = await read('../src/data/roof-volumes.json')
  for (const [file, key] of [
    ['town-architecture.json', 'geometrySha256'],
    ['roof-guides.json', 'guideSha256'],
  ]) {
    const bytes = await readFile(new URL(`../src/data/${file}`, import.meta.url))
    assert.equal(volumes[key!], createHash('sha256').update(bytes).digest('hex'), file)
  }
  assert.equal(landscape.treeCount, town.trees.length)
  assert.ok(town.trees.length > 300)
  assert.equal(landscape.bridgeCount, town.bridges.length)
  for (const layer of [landscape.ground, landscape.waterfronts]) {
    await access(new URL(`../public${layer.replace(/\.svg$/, '.webp')}`, import.meta.url))
  }
  const assets = [
    landscape.ground,
    landscape.waterMask,
    landscape.waterfronts,
    ...landscape.tiles.map((t: { sourceAsset: string }) => t.sourceAsset),
    ...[...models, ...blocks].map((t: { sourceAsset: string }) => t.sourceAsset),
  ]
  for (const asset of assets) {
    const svg = await readFile(new URL(`../public${asset}`, import.meta.url), 'utf8')
    assert.match(svg, /<(?:path|polygon|polyline)\b/, asset)
    assert.doesNotMatch(
      svg,
      /<image\b|data:image|\.jpe?g|\.png|puyuan-reference|puyuan-layered/i,
      asset,
    )
  }
})

test('the pagoda stands on dry stone with a continuous narrow inlet along the west side', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  const read = async (name: string) =>
    JSON.parse(await readFile(new URL(`../src/data/${name}.json`, import.meta.url), 'utf8'))
  const { water }: { water: { points: Point[]; holes: Point[][] }[] } = await read('town-landscape')
  const { terrace } = (await read('landmark-structures')).sites['temple-pagoda']
  const wet = (point: Point) =>
    water.some(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  for (let northing = 510; northing <= 541; northing += 0.5) {
    assert.ok(wet([890, northing]), `west inlet at ${northing}`)
    assert.ok(!wet([897, northing]), `paving at ${northing}`)
  }
  for (const point of terrace as Point[]) assert.ok(!wet(point))
  assert.ok(wet([939, 510]))
  assert.ok(!wet([936, 526]))
})

test('south garden lanes stay dry and the east timber crossing joins the two banks', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][] }
  type Walk = { id: string; profile: [number, number, number][] }
  const { water, walks, groundBeds, bridges } = await read('../src/data/town-landscape.json')
  const wet = (point: Point) =>
    (water as Water[]).filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  const garden = groundBeds.find(({ id }: { id: string }) => id === 'south-lane-court-grass')
  const groups = (await read('../src/data/street-houses.json')).background['south-garden-lane']
  const court = groups.find(({ id }: { id: string }) => id === 'south-lane-grass-court')
  const center: Point = [1093, 1180]
  assert.ok(pointInRing(center, garden.points) && pointInRing(center, court.courts[0]))
  assert.equal(wet(center).length, 0)
  for (const side of ['east', 'west']) {
    const lane = (walks as Walk[]).find(({ id }) => id === `south-lane-court-${side}`)
    assert.ok(lane)
    for (const [index, [x, y, width]] of lane.profile.slice(1).entries()) {
      const [beforeX, beforeY] = lane.profile[index]
      assert.ok(width > 0 && (side === 'east' ? x > center[0] : x < center[0]))
      for (let step = 0; step <= 8; step++) {
        const point: Point = [beforeX + ((x - beforeX) * step) / 8, beforeY + ((y - beforeY) * step) / 8]
        assert.equal(wet(point).length, 0)
      }
    }
  }
  const crossing = bridges.find(({ id }: { id: string }) => id === 'bridge-9')
  const [rear, front] = crossing.sections[Math.floor(crossing.sections.length / 2)] as [Point, Point]
  assert.equal(wet([(rear[0] + front[0]) / 2, (rear[1] + front[1]) / 2]).length, 1)
  for (const bank of [[1183, 956.5], [1236.7, 962]] as Point[]) assert.equal(wet(bank).length, 0)
})

test('stage glass bays stay on the promenade, with separate dry eaves and one lake below the platform', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  const text = (path: string) => readFile(new URL(path, import.meta.url), 'utf8')
  const read = async (path: string) => JSON.parse(await text(path))
  type Point = [number, number]
  type Water = { points: Point[]; holes: Point[][]; bankFaces?: { id: string }[] }
  const { water, trees }: { water: Water[]; trees: { id: string }[] } = await read(
    '../src/data/town-landscape.json',
  )
  const { canopy, deck } = (await read('../src/data/landmark-structures.json')).sites[
    'waterside-stage'
  ]
  const svg = await text('../public/art/landmarks/waterside-stage.svg')
  assert.equal((svg.match(/data-glazing-bay=/g) ?? []).length, canopy.ribs.length - 1)
  assert.equal(canopy.muntins.length, canopy.ribs.length - 1)
  for (const [index, bars] of (canopy.muntins as number[][][]).entries()) {
    assert.ok(svg.includes(`clip-path="url(#stage-glass-panel-${index})"`))
    for (const [startX, startY, endX, endY, gauge] of bars as [
      number,
      number,
      number,
      number,
      number,
    ][]) {
      assert.ok(Math.hypot(endX - startX, endY - startY) > 3)
      assert.ok([0, 1, 2].includes(gauge))
    }
  }
  assert.ok(svg.includes('id="stage-floating-platform"'))
  const lake = water.find((region) => region.bankFaces?.some(({ id }) => id === 'stage-arc-quay'))
  assert.ok(lake)
  const at = (point: Point) =>
    water.filter(
      (region) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  const along = (start: Point, end: Point, ratio: number): Point => [
    start[0] + (end[0] - start[0]) * ratio,
    start[1] + (end[1] - start[1]) * ratio,
  ]
  for (let bay = 1; bay < canopy.ribs.length; bay++) {
    const [back, lip, drop] = canopy.ribs[bay - 1] as [Point, Point, number]
    const [nextBack, nextLip, nextDrop] = canopy.ribs[bay] as [Point, Point, number]
    for (let radial = 0; radial <= 20; radial++) {
      const rear = along(back, nextBack, radial / 20)
      const foot = along(
        [lip[0], lip[1] + drop + 1],
        [nextLip[0], nextLip[1] + nextDrop + 1],
        radial / 20,
      )
      for (let depth = 0; depth <= 40; depth++)
        assert.equal(at(along(rear, foot, depth / 40)).length, 0, `stage bay ${bay}`)
    }
  }
  for (const point of [
    [986, 329],
    [997, 338],
    [1001, 332],
  ] as Point[])
    assert.equal(at(point).length, 0)
  for (const ring of [deck.corners, ...deck.sideFittings] as Point[][])
    for (const [index, corner] of ring.entries())
      for (let step = 0; step <= 16; step++) {
        const regions = at(along(corner, ring[(index + 1) % ring.length]!, step / 16))
        assert.equal(regions.length, 1)
        assert.equal(regions[0], lake)
      }
  const { tiles } = await read('../src/data/native-landscape.json')
  const layers = await Promise.all(
    tiles.map((tile: { sourceAsset: string }) => text(`../public${tile.sourceAsset}`)),
  )
  for (const id of canopy.rearTrees) {
    assert.ok(
      trees.some((tree) => tree.id === id),
      id,
    )
    assert.ok(
      layers.some((layer) => layer.includes(`mask="url(#tree-depth-${id})"`)),
      id,
    )
  }
  const { features, stageFragmentsReplacedByStructure } = await read(
    '../src/data/town-architecture.json',
  )
  const { roofs } = await read('../src/data/roof-volumes.json')
  const { surfaces } = await read('../src/data/street-observations.json')
  for (const id of stageFragmentsReplacedByStructure) {
    assert.ok(
      !features.some((entry: { id: string }) => entry.id === id) &&
        !(id in roofs) &&
        !(id in surfaces),
      id,
    )
  }
})

test('temple garden paths meet opposite dry ends without paving across the canal', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  type Walk = { id: string; profile: [number, number, number][] }
  const town = JSON.parse(await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'))
  const wet = (point: Point) => town.water.some((region: { points: Point[]; holes: Point[][] }) =>
    pointInRing(point, region.points) && !region.holes.some((ring) => pointInRing(point, ring)),
  )
  const profile = (id: string) => (town.walks as Walk[]).find((walk) => walk.id === id)!.profile
  const west = profile('temple-garden-west-approach')
  const east = profile('temple-garden-east-approach')
  const bridge = town.bridges.find(({ id }: { id: string }) => id === 'bridge-5')
  for (const [x, y] of [...west, ...east]) assert.ok(!wet([x, y]))
  for (const [tip, section] of [[west.at(-1), bridge.sections[0]], [east[0], bridge.sections.at(-1)]]) {
    const [left, right] = section
    assert.ok(Math.hypot(tip[0] - (left[0] + right[0]) / 2, tip[1] - (left[1] + right[1]) / 2) < 1)
  }
  assert.ok(wet([bridge.x, bridge.y]))
  assert.deepEqual(east.at(-1), profile('street-temple-west-lane-18')[0])
})

test('the designer quay lane meets the dry north end of the west slab bridge', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  const town = JSON.parse(await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'))
  const lane = town.walks.find(({ id }: { id: string }) => id === 'street-designer-quay-lane-26')
  const bridge = town.bridges.find(({ id }: { id: string }) => id === 'designer-west-slab')
  assert.ok(lane && bridge)
  const radians = (bridge.angle * Math.PI) / 180
  const station = (fraction: number): Point => [
    bridge.x + (fraction - 0.5) * bridge.length * Math.cos(radians),
    bridge.y + (fraction - 0.5) * bridge.length * Math.sin(radians),
  ]
  const wet = (point: Point) => town.water.some((region: { points: Point[]; holes: Point[][] }) =>
    pointInRing(point, region.points) && !region.holes.some((ring) => pointInRing(point, ring)),
  )
  const north = station(0)
  const south = station(1)
  const [endX, endY] = lane.profile.at(-1)
  assert.ok(Math.hypot(endX - north[0], endY - north[1]) < 1, 'lane must reach the northern abutment')
  assert.ok(south[0] < north[0] && south[1] > north[1])
  assert.ok(!wet([endX, endY]) && !wet(north) && !wet(south))
  const crossing = Array.from({ length: 41 }, (_, index) => wet(station(index / 40)))
  assert.ok(crossing[20])
  assert.equal(crossing.filter((inWater, index) => inWater && !crossing[index - 1]).length, 1)
})

test('native water surrounds boat hulls and the stage deck but not the promenade', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  const town = JSON.parse(
    await readFile(new URL('../src/data/town-landscape.json', import.meta.url), 'utf8'),
  )
  const wet = (point: Point) =>
    town.water.some(
      (region: { points: Point[]; holes: Point[][] }) =>
        pointInRing(point, region.points) && !region.holes.some((hole) => pointInRing(point, hole)),
    )
  for (const boat of town.boats) {
    const angle = (boat.angle * Math.PI) / 180
    const hull: Point[] = [
      [-14, 0],
      [-11, 4],
      [0, 6],
      [9, 5],
      [16, -1],
      [9, -4],
      [0, 0],
    ]
    for (const [hullX, down] of hull) {
      const across = boat.bow === 'west' ? -hullX : hullX
      assert.ok(
        wet([
          boat.x + boat.scale * (across * Math.cos(angle) - down * Math.sin(angle)),
          boat.y + boat.scale * (across * Math.sin(angle) + down * Math.cos(angle)),
        ]),
        boat.id,
      )
    }
  }
  const bridge = town.bridges.find((item: { id: string }) => item.id === 'east-islet-arch')
  assert.ok(bridge && wet([bridge.x, bridge.y]))
  const radians = (bridge.angle * Math.PI) / 180
  for (const end of [-0.5, 0.5])
    assert.ok(
      !wet([
        bridge.x + end * bridge.length * Math.cos(radians),
        bridge.y + end * bridge.length * Math.sin(radians),
      ]),
    )
  for (const point of [
    [1334, 718],
    [1333, 723],
    [1303, 769],
    [1354, 770],
  ] as Point[])
    assert.ok(wet(point), String(point))
  for (const point of [
    [1359, 725],
    [1329, 761],
    [1303, 795],
    [1292, 805],
  ] as Point[])
    assert.ok(!wet(point), String(point))
  for (const point of [
    [1040, 357],
    [1077, 354],
    [1082, 372],
    [1044, 376],
    [1077, 376],
  ] as Point[])
    assert.ok(wet(point), String(point))
  for (const point of [
    [1031, 308],
    [1113, 294],
    [1090, 330],
  ] as Point[])
    assert.ok(!wet(point), String(point))
})

test('ordinary infill houses stay on dry land from the rear eave to the foot of the wall', async () => {
  const { readFile } = await import('node:fs/promises')
  const { pointInRing } = await import('../src/lib/geography.ts')
  type Point = [number, number]
  type House = [number, number, number, number, number, string, number?]
  type Water = { points: Point[]; holes: Point[][] }
  const read = async (path: string) =>
    JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'))
  const { water }: { water: Water[] } = await read('../src/data/town-landscape.json')
  const { sites }: { sites: Record<string, { houses?: House[] }> } = await read(
    '../src/data/town-completions.json',
  )
  const regions = water.map(({ points, holes }) => ({
    points,
    holes,
    left: Math.min(...points.map(([x]) => x)),
    right: Math.max(...points.map(([x]) => x)),
    top: Math.min(...points.map(([, y]) => y)),
    bottom: Math.max(...points.map(([, y]) => y)),
  }))
  for (const [site, group] of Object.entries(sites)) {
    for (const [index, [x, y, width, depth, height, , degrees = 0]] of (
      group.houses ?? []
    ).entries()) {
      const angle = (degrees * Math.PI) / 180
      for (let down = 0; down <= depth + height; down++) {
        const left = down <= depth ? 0 : 2
        const right =
          down < depth - 3 ? width : width + 2 - 2 * Math.max(0, down - depth - height + 2)
        for (let across = left; across <= right; across++) {
          const point: Point = [
            x + across * Math.cos(angle) - down * Math.sin(angle),
            y + across * Math.sin(angle) + down * Math.cos(angle),
          ]
          assert.ok(
            !regions.some(
              (region) =>
                region.left <= point[0] &&
                point[0] <= region.right &&
                region.top <= point[1] &&
                point[1] <= region.bottom &&
                pointInRing(point, region.points) &&
                !region.holes.some((hole) => pointInRing(point, hole)),
            ),
            `${site} house ${index} at ${point}`,
          )
        }
      }
    }
  }
})
